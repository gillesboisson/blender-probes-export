import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class





class ProbeExportSceneSettings(bpy.types.PropertyGroup):
    export_path: StringProperty(name="Data path", default="")
    export_directory_path: StringProperty(name="Render directory", default="")

    reflection_cubemap_default_map_size: IntProperty(name="Map size", default=256)
    reflection_cubemap_default_samples_max: IntProperty(name="Samples max", default=32)
    reflection_cubemap_default_radiance_levels: IntProperty(name="Radiance levels", default=4)

    irradiance_volume_default_map_size: IntProperty(name="Map size", default=128)
    irradiance_volume_default_samples_max: IntProperty(name="Samples max", default=8)


# FileSelectEntry
   
classes = (
    ProbeExportSceneSettings,
    # SetProbeExportDirectory
)


def register_export_settings():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.probes_export = PointerProperty(type=ProbeExportSceneSettings)
def unregister_export_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.Scene, 'probes_export')
