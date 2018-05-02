from .ExternalInterface import ExternalInterface
import os
import re
import glob

class PyMol(ExternalInterface):
    """
    A class to get 3D models using PyMol.
    """

    def make_vis_script(self, my_operator):
        """
        Make the visualization script to pass to PyMol, and save it to the
        temporary directory.

        :param ??? my_operator: The operator, used to access user-parameter
                    variables.
        """

        python_script = """
                import pymol
                from pymol import cmd
                import os

                # Useful page: 
                #    https://pymol.org/dokuwiki/doku.php?id=api:cmd:alpha
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
                all_protein_nuc_sel = "resn ala+arg+asn+asp+asx+cys+gln+glu+glx+gly+his+hsp+hyp+ile+leu+lys+met+pca+phe+pro+ser+thr+trp+tyr+val+dg+dc+dt+da+g+c+t+a+u+rg+rc+rt+ra+ru"
                water_sel = "resn wat+hoh+h2o+tip+tip3"
                all_metals_sel = "symbol " + "+".join(["fe", "ag", "co", "cu",
                                                       "ca", "zn", "mg", "ni",
                                                       "mn", "au"])

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
                    ligand_sel = "(chain " + chain + ") and (not " + all_protein_nuc_sel + " and not " + water_sel + ") and not (not symbol h+he+li+be+b+c+n+o+f+ne+na+mg+al+si+p+s+se+cl+br+f) and (not resn mse)"
                    nearby_resi_sel = "byres ((" + all_protein_nuc_sel + ") within 8 of (" + ligand_sel + "))"
                    protein_nuc_sel = "(chain " + chain + ") and (" + all_protein_nuc_sel + ",mse)"
                    metals_sel = "(chain " + chain + ") and (" + all_metals_sel + ")"
            """

            # Consider ligands
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

            # PyMol doesn't support this.
            # if my_operator.ligand_balls == True:
            #     python_script = python_script + self.get_balls_code("ligand_balls", ligand_sel_str)

            if my_operator.ligand_vdw == True:
                python_script = python_script + """
                    # Save the ligand of this chain using VDW representation
                    # (1.0 * van der waals radius)
                    render_vdw(ligand_sel, "ligand_vdw_" + chain + ".wrl")
                """

            # Consider interacting residues
            if my_operator.near_ligand_surface == True:
                python_script = python_script + """
                    # Save the surrounding residues of this chain using
                    # surface representation
                    render_surf(nearby_resi_sel, "interacting_surf_" + chain + ".wrl")
                """

            if my_operator.near_ligand_sticks == True:
                python_script = python_script + """
                    # Save the surrounding residues of this chain using sticks representation
                    render_sticks(nearby_resi_sel, "interacting_sticks_" + chain + ".wrl")
                """

            # PyMol doesn't support this.
            # if my_operator.near_ligand_balls == True:
            #     python_script = python_script + self.get_balls_code("interacting_balls", protein_near_lig_sel_str)

            if my_operator.near_ligand_vdw == True:
                python_script = python_script + """
                    # Save the surrounding residues of this chain using VDW
                    # representation (1.0 * van der waals radius)
                    render_vdw(nearby_resi_sel, "interacting_vdw_" + chain + ".wrl")
                """
            
            # Consider proteins
            if my_operator.protein_surface == True:
                python_script = python_script + """
                    # Save the protein of this chain using surface representation
                    render_surf(protein_nuc_sel, "protein_nucleic_surf_" + chain + ".wrl")
                """

            if my_operator.protein_sticks == True:
                python_script = python_script + """
                    # Save the protein of this chain using sticks representation
                    render_sticks(protein_nuc_sel, "protein_nucleic_sticks_" + chain + ".wrl")
                """

            # PyMol doesn't support this.
            # if my_operator.protein_balls == True:
            #     python_script = python_script + self.get_balls_code("protein_nucleic_balls", protein_nuc_sel_str)

            if my_operator.protein_vdw == True:
                python_script = python_script + """
                    # Save the protein of this chain using VDW representation
                    # (1.0 * van der waals radius)
                    render_vdw(protein_nuc_sel, "protein_nucleic_vdw_" + chain + ".wrl")
                """

            if my_operator.protein_ribbon == True:
                python_script = python_script + """
                    # Save the protein of this chain using ribbon
                    # representation
                    render_cartoon(protein_nuc_sel, "protein_nucleic_ribbon_" + chain + ".wrl")
                """

            # Consider metals
            if my_operator.metals_vdw == True:
                python_script = python_script + """
                    # Save the protein of this chain using VDW representation
                    # (1.0 * van der waals radius)
                    render_vdw(metals_sel, "metals_" + chain + ".wrl")
                """ 
        else:
            # Must be a PSE  file
            python_script = python_script + '''
                # Switch to the first frame
                cmd.frame(0)

                # Load the PSE file
                cmd.load("''' + filename + '''")

                # Reset the camera
                reset_camera()

                # Save scene
                cmd.save("''' + self.tmp_dir + '''user_defined.wrl")
            '''

        python_script = python_script + """
                cmd.quit()
        """

        # Remove some tabs to make it work in python.
        lines = [l for l in python_script.split("\n") if l != ""]
        tabs = lines[0][0:(len(lines[0]) - len(lines[0].lstrip()))]
        lines = [l[len(tabs):] for l in lines]
        python_script = "\n".join(lines)

        # Save the PyMol script.
        open(self.tmp_dir + "render.py", 'w').write(python_script)

    def run_external_program(self, exec_path):
        """
        Runs the PyMol executable with the generated script.

        :param str exec_path: The path to the executable.
        """

        # Execute PyMol to generate the obj files
        cmd = '"' + exec_path + '"' + " -c " + self.tmp_dir + "render.py"
        print(cmd)
        os.system(cmd)
