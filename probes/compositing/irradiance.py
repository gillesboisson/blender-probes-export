import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *
from ..helpers.poll import get_context_probes_names


from .shader import *
from .pack import *

from ..helpers.files import get_render_cache_subdirectory, load_probe_json_render_data, save_probe_json_pack_data, save_scene_json_pack_data,global_probe_render_name

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


def pack_irradiance_probe_to_image(export_directory: str, data, cubemap_size, max_texture_size = 1024):

    source_files_path = []
    final_export_directory = get_render_cache_subdirectory(export_directory, data['name'])
    for file in data['files']:
        source_files_path.append(final_export_directory + '/' + file)

    pack_irradiance_cubemap(
        source_files_path,
        export_directory + data['name'] + '_packed.png',
        cubemap_size, 'irradiance_pack',
        max_texture_size,
    )

    pack_data =  {
        'name': data['name'],
        'file': data['name'] + '_packed.png',
        'cubemap_size': cubemap_size,
        'texture_size': max_texture_size,
        'type': 'irradiance',
        'position': data['position'],
        'scale': data['scale'],
        'clip_start': data['clip_start'],
        'clip_end': data['clip_end'],
        'data': {
            'falloff': data['falloff'],
            'resolution': data['resolution'],  
            'influence_distance': data['influence_distance'],
        }
    }

    save_probe_json_pack_data(export_directory, data['name'], pack_data)

    return


def pack_irradiance_probe(context, prob_object = None):
    export_directory = context.scene.probes_export.export_directory_path
        
    if(prob_object == None):
        prob_object = context.object

    prob = prob_object.data
    settings = prob.probes_export

    if(settings.use_default_settings):
        map_size = context.scene.probes_export.irradiance_volume_default_export_map_size
        export_max_texture_size = context.scene.probes_export.irradiance_volume_default_export_max_texture_size
    else:
        map_size = settings.export_map_size
        export_max_texture_size = settings.export_max_texture_size


    data = load_probe_json_render_data(export_directory, prob_object.name)

    if(data == None):
        return None
    

    pack_irradiance_probe_to_image(export_directory, data, map_size, export_max_texture_size) 

    probe_names = get_context_probes_names(context)

    save_scene_json_pack_data(export_directory, probe_names)

    return data
