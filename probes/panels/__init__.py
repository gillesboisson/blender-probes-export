
import bpy

from .scene_settings_panel import SceneSettingsPanel
from .probe_settings_panel import ProbeSettingsPanel

classes = (
    SceneSettingsPanel,
    ProbeSettingsPanel
)

def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)