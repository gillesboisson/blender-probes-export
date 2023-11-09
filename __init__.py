from .probes import register_probes, unregister_probes

bl_info = {
    "name" : "GI bake",
    "description" : "Global illumination bake is tool for baking global illumination in Blender. This include irradiance and radiance probes, and diffuse map (TBD).",
    "author" : "Gilles Boisson",
    "version" : (0,1),
    "blender": (2,90,0),
    "location" : "View3D",
    "category" : "3D view",
}

def register():
    register_probes()

def unregister():
    unregister_probes()

if __name__ == "__main__":
    register()