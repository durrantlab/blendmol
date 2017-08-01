import os
import tempfile
import shutil
import glob
import bpy

class ExternalInterface:
    def make_tmp_dir(self):
        self.tmp_dir = tempfile.mkdtemp() + os.sep
        self.script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + "scripts" + os.sep

    def populate_tmp_dir(self, ext, filename):
        pass

    def get_ext(self, filename):
        _, ext = os.path.splitext(filename)
        ext = ext.upper()
        return ext

    def run_external_program(self, exec_path):
        pass

    def import_all_objs(self, my_operator):
        # Import the objs, keeping track of existing ones
        existing_obj_names = set([obj.name for obj in bpy.data.objects])
        for filename in glob.glob(self.tmp_dir + "*.obj"):
            bpy.ops.import_scene.obj(filepath=filename)
        new_obj_names = set([obj.name for obj in bpy.data.objects]) - existing_obj_names

        new_objs = [bpy.data.objects[obj_name] for obj_name in new_obj_names]

        # Also go through and remove doubles
        if my_operator.remove_doubles == True:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in new_objs:
                bpy.context.scene.objects.active = obj
                obj.select = True
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')
                
                # Remove doubles
                bpy.ops.mesh.remove_doubles(threshold=0.000001)

                # Recalculate normals
                bpy.ops.mesh.normals_make_consistent()

                bpy.ops.object.mode_set(mode = 'OBJECT')

        # Scale 0.1. VMD output is huge. So units are nm, not Angstroms.
        if my_operator.nanometers == True:
            for obj in new_objs:
                obj.scale = [0.1, 0.1, 0.1]
        
        # Reset rotation. Weird that this is imported wrong...
        for obj in new_objs:
            obj.rotation_euler = [0.0, 0.0, 0.0]

        return new_obj_names

    def del_tmp_dir(self):
        # Delete tmp directory.
        shutil.rmtree(self.tmp_dir)

    def make_vis_script(self, my_operator):
        pass

