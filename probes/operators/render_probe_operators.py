import typing
import bpy
from bpy.types import Context, Event, Operator

import json

from ..helpers.create import unlink_pano_camera

from ..compositing.reflectance import pack_reflectance_probe
from ..compositing.irradiance import pack_irradiance_probe
from ..compositing.global_probe import pack_global_probe

from ..helpers.poll import (
    is_exportable_default_light_probe,
    is_exportable_irradiance_light_probe,
    is_exportable_light_probe,
    is_exportable_reflection_light_probe,
)

from ..helpers.render import (
    DefaultProbeVolumeRenderer,
    IrradianceProbeVolumeRenderer,
    ReflectionProbeVolumeRenderer,
    # reset_objects_render_settings,
    # save_pano_irradiance_probe_render,
    # save_pano_reflection_probe_render,
)

from ..helpers.files import (
    clear_render_cache_subdirectory,
    render_cache_subdirectory_exists,
    clear_render_cache_directory,
    save_probe_json_render_data,
)

from .multirender import BatchRenderer




class RenderReflectionProbeOperator(Operator, ReflectionProbeVolumeRenderer):
    bl_idname = "probes_export.render_reflectance"
    bl_label = "Render reflection probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return BatchRenderer.getDefault().available() and is_exportable_reflection_light_probe(context)

    def execute(self, context):
        self.setup_render_batch(context, self, context.object)

        return BatchRenderer.getDefault().execute(
            context,
            self,
            self.render_nb_probes,
            onRenderComplete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = BatchRenderer.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class RenderIrradianceProbeOperator(Operator, IrradianceProbeVolumeRenderer):
    bl_idname = "probes_export.render_irradiance"
    bl_label = "Render irradiance probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return BatchRenderer.getDefault().available() and is_exportable_irradiance_light_probe(context)

    def execute(self, context):
        self.setup_render_batch(context, self, context.object)

        return BatchRenderer.getDefault().execute(
            context,
            self,
            self.render_nb_probes,
            onRenderComplete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = BatchRenderer.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class RenderDefaultProbeOperator(Operator, DefaultProbeVolumeRenderer):
    bl_idname = "probes_export.render_default"
    bl_label = "Render default probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return BatchRenderer.getDefault().available() and is_exportable_default_light_probe(context) 

    def execute(self, context):
        self.setup_render_batch(context, self, context.object)

        return BatchRenderer.getDefault().execute(
            context,
            self,
            self.render_nb_probes,
            onRenderComplete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = BatchRenderer.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class RenderAllProbesOperator(Operator):
    bl_idname = "probes_export.render_all"
    bl_label = "Render all probes"
    bl_description = ""
    bl_options = {"REGISTER"}

    __probes_volumes = None
    __probes_renderers = None
    __probes_renderers_indices = None
    __probes_renderers_nb_probes = None
    __current_renderer_index = 0

    @classmethod
    def poll(cls, context):
        return BatchRenderer.getDefault().available()

    def setup_render(self, context, shot_index, nb_shots):
        renderer = self.__probes_renderers[self.__current_renderer_index]
        probe_index = self.__probes_renderers_indices[self.__current_renderer_index]
        nb_probes = self.__probes_renderers_nb_probes[self.__current_renderer_index]
        probe_volume = self.__probes_volumes[self.__current_renderer_index]

        relative_probe_index = shot_index - probe_index

        if relative_probe_index == 0:
            print(
                "> setup render batch", self.__current_renderer_index, probe_volume.name
            )
            renderer.setup_render_batch(context, self, probe_volume)

        print(">> setup render", shot_index, nb_shots, relative_probe_index, nb_probes)
        renderer.setup_render(context, relative_probe_index, nb_probes)

    def finalize_render(self, context, shot_index, nb_shots):
        renderer = self.__probes_renderers[self.__current_renderer_index]
        probe_index = self.__probes_renderers_indices[self.__current_renderer_index]
        nb_probes = self.__probes_renderers_nb_probes[self.__current_renderer_index]
        probe_volume = self.__probes_volumes[self.__current_renderer_index]

        relative_probe_index = shot_index - probe_index

        print(
            ">> finalize render", shot_index, nb_shots, relative_probe_index, nb_probes
        )
        renderer.finalize_render(context, relative_probe_index, nb_probes)

        if relative_probe_index >= nb_probes - 1:
            print(
                "> finalize render batch",
                self.__current_renderer_index,
                probe_volume.name,
            )
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

            if object.type == "LIGHT_PROBE" and object.data.probes_export.enable_export:
                if object.data.type == "CUBEMAP":
                    if object.data.probes_export.is_global_probe:
                        renderer = DefaultProbeVolumeRenderer()
                    else:
                        renderer = ReflectionProbeVolumeRenderer()
                elif object.data.type == "GRID":
                    renderer = IrradianceProbeVolumeRenderer()

            if renderer is not None:
                nb_probes = renderer.get_nb_probes(object)
                self.__probes_renderers.append(renderer)
                self.__probes_renderers_indices.append(probe_index)
                self.__probes_renderers_nb_probes.append(nb_probes)
                self.__probes_volumes.append(object)

                probe_index += nb_probes

        total_nb_probes = probe_index
        if probe_index > 0:
            return BatchRenderer.getDefault().execute(
                context,
                self,
                total_nb_probes,
                onRenderComplete=self.finalize_render,
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
        ] = BatchRenderer.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.report({"INFO"}, "Finished rendering all probes")
            # self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class ClearRenderProbeCache(Operator):
    bl_idname = "probes_export.clear_cache"
    bl_label = "Clear volume cache"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if is_exportable_light_probe(context) is False:
            return False

        if context.object.data.probes_export.is_global_probe:
            cache_name = context.object.name
        else:
            cache_name = context.object.name

        return render_cache_subdirectory_exists(
            context.scene.probes_export.export_directory_path, cache_name
        )

    def execute(self, context):
        if context.object.data.probes_export.is_global_probe:
            cache_name = context.object.name
        else:
            cache_name = context.object.name

        clear_render_cache_subdirectory(
            context.scene.probes_export.export_directory_path, cache_name
        )
        return {"FINISHED"}


class ClearProbeCacheDirectory(Operator):
    bl_idname = "probes_export.clear_main_cache_directory"
    bl_label = "Clear probes cache"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        clear_render_cache_directory(context.scene.probes_export.export_directory_path)
        return {"FINISHED"}
