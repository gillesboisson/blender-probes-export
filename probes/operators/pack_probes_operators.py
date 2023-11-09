
from bpy.types import Operator
import json

from ..helpers.poll import get_context_probes_names, is_exportable_grid_light_probe, is_exportable_reflection_light_probe



from ..compositing.irradiance import pack_irradiance_probe, pack_irradiance_probe_to_image
from ..compositing.reflectance import pack_reflectance_probe
from ..compositing.global_probe import pack_global_probe

from ..helpers.files import load_probe_json_render_data, render_cache_subdirectory_exists, save_scene_json_pack_data


class BasePackProbe(Operator):    
    
    def a():
        pass
    


class PackIrradianceProbe(BasePackProbe):
    bl_idname = "probe.pack_irradiance"
    bl_label = "Pack irradiance probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_grid_light_probe(context) and render_cache_subdirectory_exists(
            context.scene.probes_export.export_directory_path,
            context.object.name
        )



    def execute(self, context):

        if(pack_irradiance_probe(context) == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}        

        return {"FINISHED"}

class PackReflectionProbe(BasePackProbe):
    bl_idname = "probe.pack_relection"
    bl_label = "Pack radiance probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_reflection_light_probe(context) and render_cache_subdirectory_exists(
            context.scene.probes_export.export_directory_path,
            context.object.name
        )
    
    def execute(self, context):

        if(pack_reflectance_probe(context) == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}
       
        return {"FINISHED"}

class PackGlobalProbe(BasePackProbe):
    bl_idname = "probe.pack_global"
    bl_label = "Pack default probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_reflection_light_probe(context) and render_cache_subdirectory_exists(
            context.scene.probes_export.export_directory_path,
            context.object.name
        )
    
    def execute(self, context):
        if(pack_global_probe(context) == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}
       
        return {"FINISHED"}

