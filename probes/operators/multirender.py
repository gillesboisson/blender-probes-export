import time
import bpy

from bpy.types import Operator


class RenderBatch:
    # Define some variables to register
    _timer = None
    nb_shots = 0
    shot_index = 0
    isCancelled = None
    # rendering = None
    __renderState = "OFF"
    setupRenderDelegate = None
    onRenderComplete = None
    onStateChanged = None
    # onCancelled = None
    # onComplete = None

    __defaultRenderBatch = None

    @classmethod
    def getDefault(cls) -> "RenderBatch":
        if RenderBatch.__defaultRenderBatch is None:
            RenderBatch.__defaultRenderBatch = RenderBatch()
        return RenderBatch.__defaultRenderBatch
    
    @classmethod
    def disposeDefault(cls):
        if RenderBatch.__defaultRenderBatch is not None:
            RenderBatch.__defaultRenderBatch.reset()
        RenderBatch.__defaultRenderBatch = None

    # Define the handler functions. I use pre and
    # post to know if Blender "is rendering"
    def __preRender(self, scene, context=None):
        # print("Pre Render")
        if self.__renderState == "RENDER_STARTED":
            self.setRenderState("IN_PROGRESS")

    def __postRender(self, scene, context=None):
        # print("Post Render")
        if self.__renderState == "IN_PROGRESS":
            self.setRenderState("RENDER_COMPLETE")

    def __renderCancelled(self, scene, context=None):
        if self.__renderState != "OFF":
            self.setRenderState("CANCELLED")

    def cancel(self, context):
        self.setRenderState("CANCELLED")

    def reset(self):
        self.__clearListenners(bpy.context)

        self.onRenderComplete = None
        self.onStateChanged = None
        self.operator = None
        self.nb_shots = 0
        self.shot_index = 0
        self.setRenderState("OFF")

    def __clearListenners(self, context):
        # print("> __clearListenners")
 
        try:
            bpy.app.handlers.render_init.remove(self.__preRender)
            bpy.app.handlers.render_write.remove(self.__postRender)
            bpy.app.handlers.render_cancel.remove(self.__renderCancelled)
        except:
            pass


        if self._timer is not None:
            bpy.context.window_manager.event_timer_remove(self._timer)
            self._timer = None


    def __addListenners(self, context):
        self.__clearListenners(context)
        
        bpy.app.handlers.render_init.append(self.__preRender)
        bpy.app.handlers.render_write.append(self.__postRender)
        bpy.app.handlers.render_cancel.append(self.__renderCancelled)

        # The timer gets created and the modal handler
        # is added to the window manager
        if self._timer is None:
            self._timer = context.window_manager.event_timer_add( 
                0.5, window=context.window
            )
       

    def execute(
        self,
        context,
        operator: Operator,
        nbShots,
        onRenderComplete=None,
        onStateChanged=None,
    ):
        # print("Executing RenderBatch")
        if not self.available():
            # warn user other rendering bactch is in progress
            operator.report({"WARNING"}, "Renderer not available")
            return {"CANCELLED"}

        if nbShots == 0:
            self.report({"WARNING"}, "No shots to render")
            return {"CANCELLED"}

        self.nb_shots = nbShots
        self.onRenderComplete = onRenderComplete
        self.onStateChanged = onStateChanged

        self.operator = operator

        self.isCancelled = False
        self.rendering = False
        self.shot_index = 0

        if self.operator is not None:
            context.window_manager.modal_handler_add(self.operator)
        
        self.__addListenners(context)

        self.setRenderState("ON")

        return {"RUNNING_MODAL"}

    def setRenderState(self, state):
        if state != self.__renderState:
            # print("Render State: " + state)
            self.__renderState = state
            if self.onStateChanged is not None:
                self.onStateChanged(self.__renderState)

    def getRenderState(self):
        return self.__renderState

    def available(self):
        return self.__renderState == "OFF" or self.__renderState == "CANCELLED"
    
    def modal(self, context, event, setupRenderDelegate):
        operatorResult = "PASS_THROUGH"
        if event.type == "TIMER":  # This event is signaled every half a second
            if self.__renderState == "CANCELLED":
                operatorResult = "CANCELLED"

            # START > STARTED state switch as direct render cause proc races issues on render listenners
            # it requires one operator extra modal iteration for better render ops call 
            elif(self.__renderState == "RENDER_START"):
                self.setRenderState("RENDER_STARTED")
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
            else:
                if self.__renderState == "RENDER_COMPLETE":
                    if self.onRenderComplete is not None:
                        self.onRenderComplete(context, self.shot_index, self.nb_shots)

                    self.shot_index += 1

                    if self.shot_index >= self.nb_shots:
                        operatorResult = "FINISHED"
                        self.setRenderState("BATCH_COMPLETE")
                    else:
                        self.setRenderState("ON")

                if self.__renderState == "ON":
                    doRender = setupRenderDelegate(
                        context, self.shot_index, self.nb_shots
                    )

                    if doRender is False:
                        operatorResult = "CANCELLED"
                        self.setRenderState("CANCELLED")
                    else:
                        # START > STARTED state switch as direct render cause proc races issues on render listenners
                        self.setRenderState("RENDER_START")                       

            if (
                self.__renderState == "BATCH_COMPLETE"
                or self.__renderState == "CANCELLED"
            ):
                bpy.ops.render.view_show()
                self.setRenderState("OFF")
                self.__clearListenners(context)

        return [operatorResult, self.__renderState, self.shot_index, self.nb_shots]


