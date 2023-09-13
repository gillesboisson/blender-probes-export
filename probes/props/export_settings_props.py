import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class





class ProbeExportSceneSettingsProps(bpy.types.PropertyGroup):
    export_path: StringProperty(name="Data path", default="")
    export_directory_path: StringProperty(name="Render directory", default="")


    # render props
    reflection_cubemap_default_map_size: IntProperty(name="Map size", default=256)
    reflection_cubemap_default_samples_max: IntProperty(name="Samples max", default=32)
    reflection_cubemap_default_radiance_levels: IntProperty(name="Radiance levels", default=4)

    # export props
    reflection_volume_default_export_map_size: IntProperty(name="Cubemap face size", default=128)
    reflection_volume_default_export_max_texture_size: IntProperty(name="Max final texture size", default=2048)
    reflection_volume_default_export_nb_levels: IntProperty(name="Irradiance levels amount", default=1,  min=1, max=4)
    reflection_volume_default_export_start_roughness: FloatProperty(name="Start roughness", default=0.25, min=0.0, max=1.0)
    reflection_volume_default_export_level_roughness: FloatProperty(name="Roughness step", description="Roughness step increase in each level", default=0.25 , min=0.1, max=1.0)
    
    irradiance_volume_default_map_size: IntProperty(name="Map size", default=128)
    irradiance_volume_default_samples_max: IntProperty(name="Samples max", default=8)
    
    irradiance_volume_default_export_map_size: IntProperty(name="Cubemap face size", default=64)
    irradiance_volume_default_export_max_texture_size: IntProperty(name="Map size", default=2048)
    
    
# FileSelectEntry
   
classes = (
    ProbeExportSceneSettingsProps,
    # SetProbeExportDirectory
)


def register_export_settings():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.probes_export = PointerProperty(type=ProbeExportSceneSettingsProps)
def unregister_export_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.Scene, 'probes_export')