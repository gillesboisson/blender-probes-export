import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator


class SetProbeExportDirectory(Operator, ExportHelper):

    bl_idname = "probes_export.set_export_directory"
    bl_label = "Set probes baking directory"
    
    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    filename_ext = ".jpg"

    directory: StringProperty()


    @classmethod
    def poll(cls, context):
        return True

    filepath: StringProperty()

    def execute(self, context):
        """Do something with the selected file(s)."""

        self.filepath = bpy.path.abspath(self.filepath)
        
        print('Selected file:', self.filepath)
        print('Selected directory:', self.directory)

        context.scene.probes_export.export_directory_path = self.directory
        
        return {'FINISHED'}