BlendMol
========

BlendMol is a Blender plugin that can easily import VMD "Visualization State"
and PyMOL "Session" files. It interfaces directly with the VMD or PyMOL
executable to 1) normalize the VMD/PyMOL camera position, 2) render molecular
meshes to Blender-compatible files, 3) import those files into Blender, and 4)
optimize mesh geometries as needed. 

One can also work entirely within Blender, without ever opening a dedicated
molecular-visualization program. If the user provides a PDB ID or a PDB file,
the plugin uses VMD or PyMOL to automatically generate a simple, default
visualization.

BlendMol empowers scientific researchers and artists by marrying molecular
visualization and industry-standard rendering techniques. The plugin works
seamlessly with popular analysis programs (i.e., VMD/PyMOL). Users import into
Blender the very molecular representations they set up in VMD/PyMOL.

The Latest Version
==================

To view the source code of the latest version, visit
[http://git.durrantlab.com/jdurrant/blendmol](http://git.durrantlab.com/jdurrant/blendmol).
The same code is mirrored on GitHub.

Visit [http://durrantlab.com/blendmol/](http://durrantlab.com/blendmol/) to:

* read the documenation
* suggest an improvement
* point out a bug
* ask a question about usage


Installation
============

BlendMol installation within Blender is the same as with any Blender plugin:

1. Visit [http://durrantlab.com/blendmol/](http://durrantlab.com/blendmol/) to
   download the BlendMol ZIP file. 
2. Within Blender, click on the ```File > User Preferences...``` menu item to
   open the ```Blender User Preferences``` window. 
3. Click the ```Add-ons``` button at the top of that window to open the
   add-ons panel. 
4. Specify the location of the downloaded ZIP file by clicking on the
   ```Install Add-on from File...``` button at the bottom of the window. 
5. Once installed, click the ```Import-Export: BlendMol - PDB/VMD/PyMOL```
   checkbox to activate the plugin. 
6. To keep the plugin active after Blender restarts, click the ```Save User
   Settings``` button at the bottom of the window.
7. Critical plugin preferences can be set from the Add-ons panel by clicking 
   the expanding carat. See the BlendMol manuscript for full details.

Example Files
=============

Example files can be found in `./examples/`.

* `./examples/vmd-files/` includes a PDB and VMD state file.
* `./examples/pymol-files/` includes a PyMOL session file.
* `./examples/web-files/baked-lighting-shadows/` demonstrates browser-based
  molecular visualization with advanced lighting and shadows.
* `./examples/web-files/virtual-reality/` demonstrates browser-based
  virtual-reality molecular visualization.

Authors and Contacts
====================

BlendMol was created by Jacob Durrant
([durrantj@pitt.edu](mailto:durrantj@pitt.edu)).

Tutorial
========

![Video Tutorial](http://durrantlab.com/apps/blendmol/docs/VideoS1.BlendMol-Tutorial.mp4)


Installation
------------

[Download the BlendMol plugin](http://durrantlab.com/blendmol/).

Click on `File -> User Preferences...` to install the plugin.

![Video Tutorial](http://durrantlab.com/apps/blendmol/docs/fig1.jpg)

Click the `Install Add-on from File...` button.

![Video Tutorial](http://durrantlab.com/apps/blendmol/docs/fig2.jpg)

Select the BlendMol ZIP file and click the `Install Add-on from File...` button.

![Video Tutorial](http://durrantlab.com/apps/blendmol/docs/fig3.jpg)

Tick the checkbox (yellow) to activate the plugin. Then click the down caret
button (red) to show the plugin options. Specify the location of the VMD and
PyMol executables using the appropriate buttons (green).

![Video Tutorial](http://durrantlab.com/apps/blendmol/docs/fig4.jpg)

If you would like BlendMol to auto load when you restart Blender, click the
`Save User Settings` button.

![Video Tutorial](http://durrantlab.com/apps/blendmol/docs/fig45.jpg)

Plugin Usage
------------

