import bpy
from bpy.types import Context

from ..helpers.poll import is_exportable_light_probe



class ObjectProbeRenderPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_object_probe_render'
    bl_label = 'Probes export'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"


    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'
    
    # def draw_header(self, context: Context):
    #     data = context.object
    #     prop = data.probes_render
    #     self.layout.prop(prop, 'static_object', text='')

    def draw(self, context):
        
        ob = context.object
        prop = ob.probes_render

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        master_row = layout.column()

        row = master_row.row(align=True)
        col = row.column()
        
        col.prop(prop, 'render_by_reflection_probes')
        col.prop(prop, 'render_by_irradiance_probes')
        col.prop(prop, 'render_by_global_probe')


        pass


