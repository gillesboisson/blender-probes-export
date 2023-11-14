import bpy
from bpy.types import Context, Event, Operator
from ..renderer import (
    Reflection_probe_volume_renderer,
    Default_probe_volume_renderer,
    Irradiance_probe_volume_renderer,
)

from ..helpers.poll import (
    is_exportable_default_light_probe,
    is_exportable_irradiance_light_probe,
    is_exportable_light_probe,
    is_exportable_reflection_light_probe,
)


from ..helpers.files import (
    clear_render_cache_subdirectory,
    render_cache_subdirectory_exists,
    clear_render_cache_directory,
)

from ..renderer.batch_renderer import Batch_renderer


class BAKE_GI_OP_render_reflection_probes(Operator, Reflection_probe_volume_renderer):
    bl_idname = "bake_gi.render_reflection_probes"
    bl_label = "Render selected reflection probe volume"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (
            Batch_renderer.get_default().available()
            and is_exportable_reflection_light_probe(context)
        )

    def execute(self, context):
        
        if self.setup_render_batch(context, self, context.object) == None:
            return {"CANCELLED"}

        return Batch_renderer.get_default().execute(
            context,
            self,
            self.render_nb_probes,
            on_render_complete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = Batch_renderer.get_default().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class BAKE_GI_OP_render_irradiance_probes(Operator, Irradiance_probe_volume_renderer):
    bl_idname = "bake_gi.render_irradiance_probes"
    bl_label = "Render selected irradiance probe volume"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (
            Batch_renderer.get_default().available()
            and is_exportable_irradiance_light_probe(context)
        )

    def execute(self, context):
        if self.setup_render_batch(context, self, context.object) == None:
            return {"CANCELLED"}

        return Batch_renderer.get_default().execute(
            context,
            self,
            self.render_nb_probes,
            on_render_complete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = Batch_renderer.get_default().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class BAKE_GI_OP_render_default_probe(Operator, Default_probe_volume_renderer):
    bl_idname = "bake_gi.render_default_probes"
    bl_label = "Render selected default probe volume"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return (
            Batch_renderer.get_default().available()
            and is_exportable_default_light_probe(context)
        )

    def execute(self, context):
        if self.setup_render_batch(context, self, context.object) == None:
            return {"CANCELLED"}

        return Batch_renderer.get_default().execute(
            context,
            self,
            self.render_nb_probes,
            on_render_complete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = Batch_renderer.get_default().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class BAKE_GI_OP_render_all_probes(Operator):
    bl_idname = "bake_gi.render_all_probes"
    bl_label = "Render all probe volumes"
    bl_description = ""
    bl_options = {"REGISTER"}

    __probes_volumes = None
    __probes_renderers = None
    __probes_renderers_indices = None
    __probes_renderers_nb_probes = None
    __current_renderer_index = 0

    @classmethod
    def poll(cls, context):
        return Batch_renderer.get_default().available()

    def setup_render(self, context, shot_index, nb_shots):
        renderer = self.__probes_renderers[self.__current_renderer_index]
        probe_index = self.__probes_renderers_indices[self.__current_renderer_index]
        nb_probes = self.__probes_renderers_nb_probes[self.__current_renderer_index]
        probe_volume = self.__probes_volumes[self.__current_renderer_index]

        relative_probe_index = shot_index - probe_index

        if relative_probe_index == 0:
            # print(
            #     "> setup render batch", self.__current_renderer_index, probe_volume.name
            # )
            renderer.setup_render_batch(context, self, probe_volume)

        # print(">> setup render", shot_index, nb_shots, relative_probe_index, nb_probes)
        renderer.setup_render(context, relative_probe_index, nb_probes)

    def finalize_render(self, context, shot_index, nb_shots):
        renderer = self.__probes_renderers[self.__current_renderer_index]
        probe_index = self.__probes_renderers_indices[self.__current_renderer_index]
        nb_probes = self.__probes_renderers_nb_probes[self.__current_renderer_index]
        probe_volume = self.__probes_volumes[self.__current_renderer_index]

        relative_probe_index = shot_index - probe_index

        # print(
        #     ">> finalize render", shot_index, nb_shots, relative_probe_index, nb_probes
        # )
        renderer.finalize_render(context, relative_probe_index, nb_probes)

        if relative_probe_index >= nb_probes - 1:
            # print(
            #     "> finalize render batch",
            #     self.__current_renderer_index,
            #     probe_volume.name,
            # )
            renderer.finalize_render_batch(context, self)
            self.__current_renderer_index += 1

    def execute(self, context):
        self.__probes_renderers = []
        self.__probes_renderers_indices = []
        self.__probes_renderers_nb_probes = []
        self.__probes_volumes = []
        self.__current_renderer_index = 0
        probe_index = 0

        for object in bpy.data.objects:
            renderer = None

            if object.type == "LIGHT_PROBE" and object.data.bake_gi.enable_export:
                if object.data.type == "CUBEMAP":
                    if object.data.bake_gi.is_global_probe:
                        renderer = Default_probe_volume_renderer()
                    else:
                        renderer = Reflection_probe_volume_renderer()
                elif object.data.type == "GRID":
                    renderer = Irradiance_probe_volume_renderer()

            if renderer is not None:
                nb_probes = renderer.get_nb_probes(object)
                self.__probes_renderers.append(renderer)
                self.__probes_renderers_indices.append(probe_index)
                self.__probes_renderers_nb_probes.append(nb_probes)
                self.__probes_volumes.append(object)

                probe_index += nb_probes

        total_nb_probes = probe_index
        if probe_index > 0:
            return Batch_renderer.get_default().execute(
                context,
                self,
                total_nb_probes,
                on_render_complete=self.finalize_render,
            )
        else:
            return {"FINISHED"}

    def reset(self, context):
        self.__probes_renderers = None
        self.__probes_renderers_indices = None
        self.__probes_renderers_nb_probes = None
        self.__current_renderer_index = 0

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = Batch_renderer.get_default().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.report({"INFO"}, "Finished rendering all probes")
            # self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class BAKE_GI_OP_clear_probes_render_cache(Operator):
    bl_idname = "bake_gi.clear_probes_cache"
    bl_label = "Clear selected probes volume cache"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if is_exportable_light_probe(context) is False:
            return False

        if context.object.data.bake_gi.is_global_probe:
            cache_name = context.object.name
        else:
            cache_name = context.object.name

        return render_cache_subdirectory_exists(
            context.scene.bake_gi.export_directory_path, cache_name
        )

    def execute(self, context):
        if context.object.data.bake_gi.is_global_probe:
            cache_name = context.object.name
        else:
            cache_name = context.object.name

        clear_render_cache_subdirectory(
            context.scene.bake_gi.export_directory_path, cache_name
        )
        return {"FINISHED"}


class BAKE_GI_OP_clear_all_probes_render_cache(Operator):
    bl_idname = "bake_gi.clear_all_probes_cache"
    bl_label = "Clear all probe volumes cache"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        clear_render_cache_directory(context.scene.bake_gi.export_directory_path)
        return {"FINISHED"}
