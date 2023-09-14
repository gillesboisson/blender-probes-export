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

#### File structure

Scene probes data are exported in a folder defined by user, in scene probes export panel.

- export_directory
    - probes.json
    - reflection_1_packed.png
    - irradiance_2_packed.png
    - probes.json
    - __render_cache                    : cache folder for rendered / packed probes
        - reflection_1                  : per probe folder
            - 0_0_0.png                 
            - 1_0_0.png                 
            - ...
            - packed_probe.json         : packed probe data (use as cache data)
            - rendered_probe.json       : rendered probe data (use as cache data)

        - irradiance_2                  : per probe folder
            - pano.png                  : per probe equirectangle is baked
            - packed_probe.json         : (use as cache data)
            - rendered_probe.json       : (use as cache data)


#### image
##### Irradiance

For each irradiance grid cell, a panoramic equirectangle is baked and saved in a png file

![0_0_0.png](./doc/images/0_0_0.png)

Final packed data is saved in a png file

![IrradianceVolume_packed.png](./doc/images/IrradianceVolume_packed.png)

##### Reflection

For each reflection probe, a panoramic equirectangle is baked and saved in a png file

![pano.png](./doc/images/pano.png)

Final packed data is saved in a png file with all roughness level

![ReflectionCubemap_packed.png](./doc/images/ReflectionCubemap_packed.png)

#### Data structure

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

        // probe type specific data
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

        // probe type  specific data
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
