from .ExternalInterface import ExternalInterface
import os
import re
import glob

class VMD(ExternalInterface):
    """
    A class to get 3D models using VMD.
    """

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

        if ext == ".PDB":
            # Set the selections
            nuc_sel_raw = "(nucleic and not resname ATP UTP TTP CTP GTP AMP UMP TMP CMP GMP ADP UDP TDP CDP GDP)"

            lig_sel_raw = (
                '((chain $chain) and (not protein and not ' + nuc_sel_raw + ' and not water) and not ' +
                '((not element N C O P S Se Cl Br F) and mass > 16) and ' +
                '(not resname MSE))'
            )

            ligand_sel_str = '"' + lig_sel_raw + '"'
            
            # protein_near_lig_sel_str = (
            #     '"(same residue as (protein within 8 of ((chain $chain) ' +
            #     'and (not protein and not nucleic and not water) and not ((not element N C ' +
            #     'O P S Se Cl Br F) and mass > 16) and (not resname MSE))))"'
            # )

            protein_near_lig_sel_str = (
                '"(protein or ' + nuc_sel_raw + ') and (same residue as (all within 8 of ' +
                lig_sel_raw + '))"'
            )

            metals_sel_str = (
                '"(chain $chain) and (not element N C O P S Se Cl Br F) ' +
                'and (mass > 16) and (not resname MET CYS MSE)"'
            )

            protein_nuc_sel_str = '"chain $chain and (protein or ' + nuc_sel_raw + ' or resname MSE)"'

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

            # Let's deal with ligands
            if my_operator.ligand_surface == True:
                if my_operator.vmd_msms_repr == True:
                    tcl_script = (
                        tcl_script +
                        self.msms_code("ligand_msms", ligand_sel_str)
                    )
                else:
                    tcl_script = (
                        tcl_script +
                        self.surf_code("ligand_surf", ligand_sel_str)
                    )

            if my_operator.ligand_sticks == True:
                tcl_script = (
                    tcl_script +
                    self.stick_code("ligand_sticks", ligand_sel_str)
                )

            if my_operator.ligand_balls == True:
                tcl_script = (
                    tcl_script +
                    self.balls_code("ligand_balls", ligand_sel_str)
                )

            if my_operator.ligand_vdw == True:
                tcl_script = (
                    tcl_script +
                    self.balls_code("ligand_vdw", ligand_sel_str)
                )

            # Let's deal with interacting residues
            if my_operator.near_ligand_surface == True:
                if my_operator.vmd_msms_repr == True:
                    tcl_script = (
                        tcl_script +
                        self.msms_code(
                            "interacting_msms", protein_near_lig_sel_str
                        )
                    )
                else:
                    tcl_script = (
                        tcl_script +
                        self.surf_code(
                            "interacting_surf", protein_near_lig_sel_str
                        )
                    )

            if my_operator.near_ligand_sticks == True:
                tcl_script = (
                    tcl_script +
                    self.stick_code(
                        "interacting_sticks", protein_near_lig_sel_str
                    )
                )

            if my_operator.near_ligand_balls == True:
                tcl_script = (
                    tcl_script +
                    self.balls_code(
                        "interacting_balls", protein_near_lig_sel_str
                    )
                )

            if my_operator.near_ligand_vdw == True:
                tcl_script = (
                    tcl_script +
                    self.vdw_code(
                        "interacting_vdw", protein_near_lig_sel_str
                    )
                )
            
            # Now deal with proteins
            if my_operator.protein_surface == True:
                if my_operator.vmd_msms_repr == True:
                    tcl_script = (
                        tcl_script +
                        self.msms_code("protein_nucleic_msms", protein_nuc_sel_str)
                    )
                else:
                    tcl_script = (
                        tcl_script +
                        self.surf_code("protein_nucleic_surf", protein_nuc_sel_str)
                    )

            if my_operator.protein_sticks == True:
                tcl_script = (
                    tcl_script +
                    self.stick_code("protein_nucleic_sticks", protein_nuc_sel_str)
                )

            if my_operator.protein_balls == True:
                tcl_script = (
                    tcl_script +
                    self.balls_code("protein_nucleic_balls", protein_nuc_sel_str)
                )

            if my_operator.protein_vdw == True:
                tcl_script = (
                    tcl_script + self.vdw_code("protein_nucleic_vdw", protein_nuc_sel_str)
                )

            if my_operator.protein_ribbon == True:
                tcl_script = (
                    tcl_script +
                    self.ribbon_code("protein_nucleic_ribbon", protein_nuc_sel_str)
                )

            # Metals
            if my_operator.metals_vdw == True:
                tcl_script = (
                    tcl_script +
                    self.vdw_code("metals", metals_sel_str)
                )

            tcl_script = tcl_script + """
                }
            """
        else:
            # Must be a VMD or TCL file
            tcl_script = tcl_script + '''
                cd ''' + os.path.dirname(filename) + '''
                ''' + open(filename, 'r').read() + '''

                # Go to first frame
                animate goto 0

                ''' + reset_viewport_tcl + '''
                render Wavefront "''' + self.tmp_dir + os.sep + '''user_defined.obj"
            '''

        tcl_script = tcl_script + """
            quit
        """

        open(self.tmp_dir + "vmd.vmd", 'w').write(tcl_script)
        
    def code_start(self, selection):
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
    
    def code_end(self, filename_id):
        """
        TCL code to render a representation.
    
        :param str filename_id: The filename id to use when saving.

        :returns: The TCL code.
        :rtype: :class:`str`
        """

        return '''
                mol addrep top
                render Wavefront "''' + self.tmp_dir + os.sep + filename_id + '''_${chain}.obj"
            }
        '''

    def msms_code(self, filename_id, selection):
        """
        TCL code to render a MSMS representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.code_start(selection) + """
            mol representation MSMS 1.500000 5.000000 0.000000 0.000000
        """ + self.code_end(filename_id)

    def surf_code(self, filename_id, selection):
        """
        TCL code to render a surf representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.code_start(selection) + """
            mol representation Surf 1.400000 0.000000
        """ + self.code_end(filename_id)

    def stick_code(self, filename_id, selection):
        """
        TCL code to render a stick representation  and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.code_start(selection) + """
            mol representation Licorice 0.300000 20.000000 20.000000
        """ + self.code_end(filename_id)
    
    def balls_code(self, filename_id, selection):
        """
        TCL code to render a balls representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.code_start(selection) + """
            mol representation VDW 0.2000000 12.000000
        """ + self.code_end(filename_id)

    def vdw_code(self, filename_id, selection):
        """
        TCL code to render a VDW representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.code_start(selection) + """
            mol representation VDW 1.0000000 12.000000
        """ + self.code_end(filename_id)

    def ribbon_code(self, filename_id, selection):
        """
        TCL code to render a ribbon representation and save it as an OBJ file.
    
        :param str filename_id: The filename id to use when saving.

        :param str selection: The selection string.

        :returns: TCL code.
        :rtype: :class:`str`
        """

        return self.code_start(selection) + """
            mol representation NewCartoon 0.300000 10.000000 4.100000 0
        """ + self.code_end(filename_id)

    def run_external_program(self, exec_path):
        """
        Runs the VMD executable.

        :param str exec_path: The path to the executable.
        """

        # Execute VMD to generate the obj files
        os.system(
            '"' + exec_path + '"' + " -dispdev text -e " +
            self.tmp_dir + "vmd.vmd"
        )