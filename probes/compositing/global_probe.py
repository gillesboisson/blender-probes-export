import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from gpu.types import *

from .gpu import prepare_renderer_from_image, save_render

from .shader import *
from .pack import *

from .irradiance import pack_irradiance_cubemap
from .reflection import pack_reflectance_cubemap

from ..helpers import (
    get_render_cache_subdirectory,
    save_probe_json_pack_data,
    load_probe_json_render_data,
    save_scene_json_pack_data,
    get_context_probes_names,
    get_export_extension,
)


def pack_global_probe(context, prob_object=None):
    export_directory = context.scene.bake_gi.export_directory_path
    file_extension = get_export_extension(context)
    props = context.scene.bake_gi

    if prob_object == None:
        prob_object = context.object

    data = load_probe_json_render_data(export_directory, prob_object.name)

    if data == None:
        return None

    # pack irradiance cubemap
    name = data["name"]
    final_export_directory = get_render_cache_subdirectory(export_directory, name)
    source_file_path = final_export_directory + "/" + data["file"]
    irradiance_filename = name + "_irradiance_packed"
    radiance_filename = name + "_radiance_packed"

    (final_irradiance_path, final_irradiance_filename) = pack_irradiance_cubemap(
        context,
        [source_file_path],
        irradiance_filename,
        props.global_irradiance_bake_settings.map_size,
        props.global_irradiance_bake_settings.max_texture_size,
    )

    (final_reflectance_path, final_reflectance_filename) = pack_reflectance_cubemap(
        context,
        source_file_path,
        radiance_filename,
        props.global_reflection_bake_settings.map_size,
        props.global_reflection_bake_settings.max_texture_size,
        props.global_reflection_bake_settings.start_roughness,
        props.global_reflection_bake_settings.level_roughness,
        props.global_reflection_bake_settings.nb_levels,
    )

  
    del data["file"]

    baking_data = {
        "irradiance": {
            "cubemap_face_size": props.global_irradiance_bake_settings.map_size,
            "max_texture_size": props.global_irradiance_bake_settings.max_texture_size,
        },
        "reflection": {
            "cubemap_face_size": props.global_reflection_bake_settings.map_size,
            "start_roughness": props.global_reflection_bake_settings.start_roughness,
            "level_roughness": props.global_reflection_bake_settings.level_roughness,
            "nb_levels": props.global_reflection_bake_settings.nb_levels,
        },
    }

    
    final_data = {
        "name": data["name"],
        "probe_type": data["probe_type"],
        "transform": data["transform"],
        "render": data["render"],
        "irradiance_file": final_irradiance_filename,
        "reflection_file": final_reflectance_filename,
        "data": {},
        "baking": baking_data,
        "baked_objects": data["baked_objects"],
    }
    
    save_probe_json_pack_data(export_directory, name, final_data)
    probe_names = get_context_probes_names(context)
    save_scene_json_pack_data(export_directory, probe_names)
    return data
