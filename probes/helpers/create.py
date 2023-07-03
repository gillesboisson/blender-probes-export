import bpy

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
