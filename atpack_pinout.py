import os
import sys
import json

from pinoutOverview import page
from pinoutOverview import pinouts
from pinoutOverview import config as Config
from pinoutOverview import packages
from pinoutOverview import pins
from pinoutOverview import functions

from template import function_label
from template import dxcore

class Variant():
    def __init__(self, data):
        #print("loading variant: {}".format(data))
        atpack = Atpack(data)
        self.config = atpack.build_variant_config()

        self.family_functions = atpack.get_family_functions()

        self.page = self.config.page
        self.pins = pins.Pins(self.config.pins, self.family_functions.functions)
        self.package = packages.PackageFactory(self.config.package, self.pins.spacing)
        
        return

class Atpack():
    def __init__(self, variant):
        self.variant = variant
        return

    def build_variant_config(self):
        config = Config.VariantConfig()
        config.package = self.get_package_config()
        config.page = self.get_page_config()
        config.pins = dict(pin_map=self.variant['pin_map'], split='')
        
        return config

    def get_package_config(self):
        package_map = dict(soic='sop')
        shape, sep, count = self.variant['shape'].partition('-')
        if shape.lower() in package_map:
            shape = package_map[shape.lower()]
            
        package = dict(
            type = shape,
            pin_count = int(count),
            text1 = self.variant['part_range'],
            text2 = self.variant['shape']
        )
        
        return package

    def get_page_config(self):
        page = dict(
            template = dxcore.page_template,
            data = dict(
                header = dict(
                    text1 = 'xxx',
                    text2 = ''
                ),
                quadrant = dict(
                    text1 = '{}'.format(self.variant['notes'][0]),
                    text2 = '{}'.format(self.variant['notes'][1]),
                    text3 = '{}'.format(self.variant['notes'][2]),
                    text4 = '{}'.format(self.variant['notes'][3])
                )
            )
        )
        
        return page
    
    def get_family_functions(self):
        family_functions = Config.FamilyFunctions()
        family_functions.styles = 'dxcore_functions'
        
        for pin_name, function_list in self.variant['pins'].items():
            #print(pin_name)
            for key,values in function_list.items():
                #print(' {} {}'.format(key,values))

                # get function type and peripheral index
                ftype = key.rstrip('0123456789').lower()
                try:
                    index = int(key[len(ftype):])
                except:
                    index = 0
                    
                if ftype in ['tca','tcb','tcd']:
                    ftype = 'pwm'

                if ftype in ['ac', 'ain', 'zcd']:
                    ftype = 'analog'

                if ftype in ['usart', 'twi', 'spi', 'vrefa']:
                    ftype = 'serial'
                    
                if ftype in ['ccl', 'evsys']:
                    ftype = 'logic'
                    
                if ftype in ['pin', 'vddio', 'vdd', 'gnd']:
                    index = 0

                for fname in values:
                    fname = str(fname)
                    #print(fname)

                    if index > 0:
                        fname = '{},{}'.format(index, fname)

                    is_alt = False
                    if 'ALT' in fname:
                        is_alt = True
                        fname = fname.replace('_ALT','')
                    
                    family_functions.append(pin_name, fname, ftype, is_alt)

        return family_functions


def load(name):
    section = 'atpack'

    basename = os.path.basename(name)
    name, suffix = os.path.splitext(basename)

    path = '{}/{}.json'.format(section,name)
    print('importing config file: {}'.format(path))

    with open(path, 'r') as fp:
        variants = json.load(fp)
        
    return variants
    

if __name__ == "__main__":
    
    functions.Label(template=dxcore.label_template)
    functions.Function(function=None, type_templates=dxcore.function_types)

    layout = 'horizontal' #'orthogonal' # horizontal, diagonal

    variants = load(sys.argv[1])
    for name, item in variants.items():
        variant = Variant(item)
        pinout = pinouts.PinoutFactory(layout, variant)
    
        page = page.Page(variant.page, pinout) #.page

        print('saving to {}'.format(name))
        page.save(name)
        

