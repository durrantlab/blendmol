import bpy
import os
import json

prefs_path = bpy.utils.user_resource("CONFIG") + os.sep + "vmd_import_config.json"

def load_preferences_from_file():
    # The path to the preferences file
    
    # Get the preferences
    if not os.path.exists(prefs_path):
        # Never saved before, so go with defaults.
        prefs = {
            "vmd_exec_path": "/PATH/TO/VMD/EXECUTABLE",
            "pymol_exec_path": "/PATH/TO/PYMOL/EXECUTABLE",
            "prefer_vmd": True,
            "user_vmd_msms_representation": False
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
        if not "user_vmd_msms_representation" in prefs.keys():
            prefs["user_vmd_msms_representation"] = False

    # Set user preferences according to those defaults.
    bpy.context.user_preferences.addons[__package__].preferences.vmd_exec_path = prefs["vmd_exec_path"]
    bpy.context.user_preferences.addons[__package__].preferences.pymol_exec_path = prefs["pymol_exec_path"]
    bpy.context.user_preferences.addons[__package__].preferences.prefer_vmd = prefs["prefer_vmd"]
    bpy.context.user_preferences.addons[__package__].preferences.user_vmd_msms_representation = prefs["user_vmd_msms_representation"]

    return prefs

def save_preferences_to_file():
    prefs = {
        "vmd_exec_path": bpy.context.user_preferences.addons[__package__].preferences.vmd_exec_path,
        "pymol_exec_path": bpy.context.user_preferences.addons[__package__].preferences.pymol_exec_path,
        "prefer_vmd": bpy.context.user_preferences.addons[__package__].preferences.prefer_vmd,
        "user_vmd_msms_representation": bpy.context.user_preferences.addons[__package__].preferences.user_vmd_msms_representation
    }
    json.dump(prefs, open(prefs_path, 'w'))
    


