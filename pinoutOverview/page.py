import os
import sys

import drawsvg as dw
import markdown as md

import requests
from io import BytesIO
from PIL import ImageFont

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
        #self.height = 50 + 20
        #y += self.height / 2
        
        self.x = x
        self.y = y

        #print(self.template)
        
        text = utils.Text(self.template['title'])
        self.append(text.generate(items['title'], x=self.x, y=self.y))

        text = utils.Text(self.template['subtitle'])
        self.append(text.generate(items['subtitle'], x=self.x, y=self.y))

        return self

class Footer(Header):
    pass

class TextBlock(utils.Region):
    def __init__(self, template, id=None, width=0, height=0):
        self.template = template
        super().__init__(id=id, width=width, height=height)

        self.text = utils.Text(self.template['text'])
        #print(self.text.style['font_family'], self.text.style['font_size'], width, height)

        font_family = self.get_font_family()
        if font_family is None:
            font_family = self.get_google_font(self.text.style['font_family'])
            self.set_font_family(font_family)

        self.font_size = self.text.style['font_size']
        self.font = ImageFont.truetype(font_family, self.font_size)
        
        return

    @classmethod
    def set_font_family(cls, font_family):
        cls._font_family = font_family
        return font_family

    @classmethod
    def get_font_family(cls):
        try:
            cls._font_family.seek(0)
            return cls._font_family
        except:
            return None

    def get_google_font(self, family_name, kwargs=dict()):
        google_url = "https://fonts.googleapis.com/css2"
        kwargs.update(dict(family=family_name))
        req = requests.get(google_url, params=kwargs)
        print('downloading {}'.format(req.url))
    
        text = req.text
        start = text.rfind('url(')
        line = text[start+4:]
        end = line.find(')')
        font_url = line[:end]
    
        req = requests.get(font_url)
        font_family = BytesIO(req.content)
        #print(req.url)
    
        return font_family

    def wrap_string(self, string):
        words = string.split(' ')
        
        lines = []
        line = ''
        line_length = self.font.getlength(line)
        for word in words:
            word = word.strip()
            word_length = self.font.getlength(word)
            if  (line_length + word_length) < (self.width):
                line += word + ' '
            else:
                lines.append(line)
                line = word + ' '

            line_length = self.font.getlength(line)

        lines.append(line)
        height = len(lines) * self.font_size * 1.2

        return lines, height
    
    def place(self, strings, x, y, rotation=0):
        self.x = x
        self.y = y

        y_offset = 0
        for string in strings:
            #print(string)
            lines, height = self.wrap_string(string)
            self.append(self.text.generate(lines, x=self.x, y=self.y+y_offset))
            y_offset += height

        return self
    
class Border(utils.Region):
    def place(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation

        self.append(dw.Rectangle(-self.width/2, -self.height/2, self.width, self.height,
                                 stroke="black", stroke_width=2, fill="white"))
        return self

class Page():
    def __init__(self, page, pinout):
        self.template = page['template']
        self.variant = page['data']
        #self.template = config.PageConfig('dxcore_page').settings
        
        self.pinout = pinout


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
        dw_page.embed_google_font('Roboto Mono')
        dw_page.embed_google_font('Roboto')

        # add a Border
        border = Border(self.canvas_width, self.canvas_height)
        dw_page.append(border.place(0, 0))

        x_margin = border.width / 20
        y_margin = border.height / 20 

        # Attach Header (FIX height/2)
        if 'header' in self.variant:
            header = Header(self.template['header'])
            dw_page.append(header.place(self.variant['header'], x=0, y=border.top+header.height/2))
        
        # Attach Footer
        if 'footer' in self.variant:
            footer = Footer(self.template['footer'])
            dw_page.append(footer.place(self.variant['footer'], x=0, y=border.bottom-footer.height))

        dw_page.append(self.pinout.place(self.package_x_offset, self.package_y_offset))

        # Add quadrant text fields
        quads = dw.Group(id="quadrant_text")

        q_width = (border.width - self.pinout.width) / 2 - (2 * x_margin)
        q_height = (border.height - self.pinout.height) / 2 - header.height - x_margin

        # Attach Pin Function Legend to first quadrant
        x = -border.width/2 + x_margin
        y = header.bottom + y_margin
        
        legend = self.pinout.legend()
        dw_page.append(dw.Use(legend.generate(self.canvas_width), x,y))

        #print(self.variant['quadrant']
        for i in range(4):
            if i in [0,2] : x = -border.width/2 + x_margin
            if i == 0     : x += legend.width
            if i in [0,1] : y = header.bottom + y_margin

            if i in [1,3] : x = x_margin + self.pinout.width/2
            if i in [2,3] : y = self.pinout.bottom + y_margin

            id = f'quadrant_{i}'
            text = self.variant['quadrant'][f'text{i+1}']
            quad = TextBlock(self.template['quadrant'], id=id, width=q_width, height=q_height) #, fill='none', stroke='black'
            quads.append(quad.place(text, x, y))
            # quads.append(dw.Circle(x,y, 6, fill='black'))
            
        dw_page.append(quads)

        return dw_page

    def save(self, name):
        section = 'variant'
        
        dw = self.generate()

        basename = os.path.basename(name)
        name, suffix = os.path.splitext(basename)

        name = '{}/{}.svg'.format(section, name)

        dw.save_svg(name)

