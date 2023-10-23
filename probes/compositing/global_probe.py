import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *
from ..helpers.poll import get_context_probes_names


from .shader import *
from .pack import *

from ..helpers.files import (
    global_pano_file,
    load_probe_json_render_data,
    save_probe_json_pack_data,
    save_scene_json_pack_data,
    global_probe_render_name,
)


def pack_global_probe(context, prob_object=None):
    export_directory = context.scene.probes_export.export_directory_path

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
        context.scene.probes_export.export_directory_path
    )
    map_image = bpy.data.images.load(cached_probe_file)
    texture = gpu.texture.from_image(map_image)
    

    offscreen = GPUOffScreen(
        width=texture_width, height=texture_height, format=texture.format
    )


    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

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

        bpy.data.images.remove(map_image)

        buffer = fb.read_color(0, 0, texture_width, texture_height, 4, 0, "FLOAT")
        # buffer = fb.read_color(0,0,texture_width,texture_height,4,0,'UBYTE')



    offscreen.free()
    # context.scene.render.image_settings.file_format = 'PNG'
    context.scene.render.image_settings.file_format = 'OPEN_EXR'
    image_name = global_probe_render_name

    if image_name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[image_name])
    
    bpy.data.images.new(image_name, texture_width, texture_height, alpha=False, float_buffer=True)

    
    image = bpy.data.images[image_name]
    image.file_format = 'OPEN_EXR'
    image.scale(texture_width, texture_height)
    buffer.dimensions = texture_width * texture_height * 4
    image.pixels = buffer
    # image.pixels = [v / 255 for v in buffer]
    
    output_file_path = export_directory + "/" + image_name + ".exr"
    # output_file_path = export_directory + "/" + image_name + ".png"
    image.save_render(output_file_path)

    # copy render cache hdr to export directory
    # cached_probe = global_pano_file(context.scene.probes_export.export_directory_path)
    # os.popen('cp "' + cached_probe + '" "' + export_directory + '"')

    probe_names = get_context_probes_names(context)

    save_scene_json_pack_data(export_directory, probe_names)

    return data
