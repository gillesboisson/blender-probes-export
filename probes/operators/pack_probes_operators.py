
from bpy.types import Operator
import json

from ..helpers.poll import get_context_probes_names, is_exportable_grid_light_probe, is_exportable_reflection_light_probe



from ..compositing.irradiance import pack_irradiance_probe, pack_irradiance_probe_to_image
from ..compositing.reflectance import pack_reflectance_probe, pack_reflectance_probe_to_image

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

        # export_directory = context.scene.probes_export.export_directory_path
        
        # prob_object = context.object
        # prob = prob_object.data
        # settings = prob.probes_export

        # if(settings.use_default_settings):
        #     map_size = context.scene.probes_export.irradiance_volume_default_export_map_size
        #     export_max_texture_size = context.scene.probes_export.irradiance_volume_default_export_max_texture_size
        # else:
        #     map_size = settings.export_map_size
        #     export_max_texture_size = settings.export_max_texture_size


        # data = load_probe_json_render_data(export_directory, context.object.name)

        # if(data == None):
        #     self.report({'ERROR'}, 'No data found for this probe')
        #     return {"FINISHED"}
        

        # pack_irradiance_probe_to_image(export_directory, data, map_size, export_max_texture_size) 

        # probe_names = get_context_probes_names(context)

        # save_scene_json_pack_data(export_directory, probe_names)
     
        if(pack_irradiance_probe(context) == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}        

        return {"FINISHED"}

class PackReflectionProbe(BasePackProbe):
    bl_idname = "probe.pack_relection"
    bl_label = "Pack reflection probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_reflection_light_probe(context) and render_cache_subdirectory_exists(
            context.scene.probes_export.export_directory_path,
            context.object.name
        )
    
    def execute(self, context):

        # export_directory = context.scene.probes_export.export_directory_path
        
        # prob_object = context.object
        # prob = prob_object.data
        # settings = prob.probes_export
        
        # if(settings.use_default_settings):
        #     map_size = context.scene.probes_export.reflection_volume_default_export_map_size
        #     export_max_texture_size = context.scene.probes_export.reflection_volume_default_export_max_texture_size
        #     export_nb_levels = context.scene.probes_export.reflection_volume_default_export_nb_levels
        #     export_start_roughness = context.scene.probes_export.reflection_volume_default_export_start_roughness
        #     export_level_roughness = context.scene.probes_export.reflection_volume_default_export_level_roughness

        # else:
        #     map_size = settings.export_map_size
        #     export_max_texture_size = settings.export_max_texture_size
        #     export_nb_levels = settings.export_nb_levels
        #     export_start_roughness = settings.export_start_roughness
        #     export_level_roughness = settings.export_level_roughness
        

        # data = load_probe_json_render_data(export_directory, context.object.name)

        # if(data == None):
        #     self.report({'ERROR'}, 'No data found for this probe')
        #     return {"FINISHED"}
        

        # pack_reflectance_probe_(
        #     export_directory,
        #     data,
        #     map_size,
        #     export_max_texture_size,
        #     export_nb_levels,
        #     export_start_roughness,
        #     export_level_roughness
        # ) 

        # probe_names = get_context_probes_names(context)

        # save_scene_json_pack_data(export_directory, probe_names)

        if(pack_reflectance_probe(context) == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}
       
        return {"FINISHED"}

