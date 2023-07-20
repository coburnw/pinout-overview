import os
import sys

import drawsvg as dw
import yaml
from yamlinclude import YamlIncludeConstructor
import markdown as md

from pinoutOverview import shapes
from pinoutOverview import packages

class HtmlDiv(dw.DrawingParentElement):
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Element/foreignObject
    # https://stackoverflow.com/a/66771364
    # css https://stackoverflow.com/a/20720935
    
    TAG_NAME = 'foreignObject'

    def __init__(self, width, height, **kwargs):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.kwargs = kwargs
        return
    
    def place(self, html, x, y, rotation=0):
        # one dirty little trick
        super().__init__(x=x, y=y, width=self.width, height=self.height, **self.kwargs)
        self.x = x
        self.y = y
        self.rotation = rotation

        raw = dw.Raw('<div xmlns="http://www.w3.org/1999/xhtml">{}</div>'.format(html))
        self.append(raw)

        return self

    @property
    def top(self):
        return self.y - self.height

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def left(self):
        return self.x - self.width/2

    @property
    def right(self):
        return self.x + self.width/2

class Markdown(HtmlDiv):
    def place(self, markdown, x, y, rotation=0):
        html = md.markdown(markdown)
        p = super().place(html, x, y, rotation)
        return p

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

class Region(dw.Group):
    # a group of drawing elements that keeps a simplistic view of its own size and position
    def __init__(self, width=0, height=0, **kwargs):
        super().__init__(**kwargs)
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.rotation = 0
        return

    @property
    def top(self):
        return self.y - self.height/2

    @property
    def bottom(self):
        return self.y + self.height/2

    @property
    def left(self):
        return self.x - self.width/2

    @property
    def right(self):
        return self.x + self.width/2

    def place(self, x, y, **kwargs):
        raise NotImplmented
        
class Pinout(Region):
    def __init__(self, data, **kwargs):
        self.data = data
        self.mapping = self.data['mapping']        

        pkg         = self.data['footprint'].split('-')[0]
        pin_count   = int(self.data['footprint'].split('-')[1])
        pin_spacing = self._calculate_pin_spacing()

        height = (pin_count+1)/2 * pin_spacing
        super().__init__(width=0, height=height, **kwargs)
        
        if pkg == 'QFN':
            self.package = packages.QFN(self.data, pin_count, pin_spacing)
        elif pkg == 'QFP':
            self.package = packages.QFP(self.data, pin_count, pin_spacing)
        elif pkg == 'SOP':
            self.package = packages.SOP(self.data, pin_count)
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

    def place(self, x, y):
        self.x = x
        self.y = y
        #dw_pinout = dw.Group(id="pinout")

        dw_footprint = self.package.generate()
        self.append(dw.Use(dw_footprint, 0, 0))
        
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

        self.append(dw.Use(dw_lineholder, 0, 0))
        self.append(dw.Use(dw_labels, 0, 0))
    
        return self                

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

class Header(Region):
    def place(self, data, x, y):
        self.height = 50 + 20
        y += self.height / 2
        
        self.x = x
        self.y = y

        print(data['name'], self.x, self.y)
        self.append(dw.Text(data['name'], 40, x, y,
                            text_anchor='middle', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono'))
        
        self.append(dw.Text(data['subtitle'], 20, x, y+50,
                            text_anchor='middle', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono'))

        return self

    
class Footer(Region):
    def place(self, data, x, y):
        self.height = 50 + 20
        y -= self.height

        self.x = x
        self.y = y 

        print(data['name'], self.x, self.y)
        self.append(dw.Text(data['name'], 40, x, y,
                            text_anchor='middle', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono'))
        
        self.append(dw.Text(data['subtitle'], 20, x, y+50,
                            text_anchor='middle', dominant_baseline='middle',
                            fill="black", font_weight='bold', font_family='Roboto Mono'))

        
        return self

class Border(Region):
    def place(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation

        self.append(dw.Rectangle(-self.width/2, -self.height/2, self.width, self.height,
                                 stroke="black", stroke_width=2, fill="white"))
        return self

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
        print(self.canvas_width, "  ", self.canvas_height)

        # start with a page
        dw_page = dw.Drawing(self.canvas_width, self.canvas_height, origin='center', displayInline=True)
        dw_page.embed_google_font("Roboto Mono")

        # add a Border
        border = Border(self.canvas_width-25, self.canvas_height-25)
        dw_page.append(border.place(0, 0))
                       
        # Attach Header
        header = Header(width=border.width, height=0)
        dw_page.append(header.place(self.data, x=0, y=border.top)) #-self.canvas_height/2+60
        print(header.bottom)
        
        # Attach Footer
        footer = Footer(width=border.width, height=0)
        dw_page.append(footer.place(self.data, x=0, y=border.bottom))
        print(footer.top)
        
        # Build and place pinout
        pinout = Pinout(self.data)
        dw_page.append(pinout.place(self.package_x_offset, self.package_y_offset))

        # Attach Pin Function Legend
        legend = PinLegend(self.data)
        dw_page.append(dw.Use(legend.generate(self.canvas_width), -self.canvas_width/2, self.canvas_height/2-160))

        # Add quadrant text fields
        quads = dw.Group(id="quad_markdown")

        x_margin = border.width / 20  #100
        y_margin = border.height / 20 #50
        q_width = (border.width / 2) - (2 * x_margin)
        q_height = (border.height - pinout.height) / 2 - header.height - x_margin

        for i in range(4):
            if i in [0,2] : x = -border.width/2 + x_margin
            if i in [0,1] : y = header.bottom + y_margin

            if i in [1,3] : x = x_margin
            if i in [2,3] : y = pinout.bottom + y_margin

            id = f'quad_{i}'
            md = self.data['markdown'][id]
            quad = Markdown(id=id, width=q_width, height=q_height, fill='none', stroke='black')
            quads.append(quad.place(md, x, y))
            
        dw_page.append(quads)

        return dw_page

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

