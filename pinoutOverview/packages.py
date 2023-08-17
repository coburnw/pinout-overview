import math

import drawsvg as dw
from pinoutOverview import shapes
#from pinoutOverview import footprint as fp
from template import packages as package_templates
from pinoutOverview import utils as pinout

class label_line:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.side = -1
        self.direction = 1

# pin is confusing with pin in upper classes.  Perhaps pad would be better.
class Pin:
    def __init__(self, template):
        self.template = template
        
        self.length      = self.template['length']
        self.width       = self.template['width']

        return

    def generate(self, number, side):
        dw_pin = dw.Group(id=f"p{number}")
        shape = shapes.qfn_pin(self.width, self.length, **self.template['style'])

        dw_pin.append(shape)

        #self.data['pin']['text_style']['text_anchor'] = 'middle'  # add to package_pin.yaml config
        t = pinout.Text(self.template['text'])
        text = t.generate(str(number))

        rotation = 180 if side in [2,3] else 0
        dw_pin.append(dw.Use(text, 0, 0, transform=f'rotate({rotation})'))

        rotation = side * -90
        return dw.Use(dw_pin, 0, 0, transform=f'rotate({rotation})')


class PackageFactory():
    def __new__(cls, package_config, pin_spacing):
        name = package_config['type'].lower()

        #print(package_config)
        if package_config['type'] == 'qfn':
            package_template = package_templates.qfn_template
            package = QFN(package_template, package_config, pin_spacing)
        elif name == 'qfp':
            package_template = package_templates.qfp_template
            package = QFP(package_template, package_config, pin_spacing)
        elif name == 'sop':
            package_template = package_templates.sop_template
            package = SOP(package_template, package_config, pin_spacing)
        else:
            raise 'unrecognized package: "{}"'.format(name)

        return package

class Package(object):
    def __init__(self, package_template, package_config, pin_spacing):
        self.template = package_template
        self.data = package_config
        self.pin_spacing = pin_spacing 

        self.number_of_pins = package_config['pin_count']
        
        return

    @property
    def pin_offset(self):
        proto_pin = Pin(self.template.pad)
        return (self.width - proto_pin.length) / 2

    def _calc_offset_point(self, pin_number, offset=None, rotation=None):
        # find x,y position of a point relative to a pin_number, offset from 0,0 by specified amount

        if offset is None:
            offset = self.width/2
        else:
            offset += self.width/2
            
        side_index, pin_index = self.side_from_pin_number(pin_number)

        # pos names...
        # pin_offset: how far the row is offset from origin 0
        # row_offset: how far the pin is offset in its row from row center 
        pin_offset = offset 
        row_offset = -(self.pin_spacing * pin_index) + (self.pin_spacing * (self.pins_per_side-1)) / 2 

        direction = 1
        if side_index in [0,1]:
            direction = -direction

        if side_index in [1,3]:           # bottom and top
            x = row_offset * direction    # movement along line parallel to edge of package
            y = pin_offset * -direction   # distance from origin 
            direction = -direction        # invert direction for vertical pins so it works logically for caller
        else:
            x = pin_offset * direction
            y = row_offset * direction

        point = {'x':x,'y':y}
        return point, side_index, direction 

    def _build_pins(self, proto_pin):
        # assemble full complement of pads in position around 0,0

        pins = dw.Group(id="side_pins")
        pin_offset = -proto_pin.length / 2
        
        for pin_numb in self.pin_numbers:
            position, side, direction = self._calc_offset_point(pin_numb, pin_offset)
            dw_pin = proto_pin.generate(pin_numb+1, side)
            pins.append(dw.Use(dw_pin, **position))

        return pins
        
    def generate(self):
        # specific package should construct and return a dw_footprint
        raise NotImplementedError
    
class Dual(Package):
    def __init__(self, package_template, package_config, pin_spacing):
        super().__init__(package_template, package_config, pin_spacing)
        
        self.number_of_sides = 2
        self.pins_per_side   = int(self.number_of_pins/self.number_of_sides)
        
        self.pin_numbers     = range(0, self.number_of_pins)
        self.sides           = [0,2]

        self.corner_spacing  = self.pin_spacing*1.5
        
        self.height = (self.pins_per_side-1) * self.pin_spacing + 2*self.corner_spacing
        self.width  = self.pin_spacing * 6
        
        return

    def side_from_pin_number(self, pin_number):
        # returns 0-based side_index and pin_index from 0-based pin_number

        if not (0 <= pin_number < self.number_of_pins):
            raise IndexOutOfBounds

        if pin_number < self.pins_per_side:
            pin_index = pin_number
            side_index = 0
        else:
            pin_index = pin_number - self.pins_per_side
            side_index = 2
            
        return side_index, pin_index
    
class Quad(Package):
    def __init__(self, package_template, package_config, pin_spacing):
        super().__init__(package_template, package_config, pin_spacing)
        
        self.number_of_sides = 4
        self.pins_per_side   = int(self.number_of_pins/self.number_of_sides)
        
        self.pin_numbers     = range(0, self.number_of_pins)
        self.sides           = [0,1,2,3] # dip might be [0,2]

        self.corner_spacing  = self.pin_spacing*1.5
        
        self.height   = (self.pins_per_side-1) * self.pin_spacing + 2*self.corner_spacing
        self.width  = self.height
        
        return

    def side_from_pin_number(self, pin_number):
        # returns 0-based side_index and pin_index from 0-based pin_number

        if not (0 <= pin_number < self.number_of_pins):
            raise IndexOutOfBounds

        pin_index = 0
        for side_index in self.sides:
            if pin_number < (side_index+1) * self.pins_per_side:
                pin_index = pin_number - side_index * self.pins_per_side
                break

        return side_index, pin_index
    
class QFN(Quad):
    def generate(self, diagonal=False):
        pad_width       = self.width - self.corner_spacing*2
        marker_dia       = self.pin_spacing/4
        marker_position    = -self.width/2 + self.corner_spacing + marker_dia/2
        rotate_opt      = f"rotate({-45 if diagonal else 0}, {0}, {0})"

        border    = shapes.qfn_border(self.width, **self.template['style'])
        pad       = shapes.qfn_pad(pad_width, **self.template['pad']['style'])
        marker       = dw.Circle( marker_position, marker_position, marker_dia,
                               **self.template['marker_style'])

        s = self.data.get('text1', 'text')
        t = pinout.Text(self.template['text'])
        dw_text = t.generate(s)

        s = self.data.get('text2', 'subtext')
        t = pinout.Text(self.template['sub_text'])
        dw_subtext = t.generate(s)

        proto_pin = Pin(self.template['pad'])
        pins = self._build_pins(proto_pin)
        
        package = dw.Group(id="package")
        package.append(border)
        package.append(pad)
        package.append(marker)
        package.append(pins)

        package.append(dw.Use(dw_text, 0, 0, transform=rotate_opt))
        package.append(dw.Use(dw_subtext, 0, 0, transform=rotate_opt))

        return package
    
class QFP(Quad):
    def generate(self, diagonal=False):
        marker_dia     = self.pin_spacing/3
        marker_position  = -self.width/2 + self.corner_spacing + marker_dia/2
        rotate_opt    = f"rotate({-45 if diagonal else 0}, {0}, {0})"
        
        proto_pin = Pin(self.template['pad'])
        border    = shapes.qfn_border(self.width-2*proto_pin.length, **self.template['style'])
        marker       = dw.Circle(marker_position, marker_position, marker_dia, **self.template['marker_style'])
        
        pins = self._build_pins(proto_pin)

        s = self.data.get('text', 'text')
        t = pinout.Text(self.template['text'])
        dw_text = t.generate(s)

        s = self.data.get('sub_text', 'subtext')
        t = pinout.Text(self.template['sub_text'])
        dw_subtext = t.generate(s)
        
        package = dw.Group(id="package")
        package.append(border)
        package.append(marker)
        package.append(pins)
        package.append(dw.Use(dw_text, 0, 0, transform=rotate_opt))
        package.append(dw.Use(dw_subtext, 0, 0, transform=rotate_opt))

        return package

class SOP(Dual):
    def generate(self, diagonal=False):
        marker_dia = self.pin_spacing/3
        marker_x   = -self.width/2 + self.corner_spacing + marker_dia/2
        marker_y   = -self.height/2 + self.corner_spacing + marker_dia/2
        
        proto_pin = Pin(self.template['pad'])
        border    = shapes.sop_border(self.width-2*proto_pin.length, self.height-2*proto_pin.length, **self.template['style'])
        marker    = dw.Circle(marker_x, marker_y, marker_dia, **self.template['marker_style'])
        
        pins = self._build_pins(proto_pin)

        s = self.data.get('text1', 'text')
        t = pinout.Text(self.template['text'])
        dw_text = t.generate(s)

        s = self.data.get('text2', 'subtext')
        t = pinout.Text(self.template['sub_text'])
        dw_subtext = t.generate(s)
        
        package = dw.Group(id="package")
        package.append(border)
        package.append(marker)
        package.append(pins)
        package.append(dw.Use(dw_text, 0, 0))
        package.append(dw.Use(dw_subtext, 0, 0))

        return package


