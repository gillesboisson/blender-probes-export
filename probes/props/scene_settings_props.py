import bpy
from bpy.props import *
from bpy.utils import register_class, unregister_class

from .common import *


class BAKE_GI_scene_settings(bpy.types.PropertyGroup):
    export_path: StringProperty(name="Data export path", default="./")
    export_directory_path: StringProperty(name="Export directory", default="./")

    # export type
    export_format: EnumProperty(
        name="Export format",
        items=(
            ("SDR", "SDR : PNG image", "Export SDR"),
            ("HDR", "HDR : Open EXR", "Export HDR"),
        ),
        default="HDR",
    )

    export_exposure: FloatProperty(
        description="For SDR and preview only",
        name="Exposure",
        default=1.0,
        min=0.0,
        max=10.0,
    )

    # global envmap props

    global_render_settings: PointerProperty(type=BAKE_GI_probes_render_settings)
    global_reflection_bake_settings: PointerProperty(type=BAKE_GI_probes_bake_settings)
    global_irradiance_bake_settings: PointerProperty(type=BAKE_GI_probes_bake_settings)

    default_reflection_render_settings: PointerProperty(
        type=BAKE_GI_probes_render_settings
    )
    default_reflection_bake_settings: PointerProperty(type=BAKE_GI_probes_bake_settings)

    default_irradiance_render_settings: PointerProperty(
        type=BAKE_GI_probes_render_settings
    )
    default_irradiance_bake_settings: PointerProperty(type=BAKE_GI_probes_bake_settings)

    batch_render_progress: IntProperty(name="Render progress", default=0, min=0, max=100, subtype="PERCENTAGE")

    render_only_non_cached_probes: bpy.props.BoolProperty(
        name="Bake only none cached probes", default=False
    )


# FileSelectEntry

classes = (
    BAKE_GI_scene_settings,
    # SetProbeExportDirectory
)


def register_export_settings():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.bake_gi = PointerProperty(type=BAKE_GI_scene_settings)


def unregister_export_settings():
    for cls in reversed(classes):
        unregister_class(cls)

    delattr(bpy.types.Scene, "bake_gi")
