import math

import drawsvg as dw
from pinoutOverview import shapes
from pinoutOverview import footprint as fp
from template import packages as package_templates
from pinoutOverview import utils as pinout

# SIN_45 = math.sin(math.radians(45)) #0.7071067811865475

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
            package = QFP(package_config, pin_spacing)
        elif name == 'sop':
            package = SOP(package_config, pin_spacing)
        else:
            raise 'unrecognized package: "{}"'.format(name)

        return package

class Package(object):
    pass

class Quad(Package):
    def __init__(self, package_template, package_config, pin_spacing):
        self.template = package_template
        self.data = package_config
        #self.pin_map = package_config['pin_map']
        self.number_of_pins = package_config['pin_count'] #len(self.pin_map)

        self.number_of_sides = 4
        self.pins_per_side   = int(self.number_of_pins/self.number_of_sides)
        
        self.pin_numbers     = range(0, self.number_of_pins)
        self.sides           = [0,1,2,3] # dip might be [0,2]

        self.pin_spacing = pin_spacing 
        self.corner_spacing  = self.pin_spacing*1.5
        
        self.width   = (self.pins_per_side-1) * self.pin_spacing + 2*self.corner_spacing
        self.height  = self.width
        
        return

    @property
    def pin_offset(self):
        proto_pin = Pin(self.template.pad)
        return (self.width - proto_pin.length) / 2

    def get_pin_side(self, pin_number):
        pass

    def get_pin_direction(self, pin_number):
        pass

    def get_pin_index(self, pin_number):
        pass
        
    def side_from_pin_number(self, pin_number):
        # returns 0-based side_index and pin_index from 0-based pin_number

        if not (0 <= pin_number < self.number_of_pins):
            raise IndexOutOfBounds

        pin_index = 0 # huh
        for side_index in self.sides:
            if pin_number < (side_index+1) * self.pins_per_side:
                pin_index = pin_number - side_index * self.pins_per_side
                break

        return side_index, pin_index
    
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
    
class QFN(Quad):
    def generate(self, diagonal=False):
        pad_width       = self.width - self.corner_spacing*2
        dot_width       = self.pin_spacing/4
        dot_position    = -self.width/2 + self.corner_spacing + dot_width/2
        rotate_opt      = f"rotate({-45 if diagonal else 0}, {0}, {0})"

        #print(self.template)
        
        border    = shapes.qfn_border(self.width, **self.template['style'])
        pad       = shapes.qfn_pad(pad_width, **self.template['pad']['style'])
        dot       = dw.Circle( dot_position, dot_position, dot_width,
                               **self.template['marker_style'])

        s = self.data.get('text', 'text')
        t = pinout.Text(self.template['text'])
        dw_text = t.generate(s)

        s = self.data.get('sub_text', 'subtext')
        t = pinout.Text(self.template['sub_text'])
        dw_subtext = t.generate(s)

        proto_pin = Pin(self.template['pad'])
        pins = self._build_pins(proto_pin)
        
        package = dw.Group(id="package")
        package.append(border)
        package.append(pad)
        package.append(dot)
        package.append(pins)

        package.append(dw.Use(dw_text, 0, 0, transform=rotate_opt))
        package.append(dw.Use(dw_subtext, 0, 0, transform=rotate_opt))

        return package
    
class QFP(Quad):
    def generate(self, diagonal=False):
        dot_width     = self.pin_spacing/3
        dot_position  = -self.width/2 + self.corner_spacing + dot_width/2
        rotate_opt    = f"rotate({-45 if diagonal else 0}, {0}, {0})"
        
        proto_pin = Pin(self.template['pad'])
        border    = shapes.qfn_border(self.width-2*proto_pin.length, **self.template['style'])
        dot       = dw.Circle(dot_position, dot_position, dot_width, **self.template['marker_style'])
        
        pins = self._build_pins(proto_pin)

        s = variant.get('text', 'text')
        t = pinout.Text(self.template['text'])
        dw_text = t.generate(s)

        s = variant.get('sub_text', 'subtext')
        t = pinout.Text(self.template['sub_text'])
        dw_subtext = t.generate(s)
        
        package = dw.Group(id="package")
        package.append(border)
        package.append(dot)
        package.append(pins)
        package.append(dw.Use(dw_text, 0, 0, transform=rotate_opt))
        package.append(dw.Use(dw_subtext, 0, 0, transform=rotate_opt))

        return package

class SOP:
    def __init__(self, data):
        self.data = data
        return

    def _generate_footprint(self):
        footprint       = self.data['footprint'].split('-')[0]
        pin_number      = int(self.data['footprint'].split('-')[1])
        pin_spacing     = self.data['pin']['spacing_calc']
        
        corner_spacing  = pin_spacing*1.5
        
        dw_footprint = dw.Group(id=self.data['name'])
        
        if footprint == "QFN":
            self.data['package']['width']   = (pin_number/4-1) * pin_spacing + 2*corner_spacing
            self.data['package']['height']  = (pin_number/4-1) * pin_spacing + 2*corner_spacing
            dw_footprint = self.__draw_QFN()
        elif footprint == "SOP":
            dw_footprint = self.__draw_SOP()
        return dw_footprint
    
    def __draw_SOP(self):
        
        pin_number      = int(self.data['footprint'].split('-')[1])

        pin_length      = self.data['pin']['length']
        pin_width       = self.data['pin']['width']
        pin_spacing_og  = self.data['pin']['spacing']
        pin_spacing     = self.data['pin']['spacing_calc']
        pin_side        = int(pin_number/2)
        pin_no_offset   = self.data['pin']['number_offset']
        
        package_height  = (pin_number/2+1) * pin_spacing
        package_width   = self.data['package']['width']
        
        footprint   = dw.Group(id=self.data['name'])
        pins        = dw.Group(id="pins")
        pin_numbers = dw.Group(id="pin-numbers")
        border      = shapes.sop_border(package_width, package_height, **self.data['package']['style'])
        marker      = dw.Circle(-package_width/2+pin_spacing_og, -package_height/2+pin_spacing_og,
                                pin_width/2, **self.data['package']['marker_style'])

        fp_font_size = int(self.data['package']['text_style']['font_size'])
        pd_font_size = int(self.data['package']['sub_text_style']['font_size'])
        del self.data['package']['text_style']['font_size']
        del self.data['package']['sub_text_style']['font_size']

        fp_text = dw.Text(self.data['package_text']['text'], fp_font_size, 0, -15,
                          **self.data['package']['text_style'])
        pd_text = dw.Text(self.data['package_text']['sub_text'], pd_font_size, 0, 50,
                          **self.data['package']['sub_text_style'])
        pin     = shapes.sop_pin(pin_width, pin_length, **self.data['pin']['style'])
        
        
        for p in range(pin_side):
            y = - package_height/2 + pin_spacing * (p+1)
            x = - package_width/2 - pin_length/2
            pins.append(dw.Use(pin, x, y))
            pin_numbers.append(dw.Text(str(p+1), pin_width, x+pin_length/2+pin_no_offset, 
                                       y+pin_width/10, **self.data['pin']['text_style'], text_anchor='start'))

            x = package_width/2+pin_length/2
            pins.append(dw.Use(pin,  x, y))
            pin_numbers.append(dw.Text(str(pin_number-p), pin_width, x-pin_length/2-pin_no_offset,
                                       y+pin_width/10, **self.data['pin']['text_style'], text_anchor='end'))

        footprint.append(pins)
        footprint.append(border)
        footprint.append(marker)
        footprint.append(fp_text)
        footprint.append(pd_text)
        footprint.append(pin_numbers)

        return footprint
        

    def __calc_index_SOP(self):
        
        pin_number          = int(self.data['footprint'].split('-')[1])
        pin_spacing         = self.data['pin']['spacing_calc']
        package_width       = self.data['package']['width']
        pin_length          = self.data['pin']['length']
        label_width         = self.data['label']['width']
        label_start         = self.data['label']['offset']
        corner_spacing      = self.data['pin']['spacing_calc']*1.5

        label_pos_index     = []

        for i in range(int(pin_number/2)):
            line = label_line()
            overall_ofs_y = -(pin_spacing) * ((pin_number/2)/2)
            offset_y = (i+0.5)*(pin_spacing) + overall_ofs_y
            line.start_x = -package_width/2-pin_length
            line.start_y = offset_y
            line.end_x = -label_start-pin_length-label_width
            line.end_y = offset_y
            label_pos_index.append(line)

        for i in range(int(pin_number/2)):
            line = label_line()
            i2 = pin_number/2 - i - 1
            overall_ofs_y = -(pin_spacing) * (pin_number/4)
            offset_y = corner_spacing + (i2-1)*(pin_spacing) + overall_ofs_y
            line = label_line()
            line.start_x = package_width/2+pin_length
            line.start_y = offset_y
            line.end_x = label_start+pin_length+label_width
            line.end_y = offset_y
            line.side = 1
            label_pos_index.append(line)
        return label_pos_index
    
