import bpy
from bpy.types import Context
from .common import (
    draw_irradiance_bake_settings,
    draw_render_settings,
    draw_reflection_bake_settings,
    setup_panel_layout,
)

from ..helpers.poll import (
    is_exportable_default_light_probe,
    is_exportable_irradiance_light_probe,
    is_exportable_light_probe,
    is_exportable_reflection_light_probe,
    is_export_enabled,
    is_using_default_settings,
)

from ..renderer.batch_renderer import Batch_renderer

class BAKE_GI_PT_probe_render_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_probe_render_settings"
    bl_label = "Probe rendering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BAKE_GI_PT_probe_settings"

    @classmethod
    def poll(cls, context):
        return (
            is_export_enabled(context.object)
            and not is_using_default_settings(context.object)
            and not is_exportable_default_light_probe(context.object)
        )

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)
        draw_render_settings(
            context, self.layout, context.object.data.bake_gi.render_settings
        )




class BAKE_GI_PT_probe_bake_reflection_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_probe_bake_reflection_settings"
    bl_label = "Reflection volume baking"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BAKE_GI_PT_probe_settings"

    @classmethod
    def poll(cls, context):
        return (
            is_export_enabled(context.object)
            and not is_using_default_settings(context.object)
            and is_exportable_reflection_light_probe(context.object)
        )

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)
        draw_reflection_bake_settings(
            context, self.layout, context.object.data.bake_gi.bake_settings
        )


class BAKE_GI_PT_probe_bake_irradiance_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_probe_bake_irradiance_settings"
    bl_label = "Irradiance volume baking"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BAKE_GI_PT_probe_settings"

    @classmethod
    def poll(cls, context):
        return (
            is_export_enabled(context.object)
            and not is_using_default_settings(context.object)
            and is_exportable_irradiance_light_probe(context.object)
        )

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)
        draw_irradiance_bake_settings(
            context, self.layout, context.object.data.bake_gi.bake_settings
        )


class BAKE_GI_PT_probe_render_global_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_probe_render_global_settings"
    bl_label = "Rendering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BAKE_GI_PT_probe_settings"

    @classmethod
    def poll(cls, context):
        return (
            is_export_enabled(context.object)
            and is_exportable_default_light_probe(context.object)
        )

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)
        draw_render_settings(
            context, self.layout, context.scene.bake_gi.global_render_settings
        )


class BAKE_GI_PT_probe_bake_global_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_probe_bake_global_settings"
    bl_label = "Global volume baking"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BAKE_GI_PT_probe_settings"

    @classmethod
    def poll(cls, context):
        return is_exportable_default_light_probe(
            context.object
        )

    def draw(self, context):
        layout = self.layout
        setup_panel_layout(context, layout)
        
        layout.separator()
        layout.label(text = "Irradiance")
        draw_irradiance_bake_settings(
            context, layout, context.scene.bake_gi.global_irradiance_bake_settings
        )

        layout.separator()
        layout.label(text = "Reflection")
        draw_reflection_bake_settings(
            context, layout, context.scene.bake_gi.global_reflection_bake_settings
        )


class BAKE_GI_PT_probe_settings(bpy.types.Panel):
    bl_idname = "BAKE_GI_PT_probe_settings"
    bl_label = "GI bake volume"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return is_exportable_light_probe(context.object)

    def draw_header(self, context: Context):
        data = context.object.data
        prop = data.bake_gi
        self.layout.prop(prop, "enable_export", text="")

    def draw(self, context):
        if is_export_enabled(context.object):
            data = context.object.data
            bake_gi = data.bake_gi

            layout = self.layout
            setup_panel_layout(context, layout)


            batch_renderer = Batch_renderer.get_default()
            col = layout.column()

            if batch_renderer.available():
                

                render_op_row = col.row(align=True)
                render_op_row.split(factor=2)
                render_op_row.scale_y = 1.5

                if not bake_gi.is_global_probe:
                    if data.type == 'GRID':
                        render_op_row.operator('bake_gi.render_irradiance_probes', icon='RENDER_RESULT', text="Bake")
                    elif data.type == 'CUBEMAP' :
                        render_op_row.operator('bake_gi.render_reflection_probes', icon='RENDER_RESULT', text="Bake")
                else:
                    render_op_row.operator('bake_gi.render_default_probes', icon='RENDER_RESULT', text="Bake")
                
                render_op_row.separator_spacer()
                render_op_row.operator('bake_gi.clear_probes_cache', icon='TRASH', text="Clear cache")
            else:
                row = col.row()
                row.prop(context.scene.bake_gi, "batch_render_progress", text="Baking")
                row.operator('bake_gi.cancel_render', icon='CANCEL', text="")

            
            col.separator_spacer()

            if data.type == "CUBEMAP":
                col.prop(bake_gi, "is_global_probe", text="Use as global probe")

            if not is_exportable_default_light_probe(context.object):
                col.prop(bake_gi, "use_default_settings")

            
            

        # layout = self.layout
        # layout.use_property_split = True
        # layout.use_property_decorate = False

        # row = layout.row()

        # # scene_settings = context.scene.bake_gi

        # master_row = layout.column()
        # master_row.active = prop.enable_export

        # row = master_row.row()

        # if data.type == 'CUBEMAP':
        #     row.prop(prop, 'is_global_probe', text='Use as default probe')

        # master_row.separator(factor=4)

        # # global_props = context.scene.bake_gi

        # if not prop.is_global_probe:
        #     row = master_row.row(align=True)
        #     col = row.column()
        #     # col.operator('probe.render', icon='RENDER_RESULT')
        #     if data.type == 'GRID':
        #         col.operator('bake_gi.render_irradiance_probes', icon='RENDER_RESULT')
        #         col = row.column()
        #     elif data.type == 'CUBEMAP' :
        #         col.operator('bake_gi.render_reflection_probes', icon='RENDER_RESULT')
        #         col = row.column()

        #     col.operator('bake_gi.clear_probes_cache', icon='TRASH')

        #     master_row.separator(factor=2)

        #     row = master_row.row()
        #     row.prop(prop, 'use_default_settings')

        #     master_row = layout.column()
        #     master_row.active = prop.enable_export and not prop.use_default_settings

        #     # if not prop.use_default_settings:
        #     col = master_row.column()
        #     col.prop(prop, 'map_size')
        #     col.prop(prop, 'samples_max')

        #     col.separator(factor=2)
        #     col.prop(prop, 'export_map_size')
        #     col.prop(prop, 'export_max_texture_size')

        #     if data.type == 'CUBEMAP':
        #         col = master_row.column()

        #         col.prop(prop, 'export_nb_levels')
        #         col.prop(prop, 'export_level_roughness')
        #         col.prop(prop, 'export_start_roughness')

        # else:

        #     row = master_row.row(align=True)
        #     col = row.column()
        #     col.operator('bake_gi.render_default_probes', icon='RENDER_RESULT')

        #     col = row.column()
        #     col.operator('bake_gi.clear_probes_cache', icon='TRASH')

        #     col = master_row.column()
        #     col.separator(factor=2)

        #     col.prop(global_props, 'global_map_size')
        #     col.prop(global_props, 'global_samples_max')

        #     col.separator(factor=2)
        #     row = col.row()
        #     row.label(text="Irradiance")

        #     col.prop(global_props, 'global_irradiance_export_map_size', text = "Cubemap size")
        #     col.prop(global_props, 'global_irradiance_max_texture_size', text = "Final texture max width")

        #     col.separator(factor=2)
        #     row = col.row()
        #     row.label(text="Reflectance")
        #     col.prop(global_props, 'global_reflectance_export_map_size', text = "Cubemap size")
        #     col.prop(global_props, 'global_reflectance_max_texture_size', text = "Final texture max width")
        #     col.prop(global_props, 'global_reflectance_nb_levels', text = "Levels amount")
        #     col.prop(global_props, 'global_reflectance_start_roughness', text = "Start roughness")
        #     col.prop(global_props, 'global_reflectance_level_roughness', text = "Roughness step")
        pass


classes = (
    BAKE_GI_PT_probe_settings,
    BAKE_GI_PT_probe_render_global_settings,
    BAKE_GI_PT_probe_render_settings,
    BAKE_GI_PT_probe_bake_reflection_settings,
    BAKE_GI_PT_probe_bake_irradiance_settings,
    BAKE_GI_PT_probe_bake_global_settings,
)


def register_panels():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_panels():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
