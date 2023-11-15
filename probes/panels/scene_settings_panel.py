import bpy
from bpy.types import Context
from ..helpers.files import probe_is_cached
from ..helpers.poll import get_available_probe_volumes

from .common import *
from ..renderer.batch_renderer import Batch_renderer



class BAKE_GI_PT_base_scene_volumes_list(bpy.types.Panel):

    def draw(self, context: Context):
        
        layout = self.layout
        col = layout.column()

        volumes = get_available_probe_volumes(context)
        row = col.grid_flow(columns=2, even_columns= False, even_rows=False, row_major=True)

        for volume in volumes:
            
            [volume_object, volume_type, operator, is_cached] = volume

            row.label(text=volume_object.name)

            op_row = row.row(align=True)
            render_op = op_row.operator(operator, icon="RENDER_RESULT", text="")

            render_op.probe_volume_name = volume_object.name
                
            if probe_is_cached(context.scene.bake_gi.export_directory_path,  volume_object.name):
                clear_cache_op = op_row.operator("bake_gi.clear_probes_cache", icon="TRASH", text="")
                clear_cache_op.probe_volume_name = volume_object.name

class BAKE_GI_PT_scene_volumes_list(BAKE_GI_PT_base_scene_volumes_list):
    bl_idname = "BAKE_GI_PT_scene_volumes_list"
    bl_parent_id = "BAKE_GI_PT_scene_settings"
    bl_label = "Probe volumes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    pass

class BAKE_GI_PT_scene_export_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_export_settings"
    bl_parent_id = "BAKE_GI_PT_scene_settings"
    bl_label = "Export settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        scene = context.scene
        props = scene.bake_gi

        layout = self.layout
        setup_panel_layout(context, self.layout)

        row = layout.row()

        row.prop(props, "export_directory_path")
        row.operator(
            "bake_gi.set_probes_directory", icon="FILE_FOLDER", text=""
        )  # .export_path = prop.export_path
        col = layout.column()
        col.prop(props, "export_format")

        col.separator(factor=2)
        # if prop.export_format == 'SDR':
        col.prop(props, "export_exposure")


class BAKE_GI_PT_scene_default_volume_default_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_default_volume_default_settings"
    bl_parent_id = "BAKE_GI_PT_scene_settings"
    bl_label = "Global probe settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        # scene = context.scene
        # props = scene.bake_gi

        layout = self.layout

        setup_panel_layout(context, self.layout)
        layout.separator()
        layout.label(text="Rendering")
        draw_render_settings(
            context, self.layout, context.scene.bake_gi.global_render_settings
        )

        layout.separator()
        layout.label(text="Irradiance baking")
        draw_irradiance_bake_settings(
            context,
            self.layout,
            context.scene.bake_gi.global_irradiance_bake_settings,
        )
        layout.separator()
        layout.label(text="Reflection baking")
        draw_reflection_bake_settings(
            context,
            self.layout,
            context.scene.bake_gi.global_reflection_bake_settings,
        )


class BAKE_GI_PT_scene_irradiance_volume_default_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_irradiance_volume_default_settings"
    bl_parent_id = "BAKE_GI_PT_scene_settings"
    bl_label = "Irradiance volumes default settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)

        layout = self.layout

        setup_panel_layout(context, self.layout)
        layout.separator()
        layout.label(text="Rendering")
        draw_render_settings(
            context,
            self.layout,
            context.scene.bake_gi.default_irradiance_render_settings,
        )

        layout.separator()
        layout.label(text="Baking")
        draw_irradiance_bake_settings(
            context,
            self.layout,
            context.scene.bake_gi.global_irradiance_bake_settings,
        )


class BAKE_GI_PT_scene_reflection_volume_default_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_reflection_volume_default_settings"
    bl_parent_id = "BAKE_GI_PT_scene_settings"
    bl_label = "Reflection volumes default settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)

        layout = self.layout

        setup_panel_layout(context, self.layout)
        layout.separator()
        layout.label(text="Rendering")
        draw_render_settings(
            context,
            self.layout,
            context.scene.bake_gi.default_reflection_render_settings,
        )

        layout.separator()
        layout.label(text="Baking")
        draw_reflection_bake_settings(
            context,
            self.layout,
            context.scene.bake_gi.global_reflection_bake_settings,
        )


def draw_bake_all_layout(context, layout):
    scene = context.scene
    prop = scene.bake_gi
    
    batch_renderer = Batch_renderer.get_default()
    col = layout.column()
    
    if batch_renderer.available():
        render_op_row = col.row(align=True)
        render_op_row.split(factor=2)
        render_op_row.scale_y = 1.5
        
        render_all_op = render_op_row.operator("bake_gi.render_all_probes", icon="RENDER_RESULT", text="Bake probes")
        render_op_row.operator(
            "bake_gi.clear_all_probes_cache", icon="TRASH"
        )

        row = col.row(align=True)
        row.use_property_split = False
        row.use_property_decorate = False
        row.prop(prop,"render_only_non_cached_probes")

    else:
        row = col.row()
        row.prop(context.scene.bake_gi, "batch_render_progress", text="Baking")
        row.operator('bake_gi.cancel_render', icon='CANCEL', text="")  
class BAKE_GI_PT_scene_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_settings"
    bl_label = "GI bake volumes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        

        setup_panel_layout(context, self.layout)
        # col = row.column_flow(columns=2, align=True)
        
        draw_bake_all_layout(context, self.layout)
        
        
        


classes = (
    BAKE_GI_PT_scene_settings,
    BAKE_GI_PT_scene_volumes_list,
    BAKE_GI_PT_scene_export_settings,
    BAKE_GI_PT_scene_default_volume_default_settings,
    BAKE_GI_PT_scene_reflection_volume_default_settings,
    BAKE_GI_PT_scene_irradiance_volume_default_settings,
)


def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
