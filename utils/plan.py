
from mathutils import Vector, Matrix
import math

from ..physics_2d.types import PlanDirection


matFaceX = Matrix(((0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,0,1)))
matFaceY = Matrix(((1,0,0,0),(0,0,0,0),(0,1,0,0),(0,0,0,1)))
matFaceZ = Matrix()

def get_face_orientation_matrix(orientation: PlanDirection) -> Matrix:
    if orientation == 'X':
        return matFaceX
    elif orientation == "Y":
        return matFaceY
    else:
        return matFaceZ
    

orientation_mat_z = Matrix()
orientation_mat_x = Matrix.Rotation(math.pi/2, 4, 'X') @ Matrix.Rotation(math.pi/2, 4, 'Y') 
orientation_mat_y = Matrix.Rotation(math.pi/2, 4, 'X')

def get_plan_matrix(orientation: PlanDirection) -> Matrix:
    if orientation == 'X':
        return orientation_mat_x
    elif orientation == "Y":
        return orientation_mat_y
    else:
        return orientation_mat_z
    

def clamp_matrix_to_plan(orientation: PlanDirection, matrix: Matrix, applyScale = True) -> Matrix:

    scale = matrix.to_scale()
    loc = matrix.to_translation()

    rot_euler = matrix.to_euler()
    
    if orientation == 'X':
        rot_mat = Matrix.Rotation(rot_euler.x, 4, 'X')

        scale.x = 1
        loc.x = 0
    elif orientation == "Y":
        rot_mat = Matrix.Rotation(rot_euler.y, 4, 'Y')
        scale.y = 1
        
        loc.y = 0
    else:

        rot_mat = Matrix.Rotation(rot_euler.z, 4, 'Z')
        scale.z = 1
        loc.z = 0

     
    resMat =  Matrix.Translation(loc) @ rot_mat

    if(applyScale):
        resMat = resMat @ Matrix.Scale(scale.x, 4, (1,0,0)) @ Matrix.Scale(scale.y, 4, (0,1,0)) @ Matrix.Scale(scale.z, 4, (0,0,1))

    return resMat

    

def get_plan_2d_vector(orientation: PlanDirection, vec_3: Vector) -> Vector:
    if orientation == 'X':
        return Vector((vec_3.y, vec_3.z))
    elif orientation == "Y":
        return Vector((vec_3.x, vec_3.z))
    else:
        return Vector((vec_3.x, vec_3.y))
    
def get_3d_vector_from_plan(orientation: PlanDirection, vec_2: Vector) -> Vector:
    if orientation == 'X':
        return Vector((0, vec_2.x, vec_2.y))
    elif orientation == "Y":
        return Vector((vec_2.x, 0, vec_2.y))
    else:
        return Vector((vec_2.x, vec_2.y, 0))
    
def tuple_2_to_vec_3(plan_direction: PlanDirection, vec_2: tuple[float, float]) -> Vector:
    if plan_direction == 'X':
        return Vector((0, vec_2[0], vec_2[1]))
    elif plan_direction == "Y":
        return Vector((vec_2[0], 0, vec_2[1]))
    else:
        return Vector((vec_2[0], vec_2[1], 0))


def vec_3_to_tuple_2(plan_direction: PlanDirection, vec_3: Vector) -> tuple[float, float]:
    
    if plan_direction == 'X':
        return (vec_3.y, vec_3.z)
    elif plan_direction == "Y":
        return (vec_3.x, vec_3.z)
    else:
        return (vec_3.x, vec_3.y)