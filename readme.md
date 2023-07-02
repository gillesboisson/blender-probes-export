# Blender probes

Blender probes is blender plugin allowing to precompute reflectance and indirect luminance from blender and export data for use in external engine. It is based on blender probes object (reflection cubemap and irradiance grid) which has been design for blender eevee internal engine which not allow exporting baked data.

The goal is to have a complete which export data using only blender internal API only in order to make it as multiplatform as blender.

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


### Rendering

Rendering phase Use blender cycle renderer to render scene static object in for reflectance cubemaps and panomic for reach Irradiance Grid cell, final result is a png (HDR not supported yet) for blender integration simplicity  

### Compute and Packing

Cumpute phase (In development) load renderered image into blender and use internal blender openGL to compute irradiance, create reflectance level and pack in textures sheet for fast integration

(TBD)
### Scene probes data

Scene probes data are exported as JSON and pack all probes attributes and theire data texture

(TBD)

### Progress

This plugin is only in its development phase, here is the list of milestones ordered by priority 

- [X] Irradiance probe render operator
- [X] Reflectance probe render operator
- [ ] Object probe backing settings 
- [ ] Complete scene Render operator
- [ ] Irradiance Cubemap packing
- [ ] Refletance Cubemap packing
- [ ] Blender headless python command
- [ ] HDR Support

### Infos

If this plugin could be a good use for you preject please PM as it is more a first experiment for a ThreeJS light probe integrations