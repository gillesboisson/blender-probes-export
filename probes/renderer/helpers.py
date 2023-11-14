from math import floor
def reset_objects_render_settings(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = False


def update_collection_visibility_for_probe(collection, probe_data):
    visibility_collection = probe_data.visibility_collection
    invert_visibility = probe_data.invert_visibility_collection
    hasHiddenChild = False
    for child in collection:
        if child == visibility_collection:
            child.hide_render = invert_visibility
        elif not child.children:
            child.hide_render = not invert_visibility
        else:
            child.hide_render = update_collection_visibility_for_probe(
                child.children, probe_data
            )

        hasHiddenChild = hasHiddenChild and child.hide_render

    return hasHiddenChild


def reset_collection_visibility(context):
    collections = context.scene.collection.children_recursive

    for collection in collections:
        collection.hide_render = False


def get_scene_renderered_object_names(context):
    objects = []

    for collection in context.scene.collection.children_recursive:
        if collection.hide_render == False:
            for ob in collection.objects:
                if ob.type == "MESH" and ob.hide_render == False:
                    # as visibility is reset after check, this avoid having double object in list
                    ob.hide_render = True
                    objects.append(ob.name)

    for ob in objects:
        context.scene.objects[ob].hide_render = False

    return objects