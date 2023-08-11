import os
import sys
import json

class ConfigFile():
    def __init__(self, section, name=None):
        self.section = self.get_name(section)
        self.name = name
        if self.name is not None:
            self.name = self.get_name(self.name)

        return
    
    def get_name(self, name):
        basename = os.path.basename(name)
        name, suffix = os.path.splitext(basename)
        
        return name
    
    def path(self, name):
        section = self.section
        if name is None:
            name = self.name
            
        return '{}/{}.json'.format(self.get_name(section), self.get_name(name))
        
    def load(self, name=None):
        print('importing config file: {}'.format(self.path(name)))

        if name is not None:
            self.name = self.get_name(name)

        with open(self.path(self.name), 'r') as fp:
            self.__dict__ = json.load(fp)
        
        return
    
    def save(self, name=None):
        print('exporting config to ' + self.path(name))
    
        if name is not None:
            self.name = self.get_name(name)

        with open(self.path(self.name), 'w') as fp:
            json.dump(self.__dict__, fp, indent=4)
            
        return

    def save_as(self, name):
        raise

# a relationship of pin_name to a list of pin functions for a specific family of parts.
class FamilyFunctions(ConfigFile):
    def __init__(self, name=None):
        section = 'family'
        super().__init__(section, name)

        self.styles = None
        self.functions = dict() 

        if self.name is not None:
            self.load()
            
        return

    def append(self, pin_name, function_name, function_type, is_alt=False):
        func = dict(
            name = function_name,
            type = function_type,
            alt = is_alt
        )

        if pin_name not in self.functions:
            self.functions[pin_name] = []
            
        self.functions[pin_name].append(func)
        return
    
    def initialize(self):
        self.styles = 'functions'
        
        self.functions = dict(
            VDD = [
                dict(
                    alt = False,
                    name = 'VDD',
                    type = 'pin'
                ),
            ],
            GND = [
                dict(
                    alt = False,
                    name = 'GND',
                    type = 'pin'
                ),
            ]
        )

        return
    
# contains a style entry for every possible function of some range of products.  
class FunctionStyles(ConfigFile):
    def __init__(self, name=None):
        section = 'family'
        super().__init__(section, name)

        self.styles = None
        
        if self.name is not None:
            self.load()
                    
        return

    def initialize(self):
        self.styles = dict(
            pin = dict(
                width = 80,
                description = 'PIN NAME',
                box_style = dict(
                    stroke = 'black',
                    fill = 'grey'
                ),
                text_style= dict(
                    font_family = 'Roboto Mono',
                    fill = 'white'
                )
            ),
            vss = dict(
                width = 80,
                description = 'GND',
                box_style = dict(
                    stroke = 'black',
                    fill = 'black'
                ),
                text_style = dict(
                    font_family = 'Roboto Mono',
                    fill = 'white'
                )
            ),
            vdd = dict(
                width = 120,
                description = '2.5V-3.6V',
                box_style = dict(
                    stroke = 'red',
                    fill = 'red'
                ),
                text_style = dict(
                    font_family = 'Roboto Mono',
                    fill = 'black'
                )
            ),
            spacer = dict(
                skip = True
            )
        )

        return

class VariantConfig(ConfigFile):
    def __init__(self, name=None):
        section = 'variant'
        super().__init__(section, name)
        
        self.family = ''
        pin_map = []

        self.package = dict(
            type = '',
            text1 = '',
            text2 = ''
        )
        
        self.page = dict(
            header= dict(
                text1 = '',
                text2 = ''
            ),
            quadrant = dict(
                text1 = '',
                text2 = '',
                text3 = '',
                text4 = ''
            )
        )

        if self.name is not None:
            self.load()
            
        return

class PageConfig(ConfigFile):
    def __init__(self, name):
        section = 'family'
        super().__init__(section, name)

        self.settings = None

        if self.name is not None:
            self.load()
            
        return

    def initialize(self):
        
        width = 2200
        height = 1700
        
        return
    
