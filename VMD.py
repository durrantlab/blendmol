"""
BlendMol: Advanced Molecular Visualization in Blender.
Copyright (C) 2018  Jacob D. Durrant

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from .ExternalInterface import ExternalInterface
import os
import re
import glob
# from pathlib import Path
import subprocess

class VMD(ExternalInterface):
    """
    A class to get 3D models using VMD.
    """

    def fix_path_for_tcl(self, path):
        """
        Even in windows, TCL paths must use /.

        :param string path: The path, as appropriate for the operating
                      system.

        :returns: The TCL-appropriate path.
        :rtype: :class:`str`
        """

        if os.sep != "/":
            # Windows, so switch to /
            path = path.replace("\\", "/")    
        return path

    def make_vis_script(self, my_operator):
        """
        Make the visualization script to pass to VMD, and save it to the
        temporary directory.

        :param ??? my_operator: The operator, used to access user-parameter
                    variables.
        """
        
        tcl_script = """
            #!/usr/local/bin/vmd
            # Jacob Durrant

            # Turn axes off
            axes location off
        """

        reset_viewport_tcl = """
            # Remove all translation and rotation

            ##
            ## Set transformation matrices to identity so that exported 
            ## geometry is written in the original model coordinates rather
            ## than world or eye coordinates.
            ## Code provided by John Stone, personal communication.
            set identityvpts {
                {{1.000000 0.000000 0.000000 0.000000}
                 {0.000000 1.000000 0.000000 0.000000}
                 {0.000000 0.000000 1.000000 0.000000}
                 {0.000000 0.000000 0.000000 1.000000}}
                {{1.000000 0.000000 0.000000 0.000000}
                 {0.000000 1.000000 0.000000 0.000000}
                 {0.000000 0.000000 1.000000 0.000000}
                 {0.000000 0.000000 0.000000 1.000000}}
                {{1.000000 0.000000 0.000000 0.000000}
                 {0.000000 1.000000 0.000000 0.000000}
                 {0.000000 0.000000 1.000000 0.000000}
                 {0.000000 0.000000 0.000000 1.000000}}
                {{1.000000 0.000000 0.000000 0.000000}
                 {0.000000 1.000000 0.000000 0.000000}
                 {0.000000 0.000000 1.000000 0.000000}
                 {0.000000 0.000000 0.000000 1.000000}}
            }

            for {set i 0} {$i < [molinfo num]} {incr i} {
                molinfo ${i} set {center_matrix rotate_matrix scale_matrix global_matrix} $identityvpts
            }
        """

        filename = os.path.abspath(my_operator.filepath)
        _, ext = os.path.splitext(filename)
        ext = ext.upper()
        filename = self.fix_path_for_tcl(filename)  # Make path os-specific

        if ext == ".PDB":
            # Set the selections
            nuc_sel_raw = ("(nucleic and not resname ATP UTP TTP CTP GTP AMP "
                           "UMP TMP CMP GMP ADP UDP TDP CDP GDP)")

            lig_sel_raw = ("((chain $chain) and (not protein and not " + 
                           nuc_sel_raw +
                           " and not water) and not " +
                           "((not element N C O P S Se Cl Br F) " +
                           "and mass > 16) and " +
                           "(not resname MSE))")

            ligand_sel_str = '"' + lig_sel_raw + '"'
            
            # protein_near_lig_sel_str = (
            #     '"(same residue as (protein within 8 of ((chain $chain) ' +
            #     'and (not protein and not nucleic and not water) and not ((not element N C ' +
            #     'O P S Se Cl Br F) and mass > 16) and (not resname MSE))))"'
            # )

            protein_near_lig_sel_str = (
                '"(protein or ' + nuc_sel_raw + ') and (same residue as ' + 
                '(all within 8 of ' + lig_sel_raw + '))"'
            )

            metals_sel_str = (
                '"(chain $chain) and (not element N C O P S Se Cl Br F) ' +
                'and (mass > 16) and (not resname MET CYS MSE)"'
            )

            protein_nuc_sel_str = (
                '"chain $chain and (protein or ' + nuc_sel_raw + 
                ' or resname MSE)"'
            )

            # Load the PDB
            tcl_script = tcl_script + """
                # Load the pdb file
                mol new """ + filename + """ type pdb first 0 last -1 step 1 filebonds 1 autobonds 1 waitfor all
                
                # Go to first frame
                animate goto 0
            """

            tcl_script = tcl_script + reset_viewport_tcl

            tcl_script = tcl_script + """
                # Go through each of the chains and save it separately.
                set all [atomselect top all]
                set chains [$all get chain]
                set uniq_chains [lsort -unique $chains]

                # Carbons should be grey
                color change rgb 10 0.6 0.6 0.6

                foreach chain $uniq_chains {
            """

            # Consider ligands
            if my_operator.ligand_surface == True:
                if my_operator.vmd_msms_repr == True:
                    tcl_script = (
                        tcl_script +
                        self.get_msms_code("ligand_msms", ligand_sel_str)
                    )
                else:
                    tcl_script = (
                        tcl_script +
                        self.get_surf_code("ligand_surf", ligand_sel_str)
                    )

            if my_operator.ligand_sticks == True:
                tcl_script = (
                    tcl_script +
                    self.get_stick_code("ligand_sticks", ligand_sel_str)
                )

            if my_operator.ligand_balls == True:
                tcl_script = (
                    tcl_script +
                    self.get_balls_code("ligand_balls", ligand_sel_str)
                )

            if my_operator.ligand_vdw == True:
                tcl_script = (
                    tcl_script +
                    self.get_balls_code("ligand_vdw", ligand_sel_str)
                )

            # Consider interacting residues
            if my_operator.near_ligand_surface == True:
                if my_operator.vmd_msms_repr == True:
                    tcl_script = (
                        tcl_script +
                        self.get_msms_code(
                            "interacting_msms", protein_near_lig_sel_str
                        )
                    )
                else:
                    tcl_script = (
                        tcl_script +
                        self.get_surf_code(
                            "interacting_surf", protein_near_lig_sel_str
                        )
                    )

            if my_operator.near_ligand_sticks == True:
                tcl_script = (
                    tcl_script +
                    self.get_stick_code(
                        "interacting_sticks", protein_near_lig_sel_str
                    )
                )

            if my_operator.near_ligand_balls == True:
                tcl_script = (
                    tcl_script +
                    self.get_balls_code(
                        "interacting_balls", protein_near_lig_sel_str
                    )
                )

            if my_operator.near_ligand_vdw == True:
                tcl_script = (
                    tcl_script +
                    self.get_vdw_code(
                        "interacting_vdw", protein_near_lig_sel_str
                    )
                )
            
            # Consider proteins
            if my_operator.protein_surface == True:
                if my_operator.vmd_msms_repr == True:
                    tcl_script = (
                        tcl_script +
                        self.get_msms_code(
                            "protein_nucleic_msms", 
                            protein_nuc_sel_str
                        )
                    )
                else:
                    tcl_script = (
                        tcl_script +
                        self.get_surf_code(
                            "protein_nucleic_surf", 
                            protein_nuc_sel_str
                        )
                    )

            if my_operator.protein_sticks == True:
                tcl_script = (
                    tcl_script +
                    self.get_stick_code(
                        "protein_nucleic_sticks", 
                        protein_nuc_sel_str
                    )
                )

            if my_operator.protein_balls == True:
                tcl_script = (
                    tcl_script +
                    self.get_balls_code(
                        "protein_nucleic_balls", 
                        protein_nuc_sel_str
                    )
                )

            if my_operator.protein_vdw == True:
                tcl_script = (
                    tcl_script + self.get_vdw_code(
                        "protein_nucleic_vdw", 
                        protein_nuc_sel_str
                    )
                )

            if my_operator.protein_ribbon == True:
                tcl_script = (
                    tcl_script +
                    self.get_ribbon_code(
                        "protein_nucleic_ribbon", 
                        protein_nuc_sel_str
                    )
                )

            # Consider metals
            if my_operator.metals_vdw == True:
                tcl_script = (
                    tcl_script +
                    self.get_vdw_code("metals", metals_sel_str)
                )

            tcl_script = tcl_script + """
                }
            """
        else:
            # Must be a VMD or TCL file
            tcl_script = tcl_script + '''
                cd ''' + self.fix_path_for_tcl(os.path.dirname(filename)) + '''
                ''' + open(filename, 'r').read() + '''

                # Go to first frame
                animate goto 0

                ''' + reset_viewport_tcl + '''
                render Wavefront "''' + self.fix_path_for_tcl(self.tmp_dir) + os.sep + '''user_defined.obj"
            '''

        tcl_script = tcl_script + """
            quit
        """

        # Save the VMD TCL script.
        # open(str(Path(self.tmp_dir + "vmd.vmd")), 'w').write(tcl_script)
        open(self.tmp_dir + "vmd.vmd", 'w').write(tcl_script)
        
    def get_code_start(self, selection):
        """
        TCL code to run before rendering a representation.
    
        :param str selection: The selection string.

        :returns: The TCL code.
        :rtype: :class:`str`
        """

        return '''
            puts ''' + selection + '''
            set sel [atomselect top ''' + selection + ''']
            if {[$sel num] > 0} {
                mol delrep 0 top
                mol selection ''' + selection + '''
        '''
    
    def get_code_end(self, filename_id):
        """
        TCL code to render a representation.
    
        :param str filename_id: The filename id to use when saving.

        :returns: The TCL code.
        :rtype: :class:`str`
        """

        return '''
                mol addrep top
                render Wavefront "''' + self.fix_path_for_tcl(self.tmp_dir) + os.sep + filename_id + '''_${chain}.obj"
            }
        '''

    def get_msms_code(self, filename_id, selection):
        """
        TCL code to render a MSMS representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.get_code_start(selection) + """
            mol representation MSMS 1.500000 5.000000 0.000000 0.000000
        """ + self.get_code_end(filename_id)

    def get_surf_code(self, filename_id, selection):
        """
        TCL code to render a surf representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.get_code_start(selection) + """
            mol representation Surf 1.400000 0.000000
        """ + self.get_code_end(filename_id)

    def get_stick_code(self, filename_id, selection):
        """
        TCL code to render a stick representation  and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.get_code_start(selection) + """
            mol representation Licorice 0.300000 20.000000 20.000000
        """ + self.get_code_end(filename_id)
    
    def get_balls_code(self, filename_id, selection):
        """
        TCL code to render a balls representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.get_code_start(selection) + """
            mol representation VDW 0.2000000 12.000000
        """ + self.get_code_end(filename_id)

    def get_vdw_code(self, filename_id, selection):
        """
        TCL code to render a VDW representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.get_code_start(selection) + """
            mol representation VDW 1.0000000 12.000000
        """ + self.get_code_end(filename_id)

    def get_ribbon_code(self, filename_id, selection):
        """
        TCL code to render a ribbon representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.get_code_start(selection) + """
            mol representation NewCartoon 0.300000 10.000000 4.100000 0
        """ + self.get_code_end(filename_id)

    def run_external_program(self, exec_path):
        """
        Runs the VMD executable with the generated script.

        :param str exec_path: The path to the executable.
        """

        # Execute VMD to generate the obj files
        cmd = [self.fix_path_for_tcl(exec_path), "-dispdev", "text",
               "-e", self.fix_path_for_tcl(self.tmp_dir + "vmd.vmd")]
        print(cmd)
        subprocess.check_call(cmd)
