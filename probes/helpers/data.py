


import json


def load_probe_data(export_dir, probe_name):
    with open(export_dir + 'probes.json') as json_file:
        data = json.load(json_file)
        for probe in data:
            if probe['name'] == probe_name:
                return probe
            
    return None


