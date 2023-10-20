
from bpy.utils import register_class, unregister_class

from .render_probe_operators import RenderProbe, RenderProbes, ClearRenderProbeCache, ClearProbeCacheDirectory
from .set_probes_export_directory import SetProbeExportDirectory

from .pack_probes_operators import PackIrradianceProbe, PackReflectionProbe, PackGlobalProbe

classes = (
    RenderProbe,
    RenderProbes,
    SetProbeExportDirectory,
    PackIrradianceProbe,
    PackReflectionProbe,
    ClearRenderProbeCache,
    ClearProbeCacheDirectory,
    PackGlobalProbe
)

def register_operators():
    for cls in classes:
        register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        unregister_class(cls)

