Frequently Asked Questions
==========================

Why doesn't BlendMol work with Blender 2.79 or older?
-----------------------------------------------------

The latest version of BlendMol (1.1) works with Blender 2.8. Use BlendMol 1.0
if you run Blender 2.79. Older versions of Blender are not supported.

Why can't I import via PyMol on Blender 2.8/BlendMol 1.1?
---------------------------------------------------------

There is a bug in the Blender 2.8 X3D (WRL) importer that breaks PyMol import.
Preliminary tests using Blender 2.81 alpha suggest this bug will be addressed
in the next version of Blender.

Why does "Remove Doubles" produce mesh holes in Blender 2.79b/BlendMol 1.0?
---------------------------------------------------------------------------

When using Blender 2.79b, BlendMol's "Remove Doubles" inappropriately removes
some faces, leaving holes in the mesh. This does not happen when using older
versions of Blender (e.g., 2.79). It is a Blender bug. We have filed a [bug
report](https://developer.blender.org/T56074) with the Blender team and so
expect that future Blender versions will resolve this issue.

Fortunately, most BlendMol users will not need the "Remove Doubles" feature.
If you do, please use an older version of Blender.
[MeshLab](http://www.meshlab.net/) can also remove doubles. Exporting from
Blender, processing in MeshLab, and reimporting into Blender may be another
possible solution.
