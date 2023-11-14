from .scene_settings_props import register_export_settings, unregister_export_settings
from .probes_settings import register_probes_settings, unregister_probes_settings

from .object_props import register_object_bake_props, unregister_object_bake_props

from .common import (
    register_props as register_common_props,
    unregister_props as unregister_common_props,
)


def register_props():
    register_common_props()
    register_export_settings()
    register_probes_settings()
    register_object_bake_props()


def unregister_props():
    unregister_common_props()
    unregister_export_settings()
    unregister_probes_settings()
    unregister_object_bake_props()
