import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator

from ..helpers import get_export_extension

class BAKE_GI_OP_set_probes_directory(Operator, ExportHelper):

    bl_idname = "bake_gi.set_probes_directory"
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
        
        context.scene.bake_gi.export_directory_path = self.directory
        
        return {'FINISHED'}