import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *


from .shader import *
from .pack import *

def pack_irradiance_cubemap(
        map_texture_files,
        output_file_path,
        cubemap_size,
        image_name,
        max_texture_size,
        
    ):
    nb_face_x = 6
    nb_face_y = 1

    nb_maps = len(map_texture_files)

    (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height) = get_cubemap_pack_layout(cubemap_size,nb_maps,max_texture_size, nb_face_x, nb_face_y)

    
    if nb_maps == 0:
        return None
    

    # shader = cubemap_shader
    shader = irradiance_cubemap_shader


    offscreen = GPUOffScreen(texture_width, texture_height)

    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

        uvs = get_cubemap_pack_uvs(cubemap_size, 0, nb_maps, max_texture_size, nb_face_x, nb_face_y)
        map_normals = generate_cubemap_pack_normals(nb_maps)
        map_indices = generate_cubemap_quad_indices()

        
        
        for map_ind in range(nb_maps):
            map_texture_files[map_ind] = map_texture_files[map_ind]
            map_image = bpy.data.images.load(map_texture_files[map_ind])
            texture = gpu.texture.from_image(map_image)


            shader.uniform_sampler("panorama", texture)
            

            map_uvs = uvs[map_ind]
            
            batch: GPUBatch = batch_for_shader(shader, 'TRIS', {"position": map_uvs, "normal": map_normals}, indices = map_indices)
            
            batch.draw(shader)


            bpy.data.images.remove(map_image)
            


        buffer = fb.read_color(0,0,texture_width,texture_height,4,0,'UBYTE')

    
    offscreen.free()

    if not image_name in bpy.data.images:
        bpy.data.images.new(image_name, texture_width, texture_height)

    image = bpy.data.images[image_name]
    image.scale(texture_width, texture_height)

    buffer.dimensions = texture_width * texture_height * 4
    image.pixels = [v / 255 for v in buffer]

    image.save_render(output_file_path)


def pack_irradiance_probe(export_direction: str, data, cubemap_size, max_texture_size = 1024):

    source_files_path = []

    for file in data['files']:
        source_files_path.append(export_direction  + file)

    pack_irradiance_cubemap(
        source_files_path,
        export_direction + data['name'] + '_packed.png',
        cubemap_size, 'irradiance_pack',
        max_texture_size,
    )
