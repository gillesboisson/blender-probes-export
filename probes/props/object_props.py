import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class





class BAKE_GI_object_props(bpy.types.PropertyGroup):
    static_object: BoolProperty(name="Enable", default=False)
    render_by_reflection_probes: BoolProperty(name="Baked by radiance probes", default=True)
    render_by_irradiance_probes: BoolProperty(name="Baked by irradiance probes", default=True)
    render_by_global_probe: BoolProperty(name="Baked by default environment", default=False)
    

classes = (
    BAKE_GI_object_props,
)

def register_object_bake_props():
    for cls in classes:
        register_class(cls)
    
    bpy.types.Object.bake_gi = PointerProperty(type=BAKE_GI_object_props)
def unregister_object_bake_props():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.Object, 'bake_gi')
