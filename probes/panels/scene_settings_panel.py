import bpy


class SceneGlobalEnvSettingsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_probes_export_scene_global_env_settings'
    bl_parent_id = 'VIEW3D_PT_probes_export_scene_settings'
    bl_label = 'Default probe cubmaps'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        scene = context.scene
        props = scene.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        
        col = layout.column()
        col.separator(factor=2)

        col.prop(props, 'global_map_size')
        col.prop(props, 'global_samples_max')
        
        col = layout.column()

        col.separator(factor=2)
        row = col.row()
        row.label(text="Irradiance")

        col.prop(props, 'global_irradiance_export_map_size', text = "Cubemap size")
        col.prop(props, 'global_irradiance_max_texture_size', text = "Max final texture size")
        
        col.separator(factor=2)
        row = col.row()
        row.label(text="Reflectance")
        col.prop(props, 'global_reflectance_export_map_size', text = "Cubemap size")
        col.prop(props, 'global_reflectance_max_texture_size', text = "Max final texture size")
        col.prop(props, 'global_reflectance_nb_levels', text = "Levels amount")
        col.prop(props, 'global_reflectance_level_roughness', text = "Roughness step")
        col.prop(props, 'global_reflectance_start_roughness', text = "Start roughness")

class SceneReflectionSettingsPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_probes_export_scene_irradiance_settings'
    bl_parent_id = 'VIEW3D_PT_probes_export_scene_settings'
    bl_label = 'Radiance cubemaps'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

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
    bl_context = "render"

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
    bl_label = 'GI bake'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):

        scene = context.scene
        prop = scene.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        # col = row.column_flow(columns=2, align=True)
        col = layout.row()
        
        
        col.prop(prop, 'export_directory_path')
        col.operator('probes_export.set_export_directory', icon='FILE_FOLDER', text='') #.export_path = prop.export_path
        col = layout.column()
        col.prop(prop, 'export_format') 
        if prop.export_format == 'SDR':
            col.prop(prop, 'export_exposure')

        col = layout.row()
        
        layout.separator(factor=2)
        col = layout.column()
        row = col.row(align=True)
        scol = row.column()
        scol.operator('probes_export.render_all', icon='RENDER_STILL')
        scol = row.column()
        scol.operator('probes_export.clear_main_cache_directory', icon='TRASH') #.export_path = prop.export_path
        




        