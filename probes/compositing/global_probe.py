import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *
from .gpu import prepare_renderer_from_image,save_render
from ..helpers.poll import get_context_probes_names


from .shader import *
from .pack import *

from .irradiance import pack_irradiance_cubemap
from .reflectance import pack_reflectance_cubemap

from ..helpers.config import get_export_extension
from ..helpers.files import (
    get_render_cache_subdirectory,
    save_probe_json_pack_data,
    load_probe_json_render_data,
    save_scene_json_pack_data,
)


def pack_global_probe(context, prob_object=None):
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)
    props = context.scene.probes_export



    if prob_object == None:
        prob_object = context.object

    data = load_probe_json_render_data(export_directory, prob_object.name)

    if data == None:
        return None
    

    # pack irradiance cubemap
    name = data['name']
    final_export_directory = get_render_cache_subdirectory(export_directory,name)
    source_file_path = final_export_directory + '/' +data["file"]
    irradiance_filename = name + '_irradiance_packed'
    radiance_filename = name + '_radiance_packed'

    (final_irradiance_path,final_irradiance_filename) = pack_irradiance_cubemap(
        context,
        [source_file_path],
        irradiance_filename,
        props.global_irradiance_export_map_size,
        props.global_irradiance_max_texture_size,
    )

    (final_reflectance_path,final_reflectance_filename) = pack_reflectance_cubemap(
        context,
        source_file_path,
        radiance_filename,
        props.global_reflectance_export_map_size,
        props.global_reflectance_max_texture_size,
        props.global_reflectance_start_roughness,
        props.global_reflectance_level_roughness,
        props.global_reflectance_nb_levels,
    )
    
    data["irradiance_file"] = final_irradiance_filename
    data["reflectance_file"] = final_reflectance_filename
    del data["file"]

    save_probe_json_pack_data(export_directory, name, data)
    probe_names = get_context_probes_names(context)
    save_scene_json_pack_data(export_directory, probe_names)
    return data
