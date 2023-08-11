import math

import drawsvg as dw

from pinoutOverview import utils
from pinoutOverview import packages
from pinoutOverview import shapes
from pinoutOverview import pins as Pin
from pinoutOverview import functions

SIN_45 = math.sin(math.radians(45)) #0.7071067811865475

class label_line:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.side = -1
        self.direction = 1

class PinoutFactory():
    def __new__(self, layout, variant):
        if layout == 'orthogonal':
            pinout = OrthogonalPinout(variant)
        elif layout == 'diagonal':
            pinout = DiagonalPinout(variant)
        else: # horizontal
            pinout = HorizontalPinout(variant)

        return pinout
        
class Pinout(utils.Region):
    def __init__(self, variant, **kwargs):
        #self.data = variant.data
        self.package = variant.package
        self.pins = variant.pins
        
        self.row_spacing = self.pins.spacing
        width = self.package.width
        height = width
            
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

            self.height = row_count * self.row_spacing + self.package.corner_spacing * 2
            self.width = 0
            
        return wires, dw_wires
        
    def build_pin(self, pin):
        direction = self.direction_from_pin(pin.number)
        dw_pin = pin.generate(direction, slant=Pin.Label().slant_none)

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
    
class PinLegend:
    def __init__(self, data):
        self.data = data
        return
    
    def generate(self, canvas_width):
        # label_amount = len(self.data['types'])

        # column1 = canvas_width/7
        # column2 = canvas_width/3.2
        # column3 = canvas_width/2
        # column4 = canvas_width/3*2

        # legends = dw.Group(id="legends")

        # for i, typ in enumerate(self.data['types']):
        #     ftype = self.data['types'][typ]
        #     if "skip" in ftype:
        #         if ftype["skip"]:
        #             continue
        #     legend_group = dw.Group(id=f"legend_{typ}")

        #     #label = Label(self.data)
        #     label = functions.FunctionLabel()
            
        #     lbl = label.generate(typ.upper(), ftype, caption=ftype['description'])
        #     legend_group.append(dw.Use(lbl, 0, 0))
            
        #     if i < label_amount/3-1:
        #         legends.append(dw.Use(legend_group, column1, (i)*(label.height+label.spacing)))
        #     elif i < label_amount/3*2-1:
        #         legends.append(dw.Use(legend_group, column2, (i - label_amount/3)*(label.height+label.spacing)))
        #     else:
        #         legends.append(dw.Use(legend_group, column3, (i - label_amount/3*2)*(label.height+label.spacing)))

        # legend_normal = dw.Group(id="legend_normal")

        # label = Label(self.data)
        # lbl = label.generate("FUNC", {'box_style': {'fill': 'white', 'stroke': 'black'}})
        # legend_normal.append(dw.Use(lbl, 0, 0))
        # text_normal = dw.Text("Default Function", label.height, 0, 0,
        #                     text_anchor='start', dominant_baseline='middle',
        #                     fill="black", font_weight='bold', font_family='Roboto Mono')
        # legend_normal.append(dw.Use(text_normal, label.width + 10, (label.height-10)/10))
        # legends.append(dw.Use(legend_normal, column4, 0))

        # legend_alt = dw.Group(id="legend_alt")
        # label = Label(self.data)
        # lbl = label.generate("FUNC", {'box_style': {'fill': 'white', 'stroke': 'black'}}, is_alt=True)
        
        # legend_alt.append(dw.Use(lbl, 0, 0))
        # text_alt = dw.Text("Alternate Function", label.height, 0, 0,
        #                     text_anchor='start', dominant_baseline='middle',
        #                     fill="black", font_weight='bold', font_family='Roboto Mono')
        # legend_alt.append(dw.Use(text_alt, label.width + 10, (label.height-10)/10))
        # legends.append(dw.Use(legend_alt, column4, label.height+label.spacing))

        return legends

