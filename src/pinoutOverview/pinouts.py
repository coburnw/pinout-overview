import math
import importlib

import drawsvg as dw

from pinoutOverview import utils
#from pinoutOverview import packages
from pinoutOverview import shapes
from pinoutOverview import pins as Pin
from pinoutOverview import functions

#SIN_45 = math.sin(math.radians(45)) #0.7071067811865475

class label_line:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.side = -1
        self.direction = 1


# def entity(name):
#     label_template = importlib.import_module(f'template.{name}_label')
#     functions_template = importlib.import_module(f'template.{name}_functions')

#     # configure the 'static' class variables for the callers name
#     functions.Label(template=label_template.label_template)
#     functions.Function(function=None, type_templates=functions_template.function_types)
    
#     return
    
class PinoutFactory():
    def __new__(self, layout, pinmap, package, pads):
        if layout == 'orthogonal':
            pinout = OrthogonalPinout(pinmap, package, pads)
        elif layout == 'diagonal':
            pinout = DiagonalPinout(pinmap, package, pads)
        else: # horizontal
            pinout = HorizontalPinout(pinmap, package, pads)

        return pinout

class Pinout(utils.Region):
    '''
    Args:
       pinmap (dict):
       package (object):
       pads (dict):
    '''
    def __init__(self, pinmap, package, pads, **kwargs):
        #self.data = variant.data
        self.pins = pinmap
        self.package = package
        self.pads = pads
        
        self.row_spacing = self.pins.spacing
        height = self.package.height
        width = self.package.width 
            
        super().__init__(width=width, height=height, **kwargs)
        
        return

    def place(self, x, y, transform=''):
        self.x = x
        self.y = y

        diagonal = False
        if transform != '':
            diagonal = True  # true hack
            
        dw_footprint = self.package.generate(diagonal)
        self.append(dw.Use(dw_footprint, x, y, transform=transform))
        
        fanout, dw_fanout = self.build_fanout(self.package.pin_numbers, functions.Label().offset)
        self.append(dw.Use(dw_fanout, x, y))

        dw_pins = dw.Group(id='pins')
        for pin in self.pins:
            position = fanout[pin.number]
            dw_pin = self.build_pin(pin)
            dw_pins.append(dw.Use(dw_pin, position.end_x, position.end_y))
            #dw_pins.append(dw.Circle(position.end_x, position.end_y, 2, stroke='black'))

        self.append(dw.Use(dw_pins, x, y))

        return self

    def legend(self, layout='vertical'):
        return(Legend(layout))
        
class OrthogonalPinout(Pinout):
    def build_fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        for pin_number in pin_numbers:
            line = label_line()
            side_index, pin_index = self.package.side_from_pin_number(pin_number)
            position, side, direction = self.package._calc_offset_point(pin_number)
            #print(side, direction, position['x'], position['y'])
            if side in [0,2]:
                line.start_x = position['x']
                line.start_y = position['y']
            
                line.end_x = position['x'] + (offset * direction)
                line.end_y = position['y']
            else:
                line.start_x = position['x']
                line.start_y = position['y']
            
                line.end_x = position['x']
                line.end_y = position['y'] + (offset * direction)
                
            line.side = side
            line.direction = direction

            wire = dw.Line(line.start_x, line.start_y, line.end_x, line.end_y, stroke_width=2, stroke='black')
            dw_wires.append(wire)

            wires.append(line)
            
        return wires, dw_wires
        
    def build_pin(self, pin, x=0, y=0):
        side_index, pin_index = self.package.side_from_pin_number(pin.number)

        # (append direction) -1 to the left, +1 to the right, 0 stacked.
        label_direction = -1
        if side_index in [2,3]:
            label_direction = -label_direction

        dw_pin = pin.generate(label_direction, slant=functions.Label().slant_none)

        transform = 'rotate(0)'
        if side_index in [1,3]:
            transform = 'rotate(-90)'

        dw_pin = dw.Use(dw_pin, 0, 0, transform=transform)
        
        return dw_pin
        
class DiagonalPinout(Pinout):
    def __init__(self, data, pins, **kwargs):
        super().__init__(data, pins, **kwargs)
        
        self.pin_spacing = self.pin_spacing * math.sqrt(2)
        self.height = self.height * math.sqrt(2)
        self.width = 0
        
        return

    def place(self, x, y):
        transform = ''
        if self.diagonal is True:
            transform = 'rotate(45)'

        super().place(x, y, transform)
        return
        
    def _calc_offset_point(self, pin_number, offset=None, rotation=None):
        sin_45 = math.sin(math.radians(45))
        cos_45 = math.cos(math.radians(45))

        side_index, pin_index = self.package.side_from_pin_number(pin_number)
        position, side, direction = self.package._calc_offset_point(pin_number)

        x = position['x'] * cos_45 - position['y'] * sin_45
        y = position['x'] * sin_45 + position['y'] * cos_45
            
        direction = 1
        if side_index in [0,1]:
            direction = -direction
            
        point = {'x':x,'y':y}
        return point, side_index, direction 

    def build_fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        for pin_number in pin_numbers:
            line = label_line()
            position, side, direction = self._calc_offset_point(pin_number)

            line.side = side
            line.direction = direction

            line.start_x = position['x']
            line.start_y = position['y']
            
            line.end_x = position['x'] + (offset * direction)
            line.end_y = position['y']
                
            wire = dw.Line(line.start_x, line.start_y, line.end_x, line.end_y, stroke_width=2, stroke='black')
            dw_wires.append(wire)
                
            wires.append(line)

        return wires, dw_wires
        
    def build_pin(self, pin):
        side_index, pin_index = self.package.side_from_pin_number(pin.number)

        # (append direction) -1 to the left, +1 to the right, 0 stacked.
        label_direction = -1
        if side_index in [2,3]:
            label_direction = -label_direction

        slant = Pin.Label().slant_right
        if side_index in [1,3]:
            slant = Pin.Label().slant_left
            
        dw_pin = pin.generate(label_direction, slant=slant)

        return dw_pin
        
class HorizontalPinout(Pinout):
    # fanout calculates our true height and width property.  Values are invalid until construction.
    
    def build_fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        row_count = 0
        for pin_number in pin_numbers:
            line = label_line()
            side_index, pin_index = self.package.side_from_pin_number(pin_number)
            position, side, direction = self.package._calc_offset_point(pin_number)

            #print(side, direction, position['x'], position['y'])
            if side in [0,2]:
                line.start_x = position['x']
                line.start_y = position['y']
            
                line.end_x = position['x'] + (offset * direction) 
                line.end_y = position['y']

                wire = dw.Line(line.start_x, line.start_y, line.end_x, line.end_y, stroke_width=2, stroke='black')
                dw_wires.append(wire)
            
            else:
                # vertical segment first. line contains endpoint of wrong segment.
                row_count += 1
                
                if pin_index > self.package.pins_per_side/2:
                    pin_index = self.package.pins_per_side - pin_index
                    
                line.start_x = position['x']
                line.start_y = position['y']
            
                line.end_x = position['x']
                line.end_y = position['y'] + ((offset + pin_index* self.row_spacing) * direction)

                wire = dw.Line(line.start_x, line.start_y, line.end_x, line.end_y, stroke_width=2, stroke='black')
                dw_wires.append(wire)

                # horizontal segment.  line now contains the proper endpoint.
                direction = self.direction_from_pin(pin_number)
                
                line.start_x = line.end_x
                line.start_y = line.end_y
            
                line.end_x = (self.package.width/2 + offset) * direction
                line.end_y = line.start_y
                
                wire = dw.Line(line.start_x, line.start_y, line.end_x, line.end_y, stroke_width=2, stroke='black')
                dw_wires.append(wire)
                            
            line.side = side
            line.direction = direction
            wires.append(line)

            self.height = self.height + row_count * self.row_spacing # + self.package.corner_spacing * 2
            self.width = 0
            
        return wires, dw_wires
        
    def build_pin(self, pin):
        direction = self.direction_from_pin(pin.number)
        dw_pin = pin.generate(direction, slant=functions.Label().slant_none)

        return dw_pin
        
    def direction_from_pin(self, number):
        # determine horizontal direction of row for split top and bottom sides.
        side_index, pin_index = self.package.side_from_pin_number(number)

        right = +1
        left = -1
        
        direction = left
        if side_index == 1 and pin_index > self.package.pins_per_side/2:
            direction = right
            pin_index = self.package.pins_per_side - pin_index
        elif side_index == 3 and pin_index < self.package.pins_per_side/2:
            direction = right
            pin_index = self.package.pins_per_side - pin_index
        elif side_index == 2:
            direction = right

        return direction
    
class Legend(dw.Group):
    def __init__(self, data):
        super().__init__(id='Legend')
        self.data = data

        self._width = 0
        self._height = 0
        
        return

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
    
    def generate(self, canvas_width):
        function_types = functions.Function(None).types

        x = 0
        y = 0
        for type_name in function_types:
            ftype = dict(
                name = '',
                type = type_name,
                alt = False
                )
            
            function = functions.Function(ftype)
            if function.use_count == 0:
                continue
            
            label = function.label()
            y += label.height + label.vert_spacing
            self.append(dw.Use(label.generate(type_name.upper(), slant=0), x,y))

        self._width = label.width + label.spacing
        self._height = y + label.vert_spacing
        
        return self
    

