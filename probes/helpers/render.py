from math import floor, pi

from ..compositing.global_probe import pack_global_probe

from ..compositing.reflectance import pack_reflectance_probe
from ..compositing.irradiance import pack_irradiance_probe

from .files import (
    get_or_create_render_cache_subdirectory,
    irradiance_filename,
    pano_filename,
    save_probe_json_render_data,
    save_global_probe_json_render_data,
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
    nb_probes = 0

    def get_json_data(self):
        return self.json_data

    def get_probe(self):
        return self.probe_volume

    def get_nb_probes(self):
        return self.nb_probes

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
        self.nb_probes = 0

    def setup_render_settings(self, context, probe_volume):
        
        pass

    def setup_render_batch(self, context, operator, probe_volume):
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
            self.height = context.scene.probes_export.reflection_cubemap_default_map_size
        else:
            self.samples_max = settings.samples_max
            self.height = settings.map_size

    def setup_render(self, context, probe_index, nb_probes):
        export_directory = context.scene.probes_export.export_directory_path

        self.camera.location = self.object_transform.translation
        self.camera.rotation_euler = self.object_transform.to_euler()
        self.camera.rotation_euler.x += pi / 2

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
        self.nb_probes = 1
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

    def setup_render_batch(self, context, operator, probe_volume):
        self.nb_probes = (
            probe_volume.data.grid_resolution_x
            * probe_volume.data.grid_resolution_z
            * probe_volume.data.grid_resolution_y
        )

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

        set_pano_render_settings(
            context, self.camera, filepath, samples_max=self.samples_max, height=self.height
        )

    def finalize_render_batch(self, context, operator):
        super().finalize_render_batch(context, operator)
        pack_global_probe(context, self.probe_volume)
        pass



def update_objects_settings_for_irradiance(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = not ob.probes_render.render_by_irradiance_probes


def update_objects_settings_for_reflection(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = not ob.probes_render.render_by_reflection_probes


def update_objects_settings_for_global(context):
    for ob in context.scene.objects:
        if ob.type == "MESH":
            ob.hide_render = not ob.probes_render.render_by_global_probe


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


# render panorama probe for global as hdr_pano
def render_pano_global_probe(context, operator, object, progress_min=0, progress_max=1):
    prob_object = object
    prob = prob_object.data
    props = context.scene.probes_export

    transform: Matrix = prob_object.matrix_world

    camera = create_pano_camera(context)
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)
    samples_max = props.global_samples_max
    height = props.global_map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    result_data = {
        "name": prob_object.name,
        "type": "global",
        "position": [
            transform.translation.x,
            transform.translation.z,
            -transform.translation.y,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
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
    }

    try:
        camera.location = transform.translation
        camera.rotation_euler = transform.to_euler()
        camera.rotation_euler.x += pi / 2
        camera.data.clip_start = prob.clip_start
        camera.data.clip_end = prob.clip_end

        filepath = global_pano_file(export_directory, prob_object.name, file_extension)
        result_data["file"] = global_pano_filename(prob_object.name, file_extension)

        print_render_progress("Baking global probe ", progress_min, progress_max, 0)

        set_pano_render_settings(
            context, camera, filepath, samples_max=samples_max, height=height
        )
        update_collection_visibility_for_probe(
            context.scene.collection.children, prob_object.data
        )

        bpy.ops.render.render(write_still=True)

    except Exception as e:
        catched_exception = e

    names = get_scene_renderered_object_names(context)
    result_data["baked_objects"] = names
    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    save_global_probe_json_render_data(export_directory, prob_object.name, result_data)

    return result_data


# render panorama probe for reflection
def render_pano_reflection_probe(
    context, operator, object, progress_min=0, progress_max=1
):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world

    camera = create_pano_camera(context)
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    get_or_create_render_cache_subdirectory(export_directory, prob_object.name)

    result_data = {
        "type": "pano",
        "position": [
            transform.translation.x,
            transform.translation.z,
            -transform.translation.y,
        ],
        "scale": transform.to_scale().to_tuple(),
        "rotation": [0, 0, 0],
        "falloff": prob_object.data.falloff,
        "intensity": prob.intensity,
        "influence_type": prob.influence_type,
        "influence_distance": prob.influence_distance,
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "probe_type": "reflection",
        "name": object.name,
        "width": height * 2,
        "height": height,
    }

    try:
        camera.location = transform.translation
        camera.rotation_euler = transform.to_euler()
        # camera.scale = transform.to_scale()
        max_scale = max(camera.scale.x, camera.scale.y, camera.scale.z)
        camera.rotation_euler.x += pi / 2
        camera.data.clip_start = prob.clip_start
        camera.data.clip_end = prob.clip_end

        # get current file path
        # filename = pano_file(export_directory, prob_object.name)
        filepath = pano_file(export_directory, prob_object.name, file_extension)
        result_data["file"] = pano_filename(file_extension)

        print_render_progress(
            "Baking probe " + object.name, progress_min, progress_max, 0
        )

        set_pano_render_settings(
            context, camera, filepath, samples_max=samples_max, height=height
        )
        update_collection_visibility_for_probe(
            context.scene.collection.children, prob_object.data
        )
        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

        names = get_scene_renderered_object_names(context)
        result_data["baked_objects"] = names
        save_probe_json_render_data(export_directory, prob_object.name, result_data)

    except Exception as e:
        catched_exception = e

    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data


# def save_pano_reflection_probe_render(context, prob_object, json_data):
#     export_directory = context.scene.probes_export.export_directory_path
#     save_probe_json_render_data(export_directory, prob_object.name, json_data)


def setup_pano_reflection_probe_render(
    context,
    operator,
    prob_object,
    shot_index,
    samples_max,
    height,
    final_export_directory,
    object_transform,
    camera,
    file_extension,
    json_data,
):
    export_directory = context.scene.probes_export.export_directory_path

    camera.location = object_transform.translation
    camera.rotation_euler = object_transform.to_euler()
    camera.rotation_euler.x += pi / 2

    # get current file path
    filepath = pano_file(export_directory, prob_object.name, file_extension)

    set_pano_render_settings(
        context, camera, filepath, samples_max=samples_max, height=height
    )

    return json_data


def setup_pano_reflection_probe_render_batch(context, operator, object):
    probe_object = object
    probe_data = probe_object.data
    settings = probe_data.probes_export
    file_extension = get_export_extension(context)

    object_transform: Matrix = probe_object.matrix_world

    camera = create_pano_camera(context)
    camera.data.clip_start = probe_data.clip_start
    camera.data.clip_end = probe_data.clip_end

    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return None

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    final_export_directory = get_or_create_render_cache_subdirectory(
        export_directory, probe_object.name
    )

    json_data = {
        "type": "pano",
        "position": [
            object_transform.translation.x,
            object_transform.translation.z,
            -object_transform.translation.y,
        ],
        "file": pano_filename(file_extension),
        "baked_objects": get_scene_renderered_object_names(context),
        "scale": object_transform.to_scale().to_tuple(),
        "rotation": [0, 0, 0],
        "falloff": probe_object.data.falloff,
        "intensity": probe_data.intensity,
        "influence_type": probe_data.influence_type,
        "influence_distance": probe_data.influence_distance,
        "clip_start": probe_data.clip_start,
        "clip_end": probe_data.clip_end,
        "probe_type": "reflection",
        "name": object.name,
        "width": height * 2,
        "height": height,
    }

    nb_panos = 1
    return [
        nb_panos,
        samples_max,
        height,
        final_export_directory,
        object_transform,
        camera,
        file_extension,
        json_data,
    ]


def render_cubemap_reflection_probe(
    context, operator, object, progress_min=0, progress_max=1
):
    prob_object = object
    prob = prob_object.data
    settings = prob.probes_export

    transform: Matrix = prob_object.matrix_world
    radius = prob_object.data.influence_distance

    camera = create_cube_camera(context)
    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.reflection_cubemap_default_samples_max
        height = context.scene.probes_export.reflection_cubemap_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    catched_exception = None

    final_export_directory = get_or_create_render_cache_subdirectory(
        export_directory, prob_object.name
    )

    print_render_progress(
        "Baking cubemap probe " + prob_object.name, progress_min, progress_max
    )

    result_data = {
        "type": "cubemap",
        "radius": radius,
        "position": [
            transform.translation.x,
            transform.translation.z,
            -transform.translation.y,
        ],
        "scale": transform.to_scale().to_tuple(),
        "rotation": [0, 0, 0],
        "falloff": prob.falloff,
        "intensity": prob.intensity,
        "resolution": [
            prob.grid_resolution_x,
            prob.grid_resolution_y,
            prob.grid_resolution_z,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "probe_type": "reflection",
        "name": object.name,
        "size": height,
        "faces_files": [],
    }

    try:
        camera.location = transform.translation
        max_scale = max(camera.scale.x, camera.scale.y, camera.scale.z)
        camera.data.clip_start = prob.clip_start
        camera.data.clip_end = prob.clip_end
        for i in range(6):
            filename = cubemap_filename(i, file_extension)
            final_file_path = final_export_directory + "/" + filename

            print_render_progress(
                "-- Baking face " + cube_map_face_names[i],
                progress_min,
                progress_max,
                i / 6,
            )
            camera.rotation_euler = cube_map_euler_rotations[i]

            set_cube_render_settings(
                context, camera, final_file_path, samples_max=samples_max, size=height
            )
            update_collection_visibility_for_probe(
                context.scene.collection.children, prob_object.data
            )
            bpy.ops.render.render(write_still=True)

            result_data["faces_files"].append(filename)
        names = get_scene_renderered_object_names(context)
        result_data["baked_objects"] = names
        save_probe_json_render_data(export_directory, prob_object.name, result_data)

    except Exception as e:
        catched_exception = e

    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data


def setup_pano_irradiance_probe_render_batch(context, operator, object):
    prob = object.data
    settings = prob.probes_export

    camera = create_pano_camera(context)
    camera.rotation_euler.x = pi / 2
    camera.data.clip_end = prob.clip_end
    camera.data.clip_start = prob.clip_start

    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.irradiance_volume_default_samples_max
        height = context.scene.probes_export.irradiance_volume_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"ERROR"}, "No directory defined")
        return None

    if os.path.exists(export_directory) == False:
        raise Exception("Directory does not exist")

    final_export_directory = get_or_create_render_cache_subdirectory(
        export_directory, object.name
    )

    object_transform: Matrix = object.matrix_world

    transform_list = []

    for r in object_transform.row:
        transform_list.append(r.x)
        transform_list.append(r.y)
        transform_list.append(r.z)
        transform_list.append(r.w)

    translation_tupple = object_transform.translation.to_tuple()
    scale_tupple = object_transform.to_scale().to_tuple()
    rotation_euler = object_transform.to_euler()

    json_data = {
        "type": "pano",
        "probe_type": "irradiance",
        "name": object.name,
        "width": height * 2,
        "height": height,
        "position": [
            translation_tupple[0],
            translation_tupple[2],
            -translation_tupple[1],
        ],
        "scale": [scale_tupple[0], scale_tupple[2], scale_tupple[1]],
        "rotation": [rotation_euler.x, rotation_euler.z, -rotation_euler.y],
        "falloff": prob.falloff,
        "resolution": [
            prob.grid_resolution_x,
            prob.grid_resolution_z,
            prob.grid_resolution_y,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "influence_distance": prob.influence_distance,
        "files": [],
    }

    resolution_x = prob.grid_resolution_x
    resolution_y = prob.grid_resolution_y
    resolution_z = prob.grid_resolution_z

    nb_panos = resolution_x * resolution_y * resolution_z

    return [
        nb_panos,
        samples_max,
        height,
        final_export_directory,
        object_transform,
        camera,
        file_extension,
        json_data,
    ]


def setup_pano_irradance_probe_render(
    context,
    operator,
    object,
    shot_index,
    samples_max,
    height,
    final_export_directory,
    object_transform,
    camera,
    file_extension,
    json_data,
):
    prob = object.data

    resolution_x = prob.grid_resolution_x
    resolution_y = prob.grid_resolution_y
    resolution_z = prob.grid_resolution_z

    resolution_y_z = resolution_y * resolution_z

    rx = floor(shot_index / resolution_y_z)
    ry = shot_index % resolution_y
    ry = resolution_y - ry - 1  # inverted y for openGL axis conversion
    rz = floor(shot_index / resolution_y) * resolution_z

    vz = (rz + 0.5) / resolution_z * 2 - 1
    vx = (rx + 0.5) / resolution_x * 2 - 1
    vy = (ry + 0.5) / resolution_y * 2 - 1

    filename = irradiance_filename(rx, ry, rz, file_extension)
    final_file_path = final_export_directory + "/" + filename

    res_vec = object_transform @ Vector((vx, vy, vz))

    camera.location = res_vec

    set_pano_render_settings(
        context,
        camera,
        final_file_path,
        samples_max=samples_max,
        height=height,
    )


# def save_pano_irradiance_probe_render(context, prob_object, json_data):
#     export_directory = context.scene.probes_export.export_directory_path
#     save_probe_json_render_data(export_directory, prob_object.name, json_data)


def render_pano_irradiance_probe(
    context, operator, object, progress_min=0, progress_max=1
):
    prob = object.data
    settings = prob.probes_export

    camera = create_pano_camera(context)
    camera.rotation_euler.x = pi / 2
    camera.data.clip_end = prob.clip_end
    camera.data.clip_start = prob.clip_start

    export_directory = context.scene.probes_export.export_directory_path
    file_extension = get_export_extension(context)

    if settings.use_default_settings:
        samples_max = context.scene.probes_export.irradiance_volume_default_samples_max
        height = context.scene.probes_export.irradiance_volume_default_map_size
    else:
        samples_max = settings.samples_max
        height = settings.map_size

    if export_directory == "":
        # warn user
        operator.report({"INFO"}, "No directory defined")
        return {"CANCELLED"}

    catched_exception = None

    final_export_directory = get_or_create_render_cache_subdirectory(
        export_directory, object.name
    )

    transform: Matrix = object.matrix_world

    transform_list = []

    for r in transform.row:
        transform_list.append(r.x)
        transform_list.append(r.y)
        transform_list.append(r.z)
        transform_list.append(r.w)

    translation_tupple = transform.translation.to_tuple()
    scale_tupple = transform.to_scale().to_tuple()
    rotation_euler = transform.to_euler()

    result_data = {
        "type": "pano",
        "probe_type": "irradiance",
        "name": object.name,
        "width": height * 2,
        "height": height,
        "position": [
            translation_tupple[0],
            translation_tupple[2],
            -translation_tupple[1],
        ],
        "scale": [scale_tupple[0], scale_tupple[2], scale_tupple[1]],
        "rotation": [rotation_euler.x, rotation_euler.z, -rotation_euler.y],
        "falloff": prob.falloff,
        "resolution": [
            prob.grid_resolution_x,
            prob.grid_resolution_z,
            prob.grid_resolution_y,
        ],
        "clip_start": prob.clip_start,
        "clip_end": prob.clip_end,
        "influence_distance": prob.influence_distance,
        "files": [],
    }

    try:
        if os.path.exists(export_directory) == False:
            raise Exception("Directory does not exist")

        resolution_x = prob.grid_resolution_x
        resolution_y = prob.grid_resolution_y
        resolution_z = prob.grid_resolution_z

        print_render_progress(
            "Baking probe " + object.name, progress_min, progress_max, 0
        )

        nb_panos = resolution_x * resolution_y * resolution_z

        # render each pano in opengl order (x -> x, y > -z, z -> -y)
        for rx in range(resolution_x):
            vx = (rx + 0.5) / resolution_x * 2 - 1

            for rz in range(resolution_z):
                vz = (rz + 0.5) / resolution_z * 2 - 1
                for rry in range(resolution_y):
                    ry = resolution_y - rry - 1
                    vy = (ry + 0.5) / resolution_y * 2 - 1
                    filename = irradiance_filename(rx, ry, rz, file_extension)
                    final_file_path = final_export_directory + "/" + filename

                    # print('-- Baking probe at ' + str(vx) + ', ' + str(vy) + ', ' + str(vz))
                    print_render_progress(
                        "-- rendering probe at "
                        + str(vx)
                        + ", "
                        + str(vy)
                        + ", "
                        + str(vz),
                        progress_min,
                        progress_max,
                        (rx * resolution_y * resolution_z + ry * resolution_z + rz)
                        / nb_panos,
                    )
                    res_vec = transform @ Vector((vx, vy, vz))

                    camera.location = res_vec

                    set_pano_render_settings(
                        context,
                        camera,
                        final_file_path,
                        samples_max=samples_max,
                        height=height,
                    )
                    update_collection_visibility_for_probe(
                        context.scene.collection.children, prob
                    )
                    # render image
                    bpy.ops.render.render(write_still=True)

                    result_data["files"].append(filename)
        names = get_scene_renderered_object_names(context)
        result_data["baked_objects"] = names
        save_probe_json_render_data(export_directory, object.name, result_data)

    except Exception as e:
        catched_exception = e

    reset_collection_visibility(context)
    context.scene.collection.objects.unlink(camera)

    if catched_exception != None:
        raise catched_exception

    return result_data
