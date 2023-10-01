
from math import pi

from mathutils import Matrix, Vector

cube_map_face_names = [
    "negx",
    "posx",
    "negy",
    "posy",
    "negz",
    "posz"
]

cube_map_euler_rotations = [
    
    (pi / 2, 0, pi / 2),
    (pi / 2, 0, -pi / 2),
    (pi / 2, 0, pi), 
    (pi / 2, 0, 0), 
    (0, 0, 0),
    (pi, 0, 0),
]


pano_cube_map_euler_rotations = [
    
    (pi / 2, 0, pi / 2),
    (pi / 2, 0, -pi / 2),
    (0, pi / 2, pi / 2),
    (0, -pi / 2, -pi / 2),
    (pi / 2, 0, pi),  
    (pi / 2, 0, 0),

]



face_vertex_normals = [
    
    
    Vector((-1, -1, 1)).normalized(),
    Vector((-1, -1, -1)).normalized(), 
    Vector((-1, 1, 1)).normalized(),
    Vector((-1, 1, -1)).normalized(),
    
    
]

# represent 
faces_vertex_normals = []


for i in range(6):
    euler = Vector(pano_cube_map_euler_rotations[i])
    mat = Matrix.Rotation(euler.z, 4, 'Z') @ Matrix.Rotation(euler.y, 4, 'Y') @ Matrix.Rotation(euler.x, 4, 'X')
    for v in face_vertex_normals:
        faces_vertex_normals.append(mat @ v)


    
    