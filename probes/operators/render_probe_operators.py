import typing
import bpy
from bpy.types import Context, Event, Operator

import json

from ..helpers.create import unlink_pano_camera

from ..compositing.reflectance import pack_reflectance_probe
from ..compositing.irradiance import pack_irradiance_probe
from ..compositing.global_probe import pack_global_probe

from ..helpers.poll import is_exportable_default_light_probe, is_exportable_irradiance_light_probe, is_exportable_light_probe, is_exportable_reflection_light_probe

from ..helpers.render import (
    DefaultProbeVolumeRenderer,
    IrradianceProbeVolumeRenderer,
    ReflectionProbeVolumeRenderer,
    render_pano_reflection_probe,
    render_pano_irradiance_probe,
    reset_collection_visibility,
    reset_objects_render_settings,
    # save_pano_irradiance_probe_render,
    # save_pano_reflection_probe_render,
    setup_pano_irradance_probe_render,
    setup_pano_irradiance_probe_render_batch,
    setup_pano_reflection_probe_render,
    setup_pano_reflection_probe_render_batch,
    update_collection_visibility_for_probe,
    update_objects_settings_for_irradiance,
    update_objects_settings_for_reflection,
    render_pano_global_probe,
    update_objects_settings_for_global,
)

from ..helpers.files import (
    clear_render_cache_subdirectory,
    render_cache_subdirectory_exists,
    clear_render_cache_directory,
    save_probe_json_render_data,
)

from .multirender import RenderBatch


class BaseRenderProbe(Operator):
    def execute_reflection(self, context, object, progress_min=0, progress_max=1):
        render_pano_reflection_probe(context, self, object, progress_min, progress_max)
        pack_reflectance_probe(context, object)

    def execute_irradiance_grid(self, context, object, progress_min=0, progress_max=1):
        render_pano_irradiance_probe(context, self, object, progress_min, progress_max)
        pack_irradiance_probe(context, object)

    def execute_global(self, context, object, progress_min=0, progress_max=1):
        render_pano_global_probe(context, self, object, progress_min, progress_max)
        pack_global_probe(context, object)


class RenderReflectionProbeOperator(Operator, ReflectionProbeVolumeRenderer):
    bl_idname = "reflection_probe.render"
    bl_label = "Render reflection probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_reflection_light_probe(context)

    def execute(self, context):
        self.setup_render_batch(context, self, context.object)

        return RenderBatch.getDefault().execute(
            context,
            self,
            self.nb_probes,
            onRenderComplete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = RenderBatch.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}


class RenderIrradianceProbeOperator(Operator, IrradianceProbeVolumeRenderer):
    bl_idname = "irradiance_probe.render"
    bl_label = "Render irradiance probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_irradiance_light_probe(context)
    
    def execute(self, context):
        self.setup_render_batch(context, self, context.object)

        return RenderBatch.getDefault().execute(
            context,
            self,
            self.nb_probes,
            onRenderComplete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = RenderBatch.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}
class RenderDefaultProbeOperator(Operator, DefaultProbeVolumeRenderer):
    bl_idname = "default_probe.render"
    bl_label = "Render default probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_default_light_probe(context)
    
    def execute(self, context):
        self.setup_render_batch(context, self, context.object)

        return RenderBatch.getDefault().execute(
            context,
            self,
            self.nb_probes,
            onRenderComplete=self.finalize_render,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            renderState,
            shotIndex,
            nbShots,
        ] = RenderBatch.getDefault().modal(context, event, self.setup_render)
        if operatorResult == "CANCELLED":
            self.reset(context)
        elif operatorResult == "FINISHED":
            self.finalize_render_batch(context, self)
            self.reset(context)

        return {operatorResult}




class RenderProbe(BaseRenderProbe):
    bl_idname = "probe.render"
    bl_label = "Render probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    __rendered_probe_data = None
    __rendered_probe = None

    # Setup
    __nb_probes = None
    __samples_max = None
    __height = None
    __object_transform = None
    __camera = None
    __final_export_directory = None
    __file_extension = None
    __json_data = None

    @classmethod
    def poll(cls, context):
        return is_exportable_light_probe(context)

    def __reset(self, context):
        unlink_pano_camera(context)

        reset_objects_render_settings(context)
        reset_collection_visibility(context)

    def __cancelled(self, context, shotIndex, nbShots):
        self.__reset(context)

    def __setup_batch(self, context):
        self.__rendered_probe = rendered_probe = context.object
        self.__rendered_probe_data = probe_data = rendered_probe.data

        update_collection_visibility_for_probe(
            context.scene.collection.children, probe_data
        )

        if probe_data.type == "CUBEMAP":
            if probe_data.probes_export.is_global_probe:
                update_objects_settings_for_global(context)
                self.__nb_probes = 2
            else:
                update_objects_settings_for_reflection(context)
                render_batch_setup = setup_pano_reflection_probe_render_batch(
                    context, self, rendered_probe
                )

        elif probe_data.type == "GRID":
            update_objects_settings_for_irradiance(context)
            render_batch_setup = setup_pano_irradiance_probe_render_batch(
                context, self, rendered_probe
            )

        if render_batch_setup is not None:
            [
                self.__nb_probes,
                self.__samples_max,
                self.__height,
                self.__final_export_directory,
                self.__object_transform,
                self.__camera,
                self.__file_extension,
                self.__json_data,
            ] = render_batch_setup

    def __setupRender(self, context, shot_index, nb_shots):
        if self.__rendered_probe_data.type == "CUBEMAP":
            if self.__rendered_probe_data.probes_export.is_global_probe:
                a = 0
            else:
                self.__json_data = setup_pano_reflection_probe_render(
                    context,
                    self,
                    self.__rendered_probe,
                    shot_index,
                    self.__samples_max,
                    self.__height,
                    self.__final_export_directory,
                    self.__object_transform,
                    self.__camera,
                    self.__file_extension,
                    self.__json_data,
                )
            if self.__json_data is not None:
                return True
        elif self.__rendered_probe_data.type == "GRID":
            self.__json_data = setup_pano_irradance_probe_render(
                context,
                self,
                self.__rendered_probe,
                shot_index,
                self.__samples_max,
                self.__height,
                self.__final_export_directory,
                self.__object_transform,
                self.__camera,
                self.__file_extension,
                self.__json_data,
            )

            if self.__json_data is not None:
                return True

        return False

    def __renderComplete(self, context, shotIndex, nbShots):
        pass

    def __complete(self, context):
        probe_data = self.__rendered_probe_data
        export_directory = context.scene.probes_export.export_directory_path
        if probe_data.type == "CUBEMAP":
            if probe_data.probes_export.is_global_probe:
                a = 0
            else:
                save_probe_json_render_data(
                    export_directory, self.__rendered_probe.name, self.__json_data
                )
                pack_reflectance_probe(context, self.__rendered_probe)
        elif probe_data.type == "GRID":
            save_probe_json_render_data(
                export_directory, self.__rendered_probe.name, self
            )

            pack_irradiance_probe(context, self.__rendered_probe)

        self.__reset(context)
        return {"FINISHED"}

    def execute(self, context):
        self.__setup_batch(context)

        return RenderBatch.getDefault().execute(
            context,
            self,
            self.__nb_probes,
            onRenderComplete=self.__renderComplete,
        )

    def modal(self, context: Context, event: Event):
        [
            operatorResult,
            shotIndex,
            nbShots,
        ] = RenderBatch.getDefault().modal(context, event, self.__setupRender)
        if operatorResult == "CANCELLED":
            self.__cancelled(context, shotIndex, nbShots)
        elif operatorResult == "FINISHED":
            self.__complete(context)

        return {operatorResult}


class ClearRenderProbeCache(Operator):
    bl_idname = "probe.clear_cache"
    bl_label = "Clear probes cache"
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


class RenderProbes(BaseRenderProbe):
    bl_idname = "probes.export"
    bl_label = "Bake all probes"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        probes = []
        progress_min = 0
        progress_max = 0

        for object in bpy.data.objects:
            if object.type == "LIGHT_PROBE" and object.data.probes_export.enable_export:
                if object.data.type == "CUBEMAP" or object.data.type == "GRID":
                    probes.append(object)
                    progress_max += 1

        update_objects_settings_for_global(context)

        for object in probes:
            if (
                object.data.type == "CUBEMAP"
                and object.data.probes_export.is_global_probe
            ):
                self.execute_global(context, object, progress_min, progress_max)
                progress_min += 1

        update_objects_settings_for_reflection(context)

        for object in probes:
            if (
                object.data.type == "CUBEMAP"
            ) and not object.data.probes_export.is_global_probe:
                self.execute_reflection(context, object, progress_min, progress_max)
                progress_min += 1

        update_objects_settings_for_irradiance(context)
        for object in probes:
            if (
                object.data.type == "GRID"
                and not object.data.probes_export.is_global_probe
            ):
                self.execute_irradiance_grid(
                    context, object, progress_min, progress_max
                )
            progress_min += 1

        reset_objects_render_settings(context)
        return {"FINISHED"}


class ClearProbeCacheDirectory(Operator):
    bl_idname = "probes.clear_main_cache_directory"
    bl_label = "Clear probes cache"
    bl_description = ""
    bl_options = {"REGISTER"}

    def execute(self, context):
        clear_render_cache_directory(context.scene.probes_export.export_directory_path)
        return {"FINISHED"}
