from gpu.types import *
import gpu

from ..helpers import get_export_extension
import bpy

def prepare_renderer(context, texture_width, texture_height):

    if context.scene.bake_gi.export_format == 'HDR':
        gpuOffscreen = GPUOffScreen(
            width=texture_width, height=texture_height, format="RGBA16F"
        )
    else:
        gpuOffscreen = GPUOffScreen(
            width=texture_width, height=texture_height, format="RGBA8"
        )

    return gpuOffscreen

def prepare_renderer_from_image(image_source_file, texture_width, texture_height):
    image = bpy.data.images.load(image_source_file)
    texture = gpu.texture.from_image(image)
    bpy.data.images.remove(image)


    gpuOffscreen = GPUOffScreen(
        width=texture_width, height=texture_height, format=texture.format
    )

    return gpuOffscreen, texture
    
def save_render(context,framebuffer, texture_width, texture_height,name):
    export_directory = context.scene.bake_gi.export_directory_path
    file_extension = get_export_extension(context)
    
    # framebuffer: GPUFrameBuffer = gpu.state.active_framebuffer_get()

    image_name = 'pack'

    if image_name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[image_name])
    
    # for HDR source textures is 16 bit Float per channel : it is exported as open EXR
    if context.scene.bake_gi.export_format == 'HDR':
        buffer = framebuffer.read_color(0, 0, texture_width, texture_height, 4, 0, "FLOAT")
        context.scene.render.image_settings.file_format = 'OPEN_EXR'
        bpy.data.images.new(image_name, texture_width, texture_height, alpha=False, float_buffer=True)

    # for SDR source textures is 8 bit (Unsigned byte) per channel : it is exported as PNG
    else:
        buffer = framebuffer.read_color(0, 0, texture_width, texture_height, 4, 0, "UBYTE")
        context.scene.render.image_settings.file_format = 'PNG'
        bpy.data.images.new(image_name, texture_width, texture_height, alpha=False)



    image = bpy.data.images[image_name]
    image.scale(texture_width, texture_height)
    buffer.dimensions = texture_width * texture_height * 4
    
    if context.scene.bake_gi.export_format == 'HDR':
        image.file_format = 'OPEN_EXR'
        image.pixels = buffer
    # 8Bit textures is converted to float for SDR
    else:
        image.file_format = 'PNG'
        image.pixels = [v / 255 for v in buffer]



    filename = name + "."+file_extension
    output_file_path = export_directory + "/" + filename
    image.save_render(output_file_path)

    return (output_file_path, filename)

