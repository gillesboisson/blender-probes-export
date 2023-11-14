from bpy.utils import register_class, unregister_class

from .render_probe_operators import (
    BAKE_GI_OP_clear_probes_render_cache,
    BAKE_GI_OP_clear_all_probes_render_cache,
    BAKE_GI_OP_render_reflection_probes,
    BAKE_GI_OP_render_irradiance_probes,
    BAKE_GI_OP_render_default_probe,
    BAKE_GI_OP_render_all_probes,
)
from .set_probes_export_directory import BAKE_GI_OP_set_probes_directory

from .pack_probes_operators import (
    BAKE_GI_OP_pack_irradiance_probes,
    BAKE_GI_OP_pack_reflection_probes,
    PackGlobalProbe,
)

from ..renderer.batch_renderer import Batch_renderer


classes = (
    BAKE_GI_OP_set_probes_directory,
    BAKE_GI_OP_pack_irradiance_probes,
    BAKE_GI_OP_pack_reflection_probes,
    BAKE_GI_OP_clear_probes_render_cache,
    BAKE_GI_OP_clear_all_probes_render_cache,
    PackGlobalProbe,
    BAKE_GI_OP_render_reflection_probes,
    BAKE_GI_OP_render_irradiance_probes,
    BAKE_GI_OP_render_default_probe,
    BAKE_GI_OP_render_all_probes,
)


def register_operators():
    Batch_renderer.get_default()
    for cls in classes:
        register_class(cls)


def unregister_operators():
    Batch_renderer.dispose_default()

    for cls in reversed(classes):
        unregister_class(cls)
