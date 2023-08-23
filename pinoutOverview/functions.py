import drawsvg as dw

from pinoutOverview import shapes
from template import function_label

class Label(dw.Group):
    def __init__(self, style=None, template=None, id=None):
        if template is not None:
            self.set_template(template)
            return

        self.template = function_label.label_template
        super().__init__(id=id)  #id's matter. dupes create odd problems...  Use None or a unique id.
        self.style_adders = style
        return

    @classmethod
    def set_template(cls, template):
        cls.template = template
        return

    @property
    def width(self):
        return self.template['width']

    @property
    def height(self):
        return self.template['height']
        
    @property
    def offset(self):
        return self.template['offset']
    
    @property
    def spacing(self):
        return self.template['spacing']

    @property
    def vert_spacing(self):
        return self.template['vert_spacing']
        
    @property
    def line_style(self):
        return self.template['label_line_style']
         
    @property
    def skip(self):
        return "skip" in self.style and self.style['skip']

    @property
    def slant_left(self):
        return -1

    @property
    def slant_right(self):
        return +1

    @property
    def slant_none(self):
        return 0
    
    def box_generate(self, slant, is_alt):

        style = dict(self.template['box_style'])
        if is_alt:
            style = dict(self.template['alt_box_style'])

        adders = self.style_adders["box_style"] if "box_style" in self.style_adders else {}
        adders["transform"] = 'skewX({})'.format(-self.height/2*slant)
        style |= adders
        
        dw_shape = shapes.label_box(self.width, self.height, **style)

        return dw_shape

    def text_generate(self, value, x_offset=0, is_alt=False, footnote=None):

        style = dict(self.template['text_style'])
        if is_alt:
            style = dict(self.template['alt_text_style'])

        adders = dict(self.style_adders['text_style']) if 'text_style' in self.style_adders else {}

        # if x_offset != 0:
        #     adders['text_anchor'] = 'end'
            
        style |= adders

        dw_shape = shapes.label_text(str(value), self.height, x_offset, **style)

        return dw_shape

    def caption_generate(self, value, is_alt):

        style = dict(self.text_style)

        # add a caption_text section to label template
        adders = dict()
        adders['fill'] = 'black'
        adders['text_anchor'] = 'start'

        style |= adders
        
        dw_shape = shapes.label_text(str(value), self.height, **style)
        
        return dw_shape

    def info_generate(self, value):
        style = dict(self.template['text_style'])

        dw_group = dw.Group()
        dw_group.append(dw.Circle(0,0, self.height/2*0.9, stroke='black', fill='white'))
        

        # add a caption_text section to label template
        adders = dict()
        adders['fill'] = 'blue'
        #adders['text_anchor'] = 'start'

        style |= adders
        dw_group.append(shapes.label_text(str(value), self.height, **style))
                        
        return dw_group
    
    def generate(self, text, slant=0, is_alt=False, footnote=None, caption=None):

        self.append(self.box_generate(slant, is_alt))

        x_offset = 0
        if footnote is not None:
            x_offset = self.width/2-self.height/2
            self.append(dw.Use(self.info_generate(footnote), x_offset, 0))
            x_offset = self.height/2

        self.append(self.text_generate(text, x_offset, is_alt, footnote))
                    
        if caption is not None:
            dx = self.width/2 + self.width/5
            dy = (self.height-10) / 10
            self.append(dw.Use(self.caption_generate(caption, is_alt), dx, dy))

        return self

class Function():
    def __init__(self, function, type_templates=None):
        if type_templates is not None:
            self.set_types(type_templates)
            return

        self.function = function
        return
    
    @classmethod
    def set_types(cls, types):
        cls._use_count = dict()
        cls.types = types
        return

    @property
    def use_count(self):
        if self.type not in self._use_count:
            return 0
        
        return self._use_count[self.type]

    def reset_use_count(self):
        self._use_count = dict()
        return
    
    @property
    def name(self):
        return self.function['name']    

    @property
    def type(self):
        return self.function['type']

    @property
    def is_alt(self):
        return self.function['alt']

    @property
    def footnote(self):
        return self.function['footnote']

    @property
    def style(self):
        return self.types[self.type]

    @property
    def skip(self):
        style = self.types[self.function['type']]
        return "skip" in style and style['skip']
        
    @property
    def is_spacer(self):
        return self.function['type'] == 'spacer'

    @property
    def spacing(self):
        return Label().spacing

    def label(self):
        return Label(style=self.style)

    def exists(self):
        if self.function['type'] in self.types:
            raise '{} function not found in function type styles'.format(self.type)
        return True

    def generate(self, slant):
        
        label = Label(style=self.style)
        dw_lbl = label.generate(self.name, slant=slant, is_alt=self.is_alt, footnote=self.footnote)

        if self.type not in self._use_count:
            self._use_count[self.type] = 0
            
        self._use_count[self.type] += 1
        
        return dw_lbl

class Functions(dw.Group):
    # a single row of functions
    def __init__(self, row, direction, id=None):
        super().__init__()

        self.row = row
        self.direction = direction

        self.x = 0
        self.y = 0
        return
        
    @property
    def height(self):
        return Label().height
    
    @property
    def width(self):
        return abs(self.x) #+ Label().width

    @property
    def line_style(self):
        return Label().line_style

    def generate(self, slant=0):
        dw_row = dw.Group() 
        self.x = Label().width/2 * -self.direction
        
        for func in self.row:
            function = Function(func)
            if function.skip:
                continue
            
            label = function.generate(slant)

            self.x += (label.width + label.spacing) * self.direction
            dw_row.append(dw.Use(label, self.x, self.y))

        self.append(dw.Line(0,0, self.width*self.direction,0, **self.line_style))
        self.append(dw_row)
        
        return self
