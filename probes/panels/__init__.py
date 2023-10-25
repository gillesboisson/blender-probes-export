
import bpy

from .scene_settings_panel import SceneGlobalEnvSettingsPanel, SceneSettingsPanel, SceneIrradianceSettingsPanel, SceneReflectionSettingsPanel
from .probe_settings_panel import ProbeSettingsPanel

from .object_probe_render_panel import ObjectProbeRenderPanel

classes = (
    SceneSettingsPanel,
    ProbeSettingsPanel,
    # sub panels
    SceneIrradianceSettingsPanel,
    SceneReflectionSettingsPanel,
    SceneGlobalEnvSettingsPanel,
    # object panels
    ObjectProbeRenderPanel,
)

def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)