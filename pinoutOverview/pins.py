import drawsvg as dw

from pinoutOverview import shapes

class Label(dw.Group):
    def __init__(self, style=None, template=None, id=None):
        if template is not None:
            self.set_template(template)
            return

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

    def text_generate(self, value, is_alt):

        style = dict(self.template['text_style'])
        if is_alt:
            style = dict(self.template['alt_text_style'])

        adders = self.style_adders['text_style'] if 'text_style' in self.style_adders else {}
        style |= adders

        dw_shape = shapes.label_text(str(value), self.height, **style)

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
    
    def generate(self, text, slant=0, is_alt=False, caption=None):

        self.append(self.box_generate(slant, is_alt))
        self.append(self.text_generate(text, is_alt))
        
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
        cls.types = types
        return

    @property
    def name(self):
        return self.function['name']    

    @property
    def type(self):
        return self.function['type']

    @property
    def style(self):
        return self.types[self.type]

    @property
    def is_alt(self):
        return self.function['alt']    

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

    def generate(self, slant):
        label = Label(style=self.style)
        return label.generate(self.name, slant=slant, is_alt=self.is_alt)
    
class Functions(dw.Group):
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
            label = function.generate(slant)

            self.x += (label.width + label.spacing) * self.direction
            dw_row.append(dw.Use(label, self.x, self.y))

        self.append(dw.Line(0,0, self.width*self.direction,0, **self.line_style))
        self.append(dw_row)
        
        return self

# a group of function label rows for a specific pin
class Pin(dw.Group):
    def __init__(self, number, rows):
        super().__init__()
        self._number = number
        self.rows = rows
        return

    @property
    def number(self):
        return self._number
    
    @property
    def label_spacing(self):
        return Label().spacing
    
    @property
    def row_spacing(self):
        return Label().height + Label().vert_spacing
        
    @property
    def height(self):
        count = len(self.rows)
        return self.spacing * count 

    @property
    def width(self):
        return 0
    
    def generate(self, direction, slant=0):
        x_start = 0
        y_start = 0
         
        row_count = len(self.rows)
        if row_count > 4:
            raise 'exceeds four function rows per pin maximum'
        
        if row_count == 1:
            pass
        elif row_count % 2 == 0:
            y_start = -(self.row_spacing * row_count/2 - self.row_spacing/2)
        else:
            y_start = -(self.row_spacing * row_count/3)

        x = x_start
        y = y_start

        i = 0
        for r in self.rows:
            row_labels = Functions(r, direction)
            row = row_labels.generate(slant=slant)
            
            offset = i * self.row_spacing
            self.append(dw.Use(row, x,y+offset))
            i += 1
            
        if row_count > 1:
            self.append(dw.Line(0,y_start, 0,y+offset, **row.line_style))

        return self

class Pins():
    def __init__(self, names, rows):
        self.names = names   # each name can be a name or a list of names that point to a row in rows
        self.rows = rows 
        self.spacing = self.calc_spacing(names)
        return

    def __len__(self):
        return len(self.names)
    
    def __getitem__(self, i):
        names = self.names[i]
        rows = []
        
        if hasattr(names, "__len__") and not isinstance(names, str):
            for name in names:
                rows.append(self.rows[name])
        else:
            name = names
            rows.append(self.rows[name])
                
        return Pin(i, rows)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.names):
            next = self.__getitem__(self.index)
            self.index += 1
            return next
        
        raise StopIteration

    def calc_spacing(self, names):
        max_lines = 1
        
        for i, m in enumerate(names):
                if hasattr( m, "__len__" ) and not isinstance( m, str ):
                    if len(m) > max_lines:
                        max_lines = len(m)

        pin_spacing = max_lines * (Label().height + Label().vert_spacing)

        return pin_spacing

