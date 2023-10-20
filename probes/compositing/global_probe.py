
from ..helpers.poll import get_context_probes_names
from ..helpers.files import load_probe_json_render_data, save_scene_json_pack_data,global_probe_render_name,global_pano_file

import os

def pack_global_probe(context, prob_object = None):
    export_directory = context.scene.probes_export.export_directory_path
        
    if(prob_object == None):
        prob_object = context.object

    
    data = load_probe_json_render_data(export_directory, global_probe_render_name)

    if(data == None):
        return None
    
    # copy render cache hdr to export directory
    cached_probe = global_pano_file(context.scene.probes_export.export_directory_path)
    os.popen('cp "' + cached_probe + '" "' + export_directory + '"')
    
    probe_names = get_context_probes_names(context)

    save_scene_json_pack_data(export_directory, probe_names)

    return data