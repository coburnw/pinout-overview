import drawsvg as dw

#stupid import hack
if __name__ == '__main__':
    import shapes
else:
    from pinoutOverview import shapes

class Label(dw.Group):
    def __init__(self, style, template=None, id=None):
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
    def line_style(self):
        return self.template['label_line_style']
        
    def box_generate(self, slant, is_alt):
        # slant = 1,-1,0 for left, right, or square
        
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

class FunctionLabel():
    def __init__(self, function, id=None, types=None, ):
        # types are the template function styles available to be placed in a row
        if types is not None:
            self.set_types(types)
            return
        
        # function is the variant function to be labeled and placed in a row
        self.function = function
        self.name = function['name']
        self.style = self.types[function['type']]

        self.label = Label(style=self.style)
        return
        
    @classmethod
    def set_types(cls, types):
        cls.types = types
        return

    @property
    def height(self):
        return self.label.height
    
    @property
    def width(self):
        return self.label.width

    @property
    def spacing(self):
        return self.label.spacing

    @property
    def is_alt(self):
        return self.function['alt']    

    @property
    def skip(self):
        return "skip" in self.style and self.style['skip']

    @property
    def spacer(self):
        return self.function['type'] == 'spacer'
    
    def generate(self, slant=0):
        return (self.label.generate(self.name, slant=slant, is_alt=self.is_alt))
    
class FunctionRow():
    def __init__(self, id=None, direction=1):
        self.id = id
        self.direction = direction

        self.x = 0
        self.y = 0
        self.height = 0
        self.line_style = None

        self.dw_labels = dw.Group()
        return

    def append(self, label):
        if self.x == 0:
            self.x += (label.width/2) * self.direction
            self.height = label.height
            self.line_style = label.line_style
        else:
            self.x += (label.width + label.spacing) * self.direction
        
        self.dw_labels.append(dw.Use(label, self.x, self.y))
        return

    def generate(self):
        dw_row = dw.Group(id=self.id)
        
        dw_row.append(dw.Line(0,0, self.x, 0, **self.line_style))
        dw_row.append(self.dw_labels)
        
        return dw_row
    
if __name__ == '__main__':
    import os
    import yaml
    from yamlinclude import YamlIncludeConstructor

    import pprint
    
    path = '../pinouts/dxcore/dd14_20/qfp20.yaml'     
    YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader , base_dir=os.path.dirname(path))
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # Template dict has data used over many variants and is housed in various yaml files
    #
    # Label - contains the basic style of a label.
    # Types - is a dict of function-name to label style to be applied to the basic label. 
    #    Note that types contains a mechanism to disable display of particular functions (untested)
    #
    template = dict()
    template['label'] = data['label']
    template['types'] = data['types']

    #pprint.pprint(template)

    # Variant dict has variant specific data.
    #    It is the dict that would be of most interest to the microchip variant parser.
    #
    # Mapping - is a list of pin-names, in order of variant pin numbers
    # Pins    - contains a pin-name to list of variant specific functions with function-names
    # The mapping seems rather silly on the surface, but it is how multirow pins are to be implemented.
    #
    variant = dict()
    variant['mapping'] = data['mapping']
    variant['pins'] = data['pins']

    pprint.pprint(variant)

    x_max = 1500
    y_max = 1000
    dw_page = dw.Drawing(x_max, y_max, origin='center', displayInline=True)
    dw_page.embed_google_font("Roboto Mono")

    Label(style=None, template=template['label'])
    FunctionLabel(function=None, types=template['types'])

    # svg coordinates: +x to the right, +y to the bottom
    x_direction = 1  # +1 right, -1 left
    y_direction = 1   # +1 down
    x = -600 * x_direction
    y = -400 * y_direction
    
    dw_page.append(dw.Line(x_max,y, -x_max,y, stroke='black'))
    dw_page.append(dw.Line(x,y_max, x,-y_max, stroke='red'))
    
    rows = dw.Group()
    for name in variant['mapping']:
        pin = variant['pins'][name]
        row = FunctionRow(id='Pin_'+name, direction=x_direction)
        for function in pin:
            label = FunctionLabel(function)
            row.append(label.generate())

        rows.append(dw.Use(row.generate(), x, y))
        y += row.height * 1.5 * y_direction 

    dw_page.append(rows)
    dw_page.save_svg('junk.svg')
