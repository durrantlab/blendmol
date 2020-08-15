Changes
=======

1.3
---

* PyMOL no longer supported. Unlike VMD, different versions of PyMOL have
  different command-line interfaces. Accounting for these inconsistent
  interfaces is impractical. If you'd like to try your luck with PyMOL, please
  use [BlendMol 1.2](https://git.durrantlab.pitt.edu/jdurrant/blendmol), the
  latest version with PyMOL support. See `FAQ.md` for more information.
* Applied [Black formatter](https://github.com/psf/black) to improve code
  readability.

1.2
---

* Fixed bug so it is now possible to import files with spaces in their names
  via VMD.

1.1
---

* BlendMol now works with Blender 2.8. Use BlendMol 1.0 for Blender 2.79.
* Added `CONTRIBUTORS.md` and `CHANGES.md` files. Updated `FAQ.md`.
* Fixed bug so it is now possible to import files with spaces in their names
  via VMD.
* Note that PyMol import on Blender 2.8 is broken because of a Blender Bug in
  the X3D importer. Preliminary tests with Blender 2.81 alpha suggest this
  Blender bug will soon be fixed.

1.0
---

Original version.
