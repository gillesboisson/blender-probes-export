import bpy


def is_export_enabled(object):
    return object != None and object.data.bake_gi.enable_export

def is_using_default_settings(object):
    return object != None and object.data.bake_gi.use_default_settings


def is_exportable_light_probe(object):
    return (
        object != None
        and object.type == "LIGHT_PROBE"
        and (object.data.type == "CUBEMAP" or object.data.type == "GRID")
    )


def is_exportable_irradiance_light_probe(object):
    return is_exportable_light_probe(object) and object.data.type == "GRID"


def is_exportable_reflection_light_probe(object):
    return (
        is_exportable_light_probe(object)
        and object.data.type == "CUBEMAP"
        and object.data.bake_gi.is_global_probe == False
    )


def is_exportable_default_light_probe(object):
    return (
        is_exportable_light_probe(object)
        and object.data.type == "CUBEMAP"
        and object.data.bake_gi.is_global_probe == True
    )


def get_context_probes_names(context):
    names = []
    for object in bpy.data.objects:
        if object.type == "LIGHT_PROBE" and (
            object.data.type == "CUBEMAP" or object.data.type == "GRID"
        ):
            names.append(object.name)
            # if object.data.bake_gi.is_global_probe:
            #     names.append(global_probe_render_name)
            # else:
            #     names.append(object.name)
    return names
