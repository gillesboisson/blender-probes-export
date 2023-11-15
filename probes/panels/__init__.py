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

from .view_3d_panels import (
    register_panels as register_view_3d_panels,
    unregister_panels as unregister_view_3d_panels,
)

def register_panels():
    register_probe_render_panel()
    register_scene_settings_panel()
    register_probe_settings_panel()
    register_view_3d_panels()


def unregister_panels():
    unregister_probe_render_panel()
    unregister_scene_settings_panel()
    unregister_probe_settings_panel()
    unregister_view_3d_panels()
