import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class

class BAKE_GI_probes_render_settings(bpy.types.PropertyGroup):
    map_size: IntProperty(name="Map size", default=256)
    samples_max: IntProperty(name="Samples max", default=32)
    samples_min: IntProperty(name="Samples min", default=1)
    time_limit: IntProperty(name="Time limit", default=0)

class BAKE_GI_probes_bake_settings(bpy.types.PropertyGroup):
    map_size: IntProperty(name="Cubemap face size", default=128)
    max_texture_size: IntProperty(name="Final texture max width", default=2048)

    start_roughness: FloatProperty(name="Start roughness", default=0.1, min=0.0, max=1.0)
    level_roughness: FloatProperty(name="Roughness step", description="Roughness step increase in each level", default=0.2 , min=0.1, max=1.0)
    nb_levels: IntProperty(name="Rougness levels", default=4,  min=1, max=4)



classes = (
    BAKE_GI_probes_render_settings,
    BAKE_GI_probes_bake_settings,
)


def register_props():
    for cls in classes:
        register_class(cls)
def unregister_props():
    for cls in reversed(classes):
        unregister_class(cls)

