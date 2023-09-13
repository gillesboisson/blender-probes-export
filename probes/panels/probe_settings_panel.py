import bpy
from bpy.types import Context

from ..helpers.poll import is_exportable_light_probe



class ProbeSettingsPanel(bpy.types.Panel):

    bl_idname = 'VIEW3D_PT_probes_export_settings'
    bl_label = 'Export probe'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return is_exportable_light_probe(context)
    
    def draw_header(self, context: Context):
        data = context.object.data
        prop = data.probes_export
        self.layout.prop(prop, 'enable_export', text='')

    def draw(self, context):
        data = context.object.data
        prop = data.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        row = layout.row()

        scene_settings = context.scene.probes_export

        master_row = layout.column()
        master_row.active = prop.enable_export

        row = master_row.row(align=True)
        col = row.column()
        col.operator('probe.render', icon='RENDER_STILL')
        col = row.column()
        # if data.type == 'GRID':
        #     col.operator('probe.pack_irradiance', icon='EXPORT')
        # elif data.type == 'CUBEMAP' :
        #     col.operator('probe.pack_relection', icon='EXPORT')

        col = row.column()
        col.operator('probe.clear_cache', icon='TRASH')

        master_row.separator(factor=2)

        row = master_row.row()
        row.prop(prop, 'use_default_settings')    

        master_row = layout.column()
        master_row.active = prop.enable_export and not prop.use_default_settings

        # if not prop.use_default_settings:
        col = master_row.column()
        col.prop(prop, 'map_size')
        col.prop(prop, 'samples_max')

        col.separator(factor=2)
        col.prop(prop, 'export_map_size')
        col.prop(prop, 'export_max_texture_size')

        if data.type == 'CUBEMAP':
            col = master_row.column()
            
            col.prop(prop, 'export_nb_levels')
            col.prop(prop, 'export_start_roughness')
            col.prop(prop, 'export_level_roughness')

                

        # else:
            
        #     col = master_col.column()
        #     if data.type == 'CUBEMAP':
            
        #         col.label(text="Map size: " + str(scene_settings.reflection_cubemap_default_map_size))
        #         col.label(text="Samples max: " + str(scene_settings.reflection_cubemap_default_samples_max))
        #         col.label(text="Cubemap face size: " + str(scene_settings.reflection_volume_default_export_map_size))
        #         col.label(text="Max final texture size: " + str(scene_settings.reflection_volume_default_export_max_texture_size))
        #         col.label(text="Irradiance levels amount: " + str(scene_settings.reflection_volume_default_export_nb_levels))
        #         col.label(text="Start roughness: " + str(scene_settings.reflection_volume_default_export_start_roughness))
        #         col.label(text="Roughness step: " + str(scene_settings.reflection_volume_default_export_level_roughness))
        #     elif data.type == 'GRID':
        #         col.label(text="Map size: " + str(scene_settings.irradiance_volume_default_render_map_size))
        #         col.label(text="Samples max: " + str(scene_settings.irradiance_volume_default_samples_max))
        #         col.label(text="Cubemap Map size: " + str(scene_settings.irradiance_volume_default_export_max_texture_size))


            


        