# Props


## Probes volumes

Probes setup is based on blender eevee implementation.


### Visibility

Visibility is defined
- in object level : Object Properties > GI Bake > Rendered By **. It specifies which probes volume type will render the object. 
- in probes volume level : Object data > probe > visibility. It specifies which view collection is visible (Eevee implementation). 

!! Bias, Bleed Bias and Blur are supported by the plugin. More details on Irradiance sampling.

### Intensity

Define probes contribution to GI.

#### Rendering

define how the probes are baked.

- Clipping start : rendering camera near
- Clipping end : rendering camera far

#### Baking

!! some rendering settings are define in baking part as some feature are implemented by eevee and other by the plugin, it is tricky to merge them into one panel.

Baking settings are defined in render level (Render Properties > GI Bake) for default and in Data Level (Probe Data > GI Bake) for custom settings.

- Use default : use default settings
- Map size : define the render map height (For equirectangular panoramas width = 2 x height)
- Sample max : define the rendering samples max (TODO: add other sampling settings : min samples, noise threshold, ...)
- Cubemap face size : define final cubemap face size
- Final texture max width : define final texture pack max width (See irradiance packing specs)

### Transform

volume probes transform is defined in object level. It is used to define the volume position and rotation scale.

### Irradiance grid

#### Influence

It defines how the volumes influence GI on a specific positions. All metrics are multiplied by object scale.

- Distance : distance between grid bounds (based on object scale) and the influence bounds (multiplied by scale). 
- Falloff : distance between the influence bounds (IO : influence = 0) and falloff bounds (I1 influence = 1).

bounds_I0 = (1 + distance) * scale
bounds_I1 = (1 + distance - falloff) * scale  


#### Resolution

Define probes resolution vector. It is used to define the number of probes in each axis.

vProbePosition = (scale * 2 - 1) * vProbeGridIndex * mProbeWorldMap

### Radiance (Reflection) cubemap

#### Influence

- Type : Sphere or Box define influence bounds model
- Size : define the influence size, it is represented as radius for sphere and distance from center for box
- Falloff : distance between the influence bounds (IO : influence = 0) and falloff bounds (I1 influence = 1).

bounds_I0 = size * scale
bounds_I1 = (size - falloff * size) * scale

#### Roughness levels

Roughness settings are defined in render level (Render Properties > GI Bake) for default and in Data Level (Probe Data > GI Bake) for custom settings.

as explained in Radiance IBL specs, the plugin supports multiple roughness levels. It is defined in render level (Render Properties > GI Bake)

- Roughness levels : define the number of roughness levels
- Roughness step : define the roughness step between each level
- Start roughness : define the first roughness level

eg : for 3 levels, start roughness = 0.1, roughness step = 0.2, roughness levels = 4

mipmap 0 : roughness = 0.1
mipmap 1 : roughness = 0.3
mipmap 2 : roughness = 0.5
mipmap 3 : roughness = 0.7

### Default probe 

Default cubemap is enable in reflection probe data level (Probe Data > GI Bake or Render > GI Bake > Default probe). It is used to define the default cubemap. 
they have props based in both irradiance and radiance volumes props.

