import bpy

from ..utils import is_exportabled_light_probe

class SceneSettingsPanel(bpy.types.Panel):

    bl_idname = 'VIEW3D_PT_probes_export_scene_settings'
    bl_label = 'Probes export'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):

        scene = context.scene
        prop = scene.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row()
        # col = row.column_flow(columns=2, align=True)
        row.prop(prop, 'export_directory_path')
        row.operator('probes_export.set_export_directory', icon='FILE_FOLDER', text='') #.export_path = prop.export_path

        
        layout.separator(factor=2)
        row = layout.column()
        row.label(text="Reflection cubemap default settings")
        layout.separator(factor=0.5)
        row = layout.column()
        row.prop(prop, 'reflection_cubemap_default_map_size')
        row.prop(prop, 'reflection_cubemap_default_samples_max')
        row.prop(prop, 'reflection_cubemap_default_radiance_levels')

        layout.separator(factor=2)
        row = layout.column()
        row.label(text="Irradiance volume default settings")
        layout.separator(factor=0.5)
        row = layout.column()
        row.prop(prop, 'irradiance_volume_default_map_size')
        row.prop(prop, 'irradiance_volume_default_samples_max')


        