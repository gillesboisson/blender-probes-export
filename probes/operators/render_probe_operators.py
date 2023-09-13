
import bpy
from bpy.types import Operator

import json

from ..compositing.reflectance import pack_reflectance_probe
from ..compositing.irradiance import pack_irradiance_probe
from ..helpers.poll import is_exportable_light_probe

from ..helpers.render import render_pano_reflection_probe, render_pano_irradiance_probe

from ..helpers.files import clear_render_cache_subdirectory, render_cache_subdirectory_exists, clear_render_cache_directory

class BaseRenderProbe(Operator):    
    def execute_reflection(self, context, object, progress_min = 0, progress_max = 1):
        render_pano_reflection_probe(context, self, object, progress_min, progress_max)
        pack_reflectance_probe(context, object)

    def execute_grid(self, context, object, progress_min = 0, progress_max = 1):
        render_pano_irradiance_probe(context, self, object, progress_min, progress_max)
        pack_irradiance_probe(context, object)  

    
class RenderProbe(BaseRenderProbe):
    bl_idname = "probe.render"
    bl_label = "Render probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_light_probe(context) 



    def execute(self, context):
        
        if(context.object.data.type == 'CUBEMAP'):
            self.execute_reflection(context, context.object)
        elif(context.object.data.type == 'GRID'):
            self.execute_grid(context, context.object)
        

        return {"FINISHED"}

class ClearRenderProbeCache(Operator):
    bl_idname = "probe.clear_cache"
    bl_label = "Clear probe cache"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_light_probe(context) and render_cache_subdirectory_exists(
            context.scene.probes_export.export_directory_path,
            context.object.name
        )

    def execute(self, context):
        clear_render_cache_subdirectory(
            context.scene.probes_export.export_directory_path, 
            context.object.name
        )
        return {"FINISHED"}

class RenderProbes(BaseRenderProbe):
    bl_idname = "probes.export"
    bl_label = "Render all probe"
    bl_description = ""
    bl_options = {"REGISTER"}


    def execute(self, context):
        probes = []
        progress_min = 0
        progress_max = 0

        for object in bpy.data.objects:
            if object.type == 'LIGHT_PROBE':
                if object.data.type == 'CUBEMAP' or object.data.type == 'GRID':
                    probes.append(object)
                    progress_max += 1

        for object in probes:
            if(object.data.type == 'CUBEMAP'):
                self.execute_reflection(context, object , progress_min, progress_max)

            elif(object.data.type == 'GRID'):
                self.execute_grid(context, object, progress_min, progress_max)
            progress_min += 1

        return {"FINISHED"}

class ClearProbeCacheDirectory(Operator):
    bl_idname = "probes.clear_main_cache_directory"
    bl_label = "Clear cache"
    bl_description = ""
    bl_options = {"REGISTER"}


    def execute(self, context):
        clear_render_cache_directory(context.scene.probes_export.export_directory_path)
        return {"FINISHED"}