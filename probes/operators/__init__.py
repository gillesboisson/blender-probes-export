from bpy.utils import register_class, unregister_class

from .render_probe_operators import (
    RenderProbe,
    RenderProbes,
    ClearRenderProbeCache,
    ClearProbeCacheDirectory,
    RenderReflectionProbeOperator,
    RenderIrradianceProbeOperator,
    RenderDefaultProbeOperator
)
from .set_probes_export_directory import SetProbeExportDirectory

from .pack_probes_operators import (
    PackIrradianceProbe,
    PackReflectionProbe,
    PackGlobalProbe,
)

from .multirender import RenderBatch


classes = (
    RenderProbe,
    RenderProbes,
    SetProbeExportDirectory,
    PackIrradianceProbe,
    PackReflectionProbe,
    ClearRenderProbeCache,
    ClearProbeCacheDirectory,
    PackGlobalProbe,
    RenderReflectionProbeOperator,
    RenderIrradianceProbeOperator,
    RenderDefaultProbeOperator
)


def register_operators():
    RenderBatch.getDefault()
    for cls in classes:
        register_class(cls)


def unregister_operators():
    RenderBatch.disposeDefault()

    for cls in reversed(classes):
        unregister_class(cls)
