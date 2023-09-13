import bpy
from bpy.types import Context

from ..helpers.poll import is_exportable_light_probe



class ObjectProbeRenderPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_object_probe_render'
    bl_label = 'Static object render'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"


    @classmethod
    def poll(cls, context):
        return context.object.type == 'OBJECT'
    
    def draw_header(self, context: Context):
        data = context.object
        prop = data.probes_render
        self.layout.prop(prop, 'static_object', text='')

    def draw(self, context):


