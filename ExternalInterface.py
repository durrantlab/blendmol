import os
import tempfile
import shutil
import glob
import bpy
import mathutils

class ExternalInterface:
    """
    A class for managing how the program interfaces with external rendering
    programs (VMD, PyMol).
    """

    def make_tmp_dir(self):
        """
        Make a temporary directory.
        """

        self.tmp_dir = tempfile.mkdtemp() + os.sep
        self.script_dir = (
            os.path.dirname(os.path.realpath(__file__)) + os.sep +
            "scripts" + os.sep
        )

    def get_ext(self, filename):
        """
        Given a filename, get the extension.
    
        :param str filename: The filename.

        :returns: The extension.
        :rtype: :class:`str`
        """

        _, ext = os.path.splitext(filename)
        ext = ext.upper()
        return ext

    def run_external_program(self, exec_path):
        """
        Runs the executable. This will be overwritten by child classes.

        :param str exec_path: The path to the executable.
        """

        pass

    def import_all_mesh_files(self, my_operator):
        """
        Import all the meshes produced by the external visualization program
        (VMD or PyMol), saved to the temporary directory.

        :param ??? my_operator: The operator, used to access user-parameter
                    variables.

        :returns: List of the names of the added meshes.
        :rtype: :class:`str[]`
        """

        try: bpy.ops.object.mode_set(mode = 'OBJECT')
        except: pass

        meshes_to_join = {}

        # Import the objs, keeping track of existing ones
        orig_existing_obj_names = set([obj.name for obj in bpy.data.objects])
        mask1 = self.tmp_dir + "*.obj"
        mask2 = self.tmp_dir + "*.wrl"
        for filename in glob.glob(mask1) + glob.glob(mask2):
            print("Importing " + filename + "...")

            # Keep track of existing objects.
            exist_obj_names_tmp = set([obj.name for obj in bpy.data.objects])

            # Load in new objects.
            if filename.upper().endswith(".OBJ"):
                bpy.ops.import_scene.obj(filepath=filename)
                # Not sure why OBJ imported from VMD are rotated.
                initial_rotation = (90, 0, 0)
            else:
                bpy.ops.import_scene.x3d(filepath=filename)
                # Not sure why WRL imported from PyMol are rotated.
                initial_rotation = (270, 0, 180)

            # Get new objects.
            new_obj_names_tmp = set([
                obj.name for obj in bpy.data.objects
            ]) - exist_obj_names_tmp

            new_objs_tmp = [bpy.data.objects[obj_name] 
                            for obj_name in new_obj_names_tmp 
                            if bpy.data.objects[obj_name].type == "MESH"]
            meshes_to_join[filename] = new_objs_tmp

        # Get a list of the names of objects just added.
        new_obj_names = set([
            obj.name for obj in bpy.data.objects
        ]) - orig_existing_obj_names

        # Keep the ones that are meshes
        new_objs = [bpy.data.objects[obj_name] 
                    for obj_name in new_obj_names 
                    if bpy.data.objects[obj_name].type == "MESH"]

        # Delete the ones that aren't meshes
        # See https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object
        for obj_name in new_obj_names:
            obj = bpy.data.objects[obj_name]
            if obj.type != "MESH":
                bpy.ops.object.select_all(action='DESELECT')
                obj.select = True
                bpy.ops.object.delete()
        new_obj_names = [o.name for o in new_objs]

        # Apply the rotations of all meshes
        for obj in new_objs:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = obj
            obj.select = True
            bpy.ops.object.transform_apply(
                location=False, scale=False, rotation=True
            )

        # Join some of the objects
        for filename in meshes_to_join.keys():
            objs_to_merge = meshes_to_join[filename]
            if len(objs_to_merge) > 1:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in objs_to_merge:
                    obj.select = True
                bpy.context.scene.objects.active = objs_to_merge[0]
                bpy.ops.object.join()
            
            if len(objs_to_merge) > 0:
                objs_to_merge[0].name = "MIB__" + os.path.basename(filename)[:-4]
            else:
                # Sometimes PyMol (at least) doesn't save a file at all,
                # perhaps because the selection was empty?
                pass

        # Make sure origins of all new meshes is 0, 0, 0
        # See https://blender.stackexchange.com/questions/35825/changing-object-origin-to-arbitrary-point-without-origin-set
        # new_origin = mathutils.Vector((0, 0, 0))
        for obj in bpy.data.objects:
            if obj.name.startswith("MIB__"):
                loc = obj.location
                obj.data.transform(mathutils.Matrix.Translation(loc))
                obj.matrix_world.translation -= loc
        
        # Now rotate appropriately and apply
        # Reset rotation. Weird that this is imported wrong...
        for obj in new_objs:
            for i in range(3):
                obj.rotation_euler[i] = (
                    obj.rotation_euler[i] - initial_rotation[i] / 180 * 3.1416
                )
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = obj
            obj.select = True
            bpy.ops.object.transform_apply(
                location=False, scale=False, rotation=True
            )

        # Scale 0.1. VMD output is huge. So units are nm, not Angstroms.
        # Scale to nanometers if necessary.
        if my_operator.nanometers == True:
            for obj in bpy.data.objects:
                if obj.name.startswith("MIB__"):
                    obj.scale = [0.1, 0.1, 0.1]

        # Also go through and remove doubles
        if my_operator.remove_doubles == True:
            for obj in bpy.data.objects:
                if obj.name.startswith("MIB__"):
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.scene.objects.active = obj
                    obj.select = True

                    # try:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    # except:
                        # Must already be in EDIT mode.
                        # pass

                    bpy.ops.mesh.select_all(action = 'SELECT')
                    
                    # Remove doubles. Note that doesn't always fully work with
                    # PyMol sticks.
                    bpy.ops.mesh.remove_doubles(threshold=0.000001)

                    # Recalculate normals
                    bpy.ops.mesh.normals_make_consistent()

                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    obj.name = obj.name[5:]

        return new_obj_names

    def del_tmp_dir(self):
        """
        Delete tmp directory.
        """

        shutil.rmtree(self.tmp_dir)

    def make_vis_script(self, my_operator):
        """
        Make the visualization script to pass to the executable program, and
        save it to the temporary directory. The definition will be overwritten
        in the child classes.

        :param ??? my_operator: The operator, used to access user-parameter
                    variables.
        """

        pass
