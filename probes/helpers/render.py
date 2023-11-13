from math import floor, pi

from ..compositing.global_probe import pack_global_probe

from ..compositing.reflectance import pack_reflectance_probe
from ..compositing.irradiance import pack_irradiance_probe

from .files import (
    get_or_create_render_cache_subdirectory,
    irradiance_filename,
    pano_filename,
    save_probe_json_render_data,
)

import os
import bpy
from mathutils import Matrix, Vector

from .create import create_pano_camera, create_cube_camera, unlink_pano_camera
from .settings import set_pano_render_settings, set_cube_render_settings

from .files import pano_file, cubemap_filename, global_pano_filename, global_pano_file
from .config import cube_map_face_names, cube_map_euler_rotations, get_export_extension


def reset_objects_render_settings(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = False


def update_collection_visibility_for_probe(collection, probe_data):
    visibility_collection = probe_data.visibility_collection
    invert_visibility = probe_data.invert_visibility_collection
    hasHiddenChild = False
    for child in collection:
        if child == visibility_collection:
            child.hide_render = invert_visibility
        elif not child.children:
            child.hide_render = not invert_visibility
        else:
            child.hide_render = update_collection_visibility_for_probe(
                child.children, probe_data
            )

        hasHiddenChild = hasHiddenChild and child.hide_render

    return hasHiddenChild


def reset_collection_visibility(context):
    collections = context.scene.collection.children_recursive

    for collection in collections:
        collection.hide_render = False


def get_scene_renderered_object_names(context):
    objects = []

    for collection in context.scene.collection.children_recursive:
        if collection.hide_render == False:
            for ob in collection.objects:
                if ob.type == "MESH" and ob.hide_render == False:
                    # as visibility is reset after check, this avoid having double object in list
                    ob.hide_render = True
                    objects.append(ob.name)

    for ob in objects:
        context.scene.objects[ob].hide_render = False

    return objects


def print_render_progress(text, progress_min=0, progress_max=1, progress: float = 0):
    print(
        str(floor((progress_min + progress) / progress_max * 100)) + "%" + " :: " + text
    )


class ProbeVolumeRenderer:
    json_data = None
    probe_volume = None
    samples_max = 0
    height = 0
    export_directory = ""
    final_export_directory = ""
    object_transform = None
    camera = None
    file_extension = ""
    render_nb_probes = 0

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
        self.height = 0
        self.export_directory = ""
        self.object_transform = None
        self.camera = None
        self.file_extension = ""
        self.render_nb_probes = 0

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

        export_directory = context.scene.probes_export.export_directory_path

        if export_directory == "":
            operator.report({"INFO"}, "No directory defined")
            return None

        if os.path.exists(export_directory) == False:
            raise Exception("Directory does not exist")

        update_collection_visibility_for_probe(
            context.scene.collection.children, self.probe_volume.data
        )

        self.samples_max = self.samples_max
        self.height = self.height
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
        pass

    def finalize_render_batch(self, context, operator):
        unlink_pano_camera(context)
        names = get_scene_renderered_object_names(context)
        self.json_data["baked_objects"] = names

        export_directory = context.scene.probes_export.export_directory_path

        save_probe_json_render_data(
            export_directory, self.probe_volume.name, self.json_data
        )

        pass

    def init_json_data(self, context):
        pass


class ReflectionProbeVolumeRenderer(ProbeVolumeRenderer):
    def init_json_data(self, context):
        self.json_data = {
            "type": "pano",
            "position": [
                self.object_transform.translation.x,
                self.object_transform.translation.z,
                -self.object_transform.translation.y,
            ],
            "file": pano_filename(self.file_extension),
            "baked_objects": get_scene_renderered_object_names(context),
            "scale": self.object_transform.to_scale().to_tuple(),
            "rotation": [0, 0, 0],
            "falloff": self.probe_volume.data.falloff,
            "intensity": self.probe_volume.data.intensity,
            "influence_type": self.probe_volume.data.influence_type,
            "influence_distance": self.probe_volume.data.influence_distance,
            "clip_start": self.probe_volume.data.clip_start,
            "clip_end": self.probe_volume.data.clip_end,
            "probe_type": "reflection",
            "name": self.probe_volume.name,
            "width": self.height * 2,
            "height": self.height,
        }

    def setup_render_settings(self, context, probe_volume):

        
        settings = probe_volume.data.probes_export
        if settings.use_default_settings:
            self.samples_max = (
                context.scene.probes_export.reflection_cubemap_default_samples_max
            )
            self.height = (
                context.scene.probes_export.reflection_cubemap_default_map_size
            )
        else:
            self.samples_max = settings.samples_max
            self.height = settings.map_size

    def setup_render(self, context, probe_index, nb_probes):
        export_directory = context.scene.probes_export.export_directory_path

        self.camera.location = self.object_transform.translation
        # self.camera.rotation_euler = self.object_transform.to_euler()
        self.camera.rotation_euler.x = pi / 2

        # get current file path
        filepath = pano_file(
            self.export_directory, self.probe_volume.name, self.file_extension
        )

        set_pano_render_settings(
            context,
            self.camera,
            filepath,
            samples_max=self.samples_max,
            height=self.height,
        )

    def setup_render_batch(self, context, operator, probe_volume):
        for ob in context.scene.objects:
            if ob.type == "MESH":
                ob.hide_render = not ob.probes_render.render_by_reflection_probes

        return super().setup_render_batch(context, operator, probe_volume)

    def finalize_render(self, context, probe_index, nb_probes):
        pass

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_reflectance_probe(context, self.probe_volume)
        pass


class IrradianceProbeVolumeRenderer(ProbeVolumeRenderer):
    __current_render_filename = ""

    def init_json_data(self, context):
        translation_tupple = self.object_transform.translation.to_tuple()
        scale_tupple = self.object_transform.to_scale().to_tuple()
        rotation_euler = self.object_transform.to_euler()

        self.json_data = {
            "type": "pano",
            "probe_type": "irradiance",
            "name": self.probe_volume.name,
            "width": self.height * 2,
            "height": self.height,
            "position": [
                translation_tupple[0],
                translation_tupple[2],
                -translation_tupple[1],
            ],
            "scale": [scale_tupple[0], scale_tupple[2], scale_tupple[1]],
            "rotation": [rotation_euler.x, rotation_euler.z, -rotation_euler.y],
            "falloff": self.probe_volume.data.falloff,
            "resolution": [
                self.probe_volume.data.grid_resolution_x,
                self.probe_volume.data.grid_resolution_z,
                self.probe_volume.data.grid_resolution_y,
            ],
            "clip_start": self.probe_volume.data.clip_start,
            "clip_end": self.probe_volume.data.clip_end,
            "influence_distance": self.probe_volume.data.influence_distance,
            "files": [],
            "baked_objects": get_scene_renderered_object_names(context),
        }

    def setup_render_settings(self, context, probe_volume):
        settings = probe_volume.data.probes_export
        if settings.use_default_settings:
            self.samples_max = (
                context.scene.probes_export.irradiance_volume_default_samples_max
            )
            self.height = context.scene.probes_export.irradiance_volume_default_map_size
        else:
            self.samples_max = settings.samples_max
            self.height = settings.map_size

    def get_nb_probes(self, probe_volume):
        return (
            probe_volume.data.grid_resolution_x
            * probe_volume.data.grid_resolution_z
            * probe_volume.data.grid_resolution_y
        )

    def setup_render_batch(self, context, operator, probe_volume):
        for ob in context.scene.objects:
            if ob.type == "MESH":
                ob.hide_render = not ob.probes_render.render_by_irradiance_probes

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

        print(probe_index, rx, ry, rz)

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

        set_pano_render_settings(
            context,
            self.camera,
            final_file_path,
            samples_max=self.samples_max,
            height=self.height,
        )

        pass

    def finalize_render(self, context, probe_index, nb_probes):
        self.json_data["files"].append(self.__current_render_filename)
        pass

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_irradiance_probe(context, self.probe_volume)
        pass


class DefaultProbeVolumeRenderer(ProbeVolumeRenderer):
    __current_render_filename = ""

    def init_json_data(self, context):
        props = context.scene.probes_export

        self.json_data = {
            "name": self.probe_volume.name,
            "type": "global",
            "position": [
                self.object_transform.translation.x,
                self.object_transform.translation.z,
                -self.object_transform.translation.y,
            ],
            "clip_start": self.probe_volume.data.clip_start,
            "clip_end": self.probe_volume.data.clip_end,
            "data": {
                "map_size": props.global_map_size,
                "samples_max": props.global_samples_max,
                "irradiance_export_map_size": props.global_irradiance_export_map_size,
                "irradiance_max_texture_size": props.global_irradiance_max_texture_size,
                "reflectance_export_map_size": props.global_reflectance_export_map_size,
                "reflectance_max_texture_size": props.global_reflectance_max_texture_size,
                "reflectance_nb_levels": props.global_reflectance_nb_levels,
                "reflectance_start_roughness": props.global_reflectance_start_roughness,
                "reflectance_level_roughness": props.global_reflectance_level_roughness,
            },
            "file": global_pano_filename(self.probe_volume.name, self.file_extension),
            "baked_objects": get_scene_renderered_object_names(context),
        }

    def setup_render_settings(self, context, probe_volume):
        props = context.scene.probes_export
        self.samples_max = props.global_samples_max
        self.height = props.global_map_size

    def setup_render_batch(self, context, operator, probe_volume):
        self.nb_probes = 1

        for ob in context.scene.objects:
            if ob.type == "MESH":
                ob.hide_render = not ob.probes_render.render_by_global_probe

        return super().setup_render_batch(context, operator, probe_volume)

    def setup_render(self, context, probe_index, nb_probes):
        # res= super().setup_render(context, probe_index, nb_probes)
        filepath = global_pano_file(
            self.export_directory, self.probe_volume.name, self.file_extension
        )

        self.camera.location = self.object_transform.translation
        self.camera.rotation_euler.x = pi / 2


        set_pano_render_settings(
            context,
            self.camera,
            filepath,
            samples_max=self.samples_max,
            height=self.height,
        )

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_global_probe(context, self.probe_volume)
        pass
