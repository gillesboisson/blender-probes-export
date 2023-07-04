
import bpy
from bpy.types import Operator

import json
from ..helpers.poll import is_exportabled_grid_light_probe, is_exportabled_reflection_light_probe

from ..helpers.render import render_cubemap_reflection_probe, render_pano_irradiance_probe


from ..helpers.pack import pack_irradiance_probe, pack_reflection_probe

from ..helpers.data import load_probe_data


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
        return is_exportabled_grid_light_probe(context)



    def execute(self, context):

        export_directory = context.scene.probes_export.export_directory_path
        map_size = 32
        data = load_probe_data(export_directory, context.object.name)

        if(data == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}
        

        pack_irradiance_probe(export_directory, data, map_size,2048) 
       
        return {"FINISHED"}

class PackReflectionProbe(BasePackProbe):
    bl_idname = "probe.pack_relection"
    bl_label = "Pack reflection probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportabled_reflection_light_probe(context)



    def execute(self, context):

        export_directory = context.scene.probes_export.export_directory_path
        map_size = 256
        data = load_probe_data(export_directory, context.object.name)

        if(data == None):
            self.report({'ERROR'}, 'No data found for this probe')
            return {"FINISHED"}
        

        pack_reflection_probe(export_directory, data, map_size,2048) 
       
        return {"FINISHED"}

