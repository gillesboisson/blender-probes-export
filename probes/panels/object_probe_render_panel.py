import bpy
from bpy.types import Context




class BAKE_GI_PT_object(bpy.types.Panel):
    bl_idname = 'BAKE_GI_PT_object'
    bl_label = 'GI bake'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"


    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'
    

    def draw(self, context):
        
        ob = context.object
        prop = ob.bake_gi

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


classes = (
    BAKE_GI_PT_object,
)


def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
