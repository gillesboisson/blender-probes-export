import bpy

from .object_probe_render_panel import (
    register_panels as register_probe_render_panel,
    unregister_panels as unregister_probe_render_panel,
)

from .scene_settings_panel import (
    register_panels as register_scene_settings_panel,
    unregister_panels as unregister_scene_settings_panel,
)

from .probe_settings_panel import (
    register_panels as register_probe_settings_panel,
    unregister_panels as unregister_probe_settings_panel,
)



# from .scene_settings_panel import (
#     BAKE_GI_PT_scene_default_probes_settings,
#     BAKE_GI_PT_scene_settings,
#     BAKE_GI_PT_scene_irradiance_probes_settings,
#     BAKE_GI_PT_scene_reflection_probes_settings,
# )
# from .probe_settings_panel import (
#     BAKE_GI_PT_probe_settings,
#     BAKE_GI_PT_probe_bake_global_settings,
#     BAKE_GI_PT_probe_bake_irradiance_settings,
#     BAKE_GI_PT_probe_bake_reflection_settings,
#     BAKE_GI_PT_probe_render_settings,
#     BAKE_GI_PT_default_probe_render_settings,
# )
# from .object_probe_render_panel import (
#     BAKE_GI_PT_object,
   
# )
# classes = (
    
#     BAKE_GI_PT_scene_settings,
#     # sub panels
#     BAKE_GI_PT_scene_irradiance_probes_settings,
#     BAKE_GI_PT_scene_reflection_probes_settings,
#     BAKE_GI_PT_scene_default_probes_settings,
#     # object panels
#     BAKE_GI_PT_object,
# )


def register_panels():
    register_probe_render_panel()
    register_scene_settings_panel()
    register_probe_settings_panel()


def unregister_panels():
    unregister_probe_render_panel()
    unregister_scene_settings_panel()
    unregister_probe_settings_panel()
