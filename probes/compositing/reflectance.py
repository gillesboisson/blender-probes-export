import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *
from ..helpers.poll import get_context_probes_names


from .shader import *
from .pack import *

from .gpu import prepare_renderer, prepare_renderer_from_image, save_render

from ..helpers.files import (
    get_render_cache_subdirectory,
    load_probe_json_render_data,
    save_probe_json_pack_data,
    save_scene_json_pack_data,
)

from ..helpers.config import get_export_extension


def pack_reflectance_cubemap(
    context,
    map_texture_file,
    name,
    cubemap_size,
    max_texture_size,
    start_roughness,
    level_roughness,
    nb_levels,
):
    nb_face_x = 4
    nb_face_y = 2

    (
        texture_width,
        texture_height,
        nb_cluster_x,
        nb_cluster_y,
        cluster_width,
        cluster_height,
    ) = get_cubemap_pack_layout(
        cubemap_size, 1, max_texture_size, nb_face_x, nb_face_y
    )



    shader = specular_cubemap_shader

    (gpuOffscreen, texture) = prepare_renderer_from_image(map_texture_file, texture_width, texture_height)


    with gpuOffscreen.bind():
        framebuffer = gpu.state.active_framebuffer_get()
        framebuffer.clear(color=(0.0, 0.0, 0.0, 0.0))

        map_normals = generate_cubemap_pack_normals()
        map_indices = generate_cubemap_quad_indices()
        shader.uniform_sampler("panorama", texture)


        for level in range(nb_levels):
            roughness = start_roughness + level * level_roughness

            print("Roughness: " + str(roughness)+ " Level: " + str(level_roughness))
            

            shader.uniform_float("roughness", roughness)

            uvs = get_cubemap_pack_uvs(
                cubemap_size, level, 1, max_texture_size, nb_face_x, nb_face_y
            )

            map_uvs = uvs[0]

            batch: GPUBatch = batch_for_shader(
                shader,
                "TRIS",
                {"position": map_uvs, "normal": map_normals},
                indices=map_indices,
            )

            batch.draw(shader)

        
        packed_info = save_render(context,framebuffer, texture_width,texture_height,name)
    gpuOffscreen.free()

    return packed_info


def pack_reflectance_probe_to_image(
    context,
    export_directory: str,
    data,
    cubemap_size,
    max_texture_size=1024,
    nb_levels=3,
    start_roughness=0.25,
    level_roughness=0.25,
):
    final_export_directory = get_render_cache_subdirectory(
        export_directory, data["name"]
    )

    filename = data['name'] + '_packed.'+get_export_extension(context)

    pack_reflectance_cubemap(
        context,
        final_export_directory + "/" + data["file"],
        data["name"] + "_packed",
        cubemap_size,
        max_texture_size,
        start_roughness,
        level_roughness,
        nb_levels,
    )

    pack_data = {
        "name": data["name"],
        "file": filename,
        "cubemap_size": cubemap_size,
        "texture_size": max_texture_size,
        "type": "reflection",
        "position": data["position"],
        "scale": data["scale"],
        "rotation": data["rotation"],
        "baked_objects": data["baked_objects"],
        "clip_start": data["clip_start"],
        "clip_end": data["clip_end"],
        "data": {
            "start_roughness": start_roughness,
            "level_roughness": level_roughness,
            "end_roughness": start_roughness + level_roughness * nb_levels,
            "nb_levels": nb_levels,
            "scale": data["scale"],
            "falloff": data["falloff"],
            "influence_distance": data["influence_distance"],
            "intensity": data["intensity"],
            "influence_type": data["influence_type"],
        },
    }

    save_probe_json_pack_data(export_directory, data["name"], pack_data)


def pack_reflectance_probe(context, prob_object=None):
    export_directory = context.scene.probes_export.export_directory_path

    if prob_object == None:
        prob_object = context.object

    prob = prob_object.data
    settings = prob.probes_export

    if settings.use_default_settings:
        map_size = context.scene.probes_export.reflection_volume_default_export_map_size
        export_max_texture_size = (
            context.scene.probes_export.reflection_volume_default_export_max_texture_size
        )
        export_nb_levels = (
            context.scene.probes_export.reflection_volume_default_export_nb_levels
        )
        export_start_roughness = (
            context.scene.probes_export.reflection_volume_default_export_start_roughness
        )
        export_level_roughness = (
            context.scene.probes_export.reflection_volume_default_export_level_roughness
        )

    else:
        map_size = settings.export_map_size
        export_max_texture_size = settings.export_max_texture_size
        export_nb_levels = settings.export_nb_levels
        export_start_roughness = settings.export_start_roughness
        export_level_roughness = settings.export_level_roughness

    data = load_probe_json_render_data(export_directory, prob_object.name)

    if data == None:
        return None

    pack_reflectance_probe_to_image(
        context,
        export_directory,
        data,
        map_size,
        export_max_texture_size,
        export_nb_levels,
        export_start_roughness,
        export_level_roughness,
    )

    probe_names = get_context_probes_names(context)

    save_scene_json_pack_data(export_directory, probe_names)

    return data
