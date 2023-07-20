#import sys

import drawsvg as dw
from pinoutOverview import shapes
from pinoutOverview import footprint as fp

from pinoutOverview import utils as pinout

SIN_45 = 0.7071067811865475

class label_line:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.side = -1
        self.direction = 1

class Pin:
    def __init__(self, data):
        self.data = data
        
        self.length      = self.data['pin']['length']
        self.width       = self.data['pin']['width']

        return

    def generate(self, number, side):
        dw_pin = dw.Group(id=f"p{number}")
        shape = shapes.qfn_pin(self.width, self.length, **self.data['pin']['style'])

        dw_pin.append(shape)

        #self.data['pin']['text_style']['text_anchor'] = 'middle'  # add to package_pin.yaml config
        t = pinout.Text(self.data, 'pin')
        text = t.generate('text', str(number), 0, 0)
        
        rotation = 180 if side in [1,2] else 0
        dw_pin.append(dw.Use(text, 0, 0, transform=f'rotate({rotation})'))

        rotation = side * 90
        return dw.Use(dw_pin, 0, 0, transform=f'rotate({rotation})')

class Quad:
    def __init__(self, data, pin_count, pin_spacing):
        self.data = data
        self.pin_count = int(pin_count)
        self.pin_spacing = pin_spacing # need to to make local adjustment for diagonal

        self.is_diag = self.data['package']['diagonal']
        self.pkg_pin_spacing = self.pin_spacing
        if self.is_diag:
            self.pkg_pin_spacing = self.pin_spacing * 1.414
        
        self.sides           = [0,1,2,3] # dip might be [0,3]
        self.side_count      = 4
        self.pins_per_side   = int(self.pin_count/self.side_count)
        
        self.corner_spacing  = self.pkg_pin_spacing*1.5
        self.width   = (self.pin_count/4-1) * self.pkg_pin_spacing + 2*self.corner_spacing
        self.height  = (self.pin_count/4-1) * self.pkg_pin_spacing + 2*self.corner_spacing
        
        return

    def build_side_pins(self, proto_pin, side):
        pins = dw.Group(id="side_pins")
        for i in range(self.pins_per_side):
            pin_offset = (self.pkg_pin_spacing * i) - (self.width/2 - self.corner_spacing)
            row_offset = (self.width - proto_pin.length) / 2
            
            direction = 1
            if side in [0,1]:
                direction = -direction
                
            if side in [0,2]:
                offset_x = row_offset * direction
                offset_y = pin_offset * -direction
            else:
                offset_x = pin_offset *- direction
                offset_y = row_offset * -direction

            pin_number = i + 1 + side * self.pins_per_side
            dw_pin = proto_pin.generate(pin_number, side)
            pins.append(dw.Use(dw_pin, offset_x, offset_y))

        return pins

    def generate(self):
        # construct and return a dw_footprint
        raise NotImplemented
    
    def calc_wire_paths(self, label_offset, horizontal=True):
        if self.is_diag:
            wire_paths = self._calc_wire_index_diag(label_offset, horizontal)
        else:
            wire_paths = self._calc_wire_index(label_offset, horizontal)
        return wire_paths

    def _calc_wire_index(self, label_offset, horizontal):        
        pin_side1       = int(self.pin_count/4)
        pin_side2       = int(self.pin_count/8)
        label_start     = label_offset
        extra_side      = 0
        label_pos_index = []

        # Check for uneven number of pins
        if self.pin_count/4 % 2 != 0:
            extra_side = 1

        # Left side
        for i in range(pin_side1):
            line = label_line()
            y = -self.width/2 + self.corner_spacing + i*self.pkg_pin_spacing
            line.start_x = -self.width/2
            line.start_y = y
            line.end_x = -label_start-self.width/2
            line.end_y = y

            label_pos_index.append(line)
        
        # Bottom Left
        for i in range(pin_side2+extra_side):
            line = label_line()
            line.start_x = self.corner_spacing + i*self.pkg_pin_spacing-self.width/2
            line.start_y = self.width/2
            line.end_x = -label_start-self.width/2
            line.end_y = 2*self.corner_spacing + (i+3)*self.pkg_pin_spacing
            label_pos_index.append(line)
            
        # Bottom Right
        for i in range(pin_side2):
            line = label_line()
            i2 = pin_side1 + pin_side2 - i - 1 + extra_side
            i3 = pin_side2 + extra_side + i
            line.start_x = self.corner_spacing + i3*self.pkg_pin_spacing-self.width/2
            line.start_y = self.width/2
            line.end_x = self.width/2 + label_start
            line.end_y =2*self.corner_spacing + i2*self.pkg_pin_spacing-self.width/2
            line.side = 1
            label_pos_index.append(line)
            
        # Right side
        for i in range(pin_side1):
            line = label_line()
            i2 = pin_side1 - i - 1
            line.start_x = self.width/2
            line.start_y = self.corner_spacing + i2*self.pkg_pin_spacing-self.width/2
            line.end_x = self.width/2 + label_start
            line.end_y = self.corner_spacing + i2*self.pkg_pin_spacing-self.width/2
            line.side = 1
            label_pos_index.append(line)
            
        # Top Right
        for i in range(pin_side2):
            line = label_line()
            i2 = pin_side1 - i - 1
            line.start_x = self.corner_spacing + i2*self.pkg_pin_spacing-self.width/2
            line.start_y = -self.width/2
            line.end_x = label_start+self.width/2
            line.end_y = -self.corner_spacing - (i+extra_side)*self.pkg_pin_spacing-self.width/2
            line.side = 1
            label_pos_index.append(line)
            
        # Top Left
        for i in range(pin_side2+extra_side):
            line = label_line()
            i2 = pin_side1 - pin_side2 - i -1
            i3 = pin_side2 + extra_side - i -1
            line.start_x = self.corner_spacing + i2*self.pkg_pin_spacing-self.width/2
            line.start_y = -self.width/2
            line.end_x = -label_start-self.width/2
            line.end_y = -self.corner_spacing - i3*self.pkg_pin_spacing-self.width/2
            label_pos_index.append(line)
        return label_pos_index
    
    def _calc_wire_index_diag(self, label_offset, horizontal):
        label_pos_index     = []
        pin_side1           = int(self.pin_count/4)
        label_start         = label_offset *1.414 # + (-self.corner_spacing*2.75) * SIN_45
        center_offset       = 0

        # Left Top side
        start_x0 = (-self.corner_spacing) * SIN_45
        start_y0 = (self.corner_spacing - self.width)  * SIN_45

        start_x1 = (self.corner_spacing - self.width) * SIN_45
        start_y1 = (self.corner_spacing) * SIN_45

        # Left Top side
        for i in range(pin_side1):
            line = label_line()
            step = self.pin_spacing * i
            line.start_x = start_x0 - step
            line.start_y = start_y0 + step
            line.end_x = start_x0 - step - label_start
            line.end_y = line.start_y  #- (pin_side1-i) * self.pin_spacing # - center_offset

            label_pos_index.append(line)

        # Left Bottom side
        for i in range(pin_side1):
            line = label_line()
            step = self.pin_spacing * i
            
            line.start_x = start_x1 + step
            line.start_y = start_y1 + step
            line.end_x = start_x1 + step - label_start
            line.end_y = line.start_y #start_y1 + (i) * self.pin_spacing + center_offset
            line.direction = -1

            label_pos_index.append(line)

        # Right Bottom side
        for i in range(pin_side1):
            line = label_line()
            step = self.pin_spacing * i
            line.start_x = - start_x0 + step
            line.start_y = - start_y0 - step
            line.end_x = - start_x0 + step + label_start
            line.end_y = line.start_y #+ (pin_side1-i)  * self.pin_spacing + center_offset
            line.side = 1

            label_pos_index.append(line)

        # Right Top side
        for i in range(pin_side1):
            line = label_line()
            step = self.pin_spacing * i
            
            line.start_x = - start_x1 - step
            line.start_y = - start_y1 - step
            line.end_x = - start_x1 - step + label_start
            line.end_y = line.start_y #- start_y1 - (i) * self.pin_spacing - center_offset
            line.side = 1
            line.direction = -1

            label_pos_index.append(line)

        return label_pos_index

class QFN(Quad):
    def generate(self):
        pad_width       = self.width - self.corner_spacing*2
        dot_width       = self.pkg_pin_spacing/4  #pin_width/3
        dot_position    = -self.width/2 + self.corner_spacing + dot_width/2
        rotate_opt      = f"rotate({45 if self.is_diag else 0}, {0}, {0})"
        
        border  = shapes.qfn_border(self.width, **self.data['package']['style'])
        pad     = shapes.qfn_pad(pad_width, **self.data['pin']['style'])
        dot     = dw.Circle( dot_position, dot_position, dot_width,
                            **self.data['package']['marker_style'])
        
        pt = pinout.Text(self.data, 'package')
        fp_text = pt.generate('text')
        pd_text = pt.generate('sub_text')
        
        pins = dw.Group(id="pins")
        proto = Pin(self.data)
        for side in range(4):
            pins.append(self.build_side_pins(proto, side))
            
        package = dw.Group(id="package", transform=rotate_opt)
        package.append(border)
        package.append(pad)
        package.append(dot)
        package.append(pins)

        footprint = dw.Group(id=self.data['name'])
        footprint.append(package)
        footprint.append(fp_text)
        footprint.append(pd_text)

        return footprint
    
class QFP(Quad):
    def generate(self):
        dot_width     = self.pkg_pin_spacing/3  #pin_width/3
        dot_position  = -self.width/2 + self.corner_spacing + dot_width/2
        rotate_opt    = f"rotate({45 if self.is_diag else 0}, {0}, {0})"
        
        proto_pin     = Pin(self.data)
        border  = shapes.qfn_border(self.width-2*proto_pin.length, **self.data['package']['style'])
        dot     = dw.Circle( dot_position, dot_position, dot_width,
                            **self.data['package']['marker_style'])
        
        pt = pinout.Text(self.data, 'package')
        fp_text = pt.generate('text')
        pd_text = pt.generate('sub_text')
        
        pins = dw.Group(id="pins")
        for side in range(4):
            pins.append(self.build_side_pins(proto_pin, side))
            
        package = dw.Group(id="package", transform=rotate_opt)
        package.append(border)
        package.append(dot)
        package.append(pins)

        footprint = dw.Group(id=self.data['name'])
        footprint.append(package)
        footprint.append(fp_text)
        footprint.append(pd_text)

        return footprint

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
    
    def junk():
        # footprint       = self.data['footprint'].split('-')[0]
        # pin_number      = self.data['footprint'].split('-')[1]
        # mapping         = self.data['mapping']
        # is_diag         = self.data['package']['diagonal']

        # self._calculate_size()
        # dw_labels = dw.Group(id="labels")
        # dw_lineholder = dw.Group(id="lines")
        # dw_footprint = self._generate_footprint()
        
        
        # label_pos_index = []

        # if footprint == "QFN" and not self.is_diag:
        #     label_pos_index = self.__calc_index_QFN()

        # elif footprint == "QFN" and self.is_diag:
        #     label_pos_index = self.__calc_index_QFN_diag()

        # elif footprint == "SOP":
        #     label_pos_index = self.__calc_index_SOP()
        
        # line = self.data["label"]["label_line_style"]
        # for i, m in enumerate(mapping):
        #     if i > int(pin_number)-1:
        #         pass
        #     elif hasattr( m, "__len__" ) and not isinstance( m, str ):
        #         line_op = label_pos_index[i]
        #         line_op.end_y -= (self.data['label']['height'] + self.data['label']['vert_spacing']) * (len(m)*0.75 if len(m) % 2 == 0 else len(m)/1.5)
        #         for j, k in enumerate(m):
        #             pin = self.data['pins'][k]
        #             line_op.end_y += (self.data['label']['height'] + self.data['label']['vert_spacing'])
        #             dw_pin, extent, extentmin = self._generate_pin_labels(str(i), pin, label_pos_index[i], afpin=j)
        #             dw_lineholder.append(shapes.label_line(line_op, extent, extentmin, **line))
        #             dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

        #     else:
        #         pin = self.data['pins'][m]
        #         line_op = label_pos_index[i]
        #         dw_pin, extent, extentmin = self._generate_pin_labels(m, pin, line_op)
        #         dw_lineholder.append(shapes.label_line(line_op, extent, 0, **line))
        #         dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))
        return
        
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
    
