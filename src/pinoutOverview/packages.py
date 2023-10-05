import math
import drawsvg as dw

from pinoutOverview import shapes
from pinoutOverview import templates
from pinoutOverview import utils as pinout


# class label_line:
#     def __init__(self):
#         self.start_x = 0
#         self.start_y = 0
#         self.end_x = 0
#         self.end_y = 0
#         self.side = -1
#         self.direction = 1
#

class Pin:
    def __init__(self, template):
        self.template = template
        
        self.length = self.template['length']
        self.width = self.template['width']

        return

    def generate(self, number, side):
        dw_pin = dw.Group(id=f"p{number}")
        shape = shapes.qfn_pin(self.width, self.length, **self.template['style'])

        dw_pin.append(shape)

        t = pinout.Text(self.template['text'])
        text = t.generate(str(number))

        rotation = 180 if side in [2, 3] else 0
        dw_pin.append(dw.Use(text, 0, 0, transform=f'rotate({rotation})'))

        rotation = side * -90
        return dw.Use(dw_pin, 0, 0, transform=f'rotate({rotation})')


class Package(object):
    """
    Package (class): container of data for configuring a package.
        Typically subclassed by an application with added parsers.
    """
    def __init__(self, shape, pin_count):
        """

        Args:
            shape (string): the package shape, one of 'qfn', 'qfp', 'sop'
            pin_count (int): number of package pins
        """
        self.shape = shape
        self.pin_count = pin_count

        self.package = PackageBase(self.shape, self.pin_count)

        self.text1 = ''
        self.text2 = ''


        return

    @property
    def diagonal(self):
        return self.package._diagonal

    @diagonal.setter
    def diagonal(self, boolean):
        self.package._diagonal = boolean
        return

    @property
    def text1(self):
        return self.package.text1

    @text1.setter
    def text1(self, text):
        self.package.text1 = text
        return

    @property
    def text2(self):
        return self.package.text2

    @text2.setter
    def text2(self, text):
        self.package.text2 = text
        return

    @property
    def height(self):
        height = self.package.height
        if self.diagonal:
            height *= math.sqrt(2)

        return height

    @property
    def width(self):
        width = self.package.width
        if self.diagonal:
            width *= math.sqrt(2)

        return width

    @property
    def pin_numbers(self):
        return self.package.pin_numbers

    @property
    def pins_per_side(self):
        return self.package.pins_per_side

    def side_from_pin_number(self, pin_number):
        return self.package.side_from_pin_number(pin_number)

    def calc_offset_point(self, pin_number):
        return self.package.calc_offset_point(pin_number)

    def generate(self, pin_spacing):
        return self.package.generate(pin_spacing)


class PackageFactory(type):
    def __call__(cls, package_shape, pin_count, package_template=None):
        """

        Args:
            package_shape (str): name of package shape to construct
            pin_count (int): number of package pins
            package_template (dict): a package template describing default shape and style
        """
        if cls is PackageBase:
            # name = package_data.shape.lower()

            # print(package_config)
            if package_shape == 'qfn':
                package_template = templates.qfn_template
                return QFN(package_shape, pin_count, package_template)
            elif package_shape == 'qfp':
                package_template = templates.qfp_template
                return QFP(package_shape, pin_count, package_template)
            elif package_shape == 'sop':
                package_template = templates.sop_template
                return SOP(package_shape, pin_count, package_template)
            else:
                raise 'unrecognized package: "{}"'.format(package_shape)

        return type.__call__(cls, package_shape, pin_count, package_template)


class PackageBase(metaclass=PackageFactory):
    def __init__(self, package_shape, pin_count, package_template=None):
        """

        Args:
            package_shape (str): name of package shape to construct
            pin_count (int): number of package pins
            package_template (dict): a package template describing default shape and style
        """
        self.number_of_pins = pin_count
        self.template = package_template

        self._diagonal = False
        self._pin_spacing = None
        self._proto_pin = Pin(self.template['pad'])

        self.text1 = ''
        self.text2 = ''

        self.sin_45 = math.sin(math.radians(45))
        self.cos_45 = math.cos(math.radians(45))

        # values overridden by subclasses
        self.pins_per_side = None
        self.pin_numbers = None

        return

    @property
    def diagonal(self):
        return self._diagonal

    @property
    def pin_spacing(self):
        return self._pin_spacing

    @property
    def pin_offset(self):
        return (self.width - self._proto_pin.length) / 2

    def side_from_pin_number(self, pin_number):
        raise NotImplementedError

    def calc_offset_point(self, pin_number, offset=None, rotation=None):
        """
        Finds the x,y point of a pin, offset by some amount
        
        Args:
            pin_number: Number of 0 referenced pin 
            offset: distance in pixels to offset point by
            rotation: not implemented

        Returns:
            Point (dict): x,y position
        """
        side_index, pin_index = self.side_from_pin_number(pin_number)
        point, side, direction = self._calc_offset_point(pin_number)

        if self._diagonal:
            x = point['x'] * self.cos_45 - point['y'] * self.sin_45
            y = point['x'] * self.sin_45 + point['y'] * self.cos_45

            direction = 1
            if side_index in [0, 1]:
                direction = -direction

            point = {'x': x, 'y': y}

        return point, side_index, direction

    def _calc_offset_point(self, pin_number, offset=None, rotation=None):
        # find x,y position of a point relative to a pin_number, offset from 0,0 by specified amount

        if offset is None:
            offset = self.width/2
        else:
            offset += self.width/2
            
        side_index, pin_index = self.side_from_pin_number(pin_number)

        # pos names...
        # pin_offset: how far the row is offset from origin or center of package
        # row_offset: how far the pin is offset in its row from row center 
        pin_offset = offset 
        row_offset = -(self.pin_spacing * pin_index) + (self.pin_spacing * (self.pins_per_side-1)) / 2 

        direction = 1
        if side_index in [0, 1]:
            direction = -direction

        if side_index in [1, 3]:          # bottom and top
            x = row_offset * direction    # movement along line parallel to edge of package
            y = pin_offset * -direction   # distance from origin 
            direction = -direction        # invert direction for vertical pins, so it works logically for caller
        else:
            x = pin_offset * direction
            y = row_offset * direction

        point = {'x': x, 'y': y}
        return point, side_index, direction 

    def _generate_pins(self):
        # assemble full complement of pads in position around 0,0

        pins = dw.Group(id="side_pins")
        pin_offset = -self._proto_pin.length / 2
        
        for pin_numb in self.pin_numbers:
            position, side, direction = self._calc_offset_point(pin_numb, pin_offset)
            dw_pin = self._proto_pin.generate(pin_numb + 1, side)
            pins.append(dw.Use(dw_pin, **position))

        return pins
        
    def generate(self):
        # specific package should construct and return a dw_footprint
        raise NotImplementedError


class Dual(PackageBase):
    def __init__(self, package_shape, pin_count, package_template):
        super().__init__(package_shape, pin_count, package_template)
        
        self.number_of_sides = 2
        self.pins_per_side = int(self.number_of_pins/self.number_of_sides)
        
        self.pin_numbers = range(0, self.number_of_pins)
        self.sides = [0, 2]

        return

    @property
    def corner_spacing(self):
        return self.pin_spacing * 1.5

    @property
    def height(self):
        return(self.pins_per_side-1) * self.pin_spacing + 2*self.corner_spacing

    @property
    def width(self):
        return self.pin_spacing * 6
        

    def side_from_pin_number(self, pin_number):
        # returns 0-based side_index and pin_index from 0-based pin_number

        if not (0 <= pin_number < self.number_of_pins):
            raise IndexError

        if pin_number < self.pins_per_side:
            pin_index = pin_number
            side_index = 0
        else:
            pin_index = pin_number - self.pins_per_side
            side_index = 2
            
        return side_index, pin_index
    

class Quad(PackageBase):
    def __init__(self, package_shape, pin_count, package_template):
        super().__init__(package_shape, pin_count, package_template)

        self.number_of_sides = 4
        self.pins_per_side = int(self.number_of_pins/self.number_of_sides)
        
        self.pin_numbers = range(0, self.number_of_pins)
        self.sides = [0, 1, 2, 3]  # dip might be [0,2]

        return

    @property
    def pin_spacing(self):
        # this should be its own property, derived from pin_spacing
        if self._diagonal:
            return self._pin_spacing * 1.414

        return self._pin_spacing

    @property
    def corner_spacing(self):
        return self.pin_spacing * 1.5

    @property
    def height(self):
        return (self.pins_per_side-1) * self.pin_spacing + 2 * self.corner_spacing

    @property
    def width(self):
        return self.height

    def side_from_pin_number(self, pin_number):
        # returns 0-based side_index and pin_index from 0-based pin_number

        if not (0 <= pin_number < self.number_of_pins):
            raise IndexError

        pin_index = 0
        side_index = 0
        for side_index in self.sides:
            if pin_number < (side_index+1) * self.pins_per_side:
                pin_index = pin_number - side_index * self.pins_per_side
                break

        return side_index, pin_index

    def _generate_border(self):
        return shapes.qfn_border(self.width - 2 * self._proto_pin.length, **self.template['style'])

    def _generate_marker(self):
        marker_dia = self.pin_spacing/3
        marker_position = -self.width/2 + self.corner_spacing + marker_dia/2
        return dw.Circle(marker_position, marker_position, marker_dia, **self.template['marker_style'])

    def _generate_main_text(self):
        t = pinout.Text(self.template['text'])
        return t.generate(self.text1)

    def _generate_sub_text(self):
        t = pinout.Text(self.template['sub_text'])
        return t.generate(self.text2)


class QFN(Quad):
    def _generate_border(self):
        return shapes.qfn_border(self.width, **self.template['style'])

    def _generate_pad(self):
        pad_width = self.width - self.corner_spacing*2
        return shapes.qfn_pad(pad_width, **self.template['pad']['style'])

    def _generate_marker(self):
        marker_dia = self.pin_spacing/4
        marker_position = -self.width/2 + self.corner_spacing + marker_dia/2
        return dw.Circle(marker_position, marker_position, marker_dia, **self.template['marker_style'])

    def generate(self, pin_spacing):
        self._pin_spacing = pin_spacing

        text_transform = f"rotate({-45 if self._diagonal else 0}, {0}, {0})"
        package_transform = f"rotate({45 if self._diagonal else 0}, {0}, {0})"

        package = dw.Group(id="package")
        package.append(self._generate_border())
        package.append(self._generate_marker())
        package.append(self._generate_pad())
        package.append(self._generate_pins())
        package.append(dw.Use(self._generate_main_text(), 0, -self.height/5, transform=text_transform))
        package.append(dw.Use(self._generate_sub_text(), 0, self.height/4, transform=text_transform))

        return dw.Use(package, 0, 0, transform=package_transform)


class QFP(Quad):
    def generate(self, pin_spacing):
        self._pin_spacing = pin_spacing

        text_transform = f"rotate({-45 if self._diagonal else 0}, {0}, {0})"
        package_transform = f"rotate({45 if self._diagonal else 0}, {0}, {0})"

        package = dw.Group(id="package")
        package.append(self._generate_border())
        package.append(self._generate_marker())
        package.append(self._generate_pins())
        package.append(dw.Use(self._generate_main_text(), 0, -self.height/5, transform=text_transform))
        package.append(dw.Use(self._generate_sub_text(), 0, self.height/4, transform=text_transform))

        return dw.Use(package, 0, 0, transform=package_transform)


class SOP(Dual):
    def generate(self, pin_spacing):
        self._pin_spacing = pin_spacing

        marker_dia = self.pin_spacing/3
        marker_x = -self.width/2 + self.corner_spacing + marker_dia/2
        marker_y = -self.height/2 + self.corner_spacing + marker_dia/2
        
        #proto_pin = Pin(self.template['pad'])
        border = shapes.sop_border(self.width - 2 * self._proto_pin.length, self.height - 2 * self._proto_pin.length, **self.template['style'])
        marker = dw.Circle(marker_x, marker_y, marker_dia, **self.template['marker_style'])
        
        pins = self._generate_pins()

        s = self.text1
        t = pinout.Text(self.template['text'])
        dw_text = t.generate(s)

        s = self.text2
        t = pinout.Text(self.template['sub_text'])
        dw_subtext = t.generate(s)
        
        package = dw.Group(id="package")
        package.append(border)
        package.append(marker)
        package.append(pins)
        package.append(dw.Use(dw_text, 0, -self.height/5))
        package.append(dw.Use(dw_subtext, 0, self.height/4))

        return package
