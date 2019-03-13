"""
BlendMol 1.0.0: Advanced Molecular Visualization in Blender. Copyright (C)
2018 Jacob D. Durrant

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

#
#  Authors           : Jacob Durrant (durrantj@pitt.edu).
#
#  Homepage          : http://durrantlab.com
#

bl_info = {
    "name": "BlendMol 1.0.0 - PDB/VMD/PyMol",
    "description": "Import PDB (.pdb), VMD state files (.vmd), and PyMol session files (.pse)",
    "author": "Jacob Durrant",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": ("File -> Import -> PDB/VMD/PyMol (.pdb, .vmd, .tcl, "
                 ".pse)"),
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import tempfile
import os
import urllib.request
from pathlib import Path  # For Windows Paths: Converts / to \.
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

from .VMD import VMD
from .PyMol import PyMol
from . import Preferences
from . import FileBasedPreferences

class ImportVMD(Operator, ImportHelper):
    """
    Class for the importer file dialog.
    """

    bl_idname = "import_mesh.vmd_pymol"
    bl_label  = "Import PDB/VMD/TCL/PSE"
    bl_options = {'PRESET', 'UNDO'}

    # Define plugin variables

    filename_ext = ".pdb"
    filter_glob: StringProperty(
        default="*.pdb;*.vmd;*.tcl;*.pse", 
        options={'HIDDEN'},
    )

    protein_surface: BoolProperty(
        name = "Surface", default=True,
        description = "Protein surface representation?")
    protein_ribbon: BoolProperty(
        name = "Ribbon", default=True,
        description = "Protein ribbon representation?")
    protein_sticks: BoolProperty(
        name = "Sticks", default=False,
        description = "Protein stick representation?")
    protein_balls: BoolProperty(
        name = "Balls", default=False,
        description = "Protein ball representation?")
    protein_vdw: BoolProperty(
        name = "VDW Spheres", default=False,
        description = "Protein van-der-Waals representation?")

    ligand_surface: BoolProperty(
        name = "Surface", default=False,
        description = "Small-Molecule surface representation?")
    ligand_sticks: BoolProperty(
        name = "Sticks", default=True,
        description = "Small-Molecule stick representation?")
    ligand_balls: BoolProperty(
        name = "Balls", default=False,
        description = "Small-Molecule ball representation?")
    ligand_vdw: BoolProperty(
        name = "VDW Spheres", default=False,
        description = "Small-Molecule van-der-Waals representation?")

    near_ligand_surface: BoolProperty(
        name = "Surface", default=False,
        description = "Interacting-residues surface representation?")
    near_ligand_sticks: BoolProperty(
        name = "Sticks", default=True,
        description = "Interacting-residues stick representation?")
    near_ligand_balls: BoolProperty(
        name = "Balls", default=False,
        description = "Interacting-residues ball representation?")
    near_ligand_vdw: BoolProperty(
        name = "VDW Spheres", default=False,
        description = "Interacting-residues van-der-Waals representation?")

    metals_vdw: BoolProperty(
        name = "VDW Spheres", default=True,
        description = "Metals van-der-Waals representation?")

    remove_doubles: BoolProperty(
        name = "Remove Doubles", default=False,
        description = "Remove duplicate vertices from the meshes?")
    nanometers: BoolProperty(
        name = "Use nm, not Å?", default=True,
        
        description = ("Use units of nanometers instead of the default "
                       "Angstroms?")
    )

    vmd_exec_path: StringProperty(
        name = "VMD",
        #default = str(Path("/PATH/TO/VMD/EXECUTABLE")), 
        default = str(Path("/usr/local/bin/vmd")),
        description = "The full path to the VMD executable file.",
    )
    pymol_exec_path: StringProperty(
        name = "PyMol",
        default = str(Path("/usr/bin/pymol")), 
        description = "The full path to the PyMol executable file.",
    )

    prefer_vmd: BoolProperty(
        name = "Prefer VMD Over PyMol for PDB", 
        default=True,
        description = ("Use VMD when loading PDB files, not PyMol. For other "
                       "files, the program will be determined by the file "
                       "extension.")
    )

    vmd_msms_repr: BoolProperty(
        name = "Use MSMS for Surfaces", 
        default=False,
        description = ("Use MSMS to render surfaces in VMD. Note that VMD "
                       "doesn't include MSMS by default.")
    )

    first_draw = True

    def startup(self):
        """
        Sets initial user preferences, loading from a file if necessary.
        """

        #prefs = FileBasedPreferences.load_preferences_from_file()

        # Set the preferences
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        if addon_prefs:
            self.vmd_exec_path = addon_prefs.vmd_exec_path
            self.vmd_exec_path = "/usr/local/bin/vmd"
            self.pymol_exec_path = addon_prefs.pymol_exec_path
            self.prefer_vmd = addon_prefs.prefer_vmd
            self.vmd_msms_repr = addon_prefs.vmd_msms_repr
        #self.vmd_exec_path = prefs["vmd_exec_path"]
        #self.pymol_exec_path = prefs["pymol_exec_path"]
        #self.prefer_vmd = prefs["prefer_vmd"]
        #self.vmd_msms_repr = prefs["vmd_msms_repr"]

    def add_instruction_line(self, row, text, height=0.6):
        """
        Adds a line to the instruction paragraph (user interface, UI).
    
        :param ??? row: The UI row.
        :param str text: The text to add.
        :param float height: The line height. Defaults to 0.6.
        """

        row.scale_y = height
        row.label(text=text)

    def draw(self, context):
        """
        Layout (draw) the user interface in the appropriate import dialog.

        :param ??? context: The context.
        """

        layout = self.layout

        # If it's the first draw, also set the user preferences.
        if self.first_draw:
            self.first_draw = False
            self.startup()

        # Intro message
        intro_box = layout.box()
        first_row = intro_box.row()
        first_row.label(text="Notes on usage below...")
        
        # How to represent proteins
        protein_box = layout.box()
        first_row = protein_box.row()
        first_row.label(text="Protein/Nucleic from PDBs")
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
        left_col.prop(self, "vmd_msms_repr")

        exec_box = layout.box()
        first_row = exec_box.row()
        first_row.label(text="PyMol-Specific Settings")
        second_row = exec_box.row()
        second_row.prop(self, "pymol_exec_path")

        # Instructions
        instruction_box = layout.box()
        self.add_instruction_line(instruction_box.row(), "Notes on Use")

        self.add_instruction_line(instruction_box.row(), "", 0.01)

        lines = [
            "Select files or type a 4-letter",
            "PDB ID to download."
        ]
        for line in lines:
            self.add_instruction_line(instruction_box.row(), line)

        self.add_instruction_line(instruction_box.row(), "", 0.01)

        lines = [
            "To create the meshes, you must",
            "specify the absolute (full)",
            "paths to the VMD and/or PyMol",
            "executables."
        ]
        for line in lines:
            self.add_instruction_line(instruction_box.row(), line)

        self.add_instruction_line(instruction_box.row(), "", 0.01)

        lines = [
            "Both VMD and PyMol can load PDB",
            'files. Check "Prefer VMD Over',
            'PyMol for PDB" to use VMD. For',
            'other files, the program will',
            'be determined by the file',
            'extension.'
        ]
        for line in lines:
            self.add_instruction_line(instruction_box.row(), line)

        self.add_instruction_line(instruction_box.row(), "", 0.01)

        lines = [
            "By default, VMD renders surfaces",
            "with the Surf representation.",
            'Check "Use MSMS for Surfaces" if',
            'you have installed the MSMS',
            'renderer.'
        ]
        for line in lines:
            self.add_instruction_line(instruction_box.row(), line)

        self.add_instruction_line(instruction_box.row(), "", 0.01)

        lines = [
            "It can take some time to create",
            "and load the meshes."
        ]
        for line in lines:
            self.add_instruction_line(instruction_box.row(), line)

    def execute(self, context):
        """
        Code to run when the user presses the import button. This gets the
        import process started.

        :param ??? context: The context.
        """

        # Save changes to user preferences
        user_prefs = bpy.context.preferences.addons[__package__].preferences
        
        user_prefs.vmd_exec_path = self.vmd_exec_path
        user_prefs.pymol_exec_path = self.pymol_exec_path
        user_prefs.prefer_vmd = self.prefer_vmd
        user_prefs.vmd_msms_repr = self.vmd_msms_repr
        FileBasedPreferences.save_preferences_to_file()

        # If its a 4-letter code without a period in it, assume it's a PDB ID
        pdb_id = os.path.basename(self.filepath).upper()
        orig_path = None
        if len(pdb_id) == 4 and not "." in pdb_id:
            _, pdb_filename = tempfile.mkstemp(suffix='.pdb')
            url = "https://files.rcsb.org/view/" + pdb_id + ".pdb"
            with urllib.request.urlopen(url) as response:
                open(pdb_filename, 'wb').write(response.read())
                orig_path = self.filepath
                self.filepath = pdb_filename

        # This is in order to solve this strange 'relative path' thing.
        filepath_input = bpy.path.abspath(self.filepath)

        # First, verify that file exists
        if not os.path.exists(self.filepath):
            self.report(
                {"ERROR"}, 
                os.path.basename(self.filepath) + " does not exist!"
            )
            return {'CANCELLED'}

        # If no good executable specified, throw an error.
        vmd_exec_path = self.vmd_exec_path
        pymol_exec_path = self.pymol_exec_path

        vmd_path_exists = os.path.exists(vmd_exec_path)
        pymol_path_exists = os.path.exists(pymol_exec_path)
        if not vmd_path_exists and not pymol_path_exists:
            self.report(
                {"ERROR"}, 
                "Neither the VMD nor the PyMol executable paths exist!"
            )
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
                self.report(
                    {"ERROR"}, 
                    (
                        'Only VMD can load files of type "' + ext.lower() +
                        '", but the specified VMD path does not exist.'
                    )
                )
                return {'CANCELLED'}
        else: 
            # PyMol files
            if pymol_path_exists:
                exec_to_use = "PYMOL"
            else:
                self.report(
                    {"ERROR"},
                    (
                        'Only PyMol can load files of type "' + ext.lower() +
                        '", but the specified PyMol path does not exist.'
                    )
                )
                return {'CANCELLED'}

        tmp_dir = tempfile.mkdtemp() + os.sep
        script_dir = (
            os.path.dirname(os.path.realpath(__file__)) +
            os.sep + "scripts" + os.sep
        )
        if exec_to_use == "VMD":
            vmd = VMD()
            vmd.make_tmp_dir()
            vmd.make_vis_script(self)
            vmd.run_external_program(vmd_exec_path)
            new_obj_names = vmd.import_all_mesh_files(self)
            vmd.del_tmp_dir()
        elif exec_to_use == "PYMOL":
            pymol = PyMol()

            pymol.make_tmp_dir()
            pymol.make_vis_script(self)
            pymol.run_external_program(pymol_exec_path)
            new_obj_names = pymol.import_all_mesh_files(self)
            pymol.del_tmp_dir()

        if orig_path is not None:
            self.filepath = orig_path

        return {'FINISHED'}

def add_menu_func_import(self, context):
    """
    Add BlendMol to the 'file -> import' menu.

    :param ??? context: The context.
    """

    self.layout.operator(
        ImportVMD.bl_idname, 
        text="PDB/VMD/PyMol (.pdb, .vmd, .tcl, .pse)"
    )

classes = (
    ImportVMD,
)

def register():
    """
    Register the plugin.
    """

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(add_menu_func_import)
    Preferences.register()


def unregister():
    """
    Unregister the plugin.
    """

    #bpy.utils.unregister_module(__name__)
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(add_menu_func_import)
    Preferences.unregister()

if __name__ == "__main__":
    register()
