import os
import sys

import drawsvg as dw
import yaml
from yamlinclude import YamlIncludeConstructor

from pinoutOverview import shapes
from pinoutOverview import packages

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

    def generate(self, pin, pin_functions, op, afpin=0): #number,side        
        side = op.side
        direction = op.direction

        label_position = 0
        extent=0

        dw_pin_label = dw.Group(id=f"PIN-{pin}-{afpin}-{'left' if side == -1 else 'right'}-{direction}")

        for function in pin_functions:
            label = Label(self.data, direction)
            ftype = self.data['types'][function['type']]

            if "skip" in ftype and ftype['skip']:
                if function['type'] == 'spacer':
                    label_position += label.spacing + label.width

                continue

            lbl = label.generate(function["name"], ftype, function["alt"])
            dw_pin_label.append(dw.Use(lbl, (label_position+label.width*0.5)*side, 0))

            label_position += label.spacing + label.width
            extent=(label_position-label.width*0.5)*side
        
        return dw_pin_label, extent, -label.offset*side

class Pinout:
    def __init__(self, data):
        self.data = data
        self.mapping = self.data['mapping']        

        pkg         = self.data['footprint'].split('-')[0]
        pin_count   = int(self.data['footprint'].split('-')[1])
        pin_spacing = self._calculate_pin_spacing()
        
        if pkg == 'QFN':
            self.package = packages.Quad(self.data, pin_count, pin_spacing)
        elif pkg == 'SOP':
            self.package = SOP(self.data, pin_count)
        else:
            raise 'unsupported package'
        return

    def _calculate_pin_spacing(self):
        max_lines = 2
        for i, m in enumerate(self.mapping):
                if hasattr( m, "__len__" ) and not isinstance( m, str ):
                    if len(m) > max_lines:
                        max_lines = len(m)
        
        pin_spacing = (max_lines-1) * (self.data['label']['height'] + self.data['label']['vert_spacing'])
        return pin_spacing

    def generate(self):        
        dw_pinout = dw.Group(id="pinout")

        dw_footprint = self.package.generate()
        dw_pinout.append(dw.Use(dw_footprint, 0, 0))
        
        label = Label(self.data)

        label_pos_index = []
        label_pos_index = self.package.calc_wire_paths(label.offset)
        
        dw_labels = dw.Group(id="labels")
        dw_lineholder = dw.Group(id="lines")

        # attach function labels to each pin
        for i, m in enumerate(self.mapping):
            if i > int(self.package.pin_count)-1:
                pass
            elif hasattr( m, "__len__" ) and not isinstance( m, str ):
                line_op = label_pos_index[i]
                line_op.end_y -= (label.height + label.vert_spacing) * (len(m)*0.75 if len(m) % 2 == 0 else len(m)/1.5)
                # multi-line function list?
                for j, k in enumerate(m):
                    pin = self.data['pins'][k]
                    line_op.end_y += self.package.pin_spacing
                    labels = PinLabels(self.data)
                    dw_pin, extent, extentmin = labels.generate(str(i), pin, label_pos_index[i], afpin=j)
                    dw_lineholder.append(shapes.label_line(line_op, extent, extentmin, **label.line_style))
                    dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

            else:
                pin = self.data['pins'][m]
                line_op = label_pos_index[i]
                labels = PinLabels(self.data)
                dw_pin, extent, extentmin = labels.generate(m, pin, line_op)
                dw_lineholder.append(shapes.label_line(line_op, extent, 0, **label.line_style))
                dw_labels.append(dw.Use(dw_pin, line_op.end_x, line_op.end_y))

        dw_pinout.append(dw.Use(dw_lineholder, 0, 0))
        dw_pinout.append(dw.Use(dw_labels, 0, 0))
    
        return dw_pinout                


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
    
class Page:
    def __init__(self, path):
        self.data = self.load_data(path)

        self.canvas_height = 0
        self.canvas_width = 0

        self.canvas_width   = 2500 if 'canvas_width' not in self.data else self.data['canvas_width']
        self.canvas_height  = 1000 if 'canvas_height' not in self.data else self.data['canvas_height']

        self.package_x_offset = 0 if 'package_x_offset' not in self.data else self.data['package_x_offset']
        self.package_y_offset = 0 if 'package_y_offset' not in self.data else self.data['package_y_offset']

        return

    def load_data(self, path):
        data = {}

        YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader , base_dir=os.path.dirname(path))
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        return data

    def generate(self):
        # start with a page
        dw_page = dw.Drawing(self.canvas_width, self.canvas_height, origin='center', displayInline=True)
        dw_page.embed_google_font("Roboto Mono")

        # Attach a border
        dw_page.append(dw.Rectangle(-self.canvas_width/2, -self.canvas_height/2, self.canvas_width,
                                      self.canvas_height, stroke="black", stroke_width=2, fill="white"))

        print(self.canvas_width, "  ", self.canvas_height)

        # Build and place pinout
        pinout = Pinout(self.data)
        dw_page.append(dw.Use(pinout.generate(), self.package_x_offset, self.package_y_offset))

        # Attach Pin Function Legend
        legend = PinLegend(self.data)
        dw_page.append(dw.Use(legend.generate(self.canvas_width), -self.canvas_width/2, self.canvas_height/2-160))

        # Attach Title
        dw_page.append(dw.Use(self._generate_title(), 0, -self.canvas_height/2+60))

        # if 'custom_image' in self.data:

        # if 'text_field' in self.data:

        # if 'line' in self.data:

        # if 'custom_label' in self.data:
        return dw_page

    def _generate_title(self):
        title = dw.Group(id="title")
        title.append(dw.Text(self.data['name'], 40, 0, 0,
                            text_anchor='middle', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono'))
        title.append(dw.Text(self.data['subtitle'], 20, 0, 50,
                            text_anchor='middle', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono'))
        return title

    def _generate_image(self):
        #     print("Custom Image Found")
        #     programmer = fp.Programmer()
        #     board = programmer.draw()
        #     self.dwPinout.append(dw.Use(board, self.data['custom_image']['x_offset'], self.data['custom_image']['y_offset']))
        #     #for l in self.data['custom_image']['connections']:
        #     #    print(l[1])
        #     #    img_line_op = label_pos_index[l[1]]
        #     #    print(img_line_op)
        #     #    img_line = programmer.line(l[0], img_line_op.end_x, img_line_op.end_y, **line)
        #     #    self.dwPinout.append(img_line)
        return

    def _generate_text_field(self):
        #     for field in self.data['text_field']:
        #         self.dwPinout.append(dw.Text(field['text'], field['font_size'], field['x'], field['y'], **field['style']))
        return

    def _generate_line(self):
        dw_lineholder = dw.Group(id="lines")
        #     for l in self.data['line']:
        #         c_line = dw.Path(**l['style'])
        #         for cmd in l['path']:
        #             if cmd[0] == 'M':
        #                 c_line.M(cmd[1], cmd[2])
        #             elif cmd[0] == 'L':
        #                 c_line.L(cmd[1], cmd[2])
        #             elif cmd[0] == 'H':
        #                 c_line.H(cmd[1])
        #             elif cmd[0] == 'V':
        #                 c_line.V(cmd[1])
        #             elif cmd[0] == 'Q':
        #                 c_line.Q(cmd[1], cmd[2], cmd[3], cmd[4])
        #             elif cmd[0] == 'C':
        #                 c_line.C(cmd[1], cmd[2], cmd[3], cmd[4], cmd[5], cmd[6])
        #             elif cmd[0] == 'Z':
        #                 c_line.Z()
        #         self.dwPinout.append(c_line)
        return

    def _generate_custom_label(self):
        #     for l in self.data['custom_label']:
        #         ftype  = self.data['types'][l["type"]]
        #         if "width" in ftype:
        #             label_width = ftype["width"]
        #         c_label = self._generate_label(l['text'], ftype, label_width)
        #         self.dwPinout.append(dw.Use(c_label, l['x'], l['y']))
        return
    
        
    def save(self, out):
        dw = self.generate()
        if out == "":
            out = self.data['name'] + ".svg"
        if out[-4:] != ".svg":
            out += ".svg"
        
        dw.save_svg(out)

if __name__ == "__main__":
    page = Page(sys.argv[1])

    fname = ""
    if len(sys.argv) > 2:
        fname = sys.argv[2]
    page.save(fname)

