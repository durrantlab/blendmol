import bpy
import os
import json

"""
This module includes functions for saving and loading user preferences to the
disk.
"""

prefs_path = (
    bpy.utils.user_resource("CONFIG") + os.sep +
    "vmd_import_config.json"
)

def load_preferences_from_file():
    """
    Load the user preferences from a file.

    :returns: The loaded user preferences.
    :rtype: :class:`???`
    """
    
    # Get the preferences
    if not os.path.exists(prefs_path):
        # Never saved before, so go with defaults.
        prefs = {
            "vmd_exec_path": "/PATH/TO/VMD/EXECUTABLE",
            "pymol_exec_path": "/PATH/TO/PYMOL/EXECUTABLE",
            "prefer_vmd": True,
            "vmd_msms_repr": False
        }
        json.dump(prefs, open(prefs_path, 'w'))
    else:
        # Load previously saved values
        prefs = json.load(open(prefs_path, 'r'))

        if not "vmd_exec_path" in prefs.keys():
            prefs["vmd_exec_path"] = "/PATH/TO/VMD/EXECUTABLE"
        if not "pymol_exec_path" in prefs.keys():
            prefs["pymol_exec_path"] = "/PATH/TO/PYMOL/EXECUTABLE"
        if not "prefer_vmd" in prefs.keys():
            prefs["prefer_vmd"] = True
        if not "vmd_msms_repr" in prefs.keys():
            prefs["vmd_msms_repr"] = False

    # Set user preferences according to those defaults.
    addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
    addon_prefs.vmd_exec_path = prefs["vmd_exec_path"]
    addon_prefs.pymol_exec_path = prefs["pymol_exec_path"]
    addon_prefs.prefer_vmd = prefs["prefer_vmd"]
    addon_prefs.vmd_msms_repr = prefs["vmd_msms_repr"]

    return prefs

def save_preferences_to_file():
    """
    Save the user preferences to the disk.
    """

    addon_prefs = bpy.context.user_preferences.addons[__package__].preferences
    prefs = {
        "vmd_exec_path": addon_prefs.vmd_exec_path,
        "pymol_exec_path": addon_prefs.pymol_exec_path,
        "prefer_vmd": addon_prefs.prefer_vmd,
        "vmd_msms_repr": addon_prefs.vmd_msms_repr
    }
    json.dump(prefs, open(prefs_path, 'w'))
    

