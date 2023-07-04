
def is_exportabled_light_probe(context):
    return context.object != None and context.object.type == 'LIGHT_PROBE' and (context.object.data.type == 'CUBEMAP' or context.object.data.type == 'GRID')


def is_exportabled_grid_light_probe(context):
    return is_exportabled_light_probe(context) and context.object.data.type == 'GRID'

def is_exportabled_reflection_light_probe(context):
    return is_exportabled_light_probe(context) and context.object.data.type == 'CUBEMAP'