# Blender probes export

Blender probes is blender plugin allowing to precompute reflectance, indirect luminance from blender and export data for use in external engine. It is based on blender probes object (reflection cubemap and irradiance grid) which has been design for blender eevee internal engine but not allowing baked data export.

Probe export is done in 2 phases
- Rendering : use Blender cycle engine tu render probes
- Packing  : use Blender opengl API to compute irradiance and reflectance and pack data in texture sheet

### Rendering

Rendering phase Use blender cycle renderer to render scene static object in reflectance cubemaps and panomic equi rectangle for each Irradiance Grid cell, final result is a png (HDR not supported yet) images for each probe

### Compute and Packing

Cumpute phase  load renderered image into blender and use internal blender openGL API to compute irradiance, create reflectance level and pack final data in textures sheet for fast integration. Data are exported as JSON and PNG texture sheet, one for each probe


### Scene probes data

Scene probes data are exported as JSON and includes all probes attributes and a link to data texture
Rendered probes attributed are saved in a json file (probes.json) with a commmon main structure and sub data property with specific probe type based settings

```json
[
    // Irradiance
    {
        "name": "IrradianceVolume",
        "file": "IrradianceVolume_packed.png",
        "cubemap_size": 32,
        "texture_size": 2048,
        "type": "irradiance",
        "position": [
            0.0,
            0.0,
            5.0
        ],
        "scale": [
            14.5,
            14.5,
            5.0
        ],

        // Irradiance specific data
        "data": {
            "falloff": 1.0,
            "resolution": [
                5,
                5,
                2
            ],
            "clip_start": 0.009999999776482582,
            "clip_end": 40.0
        }
    },

    // Reflection
    {
        "name": "ReflectionCubemap",
        "file": "ReflectionCubemap_packed.png",
        "cubemap_size": 512,
        "texture_size": 2048,
        "type": "reflection",
        "position": [
            0.0,
            0.0,
            5.0
        ],
        "scale": [
            1.0,
            1.0,
            1.0
        ],

        // Reflection specific data
        "data": {
            "start_roughness": 0.0,
            "level_roughness": 0.25,
            "nb_levels": 3,
            "scale": [
                1.0,
                1.0,
                1.0
            ],
            "falloff": 0.10000000149011612,
            "radius": 22.0
        }
    }
]
```


### Progress

This plugin is in its development phase, here is the list of milestones ordered by priority 

- [X] Irradiance probe render operator
- [X] Reflectance probe render operator
- [X] Object probe baking settings 
- [X] Complete scene Render operator
- [X] Irradiance Cubemap packing
- [X] Refletance Cubemap packing
- [ ] SH irradiance packing
- [ ] Asynchronous rendering + progress bar
- [ ] Blender headless python command
- [ ] Support of other data kind using blender bake system (eg. Ambiant occlusion)
- [ ] HDR Support






## License

The MIT License (MIT)

Copyright (c) 2023-present Gilles Boisson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
