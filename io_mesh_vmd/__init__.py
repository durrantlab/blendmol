# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#
#
#  Authors           : Clemens Barth (Blendphys@root-1.de), ...
#
#  Homepage(Wiki)    : http://development.root-1.de/Atomic_Blender.php
#
#  Start of project              : 2011-08-31 by Clemens Barth
#  First publication in Blender  : 2011-11-11
#  Last modified                 : 2014-08-19
#
#  Acknowledgements
#  ================
#  Blender: ideasman, meta_androcto, truman, kilon, CoDEmanX, dairin0d, PKHG,
#           Valter, ...
#  Other  : Frank Palmino
#
#

bl_info = {
    "name": "Molecules In Blender - PDB/VMD/PyMol",
    "description": "Importing PDB and State Files from VMD and PyMol",
    "author": "Jacob Durrant",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "File -> Import -> PDB/VMD/PyMol (*.pdb, *.vmd, *.???)",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}


import tempfile
import os
import urllib.request
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        IntProperty,
        FloatProperty,
        )

# from . import import_pdb
from .vmd import VMD
from . import preferences
from . import file_based_preferences

# -----------------------------------------------------------------------------
#                                                                           GUI

# This is the class for the file dialog of the importer.
class ImportVMD(Operator, ImportHelper):
    bl_idname = "import_mesh.vmd_pymol"
    bl_label  = "PDB/VMD/PyMol (*.pdb, *.vmd, *.???)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".pdb"
    filter_glob  = StringProperty(
        default="*.pdb;*.vmd;*.tcl", 
        options={'HIDDEN'},
    )

    protein_surface = BoolProperty(
        name = "Surface", default=True,
        description = "Protein surface representation?")
    protein_ribbon = BoolProperty(
        name = "Ribbon", default=True,
        description = "Protein ribbon representation?")
    protein_sticks = BoolProperty(
        name = "Sticks", default=False,
        description = "Protein stick representation?")
    protein_balls = BoolProperty(
        name = "Balls", default=False,
        description = "Protein ball representation?")
    protein_vdw = BoolProperty(
        name = "VDW Spheres", default=False,
        description = "Protein van-der-Waals representation?")

    ligand_surface = BoolProperty(
        name = "Surface", default=False,
        description = "Small-Molecule surface representation?")
    ligand_sticks = BoolProperty(
        name = "Sticks", default=True,
        description = "Small-Molecule stick representation?")
    ligand_balls = BoolProperty(
        name = "Balls", default=False,
        description = "Small-Molecule ball representation?")
    ligand_vdw = BoolProperty(
        name = "VDW Spheres", default=False,
        description = "Small-Molecule van-der-Waals representation?")

    near_ligand_surface = BoolProperty(
        name = "Surface", default=False,
        description = "Interacting-residues surface representation?")
    near_ligand_sticks = BoolProperty(
        name = "Sticks", default=True,
        description = "Interacting-residues stick representation?")
    near_ligand_balls = BoolProperty(
        name = "Balls", default=False,
        description = "Interacting-residues ball representation?")
    near_ligand_vdw = BoolProperty(
        name = "VDW Spheres", default=False,
        description = "Interacting-residues van-der-Waals representation?")

    metals_vdw = BoolProperty(
        name = "VDW Spheres", default=True,
        description = "Metals van-der-Waals representation?")

    remove_doubles = BoolProperty(
        name = "Remove Doubles", default=True,
        description = "Remove duplicate vertices from the meshes?")
    nanometers = BoolProperty(
        name = "Use nm, not Å?", default=True,
        description = "Use units of nanometers instead of the default Angstroms?")

    vmd_exec_path = StringProperty(
        name = "VMD",
        default = "/PATH/TO/VMD/EXECUTABLE", 
        # default = bpy.context.user_preferences.addons[__name__].preferences.vmd_exec_path,
        description = "The full path to the VMD executable file.",
        # subtype="FILE_PATH"
    )
    pymol_exec_path = StringProperty(
        name = "PyMol",
        default = "/PATH/TO/PYMOL/EXECUTABLE", 
        description = "The full path to the PyMol executable file.",
        # subtype="FILE_PATH"
    )

    prefer_vmd = BoolProperty(
        name = "Prefer VMD", 
        default=True,
        description = "Use VMD when loading PDB files. Determine based on extension otherwise.")

    user_vmd_msms_representation = BoolProperty(
        name = "Use MSMS for Surfaces", 
        default=False,
        description = "Use MSMS to render surfaces in VMD. Note that VMD doesn't include MSMS by default.")

    first_draw = True

    def startup(self):
        prefs = file_based_preferences.load_preferences_from_file()

        # Set the preferences 
        self.vmd_exec_path = bpy.context.user_preferences.addons[__name__].preferences.vmd_exec_path
        self.pymol_exec_path = bpy.context.user_preferences.addons[__name__].preferences.pymol_exec_path
        self.prefer_vmd = bpy.context.user_preferences.addons[__name__].preferences.prefer_vmd
        self.user_vmd_msms_representation = bpy.context.user_preferences.addons[__name__].preferences.user_vmd_msms_representation        

    def draw(self, context):
        layout = self.layout

        if self.first_draw:
            self.first_draw = False
            self.startup()

        # How to represent proteins
        protein_box = layout.box()
        first_row = protein_box.row()
        first_row.label(text="Protein from PDBs")
        second_row = protein_box.row()
        left_col = second_row.column()
        left_col.prop(self, "protein_surface")
        left_col.prop(self, "protein_ribbon")
        left_col.prop(self, "protein_sticks")
        right_col = second_row.column(align=True)
        right_col.prop(self, "protein_balls")
        right_col.prop(self, "protein_vdw")

        # How to represent small molecules
        molecule_box = layout.box()
        first_row = molecule_box.row()
        first_row.label(text="Small Molecules from PDBs")
        second_row = molecule_box.row()
        left_col = second_row.column()
        left_col.prop(self, "ligand_surface")
        left_col.prop(self, "ligand_sticks")
        right_col = second_row.column(align=True)
        right_col.prop(self, "ligand_balls")
        right_col.prop(self, "ligand_vdw")

        # How to represent interacting residues
        molecule_box = layout.box()
        first_row = molecule_box.row()
        first_row.label(text="Interacting Residues from PDBs")
        second_row = molecule_box.row()
        left_col = second_row.column()
        left_col.prop(self, "near_ligand_surface")
        left_col.prop(self, "near_ligand_sticks")
        right_col = second_row.column(align=True)
        right_col.prop(self, "near_ligand_balls")
        right_col.prop(self, "near_ligand_vdw")

        # Metals
        molecule_box = layout.box()
        first_row = molecule_box.row()
        first_row.label(text="Metals")
        second_row = molecule_box.row()
        second_row.prop(self, "metals_vdw")

        # Settings
        molecule_box = layout.box()
        first_row = molecule_box.row()
        first_row.label(text="Import Settings")
        second_row = molecule_box.row()
        left_col = second_row.column()
        left_col.prop(self, "remove_doubles")
        left_col.prop(self, "nanometers")

        # Executable files
        exec_box = layout.box()
        first_row = exec_box.row()
        first_row.label(text="VMD-Specific Settings")
        second_row = exec_box.row()
        second_row.prop(self, "vmd_exec_path")
        third_row = exec_box.row()
        left_col = third_row.column()
        left_col.prop(self, "prefer_vmd")
        left_col.prop(self, "user_vmd_msms_representation")

        exec_box = layout.box()
        first_row = exec_box.row()
        first_row.label(text="PyMol-Specific Settings")
        second_row = exec_box.row()
        second_row.prop(self, "pymol_exec_path")

    def execute(self, context):
        # self.report({"WARNING"}, "WARNING: This could take a bit...")

        # Save changes to user preferences
        bpy.context.user_preferences.addons[__name__].preferences.vmd_exec_path = self.vmd_exec_path
        bpy.context.user_preferences.addons[__name__].preferences.pymol_exec_path = self.pymol_exec_path
        bpy.context.user_preferences.addons[__name__].preferences.prefer_vmd = self.prefer_vmd
        bpy.context.user_preferences.addons[__name__].preferences.user_vmd_msms_representation = self.user_vmd_msms_representation
        file_based_preferences.save_preferences_to_file()

        # If its a 4-letter code without a period in it, assume it's a PDB ID
        possible_pdb_id = os.path.basename(self.filepath).upper()
        orig_path = None
        if len(possible_pdb_id) == 4 and not "." in possible_pdb_id:
            _, pdb_filename = tempfile.mkstemp(suffix='.pdb')
            with urllib.request.urlopen("https://files.rcsb.org/view/" + possible_pdb_id + ".pdb") as response:
                open(pdb_filename, 'wb').write(response.read())
                orig_path = self.filepath
                self.filepath = pdb_filename

        # This is in order to solve this strange 'relative path' thing.
        filepath_input = bpy.path.abspath(self.filepath)

        # First, verify that file exists
        if not os.path.exists(self.filepath):
            self.report({"ERROR"}, os.path.basename(self.filepath) + " does not exist!")
            return {'CANCELLED'}

        # If no good executable specified, throw an error.
        vmd_exec_path = self.vmd_exec_path #.decode('string_escape')
        pymol_exec_path = self.pymol_exec_path #.decode('string_escape')

        vmd_path_exists = os.path.exists(vmd_exec_path)
        pymol_path_exists = os.path.exists(pymol_exec_path)
        if not vmd_path_exists and not pymol_path_exists:
            self.report({"ERROR"}, "Neither the VMD nor the PyMol executable paths exist!")
            return {'CANCELLED'}

        # Determine which executable to use (VMD vs. PyMol).
        _, ext = os.path.splitext(filepath_input)
        ext = ext.upper()
        exec_to_use = "VMD"
        if ext == ".PDB":
            # Pymol or VMD can load PDB
            if vmd_path_exists and pymol_path_exists:
                if self.prefer_vmd: exec_to_use = "VMD"
                else: exec_to_use = "PYMOL"
            elif vmd_path_exists: exec_to_use = "VMD"
            elif pymol_path_exists: exec_to_use = "PYMOL"
        elif ext in [".VMD", ".TCL"]:
            # VMD files
            if vmd_path_exists:
                exec_to_use = "VMD"
            else:
                self.report({"ERROR"}, "Only VMD can load files of type \"" + ext.lower() + "\", but the specified VMD path does not exist.")
                return {'CANCELLED'}
        else: 
            # PyMol files
            if pymol_path_exists:
                exec_to_use = "PYMOL"
            else:
                self.report({"ERROR"}, "Only PyMol can load files of type \"" + ext.lower() + "\", but the specified PyMol path does not exist.")
                return {'CANCELLED'}

        tmp_dir = tempfile.mkdtemp() + os.sep
        script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + "scripts" + os.sep
        if exec_to_use == "VMD":
            vmd = VMD()
            vmd.make_tmp_dir()
            # vmd.populate_tmp_dir(filepath_input)
            vmd.make_vis_script(self)
            vmd.run_external_program(vmd_exec_path)
            new_obj_names = vmd.import_all_objs(self)
            vmd.del_tmp_dir()

            #
            for obj_name in new_obj_names:
                print(obj_name)
                # Here process meshes to make better.

        if orig_path is not None:
            self.filepath = orig_path

        return {'FINISHED'}


# The entry into the menu 'file -> import'
def menu_func_import(self, context):
    self.layout.operator(ImportVMD.bl_idname, text="PDB/VMD/PyMol (*.pdb, *.vmd, *.???)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    preferences.register()

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    preferences.unregister()

if __name__ == "__main__":
    register()
