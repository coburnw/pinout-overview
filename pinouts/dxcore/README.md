# Pinout-Overview config files for DxCore

To compile the config files to an svg file:
`python pinout.py pinouts/dxcore/dd20_14/vqfn_20.yaml`
 or
`python pinout.py pinouts/dxcore/dd20_14/qfp_20.yaml`

 * default directory contains default configurations used across variants
   * `pin_types.yaml`   Available pin functions containing key, description,
   and styling for function labels
   * `package_qfn.yaml` shape and style of package
   * `pin_qfn.yaml`     shape and style of package pin
   * `label_qfn.yaml`   shape and style of function label
   
 * variant directories (such as DD20_14) contain variant specific configuration
   * `vqfn_20.yaml`     main variant configuration file.  Sets up page and
   pulls in other config files.
   * `vqfn_pins.yaml`   defines available pin functions on variant
   * `vqfn20_text.yaml` contains the four quandrant text in markdown

# Notes
  * The markdown library used follows John Gruber's
  [markdown](https://daringfireball.net/projects/markdown/syntax) syntax.
  * The wikipedia page has a usable synopsis of
  [yaml](https://en.wikipedia.org/wiki/YAML) syntax
  * Both yaml and markdown pass html without modification accommodating more
  advanced styling.  Embedding css might be a nice future enhancement.

