import bpy

from .common import *
from ..renderer.batch_renderer import Batch_renderer


class BAKE_GI_PT_scene_export_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_export_settings"
    bl_parent_id = "BAKE_GI_PT_scene_settings"
    bl_label = "Export"
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

        # col = layout.column()
        # col.separator(factor=2)

        # col.prop(props, 'global_map_size')
        # col.prop(props, 'global_samples_max')

        # col = layout.column()

        # col.separator(factor=2)
        # row = col.row()
        # row.label(text="Irradiance")

        # col.prop(props, 'global_irradiance_export_map_size', text = "Cubemap size")
        # col.prop(props, 'global_irradiance_max_texture_size', text = "Max final texture size")

        # col.separator(factor=2)
        # row = col.row()
        # row.label(text="Reflectance")
        # col.prop(props, 'global_reflectance_export_map_size', text = "Cubemap size")
        # col.prop(props, 'global_reflectance_max_texture_size', text = "Max final texture size")
        # col.prop(props, 'global_reflectance_nb_levels', text = "Levels amount")
        # col.prop(props, 'global_reflectance_level_roughness', text = "Roughness step")
        # col.prop(props, 'global_reflectance_start_roughness', text = "Start roughness")


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

        # scene = context.scene
        # prop = scene.bake_gi

        # layout = self.layout
        # layout.use_property_split = True
        # layout.use_property_decorate = False

        # col = layout.column()
        # col.label(text="Render")
        # layout.separator(factor=0.5)
        # col = layout.column()
        # col.prop(prop, "reflection_cubemap_default_map_size")
        # col.prop(prop, "reflection_cubemap_default_samples_max")
        # col.prop(prop, "reflection_cubemap_default_radiance_levels")

        # layout.separator(factor=2)
        # col = layout.column()
        # col.label(text="Export")
        # layout.separator(factor=0.5)
        # col = layout.column()
        # col.prop(prop, "reflection_volume_default_export_map_size")
        # col.prop(prop, "reflection_volume_default_export_max_texture_size")
        # col.prop(prop, "reflection_volume_default_export_nb_levels")
        # col.prop(prop, "reflection_volume_default_export_start_roughness")
        # col.prop(prop, "reflection_volume_default_export_level_roughness")


# class BAKE_GI_PT_scene_irradiance_probes_settings(bpy.types.Panel):
#     bl_idname = "BAKE_GI_PT_scene_irradiance_probes_settings"
#     bl_parent_id = "BAKE_GI_PT_scene_settings"
#     bl_label = "Irradiance cubemaps"
#     bl_space_type = "PROPERTIES"
#     bl_region_type = "WINDOW"
#     bl_context = "render"

#     def draw(self, context):
#         scene = context.scene
#         prop = scene.bake_gi

#         layout = self.layout
#         layout.use_property_split = True
#         layout.use_property_decorate = False

#         col = layout.column()
#         col.label(text="Render")
#         layout.separator(factor=0.5)
#         col = layout.column()
#         col.prop(prop, "irradiance_volume_default_map_size")
#         col.prop(prop, "irradiance_volume_default_samples_max")

#         layout.separator(factor=2)
#         col = layout.column()
#         col.label(text="Export")
#         layout.separator(factor=0.5)
#         col = layout.column()
#         col.prop(prop, "irradiance_volume_default_export_map_size")
#         col.prop(prop, "irradiance_volume_default_export_max_texture_size")


class BAKE_GI_PT_scene_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_scene_settings"
    bl_label = "GI bake"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        scene = context.scene
        prop = scene.bake_gi

        setup_panel_layout(context, self.layout)
        # col = row.column_flow(columns=2, align=True)
        
        batch_renderer = Batch_renderer.get_default()
        col = self.layout.column()
        
        if batch_renderer.available():
            render_op_row = col.row(align=True)
            render_op_row.split(factor=2)
            render_op_row.scale_y = 1.5
            
            render_op_row.operator("bake_gi.render_all_probes", icon="RENDER_RESULT")
            render_op_row.separator_spacer()
            render_op_row.operator(
                "bake_gi.clear_all_probes_cache", icon="TRASH"
            )
        else:
            row = col.row()
            row.prop(context.scene.bake_gi, "batch_render_progress", text="Baking")
            row.operator('bake_gi.cancel_render', icon='CANCEL', text="")  
        


classes = (
    BAKE_GI_PT_scene_settings,
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
