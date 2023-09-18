from cmath import pi
from math import ceil, floor
import bpy
import gpu
from mathutils import Matrix
from gpu_extras.batch import batch_for_shader

from gpu.types import *

from ..helpers.config import cube_map_face_names, cube_map_euler_rotations, faces_vertex_normals


default_vertex_shader_source = str(("void main()"
    "{"
    "  v_normal = normal;"
    "  gl_Position = vec4(position.x * 2 -1, 1 - position.y * 2, 0.0, 1.0);"
    "};"))
    
sample_spherical_map_source = str("const vec2 invAtan = vec2(0.1591, 0.3183);"
    "vec2 sampleSphericalMap(vec3 v)"
    "{"
    "    vec2 uv = vec2(atan(v.y, v.x), asin(v.z));"
    "    uv *= invAtan;"
    "    uv += 0.5;"
    "    return vec2(uv.x, 1.0 - uv.y);"
    "};")

importance_sample_ggx_source = str("vec3 importanceSampleGGX(vec2 Xi, vec3 N, float roughness)"
    "{"
    "    float a = roughness*roughness;"
    "    float phi = 2.0 * PI * Xi.x;"
    "    float cosTheta = sqrt((1.0 - Xi.y) / (1.0 + (a*a - 1.0) * Xi.y));"
    "    float sinTheta = sqrt(1.0 - cosTheta*cosTheta);"
        
    # "    // from spherical coordinates to cartesian coordinates"
    "    vec3 H;"
    "    H.x = cos(phi) * sinTheta;"
    "    H.y = sin(phi) * sinTheta;"
    "    H.z = cosTheta;"
        
    # "    // from tangent-space vector to world-space sample vector"
    "    vec3 up        = abs(N.z) < 0.999 ? vec3(0.0, 0.0, 1.0) : vec3(1.0, 0.0, 0.0);"
    "    vec3 tangent   = normalize(cross(up, N));"
    "    vec3 bitangent = cross(N, tangent);"
        
    "    vec3 sampleVec = tangent * H.x + bitangent * H.y + N * H.z;"
    "    return normalize(sampleVec);"
    "};")

radical_inverse_vdc_source = str("float RadicalInverse_VdC(uint bits)"
    "{"
    "    bits = (bits << 16u) | (bits >> 16u);"
    "    bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);"
    "    bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);"
    "    bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);"
    "    bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);"
    "    return float(bits) * 2.3283064365386963e-10;"
    "};")

hammersley_source = str("vec2 hammersley(uint i, uint N)"
    "{"
    "    return vec2(float(i)/float(N), RadicalInverse_VdC(i));"
    "};")


def init_cubemap_shader_info(name, vertex_shader_source, fragment_shader_source):
    vert_out = GPUStageInterfaceInfo(name)
    vert_out.smooth('VEC3', "v_normal")

    shader_info = GPUShaderCreateInfo()

    shader_info.sampler(0,'FLOAT_2D', "panorama")

    shader_info.vertex_in(0, 'VEC2', "position")
    shader_info.vertex_in(1, 'VEC3', "normal")

    shader_info.vertex_out(vert_out)
    
    shader_info.fragment_out(0, 'VEC4', "FragColor")

    shader_info.vertex_source(
       vertex_shader_source
    )

    shader_info.fragment_source(
        fragment_shader_source
    )

    return (shader_info, vert_out)

def create_pack_cubemap_shader():

    (shader_info, vert_out) = init_cubemap_shader_info(
        "cubemap_pack",
        # vertex_shader_source
        default_vertex_shader_source,
        # fragment_shader_source
        sample_spherical_map_source +
        "void main()"
        "{"
        "  vec3 normal = normalize(v_normal);"
        "  vec2 uv = sampleSphericalMap(normal);"
        "  vec4 color = texture(panorama, uv);"
        "  FragColor = color;"
        "};",
    )
        

    shader: GPUShader = gpu.shader.create_from_info(shader_info)
    del vert_out
    del shader_info

    return shader

def create_pack_irradiance_cubemap_shader(nb_samples = 32):

    sample_delta = pi / 2.1 / nb_samples

    (shader_info, vert_out) = init_cubemap_shader_info(
        "cubemap_irradiance_pack",
        # vertex_shader_source
        default_vertex_shader_source,
        # fragment_shader_source
        sample_spherical_map_source +

        "const float PI = 3.14159265359;"

        "const float sampleDelta = 0.025;"
      

        # "void main()"
        # "{"
        #     "vec3 irradiance = vec3(0.0);"
        #     "vec3 normal = normalize(v_normal);"
        #     "vec3 up    = vec3(0.0, 1.0, 0.0);"
        #     "vec3 right = normalize(cross(up, normal));"
        #     "up         = normalize(cross(normal, right));"

        #     "float sampleDelta = 0.025;"
        #     "float nrSamples = 0.0; "
        #     "for(float phi = 0.0; phi < 2.0 * PI; phi += sampleDelta)"
        #     "{"
        #         "for(float theta = 0.0; theta < 0.5 * PI; theta += sampleDelta)"
        #         "{"
        #             "// spherical to cartesian (in tangent space)"
        #             "vec3 tangentSample = vec3(sin(theta) * cos(phi),  sin(theta) * sin(phi), cos(theta));"
        #             "// tangent space to world"
        #             "vec3 sampleVec = tangentSample.x * right + tangentSample.y * up + tangentSample.z * N; "

        #             "irradiance += texture(environmentMap, sampleVec).rgb * cos(theta) * sin(theta);"
        #             "nrSamples++;"
        #         "}"
        #     "}"
        #     "irradiance = PI * irradiance * (1.0 / float(nrSamples));"
        #     "FragColor = vec4(irradiance, 1.0);"
        # "}"    

        
        "void main()"
        "{"
        "   int nrSamples = 0;"
        "   vec3 irradiance = vec3(0.0);"
        "   vec3 normal = normalize(v_normal);"
        "   vec3 up    = vec3(0.0, 1.0, 0.0);"
        "   vec3 right = cross(up, normal);"
        "   up         = cross(normal, right);"
        "   for(float phi = 0.001; phi < 1.0 * PI; phi += sampleDelta)"
        "   {"
        "       for(float theta = 0.001; theta < 0.5 * PI; theta += sampleDelta)"
        "       {"
        #"           vec3 tangentSample = vec3(sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta));"
        #"           vec3 sampleVec = tangentSample.x * right + tangentSample.y * up + tangentSample.z * normal;" 
        "           vec3 temp = cos(phi) * right + sin(phi) * up;"
        "           vec3 sampleVec = cos(theta) * normal + sin(theta) * temp;"
        "           vec2 sampleUv = sampleSphericalMap(sampleVec);"
        "           irradiance += texture(panorama, sampleUv).rgb * cos(theta) * sin(theta);"
        "           nrSamples++;"
        "       }"
        "   }"
        "   irradiance = PI * irradiance / float(nrSamples);"
        "   FragColor = vec4(irradiance, 1.0);"
        "};",
    )
        
    shader: GPUShader = gpu.shader.create_from_info(shader_info)
    del vert_out
    del shader_info

    return shader

def create_pack_reflectance_cubemap_shader(sample_count = 512):
    (shader_info, vert_out) = init_cubemap_shader_info(
        "cubemap_reflectance_pack",
        # vertex_shader_source
        default_vertex_shader_source,
        # fragment_shader_source

        "const float PI = 3.14159265359;" +
        sample_spherical_map_source +
        importance_sample_ggx_source +
        radical_inverse_vdc_source +
        hammersley_source +

        "const uint sampleCount = " + str(sample_count) + ";"
        
        "void main()"
        "{"
        "   vec3 N = normalize(v_normal);"
        "   vec3 R = N;"
        "   vec3 V = R;"

        "   float totalWeight = 0.0;"
        "   vec3 prefilteredColor = vec3(0.0);"

        "   for(uint i = 0u; i < sampleCount; ++i)"
        "   {"
        "       vec2 Xi = hammersley(i, sampleCount);"
        "       vec3 H  = importanceSampleGGX(Xi, N, roughness);"
        "       vec3 L  = normalize(2.0 * dot(V, H) * H - V);"

        "       float NdotL = max(dot(N, L), 0.0);"
        "       if(NdotL > 0.0)"
        "       {"
        "           vec2 uv = sampleSphericalMap(L);"
        "           prefilteredColor += texture(panorama, uv).rgb * NdotL;"
        "           totalWeight      += NdotL;"
        "       }"
        "   }"

        "   prefilteredColor = prefilteredColor / totalWeight;"
        "   FragColor = vec4(prefilteredColor, 1.0);"
        "};",
    )
    
    shader_info.push_constant('FLOAT', 'roughness')

    shader: GPUShader = gpu.shader.create_from_info(shader_info)
    del vert_out
    del shader_info

    return shader

cubemap_shader: GPUShader  = create_pack_cubemap_shader()
irradiance_cubemap_shader: GPUShader  = create_pack_irradiance_cubemap_shader()
reflectance_cubemap_shader: GPUShader  = create_pack_reflectance_cubemap_shader()