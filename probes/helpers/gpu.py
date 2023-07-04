from cmath import pi
from math import ceil, floor
import bpy
import gpu
from mathutils import Matrix
from gpu_extras.batch import batch_for_shader

from gpu.types import *

from .config import cube_map_face_names, cube_map_euler_rotations, faces_vertex_normals

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

        "const float sampleDelta = " + str(sample_delta) + ";"
        
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

def pack_irradiance_cubemap(
        map_texture_files,
        output_file_path,
        cubemap_size,
        image_name,
        max_texture_size,
        
    ):
    nb_face_x = 6
    nb_face_y = 1

    nb_maps = len(map_texture_files)

    (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height) = get_cubemap_pack_layout(cubemap_size,nb_maps,max_texture_size, nb_face_x, nb_face_y)

    
    if nb_maps == 0:
        return None
    

    # shader = cubemap_shader
    shader = irradiance_cubemap_shader


    offscreen = GPUOffScreen(texture_width, texture_height)

    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

        uvs = get_cubemap_pack_uvs(cubemap_size, 0, nb_maps, max_texture_size, nb_face_x, nb_face_y)
        map_normals = generate_cubemap_pack_normals(nb_maps)
        map_indices = generate_cubemap_quad_indices()

        
        
        for map_ind in range(nb_maps):
            map_texture_files[map_ind] = map_texture_files[map_ind]
            map_image = bpy.data.images.load(map_texture_files[map_ind])
            texture = gpu.texture.from_image(map_image)


            shader.uniform_sampler("panorama", texture)
            

            map_uvs = uvs[map_ind]
            
            batch: GPUBatch = batch_for_shader(shader, 'TRIS', {"position": map_uvs, "normal": map_normals}, indices = map_indices)
            
            batch.draw(shader)


            bpy.data.images.remove(map_image)
            


        buffer = fb.read_color(0,0,texture_width,texture_height,4,0,'UBYTE')

    
    offscreen.free()

    if not image_name in bpy.data.images:
        bpy.data.images.new(image_name, texture_width, texture_height)

    image = bpy.data.images[image_name]
    image.scale(texture_width, texture_height)

    buffer.dimensions = texture_width * texture_height * 4
    image.pixels = [v / 255 for v in buffer]

    image.save_render(output_file_path)



def pack_reflection_cubemap(
        map_texture_files,
        output_file_path,
        cubemap_size,
        max_texture_size,
        start_roughness,
        level_roughness,
        nb_levels,
        image_name,
        
        
    ):
    nb_face_x = 4
    nb_face_y = 2
    nb_maps = len(map_texture_files)

    (texture_width,texture_height,nb_cluster_x,nb_cluster_y,cluster_width,cluster_height) = get_cubemap_pack_layout(cubemap_size,nb_maps,max_texture_size, nb_face_x, nb_face_y)

    
    if nb_maps == 0:
        return None
    

    # shader = cubemap_shader
    shader = reflectance_cubemap_shader


    offscreen = GPUOffScreen(texture_width, texture_height)


    with offscreen.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0.0, 0.0, 0.0, 0.0))

        
        map_normals = generate_cubemap_pack_normals(nb_maps)
        map_indices = generate_cubemap_quad_indices()
        for level in range(nb_levels):
            roughness = start_roughness + level * level_roughness
            shader.uniform_float("roughness", roughness)


            for map_ind in range(nb_maps):
                map_texture_files[map_ind] = map_texture_files[map_ind]
                map_image = bpy.data.images.load(map_texture_files[map_ind])

                uvs = get_cubemap_pack_uvs(cubemap_size, level, nb_maps, max_texture_size, nb_face_x, nb_face_y)
                texture = gpu.texture.from_image(map_image)
                shader.uniform_sampler("panorama", texture)
                
                map_uvs = uvs[map_ind]
                
                batch: GPUBatch = batch_for_shader(shader, 'TRIS', {"position": map_uvs, "normal": map_normals}, indices = map_indices)
                
                batch.draw(shader)


                bpy.data.images.remove(map_image)
            


        buffer = fb.read_color(0,0,texture_width,texture_height,4,0,'UBYTE')

    
    offscreen.free()

    if not image_name in bpy.data.images:
        bpy.data.images.new(image_name, texture_width, texture_height)

    image = bpy.data.images[image_name]
    image.scale(texture_width, texture_height)

    buffer.dimensions = texture_width * texture_height * 4
    image.pixels = [v / 255 for v in buffer]

    image.save_render(output_file_path)
    



