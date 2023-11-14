import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *
from ..helpers.config import get_export_extension
from ..helpers.poll import get_context_probes_names


from .shader import *
from .pack import *

from .gpu import prepare_renderer, save_render

from ..helpers.files import get_render_cache_subdirectory, load_probe_json_render_data, save_probe_json_pack_data, save_scene_json_pack_data

def pack_irradiance_cubemap(
        context,
        map_texture_files,
        name,
        cubemap_size,
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


    gpuOffscreen = prepare_renderer(context, texture_width, texture_height)

    with gpuOffscreen.bind():
        framebuffer = gpu.state.active_framebuffer_get()
        framebuffer.clear(color=(0.0, 0.0, 0.0, 0.0))

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
            


        packed_info = save_render(context,framebuffer, texture_width,texture_height,name)

    

    
    gpuOffscreen.free()

    return packed_info


def pack_irradiance_probe_to_image(context, data, cubemap_size, max_texture_size = 1024):
    export_directory = context.scene.bake_gi.export_directory_path
    source_files_path = []
    final_export_directory = get_render_cache_subdirectory(export_directory, data['name'])
    for file in data['files']:
        source_files_path.append(final_export_directory + '/' + file)

    filename = data['name'] + '_packed.'+get_export_extension(context)

    pack_irradiance_cubemap(
        context,
        source_files_path,
        data['name'] + '_packed',
        cubemap_size,
        max_texture_size,
    )

    pack_data =  {
        'name': data['name'],
        'file': filename,
        'cubemap_size': cubemap_size,
        'texture_size': max_texture_size,
        'type': 'irradiance',
        'position': data['position'],
        'rotation': data['rotation'],
        'scale': data['scale'],
        'clip_start': data['clip_start'],
        'clip_end': data['clip_end'],
        'baked_objects': data['baked_objects'],
        'data': {
            'falloff': data['falloff'],
            'resolution': data['resolution'],  
            'influence_distance': data['influence_distance'],
        }
    }

    save_probe_json_pack_data(export_directory, data['name'], pack_data)

    return


def pack_irradiance_probe(context, prob_object = None):
    export_directory = context.scene.bake_gi.export_directory_path
        
    if(prob_object == None):
        prob_object = context.object

    prob = prob_object.data
    settings = prob.bake_gi

    if(settings.use_default_settings):
        map_size = context.scene.bake_gi.irradiance_volume_default_export_map_size
        export_max_texture_size = context.scene.bake_gi.irradiance_volume_default_export_max_texture_size
    else:
        map_size = settings.export_map_size
        export_max_texture_size = settings.export_max_texture_size


    data = load_probe_json_render_data(export_directory, prob_object.name)

    if(data == None):
        return None
    

    pack_irradiance_probe_to_image(context, data, map_size, export_max_texture_size) 

    probe_names = get_context_probes_names(context)

    save_scene_json_pack_data(export_directory, probe_names)

    return data
