bl_info = {
    "name": "Molecules In Blender Preferences",
    "author": "Jacob Durrant",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "SpaceBar Search -> Molecules In Blender Preferences",
    "description": "Preferences for the Molecules In Blender Plugin",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
from . import file_based_preferences


class VMDAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
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
        description = "Use VMD when loading PDB files. Determine based on extension otherwise.")

    last_prefs = StringProperty(
        name = "last_prefs",
        default = "",
        options={'HIDDEN'}
    )

    def current_prefs_as_string(self):
        return self.vmd_exec_path + " " + self.pymol_exec_path + " " + str(self.prefer_vmd)

    def draw(self, context):
        if self.last_prefs == "":
            file_based_preferences.load_preferences_from_file()
            self.last_prefs = self.current_prefs_as_string()
        
        layout = self.layout
        layout.label(text="Preferences for the Molecules In Blender plugin")
        layout.prop(self, "vmd_exec_path")
        layout.prop(self, "pymol_exec_path")
        layout.prop(self, "prefer_vmd")

        new_prefs = self.current_prefs_as_string()

        if new_prefs != self.last_prefs:
            # Prefs have changed
            file_based_preferences.save_preferences_to_file()
            self.last_prefs = new_prefs

# class OBJECT_OT_addon_prefs_vmd(Operator):
#     """Display example preferences"""
#     bl_idname = "object.addon_prefs_example"
#     bl_label = "Addon Preferences Example"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         user_preferences = context.user_preferences
#         print(user_preferences.addons)
#         import pdb; pdb.set_trace()
#         addon_prefs = user_preferences.addons[__package__].preferences

#         info = ("Path: %s, Number: %d, Boolean %r" %
#                 (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

#         self.report({'INFO'}, info)
#         print(info)

#         return {'FINISHED'}


# Registration
def register():
    # try: bpy.utils.register_class(OBJECT_OT_addon_prefs_vmd)
    # except: pass
    
    try: bpy.utils.register_class(VMDAddonPreferences)
    except: pass

def unregister():
    # bpy.utils.unregister_class(OBJECT_OT_addon_prefs_vmd)
    bpy.utils.unregister_class(VMDAddonPreferences)