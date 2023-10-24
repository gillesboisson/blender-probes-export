from math import floor, pi

from .files import (
    get_or_create_render_cache_subdirectory,
    irradiance_filename,
    pano_filename,
    save_probe_json_render_data,
    save_global_probe_json_render_data,
)

import os
import bpy
from mathutils import Matrix, Vector

from .create import create_pano_camera, create_cube_camera
from .settings import set_pano_render_settings, set_cube_render_settings

from .files import pano_file, cubemap_filename, global_pano_filename, global_pano_file
from .config import cube_map_face_names, cube_map_euler_rotations, get_export_extension


def reset_objects_render_settings(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = False


def update_objects_settings_for_irradiance(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = not ob.probes_render.render_by_irradiance_probes


def update_objects_settings_for_reflection(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = not ob.probes_render.render_by_reflection_probes


def update_objects_settings_for_global(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = not ob.probes_render.render_by_global_probe


def update_collection_visibility_for_probe(collection, probe_data):
    visibility_collection = probe_data.visibility_collection
    invert_visibility = probe_data.invert_visibility_collection
    hasVisible = False
    for child in collection:
        if child == visibility_collection:
            child.hide_render = invert_visibility
        elif not child.children:
            child.hide_render = not invert_visibility
        else:
            child.hide_render = update_collection_visibility_for_probe(
                child.children, probe_data
            )

        hasVisible = hasVisible or invert_visibility

    return hasVisible


def reset_collection_visibility(context):
    collections = context.scene.collection.children_recursive

    for collection in collections:
        collection.hide_render = False


def get_scene_renderered_object_names(context):
    objects = []
    for ob in context.scene.objects:
        if ob.type == "MESH" and ob.hide_render == False:
            objects.append(ob.name)
    return objects


def print_render_progress(text, progress_min=0, progress_max=1, progress: float = 0):
    print(
        str(floor((progress_min + progress) / progress_max * 100)) + "%" + " :: " + text
    )


# render panorama probe for global as hdr_pano
def render_pano_global_probe(context, operator, object, progress_min=0, progress_max=1):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world

    camera = create_pano_camera(context)
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)
    samples_max = settings.global_samples_max
    height = settings.global_map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    result_data = {
        "type": "global",
        "position": [
            transform.translation.x,
            transform.translation.z,
            -transform.translation.y,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
    }

    try:
        camera.location = transform.translation
        camera.rotation_euler = transform.to_euler()
        camera.rotation_euler.x += pi / 2
        camera.data.clip_start = prob.clip_start
        camera.data.clip_end = prob.clip_end

        filepath = global_pano_file(export_directory, prob_object.name, file_extension)
        result_data["file"] = global_pano_filename(prob_object.name, file_extension)

        print_render_progress("Baking global probe ", progress_min, progress_max, 0)

        set_pano_render_settings(
            context, camera, filepath, samples_max=samples_max, height=height
        )
        update_collection_visibility_for_probe(
            context.scene.collection.children, prob_object.data
        )

        bpy.ops.render.render(write_still=True)

        save_global_probe_json_render_data(export_directory, result_data)

    except Exception as e:
        catched_exception = e

    names = get_scene_renderered_object_names(context)
    result_data["baked_objects"] = names
    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data


# render panorama probe for reflection
def render_pano_reflection_probe(
    context, operator, object, progress_min=0, progress_max=1
):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world

    camera = create_pano_camera(context)
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    get_or_create_render_cache_subdirectory(export_directory, prob_object.name)

    result_data = {
        "type": "pano",
        "position": [
            transform.translation.x,
            transform.translation.z,
            -transform.translation.y,
        ],
        "scale": transform.to_scale().to_tuple(),
        "falloff": prob_object.data.falloff,
        "intensity": prob.intensity,
        "influence_type": prob.influence_type,
        "influence_distance": prob.influence_distance,
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "probe_type": "reflection",
        "name": object.name,
        "width": height * 2,
        "height": height,
    }

    try:
        camera.location = transform.translation
        camera.rotation_euler = transform.to_euler()
        # camera.scale = transform.to_scale()
        max_scale = max(camera.scale.x, camera.scale.y, camera.scale.z)
        camera.rotation_euler.x += pi / 2
        camera.data.clip_start = prob.clip_start
        camera.data.clip_end = prob.clip_end

        # get current file path
        # filename = pano_file(export_directory, prob_object.name)
        filepath = pano_file(export_directory, prob_object.name, file_extension)
        result_data["file"] = pano_filename(file_extension)

        print_render_progress(
            "Baking probe " + object.name, progress_min, progress_max, 0
        )

        set_pano_render_settings(
            context, camera, filepath, samples_max=samples_max, height=height
        )
        update_collection_visibility_for_probe(
            context.scene.collection.children, prob_object.data
        )
        bpy.ops.render.render(write_still=True)

        names = get_scene_renderered_object_names(context)
        result_data["baked_objects"] = names
        save_probe_json_render_data(export_directory, prob_object.name, result_data)

    except Exception as e:
        catched_exception = e

    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data


def render_cubemap_reflection_probe(
    context, operator, object, progress_min=0, progress_max=1
):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world
    radius = prob_object.data.influence_distance

    camera = create_cube_camera(context)
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    final_export_directory = get_or_create_render_cache_subdirectory(
        export_directory, prob_object.name
    )

    print_render_progress(
        "Baking cubemap probe " + prob_object.name, progress_min, progress_max
    )

    result_data = {
        "type": "cubemap",
        "radius": radius,
        "position": [
            transform.translation.x,
            transform.translation.z,
            -transform.translation.y,
        ],
        "scale": transform.to_scale().to_tuple(),
        "falloff": prob.falloff,
        "intensity": prob.intensity,
        "resolution": [
            prob.grid_resolution_x,
            prob.grid_resolution_y,
            prob.grid_resolution_z,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "probe_type": "reflection",
        "name": object.name,
        "size": height,
        "faces_files": [],
    }

    try:
        camera.location = transform.translation
        max_scale = max(camera.scale.x, camera.scale.y, camera.scale.z)
        camera.data.clip_start = prob.clip_start
        camera.data.clip_end = prob.clip_end
        for i in range(6):
            filename = cubemap_filename(i, file_extension)
            final_file_path = final_export_directory + "/" + filename

            print_render_progress(
                "-- Baking face " + cube_map_face_names[i],
                progress_min,
                progress_max,
                i / 6,
            )
            camera.rotation_euler = cube_map_euler_rotations[i]

            set_cube_render_settings(
                context, camera, final_file_path, samples_max=samples_max, size=height
            )
            update_collection_visibility_for_probe(
                context.scene.collection.children, prob_object.data
            )
            bpy.ops.render.render(write_still=True)

            result_data["faces_files"].append(filename)
        names = get_scene_renderered_object_names(context)
        result_data["baked_objects"] = names
        save_probe_json_render_data(export_directory, prob_object.name, result_data)

    except Exception as e:
        catched_exception = e

    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data


def render_pano_irradiance_probe(
    context, operator, object, progress_min=0, progress_max=1
):
    prob = object.data
    settings = prob.probes_export

    camera = create_pano_camera(context)
    camera.rotation_euler.x = pi / 2
    camera.data.clip_end = prob.clip_end
    camera.data.clip_start = prob.clip_start

    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.irradiance_volume_default_samples_max
        height = context.scene.probes_export.irradiance_volume_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    catched_exception = None

    final_export_directory = get_or_create_render_cache_subdirectory(
        export_directory, object.name
    )

    transform: Matrix = object.matrix_world

    transform_list = []

    for r in transform.row:
        transform_list.append(r.x)
        transform_list.append(r.y)
        transform_list.append(r.z)
        transform_list.append(r.w)

    translation_tupple = transform.translation.to_tuple()
    scale_tupple = transform.to_scale().to_tuple()

    result_data = {
        "type": "pano",
        "probe_type": "irradiance",
        "name": object.name,
        "width": height * 2,
        "height": height,
        "position": [
            translation_tupple[0],
            translation_tupple[2],
            -translation_tupple[1],
        ],
        "scale": [scale_tupple[0], scale_tupple[2], scale_tupple[1]],
        "falloff": prob.falloff,
        "resolution": [
            prob.grid_resolution_x,
            prob.grid_resolution_z,
            prob.grid_resolution_y,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "influence_distance": prob.influence_distance,
        "files": [],
    }

    try:
        if os.path.exists(export_directory) == False:
            raise Exception("Directory does not exist")

        resolution_x = prob.grid_resolution_x
        resolution_y = prob.grid_resolution_y
        resolution_z = prob.grid_resolution_z

        print_render_progress(
            "Baking probe " + object.name, progress_min, progress_max, 0
        )

        nb_panos = resolution_x * resolution_y * resolution_z

        # render each pano in opengl order (x -> x, y > -z, z -> -y)
        for rx in range(resolution_x):
            vx = (rx + 0.5) / resolution_x * 2 - 1

            for rz in range(resolution_z):
                vz = (rz + 0.5) / resolution_z * 2 - 1
                for rry in range(resolution_y):
                    ry = resolution_y - rry - 1
                    vy = (ry + 0.5) / resolution_y * 2 - 1
                    filename = irradiance_filename(rx, ry, rz, file_extension)
                    final_file_path = final_export_directory + "/" + filename

                    # print('-- Baking probe at ' + str(vx) + ', ' + str(vy) + ', ' + str(vz))
                    print_render_progress(
                        "-- rendering probe at "
                        + str(vx)
                        + ", "
                        + str(vy)
                        + ", "
                        + str(vz),
                        progress_min,
                        progress_max,
                        (rx * resolution_y * resolution_z + ry * resolution_z + rz)
                        / nb_panos,
                    )
                    res_vec = transform @ Vector((vx, vy, vz))

                    camera.location = res_vec

                    set_pano_render_settings(
                        context,
                        camera,
                        final_file_path,
                        samples_max=samples_max,
                        height=height,
                    )
                    update_collection_visibility_for_probe(
                        context.scene.collection.children, prob
                    )
                    # render image
                    bpy.ops.render.render(write_still=True)

                    result_data["files"].append(filename)
        names = get_scene_renderered_object_names(context)
        result_data["baked_objects"] = names
        save_probe_json_render_data(export_directory, object.name, result_data)

    except Exception as e:
        catched_exception = e

    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data
