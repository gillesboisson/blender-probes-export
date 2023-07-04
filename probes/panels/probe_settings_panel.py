import bpy

from ..helpers.poll import is_exportabled_light_probe


class ProbeSettingsPanel(bpy.types.Panel):

    bl_idname = 'VIEW3D_PT_probes_export_settings'
    bl_label = 'Probes export settings'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return is_exportabled_light_probe(context)

    def draw(self, context):
        data = context.object.data
        prop = data.probes_export

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row()

        scene_settings = context.scene.probes_export

        row.prop(prop, 'enable_export')

        if prop.enable_export:
            row = layout.row()
            row.prop(prop, 'use_default_settings')

            if not prop.use_default_settings:
                row = layout.row()
                row.prop(prop, 'map_size')
                row = layout.row()
                row.prop(prop, 'samples_max')
                row = layout.row()
                row.prop(prop, 'radiance_levels')
            else:
                
                col = layout.column()
                col.label(text = "Map size: " + str(scene_settings.reflection_cubemap_default_map_size))
                col.label(text="Samples max: " + str(scene_settings.reflection_cubemap_default_samples_max))
                col.label(text="Radiance levels: " + str(scene_settings.reflection_cubemap_default_radiance_levels))


            

        row = layout.row()
        row.operator('probe.export')

        if data.type == 'GRID':
            row = layout.row()
            row.operator('probe.pack_irradiance') 
        elif data.type == 'CUBEMAP' :
            row = layout.row()
            row.operator('probe.pack_relection')
        