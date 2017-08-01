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
            "prefer_vmd": True
        }
        json.dump(prefs, open(prefs_path, 'w'))
    else:
        # Load previously saved values
        prefs = json.load(open(prefs_path, 'r'))

    # Set user preferences according to those defaults.
    bpy.context.user_preferences.addons[__package__].preferences.vmd_exec_path = prefs["vmd_exec_path"]
    bpy.context.user_preferences.addons[__package__].preferences.pymol_exec_path = prefs["pymol_exec_path"]
    bpy.context.user_preferences.addons[__package__].preferences.prefer_vmd = prefs["prefer_vmd"]

    return prefs

def save_preferences_to_file():
    prefs = {
        "vmd_exec_path": bpy.context.user_preferences.addons[__package__].preferences.vmd_exec_path,
        "pymol_exec_path": bpy.context.user_preferences.addons[__package__].preferences.pymol_exec_path,
        "prefer_vmd": bpy.context.user_preferences.addons[__package__].preferences.prefer_vmd
    }
    json.dump(prefs, open(prefs_path, 'w'))
    


