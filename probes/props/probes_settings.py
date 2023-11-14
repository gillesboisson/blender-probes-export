import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class

from .common import *



    
class BAKE_GI_probes_settings(bpy.types.PropertyGroup):
    enable_export: BoolProperty(name="Enable", default=True)
    is_global_probe: BoolProperty(name="Default probe", default=False)

    use_default_settings: BoolProperty(name="Use default settings", default=True)
    render_settings: PointerProperty(type=BAKE_GI_probes_render_settings)
    bake_settings: PointerProperty(type=BAKE_GI_probes_bake_settings)
    

classes = (
    BAKE_GI_probes_settings,
)


def register_probes_settings():
    for cls in classes:
        register_class(cls)
    
    bpy.types.LightProbe.bake_gi = PointerProperty(type=BAKE_GI_probes_settings)
def unregister_probes_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.LightProbe, 'bake_gi')
