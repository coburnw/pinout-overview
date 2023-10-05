import math
import collections

import drawsvg as dw

from pinoutOverview import Functions, FunctionLabel, Region


class label_line:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.side = -1
        self.direction = 1


class Pinmap(collections.UserDict):
    """
    Pinmap Base Class.  Maintains a collection of pin_number to Pad objects mappings
    """
    @property
    def spacing(self):
        """Finds maximum pin spacing in pixels

        Returns:
           pin_spacing (int): spacing in pixels between adjacent pins
        """

        max_height = 0
        for name, pad in self.data.items():
            if pad.height > max_height:
                max_height = pad.height

        return max_height

    def sort(self):
        """
        Sorts functions in ascending order by their type_index value

        Returns:
            Nothing.  Functions are sorted in place.
        """

        for name, pad in self.data.items():
            pad.sort()

        return

    def split(self, split_functions):
        """
        Splits the functions associated with each pad into rows of functions. Each function found in
        split_functions acts as a break point

        Args:
            split_functions (Functions): A list of functions to split the row into multiple rows on.

        Returns:
            None
        """
        for name, pad in self.data.items():
            pad.split(split_functions)

        return


class PinoutFactory(type):
    def __call__(cls, layout, pinmap, package):
        if cls is Pinout:
            if layout == 'orthogonal':
                return OrthogonalPinout(layout, pinmap, package)
            if layout == 'horizontal':
                return HorizontalPinout(layout, pinmap, package)
            if layout == 'diagonal':
                package.diagonal = 'True'
                return DiagonalPinout(layout, pinmap, package)

            print('PinoutFactory(): unrecognized layout.')
            raise

        return type.__call__(cls, layout, pinmap, package)


class Pinout(Region, metaclass=PinoutFactory):
    def __init__(self, layout_name, pinmap, package, **kwargs):
        """

        Args:
            layout_name (str): name of layout style. one of 'horizontal', 'orthogonal', 'diagonal'.
            pinmap (Pinmap): a mapping of pin number to Pad objects
            package (Package): a package object
        """
        super().__init__(width=0, height=0, **kwargs)

        self.pinmap = pinmap
        self.package = package

        self.row_spacing = self.pin_spacing  # some goofyness

        return

    @property
    def pin_spacing(self):
        return self.pinmap.spacing

    def build_fanout(self, pin_numbers, offset):
        """
        fanout calculates our true height and width property.  Values are invalid until construction.

        Args:
            pin_numbers:
            offset:

        Returns:
        """
        raise NotImplementedError

    def build_pin(self, number, pad):
        """

        Args:
            number (int): the number of the physical pin 
            pad (Pad): a Pad object containing the rows of pad functions 

        Returns:
            dw.Group: a DrawingSVG group of image elements of a finished pin
        """
        raise NotImplementedError

    def place(self, x, y, transform=''):
        self.x = x
        self.y = y

        dw_footprint = self.package.generate(self.pin_spacing)
        self.append(dw.Use(dw_footprint, x, y, transform=''))  # transform
        fanout, dw_fanout = self.build_fanout(self.package.pin_numbers, FunctionLabel().offset)
        self.append(dw.Use(dw_fanout, x, y))

        dw_pins = dw.Group(id='pins')
        for number, pad in self.pinmap.items():
            position = fanout[int(number-1)]
            # print(position.end_x, position.end_y)
            dw_pin = self.build_pin(number-1, pad)
            dw_pins.append(dw.Use(dw_pin, position.end_x, position.end_y))
            # dw_pins.append(dw.Circle(position.end_x, position.end_y, 2, stroke='black'))

        self.append(dw.Use(dw_pins, x, y))

        return self

    # def legend(self, layout='vertical'):
    #     return Legend(self.pinmap)  # (Legend(layout))
        

class OrthogonalPinout(Pinout):
    def build_fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        for pin_number in pin_numbers:
            line = label_line()
            # side_index, pin_index = self.package.side_from_pin_number(pin_number)
            position, side, direction = self.package.calc_offset_point(pin_number)
            # print(side, direction, position['x'], position['y'])
            if side in [0, 2]:
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
        
    def build_pin(self, number, pad, x=0, y=0):
        side_index, pin_index = self.package.side_from_pin_number(number)

        # (append direction) -1 to the left, +1 to the right, 0 stacked.
        label_direction = -1
        if side_index in [2, 3]:
            label_direction = -label_direction

        dw_pin = pad.generate(label_direction, slant=FunctionLabel().slant_none)

        transform = 'rotate(0)'
        if side_index in [1, 3]:
            transform = 'rotate(-90)'

        dw_pin = dw.Use(dw_pin, 0, 0, transform=transform)
        
        return dw_pin
        

class DiagonalPinout(Pinout):
    def build_fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        for pin_number in pin_numbers:
            line = label_line()
            position, side, direction = self.package.calc_offset_point(pin_number)

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
        
    def build_pin(self, number, pad):
        side_index, pin_index = self.package.side_from_pin_number(number)

        # (append direction) -1 to the left, +1 to the right, 0 stacked.
        label_direction = -1
        if side_index in [2, 3]:
            label_direction = -label_direction

        slant = FunctionLabel().slant_right
        if side_index in [1, 3]:
            slant = FunctionLabel().slant_left
            
        dw_pin = pad.generate(label_direction, slant=slant)

        return dw_pin
        

class HorizontalPinout(Pinout):
    def build_fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        row_count = 0
        for pin_number in pin_numbers:
            line = label_line()
            side_index, pin_index = self.package.side_from_pin_number(pin_number)
            position, side, direction = self.package.calc_offset_point(pin_number)

            # print(side, direction, position['x'], position['y'])
            if side in [0, 2]:
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
                line.end_y = position['y'] + ((offset + pin_index * self.row_spacing) * direction)

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

            self.height = self.height + row_count * self.row_spacing  # + self.package.corner_spacing * 2
            self.width = 0
            
        return wires, dw_wires
        
    def build_pin(self, number, pad):
        direction = self.direction_from_pin(number)
        dw_pin = pad.generate(direction, slant=FunctionLabel().slant_none)

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


class Legend(Region):
    def __init__(self, pinmap, **kwargs):
        """

        Args:
            pinmap (Pinmap):
        """
        super().__init__(id='Legend')
        self.pinmap = pinmap

        return

    def place(self, x, y):
        used_functions = Functions()
        for number, pad in self.pinmap.items():
            for function in pad:
                if function not in used_functions:
                    used_functions.append(function)

        used_functions.sort()
        for label in used_functions:
            y += label.height + label.vert_spacing
            self.append(dw.Use(label.generate(legend=True, slant=0), x, y))

        self.width = used_functions[0].width + used_functions[0].spacing
        self.height = y + label.vert_spacing

        self.x = x
        self.y = y
        
        return self
