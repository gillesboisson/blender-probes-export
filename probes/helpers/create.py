import bpy

def create_pano_camera(context):


    if bpy.data.cameras.get('PanoProbeCamera') is not None:
        camera_data = bpy.data.cameras.get('PanoProbeCamera')
    else:
        camera_data = bpy.data.cameras.new(name='PanoProbeCamera')
        camera_data.type = 'PANO'
        camera_data.cycles.panorama_type = 'EQUIRECTANGULAR'
        

    if bpy.data.objects.get('PanoProbeCamera') is not None:
        camera_object = bpy.data.objects.get('PanoProbeCamera')
    else:
        camera_object = bpy.data.objects.new('PanoProbeCamera', camera_data)
        context.scene.collection.objects.link(camera_object)


    

    
    return camera_object


def unlink_pano_camera(context):
    camera_object = bpy.data.objects.get('PanoProbeCamera')
    if camera_object is not None:
        context.scene.collection.objects.unlink(camera_object)
        bpy.data.objects.remove(camera_object)
    camera_data = bpy.data.cameras.get('PanoProbeCamera')
    if camera_data is not None:
        bpy.data.cameras.remove(camera_data)

def create_cube_camera(context):
    camera_data = bpy.data.cameras.new(name='CubeProbeCamera')
    camera_data.type = 'PANO'
    camera_data.cycles.panorama_type = 'EQUIANGULAR_CUBEMAP_FACE'
    camera_data.cycles.use_perspective = False

    camera_object = bpy.data.objects.new('CubeProbeCamera', camera_data)
    context.scene.collection.objects.link(camera_object)

    return camera_object
