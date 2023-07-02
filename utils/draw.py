
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from .vertices import vertices_2d_to_vertices, tuple_2_to_vec_3
from mathutils import Vector, Matrix
from math import cos, pi, sin
from ..physics_2d.types import PlanDirection

vert_out = gpu.types.GPUStageInterfaceInfo("three_vert_interface")
vert_out.smooth('VEC3', "pos")


shader_info = gpu.types.GPUShaderCreateInfo()

shader_info.push_constant('MAT4', "viewProjectionMatrix")
shader_info.push_constant('MAT4', "modelMatrix")
shader_info.push_constant('VEC4', "color")

shader_info.vertex_in(0, 'VEC3', "position")
shader_info.vertex_out(vert_out)
shader_info.fragment_out(0, 'VEC4', "FragColor")

shader_info.vertex_source(
    "void main()"
    "{"
    "  pos = position;"
    "  gl_Position = viewProjectionMatrix * modelMatrix * vec4(position, 1.0f);"
    "}"
)

shader_info.fragment_source(
    "void main()"
    "{"
    "  FragColor = color;"
    "}"
)

shader = gpu.shader.create_from_info(shader_info)
del vert_out
del shader_info


def set_shader_uniforms(
        vp: Matrix,
        modelMat: Matrix,
        color: tuple[float, float, float, float]
    ):
    shader.uniform_float("viewProjectionMatrix", vp)
    shader.uniform_float("modelMatrix", modelMat)
    shader.uniform_float("color",color)

def draw_polyline(
        coords: list[tuple[float,float, float]],
        color: tuple[float, float, float, float],
        modelMat: Matrix,
        closePolyline: bool = True
    ):
    vp = bpy.context.region_data.perspective_matrix
    set_shader_uniforms(vp, modelMat, color)
    polyCoord = coords.copy()
    if closePolyline:
        polyCoord.append(coords[0])
    batch = batch_for_shader(shader, 'LINE_STRIP', {"position": polyCoord})
    batch.draw(shader)


def draw_polyline_2D(
        vertices2d: list[tuple[float,float]],
        color: tuple[float, float, float, float],
        orientation: PlanDirection,
        modelMat: Matrix,
        closePolyline: bool = True
    ):
    vp = bpy.context.region_data.perspective_matrix
    set_shader_uniforms(vp, modelMat, color)
    coords = vertices_2d_to_vertices(vertices2d, orientation)
    if(closePolyline):
        coords.append(coords[0])
    batch = batch_for_shader(shader, 'LINE_STRIP', {"position": coords})
    batch.draw(shader)


def draw_lines(
        coords: list[tuple[float,float, float]],
        color: tuple[float, float, float, float],
        modelMat: Matrix,
    ):
    vp = bpy.context.region_data.perspective_matrix
    set_shader_uniforms(vp, modelMat, color)


    batch = batch_for_shader(shader, 'LINES', {"position": coords})
    batch.draw(shader)



def draw_tris(
        coords: list[tuple[float,float, float]],
        color: tuple[float, float, float, float],
        modelMat: Matrix,  
        indices = None
    ):

    vp = bpy.context.region_data.perspective_matrix
    set_shader_uniforms(vp, modelMat, color)


    batch = batch_for_shader(shader, 'TRIS', {"position": coords},indices=indices)
    batch.draw(shader)



# square_geom = (
#     (-0.5,-0.5),
#     (0.5,-0.5),
#     (0.5,0.5),
#     (-0.5,0.5),
# )

# def draw_square_2D(
#         color: tuple[float, float, float, float],
#         orientation: FaceDirection,
#         modelMat: Matrix
#     ):
#     vp = bpy.context.region_data.perspective_matrix
#     set_shader_uniforms(vp, modelMat, color)
#     coords = vertices_2d_to_vertices(square_geom, orientation)
#     coords.append(coords[0])
#     batch = batch_for_shader(shader, 'LINE_STRIP', {"position": coords})
#     batch.draw(shader)


# def draw_circle_3D(
#         radius: float,
#         segments: int,
#         color: tuple[float, float, float, float],
#         orientation: FaceDirection,
#         modelMat: Matrix
#     ):
#     vp = bpy.context.region_data.perspective_matrix
#     set_shader_uniforms(vp, modelMat, color)
#     coords = list()
#     for i in range(segments):
#         angle = 2 * pi * i / segments
#         vertex2D = (cos(angle) * radius, sin(angle) * radius)
#         coords.append(vec_2_to_vec_3(orientation, vertex2D))
#     coords.append(coords[0])
#     batch = batch_for_shader(shader, 'LINE_STRIP', {"position": coords})
#     batch.draw(shader)
