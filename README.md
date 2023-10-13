
# Pinout Overview Library

pinout diagram library using Python and drawsvg

A heavily reworked fork of [pinout-overview](https://github.com/Tengo10/pinout-overview) into a library by
stripping out all parts unrelated to the pinout and legend objects themselves.

Note:  At this point documentation is more conceptual than literal.  See
[dx-pinouts](http://github.com/coburnw/dx-pinouts.git) repository for a 
working example.  The library docstrings are fairly helpful.

## Dependencies
 Uses the [DrawSVG](https://github.com/cduck/drawsvg) library for drawing the svg elements 

## Install
```commandline
mkdir <project-master>
cd <project-master>
python -m venv --prompt <my-prompt> venv
source venv/bin/activate
git clone github.com/coburnw/pinout-overview
cd pinout-overview
git checkout lib
pip install --editable .
```

## Usage

Subclass the following: 
1. Function() Create a subclass for each function that may be displayed in a pinout.  
Override any style attributes to customise the functions visual, and any 
exposed methods to parse the format of the source data.
2. Pinmap() A mapping of pin numbers to Pad objects.  
Add a method to parse the source data, instantiating a Function object for each, and
appending to the proper Pad.
3. Package() messy 

instantiate a Pinmap, parse the device data for pad/function relationships and append.

parse the device data for package shapes and pincounts and instantiate a Package.

Choose a layout: 'horizontal', 'diagonal' or 'orthogonal',
instantiate a Pinout(layout, package, pinmap) object and place

Choose a layout: 'horizontal' or 'vertical'
instantiate a Legend(layout, pinmap) object and place

## Exposed Classes

#### _Region()_ A subclass of the DrawSVG Group
* Adds simplistic
knowledge of a regions size and position.  Since Pinout and Legend are derived from
Region the application can use their 'width', 'height', 'x' and 'y' attributes
to dynamically help with size and placement of other items on the page. 

#### _Function()_ A single function label
* The primary visual effect of interest.  A container for a functions data
to be visually represented on a page ultimately associated with some pin.
* 
#### _Functions()_ A single row of function labels with a connecting line
* rarely needed by the library user.

#### _Pad(pad_name)_ A group of functions assigned to a specific pad
* rarely needed by the library user.

#### _Pinmap([pad_names])_ A mapping of pin numbers to Pad's
* The pad name list must be in order and without any missing pins.

#### _PackageData()_ A container for package data
* This should be moved to a package subclass

#### _Package()_ a displayable package
* QFP, QFN, or SOP

#### _Pinout(layout, pinmap, package)_ A package with pad fanout
* layout (str): 'horizontal', 'diagonal', or 'orthogonal'
* pinmap (Pinmap): an initialized Pinmap object
* package (Package): an initialized Package object

#### _Legend(layout, pinmap)_ describes function types
* layout (str): Vertical or Horizontal
* pinmap (Pinmap):

## Config Files

There are no config files.  Configuration is done by subclassing and overriding.

### Scaling
The size of the function label determines the scale of many of the objects.
Override the functions width and height attributes.

## TODO
- [x] legend
- [x] merge changes to qfp and sop packages
- [x] add split option
- [x] handle quadrant text internally rather than asking the browser to render it
- [ ] expand on label size for object scaling

- [ ] Error checking
- [ ] Documentation
- [ ] Improve modularity to allow for more complex footprints
