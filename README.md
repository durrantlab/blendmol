# BlendMol

## Table of Contents

- [BlendMol 1.3](#blendmol-10)
- [The Latest Version](#the-latest-version)
- [Authors and Contacts](#authors-and-contacts)
- [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Detailed Installation Instructions](#detailed-installation-instructions)
- [BlendMol Usage](#blendmol-usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
    - [Video S2: Neuraminidase](#video-s2-neuraminidase)
    - [Video S3: BlendMol/Pyrite](#video-s3-blendmolpyrite)
- [Example Files](#example-files)

## BlendMol 1.3

BlendMol 1.3 is a Blender 2.8 plugin that can easily import VMD "Visualization
State" files. It interfaces directly with the VMD executable to 1) normalize
the VMD camera position, 2) render molecular meshes to Blender-compatible
files, 3) import those files into Blender, and 4) optimize mesh geometries as
needed.

One can also work entirely within Blender, without ever opening a dedicated
molecular-visualization program. If the user provides a PDB ID or a PDB file,
the plugin uses VMD to automatically generate a simple, default visualization.

BlendMol empowers scientific researchers and artists by marrying molecular
visualization and industry-standard rendering techniques. The plugin works
seamlessly with the popular analysis program VMD. Users import into Blender
the very molecular representations they set up in VMD.

## The Latest Version

To view the source code of the latest version, visit
[http://git.durrantlab.com/jdurrant/blendmol](http://git.durrantlab.com/jdurrant/blendmol).

Visit [http://durrantlab.com/blendmol/](http://durrantlab.com/blendmol/) to:

- read the documentation
- suggest an improvement
- point out a bug
- ask a question about usage

## Authors and Contacts

BlendMol was created by Jacob Durrant
([durrantj@pitt.edu](mailto:durrantj@pitt.edu)).

## Installation

### Quick Start

BlendMol installation within Blender is the same as with any Blender plugin:

1. Visit [http://durrantlab.com/blendmol/](http://durrantlab.com/blendmol/) to
   download the BlendMol ZIP file.
2. Within Blender, click on the ```Edit > Preferences...``` menu item to open
   the ```Blender Preferences``` window.
3. Click the ```Add-ons``` button at the top of that window to open the
   add-ons panel.
4. Specify the location of the downloaded ZIP file by clicking on the
   ```Install...``` button at the bottom of the window.
5. Once installed, click the ```Import-Export: BlendMol - PDB/VMD```
   checkbox to activate the plugin.
6. To keep the plugin active after Blender restarts, you may need to check
   the ```Save Preferences``` option via the hamburger menu at the bottom
   of the window.
7. Critical plugin preferences can be set from the Add-ons panel by clicking
   the expanding carat. See the BlendMol manuscript for full details.

### Detailed Installation Instructions

(Note that some of the details in the pictures below are outdated, but they
still illustrate the basic steps.)

[Download the BlendMol plugin](http://durrantlab.com/blendmol/).

Click `Edit -> Preferences...` to install the plugin.

![Edit -> Preferences...](http://durrantlab.com/apps/blendmol/docs/fig1.jpg)

Click the `Install...` button.

![Install...](http://durrantlab.com/apps/blendmol/docs/fig2.jpg)

Select the BlendMol ZIP file and click the `Install...` button.

![Install...](http://durrantlab.com/apps/blendmol/docs/fig3.jpg)

Tick the checkbox (yellow) to activate the plugin. Then click the down
caret button (red) to show the plugin options. Specify the location of the
VMD executable using the appropriate button (green).

![VMD Executables](http://durrantlab.com/apps/blendmol/docs/fig4.jpg)

If you would like BlendMol to auto load when you restart Blender, use the
`Save Preferences` option.

![Save Preferences](http://durrantlab.com/apps/blendmol/docs/fig45.jpg)

## BlendMol Usage

(Note that some of the details in the pictures below are outdated, but they
still illustrate the basic steps.)

### Basic Usage

![Basic Usage Video Tutorial](http://durrantlab.com/apps/blendmol/docs/VideoS1.BlendMol-Tutorial.mp4)

Click `File -> Import -> PDB/VMD (.pdb, .vmd, .tcl)`.

![File -> Import -> PDB/VMD (.pdb, .vmd, .tcl)](http://durrantlab.com/apps/blendmol/docs/fig5.jpg)

To load a PDB file, select the filename. Additional options (not shown) are
given in a panel to the left. When ready, press the `Import PDB/VMD/TCL`
button.

![Import PDB/VMD/TCL](http://durrantlab.com/apps/blendmol/docs/fig6.jpg)

VMD state files can be similarly loaded.

![Import PDB/VMD/TCL](http://durrantlab.com/apps/blendmol/docs/fig7.jpg)

![Import PDB/VMD/TCL](http://durrantlab.com/apps/blendmol/docs/fig8.jpg)

You can also type a PDB ID into the filename field (boxed in red). BlendMol will
download the PDB model directly from the Protein Data Bank.

![Import PDB/VMD/TCL](http://durrantlab.com/apps/blendmol/docs/fig9.jpg)

### Advanced Usage

#### Video S2: Neuraminidase

![Video S2: Neuraminidase](http://durrantlab.com/apps/blendmol/docs/VideoS2.Neuraminidase.mp4)

Creating Video S2 required the use of many advanced Blender features that are
unrelated to BlendMol's core functionality. A detailed tutorial is beyond the
scope of this document, but interested users may benefit from the
[Blender Guru](https://www.youtube.com/user/AndrewPPrice) channel on YouTube,
which provides many useful tutorials.

#### Video S3: BlendMol/Pyrite

Coupling BlendMol and [Pyrite](https://durrantlab.pitt.edu/pyrite/), another
Durrant-lab plugin, simplifies the Blender-based visualization of molecular
dynamics simulations.

![Video S3: Pyrite Demo](http://durrantlab.com/apps/blendmol/docs/VideoS3.Pyrite-Demo.mp4)

![Video S4: BlendMol/Pyrite Tutorial](http://durrantlab.com/apps/blendmol/docs/VideoS4.BlendMol-Pyrite-Tutorial.mp4)

## Example Files

Example files can be found in `./examples/`.

- `./examples/vmd-files/` includes a PDB and VMD state file.
- `./examples/pymol-files/` includes a PyMOL session file.
- `./examples/web-files/baked-lighting-shadows/` demonstrates browser-based
  molecular visualization with advanced lighting and shadows.
- `./examples/web-files/virtual-reality/` demonstrates browser-based
  virtual-reality molecular visualization.
