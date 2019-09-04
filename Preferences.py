"""
BlendMol 1.1: Advanced Molecular Visualization in Blender. Copyright (C)
2019 Jacob D. Durrant

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

bl_info = {
    "name": "BlendMol 1.1 Preferences",
    "author": "Jacob Durrant",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "SpaceBar Search -> BlendMol Preferences",
    "description": "Preferences for the BlendMol Plugin",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
from . import FileBasedPreferences

class ExternalProgramPreferences(AddonPreferences):
    """
    The plugin preference panel in the User Preferences window.
    """

    # This must match the addon name, use '__package__' when defining this in
    # a submodule of a python package.
    bl_idname = __package__

    # Define preferences variables

    vmd_exec_path: StringProperty(
        name = "VMD executable path",
        default = "/FULL/PATH/TO/VMD/EXECUTABLE",
        description = "The full path to the VMD executable file.",
        subtype="FILE_PATH"
    )

    pymol_exec_path: StringProperty(
        name = "PyMol executable path",
        default = "/FULL/PATH/TO/PYMOL/EXECUTABLE",
        description = "The full path to the PyMol executable file.",
        subtype="FILE_PATH"
    )

    prefer_vmd: BoolProperty(
        name = "Prefer VMD Over PyMol for PDB", default = True,
        description = ("Use VMD when loading PDB files, not PyMol. For other "
                       "files, the program will be determined by the file "
                       "extension.")
    )

    vmd_msms_repr: BoolProperty(
        name = "Use MSMS for Surfaces", default = False,

        description = (
            "Use MSMS to render surfaces in VMD. Note that VMD doesn't "
            "include MSMS by default."
        )
    )

    last_prefs: StringProperty(
        name = "last_prefs",
        default = "",
        options={'HIDDEN'}
    )

    def get_current_prefs_as_string(self):
        """
        The user preferences as a string.

        :returns: The parameters in a string.
        :rtype: :class:`str`
        """

        return (
            self.vmd_exec_path + " " + self.pymol_exec_path + " " +
            str(self.prefer_vmd) + " " + str(self.vmd_msms_repr)
        )

    def draw(self, context):
        """
        Draw the user interface in the User Preferences window.

        :param ??? context: The context.
        """
        # If the preferences have never been set, set them now.
        if self.last_prefs == "":
            FileBasedPreferences.load_preferences_from_file()
            self.last_prefs = self.get_current_prefs_as_string()

        layout = self.layout

        # Note that below can be identical to what's in __init__.py.
        exec_box = layout.box()
        first_row = exec_box.row()
        first_row.label(text="VMD-Specific Settings")
        second_row = exec_box.row()
        second_row.prop(self, "vmd_exec_path")
        third_row = exec_box.row()
        left_col = third_row.column()
        left_col.prop(self, "prefer_vmd")
        left_col.prop(self, "vmd_msms_repr")

        exec_box = layout.box()
        first_row = exec_box.row()
        first_row.label(text="PyMol-Specific Settings")
        second_row = exec_box.row()
        second_row.prop(self, "pymol_exec_path")

        new_prefs = self.get_current_prefs_as_string()

        # If the preferences have changed, save them to the disk.
        if new_prefs != self.last_prefs:
            # Prefs have changed
            FileBasedPreferences.save_preferences_to_file()
            self.last_prefs = new_prefs

classes=(
    ExternalProgramPreferences,
)
def register():
    """
    Register the plugin.
    """
    from bpy.utils import register_class
    try:
        for cls in classes:
            register_class(cls)
    except: pass

def unregister():
    """
    Unregister the plugin.
    """
    from bpy.utils import unregister_class
    try:
        for cls in reversed(classes):
            unregister_class(cls)
    except: pass
