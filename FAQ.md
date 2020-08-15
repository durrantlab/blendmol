Frequently Asked Questions
==========================

Why doesn't BlendMol work with Blender 2.79 or older?
-----------------------------------------------------

The latest version of BlendMol (1.3) works with Blender 2.8. Use BlendMol 1.0
if you run Blender 2.79. Older versions of Blender are not supported.

Why can't I import via PyMol on Blender 2.8/BlendMol 1.3?
---------------------------------------------------------

The latest version of BlendMol no longer supports PyMOL. The PyMOL
command-line interface appears to be inconsistent across versions, and there
was a bug in the Blender 2.8 X3D (WRL) importer that broke PyMOL import. That
having been said, it's possible Blender has fixed the importer bug, and you
may have a version of PyMOL with a CLI that is BlendMol compatible. If you'd
like to try your luck with PyMOL, be sure to use [BlendMol
1.2](https://git.durrantlab.pitt.edu/jdurrant/blendmol), the latest version
with PyMOL support.

Why does "Remove Doubles" produce mesh holes in Blender 2.79b/BlendMol 1.0?
---------------------------------------------------------------------------

When using Blender 2.79b, BlendMol's "Remove Doubles" inappropriately removes
some faces, leaving holes in the mesh. This does not happen when using older
versions of Blender (e.g., 2.79), and we have not noticed it in Blender 2.8
either. It is a Blender 2.79b bug. We have filed a [bug
report](https://developer.blender.org/T56074) with the Blender team and so
expect that future Blender versions will resolve this issue.

Fortunately, most BlendMol users will not need the "Remove Doubles" feature.
If you do, please use a newer version of Blender.
[MeshLab](http://www.meshlab.net/) can also remove doubles. Exporting from
Blender, processing in MeshLab, and reimporting into Blender may be another
possible solution.
