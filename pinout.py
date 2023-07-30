import os
import sys

import drawsvg as dw
import yaml
from yamlinclude import YamlIncludeConstructor
import markdown as md

from pinoutOverview import utils
from pinoutOverview import shapes
from pinoutOverview import packages
from pinoutOverview import pinouts
from pinoutOverview import pins as Pin

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

class Header(utils.Region):
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

    
class Footer(utils.Region):
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

class Border(utils.Region):
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

        self.family = 'horizontal'
        if 'pinout_family' in self.data:
            self.family = self.data['pinout_family']
            
        return

    def load_data(self, path):
        data = {}

        YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader , base_dir=os.path.dirname(path))
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        template = dict()
        template['label'] = data['label']
        template['types'] = data['types']

        # load class static data.  Only happens once.
        Pin.Label(style=None, template=template['label'])
        Pin.Function(function=None, type_templates=template['types'])

        self.variant = dict()
        self.variant['pin_names'] = data['mapping']
        self.variant['function_rows'] = data['pins']


        return data

    def generate(self):
        print(self.canvas_width, "  ", self.canvas_height)

        # start with a page
        #   drawsvg's original coordinates are top left corner.
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
        pins = Pin.Pins(names=self.variant['pin_names'], rows=self.variant['function_rows'])
        if self.family == 'orthogonal':
            pinout = pinouts.OrthogonalPinout(self.data, pins)
        elif self.family == 'diagonal':
            pinout = pinouts.DiagonalPinout(self.data, pins)
        else:
            pinout = pinouts.HorizontalPinout(self.data, pins)
            
        dw_page.append(pinout.place(self.package_x_offset, self.package_y_offset))

        # Attach Pin Function Legend
        # legend = pinouts.PinLegend(self.data)
        # dw_page.append(dw.Use(legend.generate(self.canvas_width), -self.canvas_width/2, self.canvas_height/2-160))

        # Add quadrant text fields
        quads = dw.Group(id="quad_markdown")

        x_margin = border.width / 20
        y_margin = border.height / 20 
        q_width = (border.width - pinout.width) / 2 - (2 * x_margin)
        q_height = (border.height - pinout.height) / 2 - header.height - x_margin

        for i in range(4):
            if i in [0,2] : x = -border.width/2 + x_margin
            if i in [0,1] : y = header.bottom + y_margin

            if i in [1,3] : x = x_margin + pinout.width/2
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

