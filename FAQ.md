Frequently Asked Questions
==========================

"Remove Doubles" and Blender 2.79b
----------------------------------

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