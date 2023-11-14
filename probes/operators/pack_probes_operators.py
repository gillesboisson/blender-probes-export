from bpy.types import Operator

from ..helpers import (
    is_exportable_irradiance_light_probe,
    is_exportable_reflection_light_probe,
)


from ..compositing import (
    pack_irradiance_probe,
    pack_reflectance_probe,
    pack_global_probe,
)

from ..helpers.files import (
    render_cache_subdirectory_exists,
)

class BAKE_GI_OP_pack_irradiance_probes(Operator):
    bl_idname = "probe.pack_irradiance"
    bl_label = "Pack irradiance probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_irradiance_light_probe(
            context.object
        ) and render_cache_subdirectory_exists(
            context.scene.bake_gi.export_directory_path, context.object.name
        )

    def execute(self, context):
        if pack_irradiance_probe(context) == None:
            self.report({"ERROR"}, "No data found for this probe")
            return {"FINISHED"}

        return {"FINISHED"}


class BAKE_GI_OP_pack_reflection_probes(Operator):
    bl_idname = "probe.pack_relection"
    bl_label = "Pack radiance probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_reflection_light_probe(
            context.object
        ) and render_cache_subdirectory_exists(
            context.scene.bake_gi.export_directory_path, context.object.name
        )

    def execute(self, context):
        if pack_reflectance_probe(context) == None:
            self.report({"ERROR"}, "No data found for this probe")
            return {"FINISHED"}

        return {"FINISHED"}


class PackGlobalProbe(Operator):
    bl_idname = "probe.pack_global"
    bl_label = "Pack default probe"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return is_exportable_reflection_light_probe(
            context.object
        ) and render_cache_subdirectory_exists(
            context.scene.bake_gi.export_directory_path, context.object.name
        )

    def execute(self, context):
        if pack_global_probe(context) == None:
            self.report({"ERROR"}, "No data found for this probe")
            return {"FINISHED"}

        return {"FINISHED"}
