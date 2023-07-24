import math

import drawsvg as dw

from pinoutOverview import utils
from pinoutOverview import packages
from pinoutOverview import shapes

SIN_45 = math.sin(math.radians(45)) #0.7071067811865475

class Label():
    def __init__(self, data, direction=1):
        self.data = data
        self.direction = direction
        self.label = self.data['label']
        self.width    = self.label['width']
        self.height   = self.label['height']
        self.spacing  = self.label['spacing']
        self.offset   = self.label['offset']
        self.vert_spacing  = self.label['vert_spacing']

        #style dicts
        self.box_style = self.label['box_style']
        self.alt_box_style = self.label['alt_box_style']

        self.text_style = self.label['text_style']
        self.alt_text_style = self.label['alt_text_style']
        
        self.line_style    = self.label['label_line_style']
        return

    def box_generate(self, style_adders=None, is_alt=False):
        if is_alt:
            style = dict(self.alt_box_style)
        else:
            style = dict(self.box_style)

        adders = style_adders["box_style"] if "box_style" in style_adders else {}
            
        skew = -self.height/2*self.direction
        adders["transform"] = f" skewX({skew})"

        style |= adders
        
        box = shapes.label_box(self.width, self.height, **style)

        return box

    def text_generate(self, value, style_adders=None, is_alt=False):
        if is_alt:
            style = dict(self.alt_text_style)
        else:
            style = dict(self.text_style)

        adders = style_adders["text_style"] if "text_style" in style_adders else {}
            
        style |= adders

        dw = shapes.label_text(str(value), self.height, **style)

        return dw

    def caption_generate(self, value, style_adders=None, is_alt=False):
        #t = Text(self.data, 'label')
        #desc = t.generate('text', caption)

        style = dict(self.text_style)
        
        adders = dict()
        adders['fill'] = 'black'
        adders['text_anchor'] = 'start'

        style |= adders
        
        dw = shapes.label_text(str(value), self.height, **style)
        
        return dw
    
    def generate(self, name, style_adders, is_alt=False, caption=None):
        dw_label = dw.Group(id=f"Label-{name}-{'alt' if is_alt else 'std'}-{self.direction}")
        dw_label.append(self.box_generate(style_adders, is_alt))
        dw_label.append(self.text_generate(name, style_adders, is_alt))
        if caption is not None:
            dx = self.width/2 + self.width/5
            dy = (self.height-10) / 10
            dw_label.append(dw.Use(self.caption_generate(caption, style_adders, is_alt), dx, dy))

        return dw_label

class PinLabels:
    def __init__(self, data):
        self.data = data
        return

    def generate(self, pin_number, pin_functions, side_index, slant_direction=0):        
        # returns a horizontal row of labels starting at origin increasing left or right for given side_index
        #     slant_direction  # -1, 0, +1, left-slant, square, right-slant

        label_position = 0
        extent=0

        dw_labels = dw.Group()

        append_direction = -1                # (append direction) -1 to the left, +1 to the right, 0 stacked?
        if side_index in [2,3]:
            append_direction = -append_direction

        for function in pin_functions:
            label = Label(self.data, slant_direction)
            ftype = self.data['types'][function['type']]

            if "skip" in ftype and ftype['skip']:
                if function['type'] == 'spacer':
                    label_position += label.spacing + label.width

                continue

            lbl = label.generate(function["name"], ftype, function["alt"])

            x = (label_position + label.width * 0.5) * append_direction
            y = 0
                
            label_position += label.spacing + label.width
            extent=(label_position-label.width*0.5) * append_direction
        
            dw_labels.append(dw.Use(lbl, x, y))

        dw_pin_labels = dw.Group(id=f"PIN-{pin_number}")
        dw_pin_labels.append(dw.Line(0,0, extent, 0, **label.line_style))
        dw_pin_labels.append(dw_labels)

        return dw_pin_labels, extent, -label.offset*append_direction

class label_line:
    def __init__(self):
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.side = -1
        self.direction = 1

class Pinout(utils.Region):
    def __init__(self, data, diagonal=False, **kwargs):
        self.data = data
        self.diagonal = diagonal
        
        self.mapping = self.data['mapping']        

        pkg         = self.data['footprint'].split('-')[0]
        pin_count   = int(self.data['footprint'].split('-')[1])

        self.row_spacing = self._calculate_row_spacing()

        if diagonal:
            pin_spacing = self.row_spacing * math.sqrt(2)
        else:
            pin_spacing = self.row_spacing
        
        if pkg == 'QFN':
            self.package = packages.QFN(self.data, pin_count, pin_spacing)
        elif pkg == 'QFP':
            self.package = packages.QFP(self.data, pin_count, pin_spacing)
        elif pkg == 'SOP':
            self.package = packages.SOP(self.data, pin_count)
        else:
            raise 'unrecognized package: "{}"'.format(pkg)

        width = self.package.width
        height = width
        if diagonal:
            height = height * math.sqrt(2)
            
        super().__init__(width=width, height=height, **kwargs)
        
        return

    def _calculate_row_spacing(self):
        max_lines = 1
        
        for i, m in enumerate(self.mapping):
                if hasattr( m, "__len__" ) and not isinstance( m, str ):
                    if len(m) > max_lines:
                        max_lines = len(m)

        if max_lines > 1:
            raise 'multi-row pins not implemented'
        
        row_spacing = max_lines * (self.data['label']['height'] + self.data['label']['vert_spacing'])

        return row_spacing

    def attach_label_row(self, pin_number, row):
        pass

    def place(self, x, y, orthogonal=False):
        # construct a pinout
        raise NotImplemented

class OrthogonalPinout(Pinout):
    def fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        for pin_number in pin_numbers:
            line = label_line()
            side_index, pin_index = self.package.side_from_pin_number(pin_number)
            position, side, direction = self.package._calc_offset_point(pin_number)
            print(side, direction, position['x'], position['y'])
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
        
    def place(self, x, y):
        self.x = x
        self.y = y

        dw_footprint = self.package.generate()
        self.append(dw.Use(dw_footprint, 0, 0))
        
        label = Label(self.data)

        label_pos_index = []
        #label_pos_index = self._calc_wire_paths(label.offset)
        fanout, dw_fanout = self.fanout(self.package.pin_numbers, label.offset)
        label_pos_index = fanout
        
        dw_labels = dw.Group(id="labels")
        dw_lineholder = dw.Group(id="lines")

        # attach function labels to each pin
        for i, m in enumerate(self.mapping):
            if i > int(self.package.number_of_pins)-1:
                pass
            elif hasattr( m, "__len__" ) and not isinstance( m, str ):
                line_op = label_pos_index[i]
                line_op.end_y -= (label.height + label.vert_spacing) * (len(m)*0.75 if len(m) % 2 == 0 else len(m)/1.5)
                # multi-line function list
                for j, k in enumerate(m):
                    line_op.end_y += self.row_spacing
                    pin = self.data['pins'][k]
                    labels = PinLabels(self.data)
                    dw_pin, extent, extentmin = labels.generate(str(i), pin, label_pos_index[i], afpin=j)
                    dw_lineholder.append(shapes.label_line(line_op, extent, extentmin, **label.line_style))
                    dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

            else:
                line_op = fanout[i]
                dw_pin, extent, extentmin = self.build_function_row(i, m)
                dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

        self.append(dw.Use(dw_fanout, 0, 0))
        self.append(dw.Use(dw_lineholder, 0, 0))
        self.append(dw.Use(dw_labels, 0, 0))
    
        return self                

    def build_function_row(self, number, name):
        side_index, pin_index = self.package.side_from_pin_number(number)
        
        pin = self.data['pins'][name]
        labels = PinLabels(self.data)

        dw_row, extent, extentmin = labels.generate(number, pin, side_index)

        transform = 'rotate(0)'
        if side_index in [1,3]:
            transform = 'rotate(-90)'

        dw_row = dw.Use(dw_row, 0, 0, transform=transform)
        
        return dw_row, extent, extentmin
    
class DiagonalPinout(Pinout):
    def __init__(self, data, **kwargs):
        super().__init__(data, diagonal=True, **kwargs)
        
        self.width = 0
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

    def fanout(self, pin_numbers, offset):
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
        
    def place(self, x, y):
        self.x = x
        self.y = y

        dw_footprint = self.package.generate(diagonal=True)
        self.append(dw.Use(dw_footprint, 0, 0, transform='rotate(45)'))
        
        label = Label(self.data)

        #label_pos_index = self._calc_wire_paths(label.offset)
        fanout, dw_fanout = self.fanout(self.package.pin_numbers, label.offset)
        label_pos_index = fanout
        
        dw_labels = dw.Group(id="labels")
        dw_lineholder = dw.Group(id="lines")

        # attach function labels to each pin
        for i, m in enumerate(self.mapping):
            if i > int(self.package.number_of_pins)-1:
                pass
            elif hasattr( m, "__len__" ) and not isinstance( m, str ):
                line_op = label_pos_index[i]
                line_op.end_y -= (label.height + label.vert_spacing) * (len(m)*0.75 if len(m) % 2 == 0 else len(m)/1.5)
                # multi-line function list
                for j, k in enumerate(m):
                    pin = self.data['pins'][k]
                    line_op.end_y += self.row_spacing
                    labels = PinLabels(self.data)
                    dw_pin, extent, extentmin = labels.generate(str(i), pin, label_pos_index[i], afpin=j)
                    dw_lineholder.append(shapes.label_line(line_op, extent, extentmin, **label.line_style))
                    dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

            else:
                line_op = fanout[i]
                dw_pin, extent, extentmin = self.build_function_row(i, m)
                dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

        self.append(dw.Use(dw_fanout, 0, 0))
        self.append(dw.Use(dw_lineholder, 0, 0))
        self.append(dw.Use(dw_labels, 0, 0))
    
        return self                

    def build_function_row(self, number, name):
        side_index, pin_index = self.package.side_from_pin_number(number)
        
        pin = self.data['pins'][name]
        labels = PinLabels(self.data)
        
        return labels.generate(number, pin, side_index)
    
class HorizontalPinout(Pinout):
    # fanout calculates our true height and width property.  Values are invalid until construction.
    
    def fanout(self, pin_numbers, offset):
        wires = []
        dw_wires = dw.Group()
        
        row_count = 0
        for pin_number in pin_numbers:
            line = label_line()
            side_index, pin_index = self.package.side_from_pin_number(pin_number)
            position, side, direction = self.package._calc_offset_point(pin_number)

            print(side, direction, position['x'], position['y'])
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
        
    def place(self, x, y):
        self.x = x
        self.y = y

        dw_footprint = self.package.generate()
        self.append(dw.Use(dw_footprint, 0, 0))
        
        label = Label(self.data)

        #label_pos_index = self._calc_wire_paths(label.offset)
        fanout, dw_fanout = self.fanout(self.package.pin_numbers, label.offset)
        label_pos_index = fanout
        
        dw_labels = dw.Group(id="labels")
        dw_lineholder = dw.Group(id="lines")

        # attach function labels to each pin
        for i, m in enumerate(self.mapping):
            if i > int(self.package.number_of_pins)-1:
                pass
            elif hasattr( m, "__len__" ) and not isinstance( m, str ):
                line_op = label_pos_index[i]
                line_op.end_y -= (label.height + label.vert_spacing) * (len(m)*0.75 if len(m) % 2 == 0 else len(m)/1.5)
                # multi-line function list
                for j, k in enumerate(m):
                    pin = self.data['pins'][k]
                    line_op.end_y += self.row_spacing
                    labels = PinLabels(self.data)
                    dw_pin, extent, extentmin = labels.generate(str(i), pin, label_pos_index[i], afpin=j)
                    dw_lineholder.append(shapes.label_line(line_op, extent, extentmin, **label.line_style))
                    dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

            else:
                line_op = fanout[i]
                dw_pin, extent, extentmin = self.build_function_row(i, m)
                dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

        self.append(dw.Use(dw_fanout, 0, 0))
        self.append(dw.Use(dw_lineholder, 0, 0))
        self.append(dw.Use(dw_labels, 0, 0))
    
        return self                

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
    
    def build_function_row(self, number, name):
        direction = self.direction_from_pin(number)
        
        side_index = 0
        if direction > 0: # 'right'
            side_index = 2
            
        pin = self.data['pins'][name]
        labels = PinLabels(self.data)
        
        return labels.generate(number, pin, side_index)
    
class PinLegend:
    def __init__(self, data):
        self.data = data
        return
    
    def generate(self, canvas_width):
        label_amount = len(self.data['types'])

        column1 = canvas_width/7
        column2 = canvas_width/3.2
        column3 = canvas_width/2
        column4 = canvas_width/3*2

        legends = dw.Group(id="legends")

        for i, typ in enumerate(self.data['types']):
            ftype = self.data['types'][typ]
            if "skip" in ftype:
                if ftype["skip"]:
                    continue
            legend_group = dw.Group(id=f"legend_{typ}")

            label = Label(self.data)
            lbl = label.generate(typ.upper(), ftype, caption=ftype['description'])
            legend_group.append(dw.Use(lbl, 0, 0))
            
            if i < label_amount/3-1:
                legends.append(dw.Use(legend_group, column1, (i)*(label.height+label.spacing)))
            elif i < label_amount/3*2-1:
                legends.append(dw.Use(legend_group, column2, (i - label_amount/3)*(label.height+label.spacing)))
            else:
                legends.append(dw.Use(legend_group, column3, (i - label_amount/3*2)*(label.height+label.spacing)))

        legend_normal = dw.Group(id="legend_normal")

        label = Label(self.data)
        lbl = label.generate("FUNC", {'box_style': {'fill': 'white', 'stroke': 'black'}})
        legend_normal.append(dw.Use(lbl, 0, 0))
        text_normal = dw.Text("Default Function", label.height, 0, 0,
                            text_anchor='start', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono')
        legend_normal.append(dw.Use(text_normal, label.width + 10, (label.height-10)/10))
        legends.append(dw.Use(legend_normal, column4, 0))

        legend_alt = dw.Group(id="legend_alt")
        label = Label(self.data)
        lbl = label.generate("FUNC", {'box_style': {'fill': 'white', 'stroke': 'black'}}, is_alt=True)
        
        legend_alt.append(dw.Use(lbl, 0, 0))
        text_alt = dw.Text("Alternate Function", label.height, 0, 0,
                            text_anchor='start', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono')
        legend_alt.append(dw.Use(text_alt, label.width + 10, (label.height-10)/10))
        legends.append(dw.Use(legend_alt, column4, label.height+label.spacing))

        return legends

