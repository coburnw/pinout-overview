import os
import sys

import drawsvg as dw
import markdown as md

from pinoutOverview import utils
from pinoutOverview import config

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
    def __init__(self, template):
        self.template = template
        super().__init__(width=0, height=template['height'])
        return
    
    def place(self, items, x, y):
        self.height = 50 + 20
        y += self.height / 2
        
        self.x = x
        self.y = y

        text = utils.Text(self.template['text1'])
        self.append(text.generate(items['text1'], x=self.x, y=self.y))

        text = utils.Text(self.template['text2'])
        self.append(text.generate(items['text2'], x=self.x, y=self.y))

        return self

    
class Footer(Header):
    pass

class Border(utils.Region):
    def place(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation

        self.append(dw.Rectangle(-self.width/2, -self.height/2, self.width, self.height,
                                 stroke="black", stroke_width=2, fill="white"))
        return self

class Page():
    def __init__(self, variant, pinout):
        self.variant = variant
        self.pinout = pinout

        self.template = config.PageConfig('dxcore_page').settings

        self.canvas_height = self.template.get('height', 1000)
        self.canvas_width = self.template.get('width', 1000)

        self.package_x_offset = 0 
        self.package_y_offset = 0
        
        return

    def generate(self):
        print(self.canvas_width, "  ", self.canvas_height)

        # start with a page
        #   drawsvg's original coordinates are top left corner.
        #   we move zero zero to center of page
        dw_page = dw.Drawing(self.canvas_width, self.canvas_height, origin='center', displayInline=True)
        dw_page.embed_google_font("Roboto Mono")

        # add a Border
        border = Border(self.canvas_width, self.canvas_height)
        dw_page.append(border.place(0, 0))

        # Attach Header
        if 'header' in self.variant:
            header = Header(self.template['header'])
            dw_page.append(header.place(self.variant['header'], x=0, y=border.top))
        
        # Attach Footer
        if 'footer' in self.variant:
            footer = Footer(self.template['footer'])
            dw_page.append(footer.place(self.variant['footer'], x=0, y=border.bottom))

        dw_page.append(self.pinout.place(self.package_x_offset, self.package_y_offset))

        # Attach Pin Function Legend
        # legend = pinouts.PinLegend(self.data)
        # dw_page.append(dw.Use(legend.generate(self.canvas_width), -self.canvas_width/2, self.canvas_height/2-160))

        # Add quadrant text fields
        quads = dw.Group(id="quadrant_text")

        x_margin = border.width / 20
        y_margin = border.height / 20 
        q_width = (border.width - self.pinout.width) / 2 - (2 * x_margin)
        q_height = (border.height - self.pinout.height) / 2 - header.height - x_margin

        for i in range(4):
            if i in [0,2] : x = -border.width/2 + x_margin
            if i in [0,1] : y = header.bottom + y_margin

            if i in [1,3] : x = x_margin + self.pinout.width/2
            if i in [2,3] : y = self.pinout.bottom + y_margin

            id = f'quadrant_{i}'
            md = self.variant['quadrant'][f'text{i+1}']
            md = ' '.join(md.split())
            quad = Markdown(id=id, width=q_width, height=q_height, fill='none', stroke='black')
            quads.append(quad.place(md, x, y))
            
        dw_page.append(quads)

        return dw_page

    def save(self, name):
        section = 'variant'
        
        dw = self.generate()

        basename = os.path.basename(name)
        name, suffix = os.path.splitext(basename)

        name = '{}/{}.svg'.format(section, name)

        dw.save_svg(name)

