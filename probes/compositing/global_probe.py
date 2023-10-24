import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *
from .gpu import prepare_renderer_from_image,save_render
from ..helpers.poll import get_context_probes_names


from .shader import *
from .pack import *

from ..helpers.config import get_export_extension
from ..helpers.files import (
    global_pano_file,
    load_probe_json_render_data,
    save_scene_json_pack_data,
    global_probe_render_name,
)


def pack_global_probe(context, prob_object=None):
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)


    if prob_object == None:
        prob_object = context.object

    data = load_probe_json_render_data(export_directory, global_probe_render_name)

    if data == None:
        return None

    cubemap_size = 128
    nb_maps = 1
    max_texture_size = cubemap_size * 3
    nb_face_x = 3
    nb_face_y = 2

    (
        texture_width,
        texture_height,
        nb_cluster_x,
        nb_cluster_y,
        cluster_width,
        cluster_height,
    ) = get_cubemap_pack_layout(
        cubemap_size, nb_maps, max_texture_size, nb_face_x, nb_face_y
    )

    shader = cubemap_shader

    cached_probe_file = global_pano_file(
        export_directory,
        prob_object.name,
        file_extension
    )

    (gpuOffscreen, texture) = prepare_renderer_from_image(cached_probe_file, texture_width, texture_height)

    with gpuOffscreen.bind():
        framebuffer = gpu.state.active_framebuffer_get()
        framebuffer.clear(color=(0.0, 0.0, 0.0, 0.0))

        uvs = get_cubemap_pack_uvs(
            cubemap_size, 0, nb_maps, max_texture_size, nb_face_x, nb_face_y
        )
        map_normals = generate_cubemap_pack_normals(nb_maps)
        map_indices = generate_cubemap_quad_indices()

        shader.uniform_sampler("panorama", texture)

        map_uvs = uvs[0]
        batch: GPUBatch = batch_for_shader(
            shader,
            "TRIS",
            {"position": map_uvs, "normal": map_normals},
            indices=map_indices,
        )

        batch.draw(shader)

        save_render(context,framebuffer, texture_width,texture_height,global_probe_render_name)

    
    gpuOffscreen.free()

    probe_names = get_context_probes_names(context)
    save_scene_json_pack_data(export_directory, probe_names)
    
    return data
