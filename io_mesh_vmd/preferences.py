bl_info = {
    "name": "Molecules In Blender Preferences",
    "author": "Jacob Durrant",
    "version": (1, 0),
    "blender": (2, 79, 0),
    "location": "SpaceBar Search -> Molecules In Blender Preferences",
    "description": "Preferences for the Molecules In Blender Plugin",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
from . import FileBasedPreferences

class VMDAddonPreferences(AddonPreferences):
    """
    The plugin preference panel in the User Preferences window.
    """

    # This must match the addon name, use '__package__'
    # When defining this in a submodule of a python package.
    bl_idname = __package__

    vmd_exec_path = StringProperty(
        name = "VMD",
        default = "/PATH/TO/VMD/EXECUTABLE", 
        description = "The full path to the VMD executable file.",
        subtype="FILE_PATH"
    )

    pymol_exec_path = StringProperty(
        name = "PyMol",
        default = "/PATH/TO/PYMOL/EXECUTABLE", 
        description = "The full path to the PyMol executable file.",
        subtype="FILE_PATH"
    )

    prefer_vmd = BoolProperty(
        name = "Prefer VMD", default = True,
        
        description = (
            "Use VMD when loading PDB files. Determine based on "
            "extension otherwise."
        )        
    )

    vmd_msms_repr = BoolProperty(
        name = "Use MSMS for Surfaces", default = False,

        description = (
            "Use MSMS to render surfaces in VMD. Note that VMD doesn't "
            "include MSMS by default."
        )
    )

    last_prefs = StringProperty(
        name = "last_prefs",
        default = "",
        options={'HIDDEN'}
    )

    def current_prefs_as_string(self):
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

        if self.last_prefs == "":
            FileBasedPreferences.load_preferences_from_file()
            self.last_prefs = self.current_prefs_as_string()
        
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

        new_prefs = self.current_prefs_as_string()

        if new_prefs != self.last_prefs:
            # Prefs have changed
            FileBasedPreferences.save_preferences_to_file()
            self.last_prefs = new_prefs

def register():
    """
    Register the plugin.
    """

    try: bpy.utils.register_class(VMDAddonPreferences)
    except: pass

def unregister():
    """
    Unregister the plugin.
    """

    bpy.utils.unregister_class(VMDAddonPreferences)