import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class




class ProbeExportSettings(bpy.types.PropertyGroup):
    enable_export: BoolProperty(name="Enable", default=True)
    use_default_settings: BoolProperty(name="Use default settings", default=True)
    
    map_size: IntProperty(name="Map size", default=256)
    samples_max: IntProperty(name="Samples max", default=32)

    radiance_levels: IntProperty(name="Radiance levels", default=4)

   
classes = (
    ProbeExportSettings,
)


def register_probes_settings():
    for cls in classes:
        register_class(cls)
    
    bpy.types.LightProbe.probes_export = PointerProperty(type=ProbeExportSettings)
def unregister_probes_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.LightProbe, 'probes_export')
