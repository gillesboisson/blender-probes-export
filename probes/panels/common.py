def draw_render_settings(context, layout, prop):
    col = layout.column()
    col.separator(factor=0)
    col.prop(prop, "map_size")
    col.row().prop(prop, "samples_max")
    col.row().prop(prop, "samples_min")
    col.row().prop(prop, "time_limit")


def draw_reflection_bake_settings(context, layout, prop):
    col = layout.column()
    col.prop(prop, "map_size")
    # col.prop(prop, "max_texture_size")
    col.prop(prop, "start_roughness")
    col.prop(prop, "level_roughness")
    col.prop(prop, "nb_levels")


def draw_irradiance_bake_settings(context, layout, prop):
    col = layout.column()
    col.prop(prop, "map_size")
    col.prop(prop, "max_texture_size")



def setup_panel_layout(context,layout):
    layout.use_property_split = True
    layout.use_property_decorate = False
    layout.separator(factor=0)