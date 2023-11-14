from math import floor
import time
import bpy

from bpy.types import Operator


class Batch_renderer:
    __default_render_batch = None

    @classmethod
    def get_default(cls) -> "Batch_renderer":
        if Batch_renderer.__default_render_batch is None:
            Batch_renderer.__default_render_batch = Batch_renderer()
        return Batch_renderer.__default_render_batch

    @classmethod
    def dispose_default(cls):
        if Batch_renderer.__default_render_batch is not None:
            Batch_renderer.__default_render_batch.reset()
        Batch_renderer.__default_render_batch = None
    
    __timer = None
    __render_state = "OFF"
    nb_shots = 0
    shot_index = 0
    on_render_complete = None
    on_state_changed = None

    def __pre_render(self, scene, context=None):
        if self.__render_state == "RENDER_STARTED":
            self.set_render_state("IN_PROGRESS")

    def __post_render(self, scene, context=None):
        if self.__render_state == "IN_PROGRESS":
            self.set_render_state("RENDER_COMPLETE")

    def __render_cancel(self, scene, context=None):
        if self.__render_state != "OFF":
            self.set_render_state("CANCELLED")

    def __clear_listenners(self, context):
        try:
            bpy.app.handlers.render_init.remove(self.__pre_render)
            bpy.app.handlers.render_write.remove(self.__post_render)
            bpy.app.handlers.render_cancel.remove(self.__render_cancel)
        except:
            pass

        if self.__timer is not None:
            bpy.context.window_manager.event_timer_remove(self.__timer)
            self.__timer = None

    def __add_listenners(self, context):
        self.__clear_listenners(context)

        bpy.app.handlers.render_init.append(self.__pre_render)
        bpy.app.handlers.render_write.append(self.__post_render)
        bpy.app.handlers.render_cancel.append(self.__render_cancel)

        if self.__timer is None:
            self.__timer = context.window_manager.event_timer_add(
                0.5, window=context.window
            )

    def cancel(self, context):
        # bpy.ops.render.view_cancel()
        self.set_render_state("CANCELLED")

    def reset(self):
        self.__clear_listenners(bpy.context)

        self.on_render_complete = None
        self.on_state_changed = None
        self.operator = None
        self.nb_shots = 0
        self.shot_index = 0
        self.set_render_state("OFF")


    def execute(
        self,
        context,
        operator: Operator,
        nb_shots,
        on_render_complete=None,
        on_state_changed=None,
    ):
        if not self.available():
            operator.report({"WARNING"}, "Renderer not available")
            return {"CANCELLED"}

        if nb_shots == 0:
            self.report({"WARNING"}, "No shots to render")
            return {"CANCELLED"}

        self.nb_shots = nb_shots
        self.on_render_complete = on_render_complete
        self.on_state_changed = on_state_changed

        self.operator = operator

        self.shot_index = 0

        context.scene.bake_gi.batch_render_progress = 0 
        if self.operator is not None:
            context.window_manager.modal_handler_add(self.operator)

        self.__add_listenners(context)

        self.set_render_state("ON")

        return {"RUNNING_MODAL"}

    def set_render_state(self, state):
        if state != self.__render_state:
            self.__render_state = state
            if self.on_state_changed is not None:
                self.on_state_changed(self.__render_state)

    def get_render_state(self):
        return self.__render_state

    def available(self):
        return self.__render_state == "OFF" or self.__render_state == "CANCELLED"

    def modal(self, context, event, setupRenderDelegate):
        
        operator_result = "PASS_THROUGH"
        if event.type == "TIMER":  # This event is signaled every half a second
            if self.__render_state == "CANCELLED":
                operator_result = "CANCELLED"
            
            
            # START > STARTED state switch as direct render cause proc races issues on render listenners
            # it requires one operator extra modal iteration for better render ops call
            elif self.__render_state == "RENDER_START":

                context.scene.bake_gi.batch_render_progress = floor(self.shot_index / self.nb_shots * 100)
                self.set_render_state("RENDER_STARTED")
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
            else:
                
                if self.__render_state == "RENDER_COMPLETE":
                    if self.on_render_complete is not None:
                        self.on_render_complete(context, self.shot_index, self.nb_shots)

                    self.shot_index += 1
                    context.scene.bake_gi.batch_render_progress = floor(self.shot_index / self.nb_shots * 100)


                    if self.shot_index >= self.nb_shots:
                        operator_result = "FINISHED"
                        self.set_render_state("BATCH_COMPLETE")
                    else:
                        self.set_render_state("ON")

                if self.__render_state == "ON":
                    doRender = setupRenderDelegate(
                        context, self.shot_index, self.nb_shots
                    )

                    if doRender is False:
                        operator_result = "CANCELLED"
                        self.set_render_state("CANCELLED")
                    else:

                        # START > STARTED state switch as direct render cause proc races issues on render listenners
                        self.set_render_state("RENDER_START")

            if (
                self.__render_state == "BATCH_COMPLETE"
                or self.__render_state == "CANCELLED"
            ):
                bpy.ops.render.view_show()
                self.set_render_state("OFF")
                self.__clear_listenners(context)

        return [operator_result, self.__render_state, self.shot_index, self.nb_shots]
