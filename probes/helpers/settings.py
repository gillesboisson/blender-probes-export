
def set_global_pano_render_settings(context,camera, output_path, samples_max = 32, height = 256):
    context.scene.render.engine = 'CYCLES'
    context.scene.cycles.samples = samples_max


    context.scene.render.resolution_x = height * 2
    context.scene.render.resolution_y = height

    context.scene.render.image_settings.file_format = 'HDR'
    context.scene.render.filepath = output_path
    
    context.scene.camera = camera

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
