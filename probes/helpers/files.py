

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


def save_probe_json_data(export_directory, name, data):
    dir = get_render_cache_subdirectory(export_directory, name)
    with open(dir + '/' + 'probe.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)


def load_probe_json_data(export_directory, name):
    dir = get_render_cache_subdirectory(export_directory, name)
    if not os.path.exists(dir + '/' + 'probe.json'):
        return None
    with open(dir + '/' + 'probe.json') as json_file:
        return json.load(json_file)