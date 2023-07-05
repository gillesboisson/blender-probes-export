
from .export_settings_props import register_export_settings, unregister_export_settings
from .data_probes_props import register_probes_settings, unregister_probes_settings

def register_props():
    register_export_settings()
    register_probes_settings()

def unregister_props():
    unregister_export_settings()
    unregister_probes_settings()