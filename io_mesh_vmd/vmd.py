from .ExternalInterface import ExternalInterface
import os
import re
import glob

class VMD(ExternalInterface):
    def __init__(self):
        pass

    def populate_tmp_dir(self, filename):
        # No need to copy any files
        pass

        # ext = self.get_ext(filename)

        # # It's vmd. Create the input script
        # if ext == ".PDB":
        #     # It's a pdb file
        #     open(self.tmp_dir + "vmd.vmd",'w').write(
        #         open(self.script_dir + "pdb.vmd.template", 'r').read().replace(
        #             "{PDB_FILENAME}", filename
        #         ).replace(
        #             "{OUTPUT_DIR}", self.tmp_dir
        #         )
        #     )
        # else:
        #     # It must be a tcl or state file
        #     open(self.tmp_dir + "vmd.vmd",'w').write(
        #         "cd " + os.path.dirname(filename) + "\n" +
        #         open(filename, 'r').read() + "\n" +
        #         open(self.script_dir + "vmd.vmd.template", 'r').read().replace(
        #             "{OUTPUT_DIR}", self.tmp_dir
        #         )
        #     )

    def make_vis_script(self, my_operator):
        tcl_script = """
            #!/usr/local/bin/vmd
            # Jacob Durrant

            # Turn axes off
            axes location off
        """

        reset_viewport_tcl = """
            # Remove all translation and rotation

            ##
            ## Set transformation matrices to identity so that exported geometry
            ## is written in the original model coordinates rather than world or
            ## eye coordinates.
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
            ligand_sel_str = '"(chain $chain) and (not protein and not water) and not ((not element N C O P S Se Cl Br F) and mass > 16) and (not resname MSE)"'
            protein_near_lig_sel_str = '"(same residue as (protein within 8 of ((chain $chain) and (not protein and not water) and not ((not element N C O P S Se Cl Br F) and mass > 16) and (not resname MSE))))"'
            metals_sel_str = '"(chain $chain) and (not element N C O P S Se Cl Br F) and (mass > 16) and (not resname MET CYS MSE)"'
            protein_sel_str = '"chain $chain and (protein or resname MSE)"'

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
                if my_operator.user_vmd_msms_representation == True:
                    tcl_script = tcl_script + self.msms_code("ligand_msms", ligand_sel_str)
                else:
                    tcl_script = tcl_script + self.surf_code("ligand_surf", ligand_sel_str)

            if my_operator.ligand_sticks == True:
                tcl_script = tcl_script + self.stick_code("ligand_sticks", ligand_sel_str)

            if my_operator.ligand_balls == True:
                tcl_script = tcl_script + self.balls_code("ligand_balls", ligand_sel_str)

            if my_operator.ligand_vdw == True:
                tcl_script = tcl_script + self.balls_code("ligand_vdw", ligand_sel_str)

            # Let's deal with interacting residues
            if my_operator.near_ligand_surface == True:
                if my_operator.user_vmd_msms_representation == True:
                    tcl_script = tcl_script + self.msms_code("interacting_msms", protein_near_lig_sel_str)
                else:
                    tcl_script = tcl_script + self.surf_code("interacting_surf", protein_near_lig_sel_str)

            if my_operator.near_ligand_sticks == True:
                tcl_script = tcl_script + self.stick_code("interacting_sticks", protein_near_lig_sel_str)

            if my_operator.near_ligand_balls == True:
                tcl_script = tcl_script + self.balls_code("interacting_balls", protein_near_lig_sel_str)

            if my_operator.near_ligand_vdw == True:
                tcl_script = tcl_script + self.vdw_code("interacting_vdw", protein_near_lig_sel_str)
            
            # Now deal with proteins
            if my_operator.protein_surface == True:
                if my_operator.user_vmd_msms_representation == True:
                    tcl_script = tcl_script + self.msms_code("protein_msms", protein_sel_str)
                else:
                    tcl_script = tcl_script + self.surf_code("protein_surf", protein_sel_str)

            if my_operator.protein_sticks == True:
                tcl_script = tcl_script + self.stick_code("protein_sticks", protein_sel_str)

            if my_operator.protein_balls == True:
                tcl_script = tcl_script + self.balls_code("protein_balls", protein_sel_str)

            if my_operator.protein_vdw == True:
                tcl_script = tcl_script + self.vdw_code("protein_vdw", protein_sel_str)

            if my_operator.protein_ribbon == True:
                tcl_script = tcl_script + self.ribbon_code("protein_ribbon", protein_sel_str)

            # Metals
            if my_operator.metals_vdw == True:
                tcl_script = tcl_script + self.vdw_code("metals", metals_sel_str)

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
        return '''
            set sel [atomselect top ''' + selection + ''']
            if {[$sel num] > 0} {
                mol delrep 0 top
                mol selection ''' + selection + '''
        '''
    
    def code_end(self, filename_id):
        return '''
                mol addrep top
                render Wavefront "''' + self.tmp_dir + os.sep + filename_id + '''_${chain}.obj"
            }
        '''

    def msms_code(self, filename_id, selection):
        return self.code_start(selection) + """
            mol representation MSMS 1.500000 5.000000 0.000000 0.000000
        """ + self.code_end(filename_id)

    def surf_code(self, filename_id, selection):
        return self.code_start(selection) + """
            mol representation Surf 1.400000 0.000000
        """ + self.code_end(filename_id)

    def stick_code(self, filename_id, selection):
        return self.code_start(selection) + """
            mol representation Licorice 0.300000 20.000000 20.000000
        """ + self.code_end(filename_id)
    
    def balls_code(self, filename_id, selection):
        return self.code_start(selection) + """
            mol representation VDW 0.2000000 12.000000
        """ + self.code_end(filename_id)

    def vdw_code(self, filename_id, selection):
        return self.code_start(selection) + """
            mol representation VDW 1.0000000 12.000000
        """ + self.code_end(filename_id)

    def ribbon_code(self, filename_id, selection):
        return self.code_start(selection) + """
            mol representation NewCartoon 0.300000 10.000000 4.100000 0
        """ + self.code_end(filename_id)

    def run_external_program(self, exec_path):
        # Execute VMD to generate the obj files
        os.system('"' + exec_path + '"' + " -dispdev text -e " + self.tmp_dir + "vmd.vmd")

        # Edit obj files to get better names
        nm = re.compile("vmd_mol\d*_rep\d*")
        for filename in glob.glob(self.tmp_dir + "*.obj"):
            filename_txt = os.path.basename(filename).replace(".obj", "")
            obj_content = open(filename,'r').read()
            obj_content = nm.sub(filename_txt, obj_content)
            open(filename, 'w').write(obj_content)


