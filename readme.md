# Blender probes export

Blender probes is blender plugin allowing to precompute reflectance, indirect luminance from blender and export data for use in external engine. It is based on blender probes object (reflection cubemap and irradiance grid) which has been design for blender eevee internal engine but not allowing baked data export.



### Rendering

Rendering phase Use blender cycle renderer to render scene static object in reflectance cubemaps and panomic equi rectangle for each Irradiance Grid cell, final result is a png (HDR not supported yet) images for each probe

#### Data

Rendered probes attributed are saved in a json file (probes.json) in order to pack it in a different phase

**Irradiance Volume example**
```json
[
    {
        "type": "pano",
        "resolution": [
            4,
            4,
            2
        ],
        "world_mat": [
            14.5,
            0.0,
            0.0,
            0.0,
            0.0,
            14.5,
            0.0,
            0.0,
            0.0,
            0.0,
            5.0,
            5.0,
            0.0,
            0.0,
            0.0,
            1.0
        ],
        "falloff": 1.0,
        "probe_type": "irradiance",
        "name": "IrradianceVolume",
        "width": 128,
        "height": 64,
        "files": [
            "IrradianceVolume_0_0_0.png",
            "IrradianceVolume_0_0_1.png",
            "IrradianceVolume_0_1_0.png",
            "IrradianceVolume_0_1_1.png",
            "IrradianceVolume_0_2_0.png",
            "IrradianceVolume_0_2_1.png",
            "IrradianceVolume_0_3_0.png",
            "IrradianceVolume_0_3_1.png",
            "IrradianceVolume_1_0_0.png",
            "IrradianceVolume_1_0_1.png",
            "IrradianceVolume_1_1_0.png",
            "IrradianceVolume_1_1_1.png",
            "IrradianceVolume_1_2_0.png",
            "IrradianceVolume_1_2_1.png",
            "IrradianceVolume_1_3_0.png",
            "IrradianceVolume_1_3_1.png",
            "IrradianceVolume_2_0_0.png",
            "IrradianceVolume_2_0_1.png",
            "IrradianceVolume_2_1_0.png",
            "IrradianceVolume_2_1_1.png",
            "IrradianceVolume_2_2_0.png",
            "IrradianceVolume_2_2_1.png",
            "IrradianceVolume_2_3_0.png",
            "IrradianceVolume_2_3_1.png",
            "IrradianceVolume_3_0_0.png",
            "IrradianceVolume_3_0_1.png",
            "IrradianceVolume_3_1_0.png",
            "IrradianceVolume_3_1_1.png",
            "IrradianceVolume_3_2_0.png",
            "IrradianceVolume_3_2_1.png",
            "IrradianceVolume_3_3_0.png",
            "IrradianceVolume_3_3_1.png"
        ]
    },
    
]
```

**Reflection cubemap example**

```json
{
    "type": "cubemap",
    "radius": 22.0,
    "position": [
        0.0,
        0.0,
        5.0
    ],
    "falloff": 0.10000000149011612,
    "probe_type": "reflection",
    "name": "ReflectionCubemap",
    "size": 256,
    "faces_files": [
        "ReflectionCubemap_negx.png",
        "ReflectionCubemap_posx.png",
        "ReflectionCubemap_negy.png",
        "ReflectionCubemap_posy.png",
        "ReflectionCubemap_negz.png",
        "ReflectionCubemap_posz.png"
    ]
}
```


### Compute and Packing

Cumpute phase (In development) load renderered image into blender and use internal blender openGL API to compute irradiance, create reflectance level and pack final data in textures sheet for fast integration

(TBD)
### Scene probes data

Scene probes data are exported as JSON and includes all probes attributes and a link to data texture

(TBD)

### Progress

This plugin is in its development phase, here is the list of milestones ordered by priority 

- [X] Irradiance probe render operator
- [X] Reflectance probe render operator
- [ ] Object probe baking settings 
- [ ] Complete scene Render operator
- [ ] Irradiance Cubemap packing
- [ ] Refletance Cubemap packing
- [ ] Blender headless python command
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
