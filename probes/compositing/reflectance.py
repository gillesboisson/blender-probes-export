
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *


from .shader import *
from .pack import *

def pack_reflectance_cubemap(
        map_texture_files,
        output_file_path,
        cubemap_size,
        max_texture_size,
        start_roughness,
        level_roughness,
        nb_levels,
        image_name,
        
        
    ):
    nb_face_x = 4
    nb_face_y = 2
    nb_maps = len(map_texture_files)

    (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height) = get_cubemap_pack_layout(cubemap_size,nb_maps,max_texture_size, nb_face_x, nb_face_y)

    
    if nb_maps == 0:
        return None
    

    # shader = cubemap_shader
    shader = reflectance_cubemap_shader


    offscreen = GPUOffScreen(texture_width, texture_height)


    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

        
        map_normals = generate_cubemap_pack_normals(nb_maps)
        map_indices = generate_cubemap_quad_indices()
        for level in range(nb_levels):
            roughness = start_roughness + level * level_roughness
            shader.uniform_float("roughness", roughness)


            for map_ind in range(nb_maps):
                map_texture_files[map_ind] = map_texture_files[map_ind]
                map_image = bpy.data.images.load(map_texture_files[map_ind])

                uvs = get_cubemap_pack_uvs(cubemap_size, level, nb_maps, max_texture_size, nb_face_x, nb_face_y)
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
    

def pack_reflectance_probe(
        export_direction: str,
        data,
        cubemap_size,
        max_texture_size = 1024,
        start_roughness = 0.25,
        level_roughness = 0.25,
        nb_levels = 3,
    ):

    pack_reflectance_cubemap(
        [export_direction + data['file']],
        export_direction + data['name'] + '_packed.png',
        cubemap_size,
        max_texture_size,
        start_roughness,
        level_roughness,  
        nb_levels,
        'reflection_pack',
    )