import pymol
from pymol import cmd
import os

# Wait for pymol to be ready
pymol.finish_launching()

# Load the PDB file
cmd.load("2hu4.pdb", "2HU4")

# Switch to the first frame
cmd.frame(0)

# Position camera

# Make carbons gray
cmd.color("silver", "(symbol c)", 1)

# Make sure anything can be surface, not just protein. Also, only consider
# visible atoms when calculating surfaces.
cmd.set("surface_mode", 3)

# Get all the unique chains in the protein. This will be different for each
# PDB.
chains = cmd.get_chains(selection="(all)", state=0, quiet=1)

# Define some selections
all_protein_sel = "resn ala+arg+asn+asp+asx+cys+gln+glu+glx+gly+his+hsp+hyp+ile+leu+lys+met+pca+phe+pro+ser+thr+trp+tyr+val"
water_sel = "resn wat+hoh+h2o+tip+tip3"

# Functions to render different representations
def render_setup(selection, representation):
    cmd.hide("(all)")
    cmd.show_as(representation, "(" + selection + ")")
    cmd.refresh()

def render_surf(selection, filename):
    render_setup(selection, "surface")
    cmd.save(filename)

def render_sticks(selection, filename):
    render_setup(selection, "sticks")
    cmd.save(filename)

def render_vdw(selection, filename):
    render_setup(selection, "spheres")
    cmd.save(filename)

def render_cartoon(selection, filename):
    render_setup(selection, "cartoon")
    cmd.save(filename)

# For each chain, separate meshes
for chain in chains:
    ligand_sel = "(chain " + chain + ") and (not " + all_protein_sel + " and not " + water_sel + ") and not (not symbol h+he+li+be+b+c+n+o+f+ne+na+mg+al+si+p+s+se+cl+br+f) and (not resn mse)"

    # Save the ligand of this chain using surface representation
    render_surf(ligand_sel, "ligand_surf_" + chain + ".wrl")

    # Save the ligand of this chain using sticks representation
    render_sticks(ligand_sel, "ligand_sticks_" + chain + ".wrl")

    # Save the ligand of this chain using balls representation (0.2 * van der
    # waals radius)
    # render_spheres(ligand_sel, "ligand_balls_" + chain + ".wrl")  # Doesn't seem to exist

    # Save the ligand of this chain using VDW representation (1.0 * van der
    # waals radius)
    render_vdw(ligand_sel, "ligand_vdw_" + chain + ".wrl")

    ##################################################################
    # Save the surrounding-residue obj files. In VMD I use this selection:
    # "(same residue as (protein within 8 of ((chain $chain) and (not protein and not water) and not ((not element N C O P S Se Cl Br F) and mass > 16) and (not resname MSE))))"
    ##################################################################

    surrounding_residues_sel = "byres ((" + all_protein_sel + ") within 8 of (" + ligand_sel + "))"

    # Save the surrounding residues of this chain using surface representation
    render_surf(surrounding_residues_sel, "interacting_surf_" + chain + ".wrl")

    # Save the surrounding residues of this chain using sticks representation
    render_sticks(surrounding_residues_sel, "interacting_sticks_" + chain + ".wrl")

    # Save the surrounding residues of this chain using balls representation
    # (0.2 * van der waals radius)
    # some_code_to_save_to_obj_file(surrounding_residues_sel, "interacting_balls_" + chain + ".wrl")  # Not supported in pymol?

    # Save the surrounding residues of this chain using VDW representation
    # (1.0 * van der waals radius)
    render_vdw(surrounding_residues_sel, "interacting_vdw_" + chain + ".wrl")

    ##################################################################
    # Save the protein obj files. In VMD I use this selection: 
    # "chain $chain and (protein or resname MSE)"
    ##################################################################

    protein_sel = "(chain " + chain + ") and (" + all_protein_sel + ",mse)"

    # Save the protein of this chain using surface representation
    render_surf(protein_sel, "protein_surf_" + chain + ".wrl")

    # Save the protein of this chain using sticks representation
    render_sticks(protein_sel, "protein_sticks_" + chain + ".wrl")

    # Save the protein of this chain using balls representation (0.2 * van der
    # waals radius)
    # some_code_to_save_to_obj_file(protein_sel, "protein_balls_" + chain + ".wrl")  # Doesn't seem to exist

    # Save the protein of this chain using VDW representation (1.0 * van der
    # waals radius)
    render_vdw(protein_sel, "protein_vdw_" + chain + ".wrl")

    # Save the protein of this chain using ribbon representation
    render_cartoon(protein_sel, "protein_ribbon_" + chain + ".wrl")

    ##################################################################
    # Save the metal obj files. In VMD I use this selection: 
    # "(chain $chain) and (not element N C O P S Se Cl Br F) and (mass > 16) and (not resname MET CYS MSE)"
    ##################################################################

    # Save the protein of this chain using VDW representation (1.0 * van der
    # waals radius)
    some_code_to_save_to_obj_file(filename="metals_" + chain + ".wrl")



# cmd.quit()
