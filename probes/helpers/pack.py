

from .gpu import pack_irradiance_cubemap, pack_reflection_cubemap




# def pack_irradiance_probe(export_direction: str, data, cubemap_size, max_texture_size = 1024):

#     source_files_path = []

#     for file in data['files']:
#         source_files_path.append(export_direction  + file)

#     pack_irradiance_cubemap(
#         source_files_path,
#         export_direction + data['name'] + '_packed.png',
#         cubemap_size, 'irradiance_pack',
#         max_texture_size,
#     )



# def pack_reflection_probe(
#         export_direction: str,
#         data,
#         cubemap_size,
#         max_texture_size = 1024,
#         start_roughness = 0.25,
#         level_roughness = 0.25,
#         nb_levels = 3,
#     ):

#     pack_reflection_cubemap(
#         [export_direction + data['file']],
#         export_direction + data['name'] + '_packed.png',
#         cubemap_size,
#         max_texture_size,
#         start_roughness,
#         level_roughness,  
#         nb_levels,
#         'reflection_pack',
#     )