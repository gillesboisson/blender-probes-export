from math import ceil, floor

from gpu.types import *

from ..helpers.config import faces_vertex_normals


def get_cubemap_pack_layout(cubemap_size,nb_cubemap = 1, max_texture_size = 1024, nb_face_x = 4, nb_face_y = 2):
    
    # cubemap are stored in 4 x 2 grid
    cluster_width = cubemap_size * nb_face_x
    cluster_height = cubemap_size * nb_face_y

    

    nb_cluster_x = min(floor(max_texture_size / cluster_width ), nb_cubemap)
    nb_cluster_y = ceil(nb_cubemap / nb_cluster_x)

    texture_width = nb_cluster_x * cluster_width
    texture_height = nb_cluster_y * cluster_height

    return (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height)

def get_cubemap_pack_coords(cubemap_size, sub_level = 0,nb_cubemap = 1, max_texture_size = 1024, nb_face_x = 4, nb_face_y = 2 ):
        
    coords = []

    (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height) = get_cubemap_pack_layout(cubemap_size,nb_cubemap,max_texture_size,nb_face_x, nb_face_y)

    cubemap_size /=  pow(2, sub_level)

    # face_size = cubemap_size / (sub_level * sub_level + 1) 
    print(sub_level, cubemap_size)
    for i in range(nb_cubemap):
        cluster_x = i % nb_cluster_x
        cluster_y = floor(i / nb_cluster_x)

        left = cluster_x * cluster_width
        top = cluster_y * cluster_height

        for f in range(sub_level):
            left += cluster_width / (2 * (f + 1))
            top += cluster_height / (2 * (f + 1))

        
        
        map_coords = []

        for face_ind in range(6):
            face_x = face_ind % nb_face_x
            face_y = floor(face_ind / nb_face_x)

            

            face_left = left + face_x * cubemap_size
            face_top = top + face_y * cubemap_size

            map_coords.append((
                (face_left,face_top),
                (face_left + cubemap_size,face_top),
                (face_left,face_top + cubemap_size),
                (face_left + cubemap_size,face_top + cubemap_size)
            ))       

        coords.append(map_coords)

    return coords

def get_cubemap_pack_uvs(cubemap_size, sub_level = 0,nb_cubemap = 1, max_texture_size = 1024, nb_face_x = 4, nb_face_y = 2 ):
    coords = get_cubemap_pack_coords(cubemap_size, sub_level,nb_cubemap, max_texture_size, nb_face_x, nb_face_y)
    (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height) = get_cubemap_pack_layout(cubemap_size,nb_cubemap,max_texture_size, nb_face_x, nb_face_y)
    uvs = []

    for map_coord in coords:
        map_uvs = []

        for coord in map_coord:
            map_uvs.append((coord[0][0] / texture_width, coord[0][1] / texture_height))
            map_uvs.append((coord[1][0] / texture_width, coord[1][1] / texture_height))
            map_uvs.append((coord[2][0] / texture_width, coord[2][1] / texture_height))
            map_uvs.append((coord[3][0] / texture_width, coord[3][1] / texture_height))
        
        uvs.append(map_uvs)

    return uvs

def generate_cubemap_pack_normals(nb_cubemap = 1):
    normals = []

    for normal in faces_vertex_normals:
        normals.append(normal.to_tuple())



    return normals

def generate_cubemap_quad_indices():

    indices = []

    for i in range(6):
        ind_quad_offset = i * 4
        indices.append((ind_quad_offset,ind_quad_offset + 1,ind_quad_offset + 2))
        indices.append((ind_quad_offset + 1,ind_quad_offset + 3,ind_quad_offset + 2))

    return indices
