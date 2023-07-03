
from bpy.utils import register_class, unregister_class

from .export_probe import ExportProbe, ExportProbes
from .set_probes_export_directory import SetProbeExportDirectory

classes = (
    ExportProbe,
    ExportProbes,
    SetProbeExportDirectory
)

def register_operators():
    for cls in classes:
        register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        unregister_class(cls)

