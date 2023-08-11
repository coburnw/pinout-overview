
# Pinout Generator

A very work in progress pinout diagram generator using Python and drawsvg

This has been heavily reworked, arguably to make it more modifiable.  We will see.

# Usage

## Config Files

Configuration can be split across multiple config files to allow for sharing of common properties
> "style" fields are standard SVG properties like fill, font_family, etc.

#### Define family function types
function types is a dictionary of style for function types that might be
available on a broad range of products.  It defines colors, fonts and the
description of the functions.  I suspect it will mostly be hand edited.

``` json
"section": "family",
"name": "dxcore_functions",
"shape": "quad_label",
"styles": {
   "usart": {
      "description": "UART0",
      "box_style": {
         "stroke": "#CC0092",
         "fill": "#FFA3E5"
      },
      "text_style": {
         "font_family": "Roboto Mono",
         "fill": "black"
      }
   },
   "twi": {
      "description": "I2C",
      "skip": false,
      "box_style": {
         "stroke": "#00B8CC",
         "fill": "#88EBF7"
      },
      "text_style": {
         "font_family": "Roboto Mono",
         "fill": "black"
      }
   }
}

```

#### Define family port pins
This is a dictionary of port pins containing lists of usable functions for
some range of variants.  Most likely machine generated.

``` json
{
    "section": "family",
    "name": "dd14_20",
    "styles": "dxcore_functions",
    "functions": {
        "PA0": [
            {
                "name": "PA0",
                "type": "pin",
                "alt": false
            },
            {
                "name": "XTAL",
                "type": "sys",
                "alt": false
            }
        ]
    }
}
```

#### Map Pins to physical output on IC
The pinmap is a simple ordered list of pin or port-names.
Item zero is the name given to pin 1 of the chip.  The original implementation
used a list of sub pins for multirow function pins.  That doesnt seem to flow
well, and i am looking at adding a split option to the pinout section to split a
row of functions into two.

#### Chip options
the variant file describes how to buid the svg and is most likely machine generated.
  * section is this directory.  probably shouldnt be changed...
  * name is basename of both this config file and the target svg file.
  * Family holds the basename of the family functions file defined above.
  * pinout holds the mapping of pin-number to pin-names
  * package type of qfn, qfp, or sop, and appropriate pin counts and text
  * and page amends options of its respective page template.

```
{
    "section": "variant",
    "name": "DD20",
    "family": "dd14_20",
    "package": {
        "type": "qfn",
        "pin_count": 20,
        "text1": "AVR16DD20\nAVR32DD20\nAVR64DD20",
        "text2": "VQFN20"
    },
    "pinout": {
        "split": "tca",
        "pin_map": [
    	    "PA4",
            "PA5",
            "PA6"
	]
    
    },
    "page": {
        "header": {
            "text1": "big title",
            "text2": "sub title"
        },
        "quadrant": {
            "text1": "sldkfjlksjlkjsadfdjalksfdslkjalksf",
            "text2": "jsadklfdslkjalksfsldkfjlksjlk",
            "text3": "jalksfsldkfjlkjalksfksjlkjsadklfdsl",
            "text4": "fdslkjalksfsldkfjlksjlkjsadkl"
        }
    }
}

```

## Generating the Images

To generate the variant config files

``` shell
 python extract_variants.py [variant_range]
```

To generate a single Image

``` shell
 python pinout.py [variant_name]
```

# TODO
- [ ] legend
- [ ] merge changes to qfp and sop packages
- [ ] add split option
- [ ] handle quadrant text internally rather than asking the browser to render it

- [ ] Error checking
- [ ] Documentation
- [ ] Improve SVG generation
- [ ] Add different styling options
- [x] Improve modularity to allow for more complex footprints
- [ ] Clean up a lot of bad programming and improve readability 
- [x] Use config files and cli
