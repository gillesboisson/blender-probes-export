

import json
import shutil
from .config import cube_map_face_names, cube_map_euler_rotations
import os

render_cache_dirname = '__render_cache'

def get_render_cache_directory(export_directory):
    return export_directory + '/' + render_cache_dirname

def get_or_create_render_cache_directory(export_directory):
    cache_dir = get_render_cache_directory(export_directory)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir


def get_render_cache_subdirectory(export_directory, name):
    return get_render_cache_directory(export_directory) + '/' + name

def get_or_create_render_cache_subdirectory(export_directory, name):
    object_dir = get_render_cache_subdirectory(export_directory, name)
    if not os.path.exists(object_dir):
        os.makedirs(object_dir)
    return object_dir


def clear_render_cache_directory(export_directory):
    cache_dir = get_render_cache_directory(export_directory)
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

def clear_render_cache_subdirectory(export_directory, name):
    object_dir = get_render_cache_subdirectory(export_directory, name)
    if os.path.exists(object_dir):
        shutil.rmtree(object_dir)

def render_cache_subdirectory_exists(export_directory, name):
    object_dir = get_render_cache_subdirectory(export_directory, name)
    return os.path.exists(object_dir)        

def cubemap_filename(face_index, extension = 'png'):
    return cube_map_face_names[face_index] + '.' + extension



def cubemap_files(export_directory, name, extension = 'png'):
    dir = get_render_cache_subdirectory(export_directory, name)
    return [dir + '/' + cubemap_filename(i, extension) for i in range(6)]


def pano_filename( extension = 'png'):
    return 'pano.' + extension

def pano_file(export_directory, name, extension = 'png'):
    dir = get_render_cache_subdirectory(export_directory, name)
    return dir + '/' + pano_filename(extension)


def irradiance_filename(index_x, index_y, index_z,  extension = 'png'):
    return str(index_x) + '_' + str(index_y) + '_' + str(index_z) + '.' + extension


def irradiance_file(export_directory, name, index_x, index_y, index_z,  extension = 'png'):
    dir = get_render_cache_subdirectory(export_directory, name)
    return dir + '/' + irradiance_filename(index_x, index_y, index_z, extension)

probe_render_json_file = 'rendered_probe.json'
probe_pack_json_file = 'packed_probe.json'
final_probes_json_file = 'probes.json'


def save_probe_json_render_data(export_directory, name, data):
    dir = get_render_cache_subdirectory(export_directory, name)
    with open(dir + '/' + probe_render_json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def load_probe_json_render_data(export_directory, name):
    dir = get_render_cache_subdirectory(export_directory, name)
    if not os.path.exists(dir + '/' + probe_render_json_file):
        return None
    with open(dir + '/' + probe_render_json_file) as json_file:
        return json.load(json_file)
    

def save_probe_json_pack_data(export_directory, name, data):
    dir = get_render_cache_subdirectory(export_directory, name)
    with open(dir + '/' + probe_pack_json_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)
        
def load_probe_json_pack_data(export_directory, name):
    dir = get_render_cache_subdirectory(export_directory, name)
    if not os.path.exists(dir + '/' + probe_pack_json_file):
        return None
    with open(dir + '/' + probe_pack_json_file) as json_file:
        return json.load(json_file)


def save_scene_json_pack_data(export_directory, probe_names):
    # get probe pack data from render cache sub directories append json content in to a global in export directory
    
    pack_data = []


    if(os.path.exists(export_directory)):
        for name in probe_names:
            if os.path.exists(get_render_cache_subdirectory(export_directory, name) + '/' + probe_pack_json_file):
                with open(get_render_cache_subdirectory(export_directory, name) + '/' + probe_pack_json_file) as json_file:
                    data = json.load(json_file)
                    pack_data.append(data)

        if(len(pack_data) > 0):
            with open(export_directory + '/' + final_probes_json_file, 'w') as outfile:
                json.dump(pack_data, outfile, indent=4)
                    

    # save json file in export directory
    
def clear_render_cache_directory(export_directory):
    cache_dir = get_render_cache_directory(export_directory)
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)