
def is_exportabled_light_probe(context):
    return context.object != None and context.object.type == 'LIGHT_PROBE' and (context.object.data.type == 'CUBEMAP' or context.object.data.type == 'GRID')