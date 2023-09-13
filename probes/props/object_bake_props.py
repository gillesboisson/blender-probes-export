import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class





class ObjectProbesRenderProps(bpy.types.PropertyGroup):
    static_object: BoolProperty(name="Enable", default=False)
    render_by_reflection_probes: BoolProperty(name="Render by reflection probes", default=True)
    render_by_irradiance_probes: BoolProperty(name="Render by irradiance probes", default=True)
    

classes = (
    ObjectProbesRenderProps,
)

def register_probes_settings():
    for cls in classes:
        register_class(cls)
    
    bpy.types.Object.probes_render = PointerProperty(type=ObjectProbesRenderProps)
def unregister_probes_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.Object, 'probes_render')