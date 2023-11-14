
import bpy

from .scene_settings_panel import BAKE_GI_PT_scene_default_probes_settings, BAKE_GI_PT_scene_settings, BAKE_GI_PT_scene_irradiance_probes_settings, BAKE_GI_PT_scene_reflection_probes_settings
from .probe_settings_panel import BAKE_GI_PT_probe_settings

from .object_probe_render_panel import BAKE_GI_PT_object

classes = (
    BAKE_GI_PT_scene_settings,
    BAKE_GI_PT_probe_settings,
    # sub panels
    BAKE_GI_PT_scene_irradiance_probes_settings,
    BAKE_GI_PT_scene_reflection_probes_settings,
    BAKE_GI_PT_scene_default_probes_settings,
    # object panels
    BAKE_GI_PT_object,
)

def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)