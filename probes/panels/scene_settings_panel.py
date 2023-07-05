import bpy


class SceneReflectionSettingsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_probes_export_scene_irradiance_settings'
    bl_parent_id = 'VIEW3D_PT_probes_export_scene_settings'
    bl_label = 'Reflection cubemaps'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        scene = context.scene
        prop = scene.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column()
        col.label(text="Render")
        layout.separator(factor=0.5)
        col = layout.column()
        col.prop(prop, 'reflection_cubemap_default_map_size')
        col.prop(prop, 'reflection_cubemap_default_samples_max')
        col.prop(prop, 'reflection_cubemap_default_radiance_levels')

        layout.separator(factor=2)
        col = layout.column()
        col.label(text="Export")
        layout.separator(factor=0.5)
        col = layout.column()
        col.prop(prop, 'reflection_volume_default_export_map_size')
        col.prop(prop, 'reflection_volume_default_export_max_texture_size')
        col.prop(prop, 'reflection_volume_default_export_nb_levels')
        col.prop(prop, 'reflection_volume_default_export_start_roughness')
        col.prop(prop, 'reflection_volume_default_export_level_roughness')

class SceneIrradianceSettingsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_probes_export_scene_reflectance_settings'
    bl_parent_id = 'VIEW3D_PT_probes_export_scene_settings'
    bl_label = 'Irradiance cubemaps'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        scene = context.scene
        prop = scene.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column()
        col.label(text="Render")
        layout.separator(factor=0.5)
        col = layout.column()
        col.prop(prop, 'irradiance_volume_default_map_size')
        col.prop(prop, 'irradiance_volume_default_samples_max')

        layout.separator(factor=2)
        col = layout.column()
        col.label(text="Export")
        layout.separator(factor=0.5)
        col = layout.column()
        col.prop(prop, 'irradiance_volume_default_export_map_size')
        col.prop(prop, 'irradiance_volume_default_export_max_texture_size')



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
        row.operator('probes.export', icon='EXPORT')
        




        