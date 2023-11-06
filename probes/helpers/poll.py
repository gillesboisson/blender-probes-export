import bpy


def is_exportable_light_probe(context):
    return context.object != None and context.object.type == 'LIGHT_PROBE' and (context.object.data.type == 'CUBEMAP' or context.object.data.type == 'GRID')


def is_exportable_grid_light_probe(context):
    return is_exportable_light_probe(context) and context.object.data.type == 'GRID'

def is_exportable_reflection_light_probe(context):
    return is_exportable_light_probe(context) and context.object.data.type == 'CUBEMAP'



def get_context_probes_names(context):
    names = []
    for object in bpy.data.objects:
        if object.type == 'LIGHT_PROBE' and (object.data.type == 'CUBEMAP' or object.data.type == 'GRID'):
            names.append(object.name)
            # if object.data.probes_export.is_global_probe:
            #     names.append(global_probe_render_name)
            # else:
            #     names.append(object.name)
    return names