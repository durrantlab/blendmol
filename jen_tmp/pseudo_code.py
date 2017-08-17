# Here put code to setup the scene. Things like positioning the camera, making
# carbons gray, etc.

# Load in the PDB file M2_traj.pdb. Make sure it is set to the first frame.

# Get all the unique chains in the protein. This will be different for each
# PDB.
chains = ["code", "here", "to", "get", "chains", "as", "list"]

# For each chain, separate meshes
for chain in chains:
    ##################################################################
    # First save the ligand obj files. In VMD, I use this selection:
    # "(chain $chain) and (not protein and not water) and not ((not element N C O P S Se Cl Br F) and mass > 16) and (not resname MSE)"
    ##################################################################
    
    # Save the ligand of this chain using surface representation
    some_code_to_save_to_obj_file(filename="ligand_surf_" + chain + ".obj/.wrl/.whatever")

    # Save the ligand of this chain using sticks representation
    some_code_to_save_to_obj_file(filename="ligand_sticks_" + chain + ".obj/.wrl/.whatever")

    # Save the ligand of this chain using balls representation (0.2 * van der
    # waals radius)
    some_code_to_save_to_obj_file(filename="ligand_balls_" + chain + ".obj/.wrl/.whatever")

    # Save the ligand of this chain using VDW representation (1.0 * van der
    # waals radius)
    some_code_to_save_to_obj_file(filename="ligand_vdw_" + chain + ".obj/.wrl/.whatever")

    ##################################################################
    # Save the surrounding-residue obj files. In VMD I use this selection:
    # "(same residue as (protein within 8 of ((chain $chain) and (not protein and not water) and not ((not element N C O P S Se Cl Br F) and mass > 16) and (not resname MSE))))"
    ##################################################################

    # Save the surrounding residues of this chain using surface representation
    some_code_to_save_to_obj_file(filename="interacting_surf_" + chain + ".obj/.wrl/.whatever")

    # Save the surrounding residues of this chain using sticks representation
    some_code_to_save_to_obj_file(filename="interacting_sticks_" + chain + ".obj/.wrl/.whatever")

    # Save the surrounding residues of this chain using balls representation
    # (0.2 * van der waals radius)
    some_code_to_save_to_obj_file(filename="interacting_balls_" + chain + ".obj/.wrl/.whatever")

    # Save the surrounding residues of this chain using VDW representation
    # (1.0 * van der waals radius)
    some_code_to_save_to_obj_file(filename="interacting_vdw_" + chain + ".obj/.wrl/.whatever")

    ##################################################################
    # Save the protein obj files. In VMD I use this selection: 
    # "chain $chain and (protein or resname MSE)"
    ##################################################################

    # Save the protein of this chain using surface representation
    some_code_to_save_to_obj_file(filename="protein_surf_" + chain + ".obj/.wrl/.whatever")

    # Save the protein of this chain using sticks representation
    some_code_to_save_to_obj_file(filename="protein_sticks_" + chain + ".obj/.wrl/.whatever")

    # Save the protein of this chain using balls representation (0.2 * van der
    # waals radius)
    some_code_to_save_to_obj_file(filename="protein_balls_" + chain + ".obj/.wrl/.whatever")

    # Save the protein of this chain using VDW representation (1.0 * van der
    # waals radius)
    some_code_to_save_to_obj_file(filename="protein_vdw_" + chain + ".obj/.wrl/.whatever")

    # Save the protein of this chain using ribbon representation
    some_code_to_save_to_obj_file(filename="protein_ribbon_" + chain + ".obj/.wrl/.whatever")

    ##################################################################
    # Save the metal obj files. In VMD I use this selection: 
    # "(chain $chain) and (not element N C O P S Se Cl Br F) and (mass > 16) and (not resname MET CYS MSE)"
    ##################################################################

    # Save the protein of this chain using VDW representation (1.0 * van der
    # waals radius)
    some_code_to_save_to_obj_file(filename="metals_" + chain + ".obj/.wrl/.whatever")



