
import bpy
from bpy.types import Context
from ..helpers.files import probe_is_cached
from ..helpers.poll import get_available_probe_volumes, is_exportable_light_probe, is_export_enabled

from .common import *
from ..renderer.batch_renderer import Batch_renderer




from .object_probe_render_panel import BAKE_GI_PT_base_object
from .scene_settings_panel import BAKE_GI_PT_base_scene_volumes_list, draw_bake_all_layout
from .probe_settings_panel import draw_bake_volume_layout




class BAKE_GI_PT_view_3d_probe_volume_object(BAKE_GI_PT_base_object):
    bl_idname = "BAKE_GI_PT_view_3d_probe_volume_object"
    bl_label = "Object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bake GI volumes"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == "MESH"

class BAKE_GI_PT_view_3d_probe_volume_probe(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_view_3d_probe_volume_probe"
    bl_label = "Volume"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bake GI volumes"

    @classmethod
    def poll(cls, context):
        return is_exportable_light_probe(context.object) and is_export_enabled(context.object)
    
    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, self.layout)
        
        col = layout.column()

        draw_bake_volume_layout(context, col)



class BAKE_GI_PT_view_3d_probe_volumes_list(BAKE_GI_PT_base_scene_volumes_list):
    bl_idname = "BAKE_GI_PT_view_3d_probe_volumes_list"
    bl_label = "Volumes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bake GI volumes"

    pass


class BAKE_GI_PT_view_3d_probe_volume(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_view_3d_probe_volume"
    bl_label = "Bake"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bake GI volumes"



    def draw(self, context: Context):
        layout = self.layout
        setup_panel_layout(context, self.layout)
        
        if is_exportable_light_probe(context.object) and is_export_enabled(context.object):
            col = layout.column()
            draw_bake_volume_layout(context, col, bake_label="Bake volume",clear_label="Clear volume cache", display_progress=False)

        col = layout.column()

        draw_bake_all_layout(context, col)

        pass


classes = (
    BAKE_GI_PT_view_3d_probe_volume,
    BAKE_GI_PT_view_3d_probe_volumes_list,
    BAKE_GI_PT_view_3d_probe_volume_object,
    # BAKE_GI_PT_view_3d_probe_volume_probe,
)

def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
