

from .config import cube_map_face_names, cube_map_euler_rotations
import os


def cubemap_file(face_index, name, extension = 'png'):
    return name + '_' + cube_map_face_names[face_index] + '.' + extension


def cubemap_files(name, extension = 'png'):
    return [cubemap_file(i, name, extension) for i in range(6)]


def pano_file(name, extension = 'png'):
    return name + '.' + extension


def irradiance_file(name,index_x, index_y, index_z,  extension = 'png'):
    return name + '_' + str(index_x) + '_' + str(index_y) + '_' + str(index_z) + '.' + extension



def cubemap_file_exist(directory, face_index, name, extension = 'png'):
    filename = cubemap_file(face_index, name, extension)
    return os.path.exists(directory + '/' + filename)

def all_cubemap_files_exist(directory, name, extension = 'png'):
    for i in range(6):
        if not cubemap_file_exist(directory, i, name, extension):
            return False
    return True

def irradiance_file_exist(directory, name,index_x, index_y, index_z,  extension = 'png'):
    filename = irradiance_file(name,index_x, index_y, index_z,  extension)
    return os.path.exists(directory + '/' + filename)

def all_irradiance_files_exist(directory, name, resolution_x, resolution_y, resolution_z, extension = 'png'):
    for i in range(resolution_x):
        for j in range(resolution_y):
            for k in range(resolution_z):
                if not irradiance_file_exist(directory, name,i, j, k, extension):
                    return False
    return True

def pano_file_exist(directory, name, extension = 'png'):
    filename = pano_file(name, extension)
    return os.path.exists(directory + '/' + filename)



def unlink_cubemap_files(name, extension = 'png'):
    for i in range(6):
        try:
            os.unlink(cubemap_file(i, name, extension))
        except:
            pass



def unlink_irradiance_files(name, resolution_x, resolution_y, resolution_z, extension = 'png'):
    for i in range(resolution_x):
        for j in range(resolution_y):
            for k in range(resolution_z):
                try:
                    os.unlink(irradiance_file(name,i, j, k, extension))
                except:
                    pass
    
def unlink_pano_file(name, extension = 'png'):
    try:
        os.unlink(pano_file(name, extension))
    except:
        pass


