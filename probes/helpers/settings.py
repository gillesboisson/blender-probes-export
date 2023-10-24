from .config import get_export_format

def set_pano_render_settings(context, camera, output_path, samples_max, height):
    context.scene.render.engine = "CYCLES"
    context.scene.cycles.samples = samples_max
    context.scene.cycles.film_exposure = context.scene.probes_export.export_exposure
    context.scene.render.resolution_x = height * 2
    context.scene.render.resolution_y = height
    context.scene.render.image_settings.file_format = get_export_format(context)
    context.scene.render.filepath = output_path
    context.scene.camera = camera

def set_cube_render_settings(context, camera, output_path, samples_max=32, size=256):
    context.scene.render.engine = "CYCLES"
    context.scene.cycles.samples = samples_max
    context.scene.film_exposure = context.scene.probes_export.export_exposure

    context.scene.render.resolution_x = size
    context.scene.render.resolution_y = size

    context.scene.render.image_settings.file_format = get_export_format(context)
    context.scene.render.filepath = output_path
    context.scene.camera = camera
