import drawsvg as dw

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
        
class TextStyle:
    def __init__(self, section, style_key):
        self.style_dict    = section[style_key]
        self.family   = self.style_dict['font_family']
        
        parent_height = section.get('height',30)
        self.size     = self.style_dict.get('font_size', parent_height-parent_height/5)
        self.style    = self.style_dict.get('font_style', 'normal')
        self.disabled = self.style_dict.get('text_disabled', False) 

        return

    def to_dict(self):
        # make a copy of the style dict and remove font_size
        d = dict(self.style_dict)
        if 'font_size' in d:
            del d['font_size']        
        return d

class Text:
    def __init__(self, data, section_name):
        self.data = data
        self.section_key = section_name
        return

    def load_text(self, text_name):
        style_key    = f'{text_name}_style'
        offset_key   = f'{text_name}_offset'
        text_section = f'{self.section_key}_text'
        
        self.x_offset = 0
        self.y_offset = self.data[self.section_key].get(offset_key, 0)
        self.style    = TextStyle(self.data[self.section_key], style_key)

        self.text = ''
        if text_section in self.data:
            self.text = self.data[text_section].get(text_name, '')
            
        return

    def generate(self, text_name, text_value=None, x=0, y=0):
        self.load_text(text_name)
        
        if text_value is not None:
            self.text = text_value

        if self.style.disabled:
            self.text = ''

        x += self.x_offset
        y += self.y_offset
        return  dw.Text(self.text, self.style.size, x, y, **self.style.to_dict())

