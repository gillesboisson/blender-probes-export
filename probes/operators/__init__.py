from bpy.utils import register_class, unregister_class

from .render_probe_operators import (
    ClearRenderProbeCache,
    ClearProbeCacheDirectory,
    RenderReflectionProbeOperator,
    RenderIrradianceProbeOperator,
    RenderDefaultProbeOperator,
    RenderAllProbesOperator,
)
from .set_probes_export_directory import SetProbeExportDirectory

from .pack_probes_operators import (
    PackIrradianceProbe,
    PackReflectionProbe,
    PackGlobalProbe,
)

from .multirender import RenderBatch


classes = (
    SetProbeExportDirectory,
    PackIrradianceProbe,
    PackReflectionProbe,
    ClearRenderProbeCache,
    ClearProbeCacheDirectory,
    PackGlobalProbe,
    RenderReflectionProbeOperator,
    RenderIrradianceProbeOperator,
    RenderDefaultProbeOperator,
    RenderAllProbesOperator,
)


def register_operators():
    RenderBatch.getDefault()
    for cls in classes:
        register_class(cls)


def unregister_operators():
    RenderBatch.disposeDefault()

    for cls in reversed(classes):
        unregister_class(cls)
