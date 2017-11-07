from .ExternalInterface import ExternalInterface
import os
import re
import glob

class PyMol(ExternalInterface):
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
        python_script = """
                import pymol
                from pymol import cmd
                import os

                # Useful page: https://pymol.org/dokuwiki/doku.php?id=api:cmd:alpha
                # https://pymolwiki.org/index.php/Selection_Algebra

                # Use pymol -c option to run in headless mode.

                # Wait for pymol to be ready
                pymol.finish_launching()

                def reset_camera():
                    # Make sure the camera is set to a neutral
                    # position/orientation, so mesh matches pdb coordinates.
                    cmd.set_view([ 1.0,   0.0,   0.0,
                                0.0,   1.0,   0.0,
                                0.0,   0.0,   1.0,
                                0.0,   0.0,   0.0,
                                0.0,   0.0,   0.0,
                                40.0, 100.0, -20.0])
                reset_camera()
        """

        filename = os.path.abspath(my_operator.filepath)
        _, ext = os.path.splitext(filename)
        ext = ext.upper()

        if ext == ".PDB":
            # Load the PDB
            python_script = python_script + """
                # Load the PDB file
                cmd.load('""" + filename + """', "system")
                
                # Switch to the first frame
                cmd.frame(0)

                # Make carbons gray
                cmd.color("silver", "(symbol c)", 1)

                # Make sure anything can be surface, not just protein. Also,
                # only consider visible atoms when calculating surfaces.
                cmd.set("surface_mode", 3)

                # Get all the unique chains in the protein. This will be
                # different for each PDB.
                chains = cmd.get_chains(selection="(all)", state=0, quiet=1)

                # Define some selections
                all_protein_sel = "resn ala+arg+asn+asp+asx+cys+gln+glu+glx+gly+his+hsp+hyp+ile+leu+lys+met+pca+phe+pro+ser+thr+trp+tyr+val"
                water_sel = "resn wat+hoh+h2o+tip+tip3"
                all_metals_sel = "symbol " + "+".join(["fe", "ag", "co", "cu", "ca", "zn", "mg", "ni", "mn", "au"])

                # Functions to render different representations
                def render_setup(selection, representation):
                    cmd.hide("(all)")
                    cmd.show_as(representation, "(" + selection + ")")
                    reset_camera()
                    # cmd.refresh()

                def render_surf(selection, filename):
                    render_setup(selection, "surface")
                    cmd.save('""" + self.tmp_dir + """' + filename)

                def render_sticks(selection, filename):
                    render_setup(selection, "sticks")
                    cmd.save('""" + self.tmp_dir + """' + filename)

                def render_vdw(selection, filename):
                    render_setup(selection, "spheres")
                    cmd.save('""" + self.tmp_dir + """' + filename)

                def render_cartoon(selection, filename):
                    render_setup(selection, "cartoon")
                    cmd.save('""" + self.tmp_dir + """' + filename)
                    
                # For each chain, separate meshes
                for chain in [c for c in chains if c != ""]:
                    ligand_sel = "(chain " + chain + ") and (not " + all_protein_sel + " and not " + water_sel + ") and not (not symbol h+he+li+be+b+c+n+o+f+ne+na+mg+al+si+p+s+se+cl+br+f) and (not resn mse)"
                    surrounding_residues_sel = "byres ((" + all_protein_sel + ") within 8 of (" + ligand_sel + "))"
                    protein_sel = "(chain " + chain + ") and (" + all_protein_sel + ",mse)"
                    metals_sel = "(chain " + chain + ") and (" + all_metals_sel + ")"
            """

            # Let's deal with ligands
            if my_operator.ligand_surface == True:
                python_script = python_script + """
                    # Save the ligand of this chain using surface
                    # representation
                    render_surf(ligand_sel, "ligand_surf_" + chain + ".wrl")
                """

            if my_operator.ligand_sticks == True:
                python_script = python_script + """
                    # Save the ligand of this chain using sticks
                    # representation
                    render_sticks(ligand_sel, "ligand_sticks_" + chain + ".wrl")
                """

            # if my_operator.ligand_balls == True:
            #     python_script = python_script + self.balls_code("ligand_balls", ligand_sel_str)

            if my_operator.ligand_vdw == True:
                python_script = python_script + """
                    # Save the ligand of this chain using VDW representation
                    # (1.0 * van der waals radius)
                    render_vdw(ligand_sel, "ligand_vdw_" + chain + ".wrl")
                """

            # Let's deal with interacting residues
            if my_operator.near_ligand_surface == True:
                python_script = python_script + """
                    # Save the surrounding residues of this chain using
                    # surface representation
                    render_surf(surrounding_residues_sel, "interacting_surf_" + chain + ".wrl")
                """

            if my_operator.near_ligand_sticks == True:
                python_script = python_script + """
                    # Save the surrounding residues of this chain using sticks representation
                    render_sticks(surrounding_residues_sel, "interacting_sticks_" + chain + ".wrl")
                """

            # if my_operator.near_ligand_balls == True:
            #     python_script = python_script + self.balls_code("interacting_balls", protein_near_lig_sel_str)

            if my_operator.near_ligand_vdw == True:
                python_script = python_script + """
                    # Save the surrounding residues of this chain using VDW
                    # representation (1.0 * van der waals radius)
                    render_vdw(surrounding_residues_sel, "interacting_vdw_" + chain + ".wrl")
                """
            
            # Now deal with proteins
            if my_operator.protein_surface == True:
                python_script = python_script + """
                    # Save the protein of this chain using surface representation
                    render_surf(protein_sel, "protein_surf_" + chain + ".wrl")
                """

            if my_operator.protein_sticks == True:
                python_script = python_script + """
                    # Save the protein of this chain using sticks representation
                    render_sticks(protein_sel, "protein_sticks_" + chain + ".wrl")
                """

            # if my_operator.protein_balls == True:
            #     python_script = python_script + self.balls_code("protein_balls", protein_sel_str)

            if my_operator.protein_vdw == True:
                python_script = python_script + """
                    # Save the protein of this chain using VDW representation
                    # (1.0 * van der waals radius)
                    render_vdw(protein_sel, "protein_vdw_" + chain + ".wrl")
                """

            if my_operator.protein_ribbon == True:
                python_script = python_script + """
                    # Save the protein of this chain using ribbon
                    # representation
                    render_cartoon(protein_sel, "protein_ribbon_" + chain + ".wrl")
                """

            # Metals
            if my_operator.metals_vdw == True:
                python_script = python_script + """
                    # Save the protein of this chain using VDW representation
                    # (1.0 * van der waals radius)
                    render_vdw(metals_sel, "metals_" + chain + ".wrl")
                """ 
        else:
            # Must be a VMD or TCL file
            python_script = python_script + '''
                # Switch to the first frame
                cmd.frame(0)

                # Save scene
                cmd.save("''' + os.path.dirname(filename) + os.sep + '''user_defined.wrl")
            '''

        python_script = python_script + """
                cmd.quit()
        """

        # Remove some tabs to make it work in python.
        lines = [l for l in python_script.split("\n") if l != ""]
        tabs = lines[0][0:(len(lines[0]) - len(lines[0].lstrip()))]
        lines = [l[len(tabs):] for l in lines]
        python_script = "\n".join(lines)

        open(self.tmp_dir + "render.py", 'w').write(python_script)

    def run_external_program(self, exec_path):
        # Execute VMD to generate the obj files
        cmd = '"' + exec_path + '"' + " -c " + self.tmp_dir + "render.py"
        os.system(cmd)

        # import pdb; pdb.set_trace()

        # Edit obj files to get better names
        # nm = re.compile("vmd_mol\d*_rep\d*")
        # for filename in glob.glob(self.tmp_dir + "*.wrl"):
        #     filename_txt = os.path.basename(filename).replace(".wrl", "")
        #     obj_content = open(filename,'r').read()
        #     obj_content = nm.sub(filename_txt, obj_content)
        #     open(filename, 'w').write(obj_content)
