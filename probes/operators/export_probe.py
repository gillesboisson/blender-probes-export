
from math import pi
from bpy.types import Operator


import os
import bpy
from mathutils import Matrix, Vector
from ..utils import is_exportabled_light_probe

def create_pano_camera(context):
    camera_data = bpy.data.cameras.new(name='PanoProbeCamera')
    camera_data.type = 'PANO'
    camera_data.cycles.panorama_type = 'EQUIRECTANGULAR'

    camera_object = bpy.data.objects.new('PanoProbeCamera', camera_data)
    context.scene.collection.objects.link(camera_object)

    return camera_object

def create_cube_camera(context):
    camera_data = bpy.data.cameras.new(name='CubeProbeCamera')
    camera_data.type = 'PANO'
    camera_data.cycles.panorama_type = 'EQUIANGULAR_CUBEMAP_FACE'
    camera_data.cycles.use_perspective = False

    camera_object = bpy.data.objects.new('CubeProbeCamera', camera_data)
    context.scene.collection.objects.link(camera_object)

    return camera_object


def set_pano_render_settings(context,camera, output_path, samples_max = 32, height = 256):
    context.scene.render.engine = 'CYCLES'
    context.scene.cycles.samples = samples_max


    context.scene.render.resolution_x = height * 2
    context.scene.render.resolution_y = height

    context.scene.render.image_settings.file_format = 'PNG'
    context.scene.render.filepath = output_path
    
    context.scene.camera = camera

def set_cube_render_settings(context,camera, output_path, samples_max = 32, size = 256):
    context.scene.render.engine = 'CYCLES'
    context.scene.cycles.samples = samples_max


    context.scene.render.resolution_x = size
    context.scene.render.resolution_y = size

    context.scene.render.image_settings.file_format = 'PNG'
    context.scene.render.filepath = output_path
    
    context.scene.camera = camera



def render_pano_reflection_probe(context, operator, object):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world
    radius = prob_object.data.influence_distance 
    
    camera = create_pano_camera(context)
    export_directory = context.scene.probes_export.export_directory_path

    if(settings.use_default_settings):
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size
    

    if(export_directory == ''):
        # warn user
        operator.report({'INFO'}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    try:

        camera.location = transform.translation 
        camera.rotation_euler = transform.to_euler()
        # camera.scale = transform.to_scale()
        max_scale = max(camera.scale.x, camera.scale.y, camera.scale.z)
        camera.rotation_euler.x += pi / 2
        camera.data.clip_end = radius * max_scale
        camera.data.clip_start = 0.01

        # get current file path
        filepath = export_directory + '/' + prob_object.name + '.png'

        print("Baking probe "+ prob_object.name)
        set_pano_render_settings(context, camera, filepath, samples_max = samples_max, height = height)
        bpy.ops.render.render(write_still=True)
        

    except Exception as e:
        catched_exception = e

    context.scene.collection.objects.unlink(camera)
    
    if catched_exception != None:
        raise catched_exception


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

def render_cubemap_reflection_probe(context, operator, object):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world
    radius = prob_object.data.influence_distance 
    
    camera = create_cube_camera(context)
    export_directory = context.scene.probes_export.export_directory_path

    if(settings.use_default_settings):
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size
    

    if(export_directory == ''):
        # warn user
        operator.report({'INFO'}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None
    filepath = export_directory + '/' + prob_object.name 

    print('-- Baking probe ' + prob_object.name)

    try:

        camera.location = transform.translation 
        max_scale = max(camera.scale.x, camera.scale.y, camera.scale.z)
        camera.data.clip_end = radius * max_scale
        camera.data.clip_start = 0.01

        for i in range(6):
            final_file_path = filepath + '_' + cube_map_face_names[i] + '.png'
            print('-- Baking face ' + cube_map_face_names[i])
            camera.rotation_euler = cube_map_euler_rotations[i]

            set_cube_render_settings(context, camera, final_file_path, samples_max = samples_max, size = height)

            bpy.ops.render.render(write_still=True)

            
            

        

    except Exception as e:
        catched_exception = e

    context.scene.collection.objects.unlink(camera)
    
    if catched_exception != None:
        raise catched_exception
    

def render_pano_irradiance_probe(context, operator, object):
    prob = object.data
    settings = prob.probes_export




    camera = create_pano_camera(context)
    camera.rotation_euler.x = pi / 2

    camera.data.clip_end = prob.clip_end
    camera.data.clip_start = prob.clip_start

    export_directory = context.scene.probes_export.export_directory_path


    if(settings.use_default_settings):
        samples_max = context.scene.probes_export.irradiance_volume_default_samples_max
        height = context.scene.probes_export.irradiance_volume_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if(export_directory == ''):
        # warn user
        operator.report({'INFO'}, "No directory defined")
        return {"CANCELLED"}

    catched_exception = None

    try: 

        if os.path.exists(export_directory) == False:
            raise Exception("Directory does not exist")
        


        transform = object.matrix_world


        resolution_x = prob.grid_resolution_x
        resolution_y = prob.grid_resolution_y
        resolution_z = prob.grid_resolution_z


        
        filepath = export_directory + '/' + object.name

        print("Baking probe "+ object.name + " to " + filepath)

        for rx in range(resolution_x):
            vx = (rx + 0.5) / resolution_x * 2 - 1 
            for ry in range(resolution_y):
                vy = (ry + 0.5) / resolution_y * 2 - 1
                for rz in range(resolution_z):
                    vz = (rz + 0.5) / resolution_z * 2 - 1

                    final_file_path = filepath + '_' + str(rx) + '_' + str(ry) + '_' + str(rz) + '.png'
                    print('-- Baking probe at ' + str(vx) + ', ' + str(vy) + ', ' + str(vz))
                    res_vec = transform @ Vector((vx, vy, vz)) 

                    camera.location = res_vec

                    set_pano_render_settings(context, camera, final_file_path, samples_max = samples_max, height = height)
                    # render image
                    bpy.ops.render.render(write_still=True)
                    

    except Exception as e:
        catched_exception = e

    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    
    

class ExportProbe(Operator):
    bl_idname = "probe.export"
    bl_label = "Export probes"
    bl_description = ""
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):

        return is_exportabled_light_probe(context)
    
    def execute_cubemap(self, context):
        render_cubemap_reflection_probe(context, self, context.object)
        return {"FINISHED"}
    

    def execute_grid(self, context):
        render_pano_irradiance_probe(context, self, context.object)


        # print("Exporting grid")
        return {"FINISHED"}
    


    def execute(self, context):
        
        if(context.object.data.type == 'CUBEMAP'):
            return self.execute_cubemap(context)
        elif(context.object.data.type == 'GRID'):
            return self.execute_grid(context)
        

        return {"CANCELLED"}

