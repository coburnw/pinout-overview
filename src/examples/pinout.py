import os
import sys

from pinoutOverview import page
from pinoutOverview import pinouts
from pinoutOverview import config
from pinoutOverview import packages
from pinoutOverview import pins
from pinoutOverview import functions

from template import function_label

class Functions():
    def __init__(self, family_name):
        self.functions = config.FamilyFunctions(family_name)
        functions.Label(template=function_label.label_template)
        
        self.styles = config.FunctionStyles(self.functions.styles)
        functions.Function(function=None, type_templates=self.styles.styles)

        return
    
class Variant():
    def __init__(self, name):
        print("loading variant: {}".format(name))
        self.config = config.VariantConfig(name)
        self.page = self.config.page
        
        self.package = packages.PackageFactory(self.config.package, 30)
        self.functions = Functions(self.config.family)
        self.pins = pins.Pins(self.config.pins, self.functions.functions.functions) #omg
        
        return

if __name__ == "__main__":

    variant = Variant(sys.argv[1])
    
    layout = 'orthogonal' # horizontal, diagonal
    pinout = pinouts.PinoutFactory(layout, variant)
    
    page = page.Page(variant.page, pinout)

    fname = sys.argv[1]
    if len(sys.argv) > 2:
        fname = sys.argv[2]
    page.save(fname)

