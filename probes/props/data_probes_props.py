import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class




class ProbeExportSettingsProps(bpy.types.PropertyGroup):
    enable_export: BoolProperty(name="Enable", default=True)
    is_global_probe: BoolProperty(name="Default probe", default=False)





    use_default_settings: BoolProperty(name="Use default settings", default=True)
    
    map_size: IntProperty(name="Map size", default=256)
    samples_max: IntProperty(name="Samples max", default=32)

    export_map_size: IntProperty(name="Cubemap face size", default=128)
    export_max_texture_size: IntProperty(name="Final texture max width", default=2048)
    export_start_roughness: FloatProperty(name="Start roughness", default=0.25, min=0.0, max=1.0)
    export_nb_levels: IntProperty(name="Rougness levels", default=1,  min=1, max=4)
    export_level_roughness: FloatProperty(name="Roughness step", description="Roughness step increase in each level", default=0.25 , min=0.1, max=1.0)
    
    

   
classes = (
    ProbeExportSettingsProps,
)


def register_probes_settings():
    for cls in classes:
        register_class(cls)
    
    bpy.types.LightProbe.probes_export = PointerProperty(type=ProbeExportSettingsProps)
def unregister_probes_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.LightProbe, 'probes_export')
