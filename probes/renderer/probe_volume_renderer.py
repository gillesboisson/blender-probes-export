from mathutils import Matrix
from ..compositing import (
    pack_irradiance_probe,
    pack_reflectance_probe,
    pack_global_probe,
)

from ..helpers.settings import set_pano_render_settings
from ..helpers.config import get_export_extension, get_export_format
from ..helpers.create import create_pano_camera, unlink_pano_camera
from ..helpers.files import (
    get_or_create_render_cache_subdirectory,
    global_pano_file,
    global_pano_filename,
    irradiance_filename,
    pano_file,
    pano_filename,
    save_probe_json_render_data,
)

from .helpers import (
    get_scene_renderered_object_names,
    reset_collection_visibility,
    reset_objects_render_settings,
    update_collection_visibility_for_probe,
)

from mathutils import Vector
from math import floor, pi


import os


class Probe_volume_renderer:
    json_data = None
    probe_volume = None
    samples_max = 0
    map_size = 0
    export_directory = ""
    final_export_directory = ""
    object_transform = None
    camera = None
    file_extension = ""
    render_nb_probes = 0
    render_nb_probes_progress = 0

    def get_json_data(self):
        return self.json_data

    def get_probe(self):
        return self.probe_volume

    def reset(self, context):
        # unlink_pano_camera(context)
        reset_objects_render_settings(context)
        reset_collection_visibility(context)

        self.json_data = None
        self.probe_volume = None
        self.samples_max = 0
        self.samples_max = 0
        self.time_limit = 0
        self.map_size = 0
        self.export_directory = ""
        self.object_transform = None
        self.camera = None
        self.file_extension = ""
        self.render_nb_probes = 0
        self.render_nb_probes_progress = 0

    def setup_render_settings_from_props(self, context, props):
        self.samples_max = props.samples_max
        self.samples_min = props.samples_min
        self.time_limit = props.time_limit
        self.map_size = props.map_size
        pass

    def set_pano_render_settings(self, context, output_path):
        context.scene.render.engine = "CYCLES"
        context.scene.cycles.samples = self.samples_max
        context.scene.cycles.min_samples = self.samples_min
        context.scene.cycles.time_limit = self.time_limit
        context.scene.cycles.film_exposure = context.scene.bake_gi.export_exposure
        context.scene.render.resolution_x = self.map_size * 2
        context.scene.render.resolution_y = self.map_size
        context.scene.render.image_settings.file_format = get_export_format(context)
        context.scene.render.filepath = output_path
        context.scene.camera = self.camera

    def setup_render_settings(self, context, probe_volume):
        pass

    def get_nb_probes(self, probe_volume):
        return 1

    def setup_render_batch(self, context, operator, probe_volume):
        self.render_nb_probes = self.get_nb_probes(probe_volume)
        self.probe_volume = probe_volume
        probe_volume_data = probe_volume.data

        self.setup_render_settings(context, probe_volume)

        object_transform: Matrix = self.probe_volume.matrix_world

        camera = create_pano_camera(context)
        camera.data.clip_start = probe_volume_data.clip_start
        camera.data.clip_end = probe_volume_data.clip_end

        export_directory = context.scene.bake_gi.export_directory_path

        if export_directory == "":
            operator.report({"ERROR"}, "No probes export directory defined")
            return None

        if os.path.exists(export_directory) == False:
            raise Exception("Directory does not exist")

        update_collection_visibility_for_probe(
            context.scene.collection.children, self.probe_volume.data
        )

        self.samples_max = self.samples_max
        self.map_size = self.map_size
        self.export_directory = export_directory
        self.object_transform = object_transform
        self.camera = camera
        self.file_extension = get_export_extension(context)
        self.final_export_directory = get_or_create_render_cache_subdirectory(
            export_directory, self.probe_volume.name
        )

        self.init_json_data(context)
        return self.json_data

    def setup_render(self, context, probe_index, nb_probes):
        pass

    def finalize_render(self, context, probe_index, nb_probes):
        self.render_nb_probes_progress = probe_index + 1
        pass

    def finalize_render_batch(self, context, operator):
        unlink_pano_camera(context)
        names = get_scene_renderered_object_names(context)
        self.json_data["baked_objects"] = names

        export_directory = context.scene.bake_gi.export_directory_path

        save_probe_json_render_data(
            export_directory, self.probe_volume.name, self.json_data
        )

        pass

    def init_json_data(self, context):
        pass


class Default_probe_volume_renderer(Probe_volume_renderer):
    __current_render_filename = ""

    def init_json_data(self, context):
        props = context.scene.bake_gi

        self.json_data = {
            "name": self.probe_volume.name,
            "probe_type": "global",
            "type": "pano",
            "transform": {
                "position": [
                    self.object_transform.translation.x,
                    self.object_transform.translation.z,
                    -self.object_transform.translation.y,
                ],
                "scale": self.object_transform.to_scale().to_tuple(),
                "rotation": [0, 0, 0],
            },
            "render": {
                "clip_start": self.probe_volume.data.clip_start,
                "clip_end": self.probe_volume.data.clip_end,
                "map_size": self.map_size,
                "cycle_samples_max": self.samples_max,
                "cycle_samples_min": self.samples_min,
                "cycle_time_limit": self.time_limit,
            },
            # "data": {
            #     # "irradiance_export_map_size": props.global_irradiance_export_map_size,
            #     # "irradiance_max_texture_size": props.global_irradiance_max_texture_size,
            #     # "reflectance_export_map_size": props.global_reflectance_export_map_size,
            #     # "reflectance_max_texture_size": props.global_reflectance_max_texture_size,
            #     # "reflectance_nb_levels": props.global_reflectance_nb_levels,
            #     # "reflectance_start_roughness": props.global_reflectance_start_roughness,
            #     # "reflectance_level_roughness": props.global_reflectance_level_roughness,
            # },
            "file": global_pano_filename(self.probe_volume.name, self.file_extension),
            "baked_objects": get_scene_renderered_object_names(context),
        }

    def setup_render_settings(self, context, probe_volume):
        self.setup_render_settings_from_props(
            context, context.scene.bake_gi.global_render_settings
        )

    def setup_render_batch(self, context, operator, probe_volume):
        self.nb_probes = 1

        for ob in context.scene.objects:
            if ob.type == "MESH":
                ob.hide_render = not ob.bake_gi.render_by_global_probe

        return super().setup_render_batch(context, operator, probe_volume)

    def setup_render(self, context, probe_index, nb_probes):
        # res= super().setup_render(context, probe_index, nb_probes)
        filepath = global_pano_file(
            self.export_directory, self.probe_volume.name, self.file_extension
        )

        self.camera.location = self.object_transform.translation
        self.camera.rotation_euler.x = pi / 2

        self.set_pano_render_settings(
            context,
            filepath,
        )

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_global_probe(context, self.probe_volume)
        pass


class Irradiance_probe_volume_renderer(Probe_volume_renderer):
    __current_render_filename = ""

    def init_json_data(self, context):
        translation_tupple = self.object_transform.translation.to_tuple()
        scale_tupple = self.object_transform.to_scale().to_tuple()
        rotation_euler = self.object_transform.to_euler()

        self.json_data = {
            "type": "pano",
            "probe_type": "irradiance",
            "name": self.probe_volume.name,
            # "width": self.height * 2,
            # "height": self.height,
            "transform": {
                "position": [
                    translation_tupple[0],
                    translation_tupple[2],
                    -translation_tupple[1],
                ],
                "scale": [scale_tupple[0], scale_tupple[2], scale_tupple[1]],
                "rotation": [rotation_euler.x, rotation_euler.z, -rotation_euler.y],
            },
            "render": {
                "clip_start": self.probe_volume.data.clip_start,
                "clip_end": self.probe_volume.data.clip_end,
                "map_size": self.map_size,
                "cycle_samples_max": self.samples_max,
                "cycle_samples_min": self.samples_min,
                "cycle_time_limit": self.time_limit,
            },
            "data": {
                "resolution": [
                    self.probe_volume.data.grid_resolution_x,
                    self.probe_volume.data.grid_resolution_z,
                    self.probe_volume.data.grid_resolution_y,
                ],
                "influence_distance": self.probe_volume.data.influence_distance,
                "falloff": self.probe_volume.data.falloff,
            },
            "files": [],
            "baked_objects": get_scene_renderered_object_names(context),
        }

    def setup_render_settings(self, context, probe_volume):
        probe_volume_settings = probe_volume.data.bake_gi
        if probe_volume_settings.use_default_settings:
            self.setup_render_settings_from_props(
                context, context.scene.bake_gi.default_irradiance_render_settings
            )
        else:
            self.setup_render_settings_from_props(
                context, probe_volume_settings.render_settings
            )

    def get_nb_probes(self, probe_volume):
        return (
            probe_volume.data.grid_resolution_x
            * probe_volume.data.grid_resolution_z
            * probe_volume.data.grid_resolution_y
        )

    def setup_render_batch(self, context, operator, probe_volume):
        for ob in context.scene.objects:
            if ob.type == "MESH":
                ob.hide_render = not ob.bake_gi.render_by_irradiance_probes

        return super().setup_render_batch(context, operator, probe_volume)

    def setup_render(self, context, probe_index, nb_probes):
        prob = self.probe_volume.data

        resolution_x = prob.grid_resolution_x
        resolution_y = prob.grid_resolution_y
        resolution_z = prob.grid_resolution_z

        resolution_y_z = resolution_y * resolution_z

        rx = floor(probe_index / resolution_y_z)
        ry = probe_index % resolution_y
        ry = resolution_y - ry - 1  # inverted y for openGL axis conversion
        rz = floor(probe_index / resolution_y) % resolution_z

        vz = (rz + 0.5) / resolution_z * 2 - 1
        vx = (rx + 0.5) / resolution_x * 2 - 1
        vy = (ry + 0.5) / resolution_y * 2 - 1

        self.__current_render_filename = irradiance_filename(
            rx, ry, rz, self.file_extension
        )

        final_file_path = (
            self.final_export_directory + "/" + self.__current_render_filename
        )

        res_vec = self.object_transform @ Vector((vx, vy, vz))

        self.camera.location = res_vec
        self.camera.rotation_euler.x = pi / 2

        self.set_pano_render_settings(
            context,
            final_file_path,
        )
        pass

    def finalize_render(self, context, probe_index, nb_probes):
        super().finalize_render(context, probe_index, nb_probes)
        self.json_data["files"].append(self.__current_render_filename)
        pass

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_irradiance_probe(context, self.probe_volume)
        pass


class Reflection_probe_volume_renderer(Probe_volume_renderer):
    def init_json_data(self, context):
        self.json_data = {
            "type": "pano",
            "probe_type": "reflection",
            "name": self.probe_volume.name,
            "transform": {
                "position": [
                    self.object_transform.translation.x,
                    self.object_transform.translation.z,
                    -self.object_transform.translation.y,
                ],
                "scale": self.object_transform.to_scale().to_tuple(),
                "rotation": [0, 0, 0],
            },
            "position": [
                self.object_transform.translation.x,
                self.object_transform.translation.z,
                -self.object_transform.translation.y,
            ],
            "data": {
                "falloff": self.probe_volume.data.falloff,
                "intensity": self.probe_volume.data.intensity,
                "influence_type": self.probe_volume.data.influence_type,
                "influence_distance": self.probe_volume.data.influence_distance,
            },
            "render": {
                "clip_start": self.probe_volume.data.clip_start,
                "clip_end": self.probe_volume.data.clip_end,
                "map_size": self.map_size,
                "cycle_samples_max": self.samples_max,
                "cycle_samples_min": self.samples_min,
                "cycle_time_limit": self.time_limit,
            },
            "file": pano_filename(self.file_extension),
            "baked_objects": get_scene_renderered_object_names(context),
        }

    def setup_render_settings(self, context, probe_volume):
        probe_volume_settings = probe_volume.data.bake_gi
        if probe_volume_settings.use_default_settings:
            self.setup_render_settings_from_props(
                context, context.scene.bake_gi.default_reflection_render_settings
            )
        else:
            self.setup_render_settings_from_props(
                context, probe_volume_settings.render_settings
            )

        # settings = probe_volume.data.bake_gi
        # if settings.use_default_settings:
        #     self.samples_max = (
        #         context.scene.bake_gi.reflection_cubemap_default_samples_max
        #     )
        #     self.height = context.scene.bake_gi.reflection_cubemap_default_map_size
        # else:
        #     self.samples_max = settings.samples_max
        #     self.height = settings.map_size

    def setup_render(self, context, probe_index, nb_probes):
        export_directory = context.scene.bake_gi.export_directory_path

        self.camera.location = self.object_transform.translation
        # self.camera.rotation_euler = self.object_transform.to_euler()
        self.camera.rotation_euler.x = pi / 2

        # get current file path
        filepath = pano_file(
            self.export_directory, self.probe_volume.name, self.file_extension
        )

        self.set_pano_render_settings(
            context,
            filepath,
        )

    def setup_render_batch(self, context, operator, probe_volume):
        for ob in context.scene.objects:
            if ob.type == "MESH":
                ob.hide_render = not ob.bake_gi.render_by_reflection_probes

        return super().setup_render_batch(context, operator, probe_volume)

    def finalize_render(self, context, probe_index, nb_probes):
        super().finalize_render(context, probe_index, nb_probes)
        pass

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_reflectance_probe(context, self.probe_volume)
        pass
