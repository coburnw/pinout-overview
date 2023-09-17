import drawsvg as dw

from pinoutOverview import shapes
#from template import default_function_template #default_label
#from template import default_label_template

default_label_template = dict(
    width = 70,
    height = 20,
    spacing= 10,
    offset= 30,
    vert_spacing = 10,
    center_offset = 20,
    
    box_style = dict(
        stroke_width = '2',
        rx = '2',
        ry = '2',
        stroke_dasharray = '',
        ),
    text_style = dict(
        font_family = 'Roboto Mono',
        dominant_baseline = 'middle',
        text_anchor = 'middle',
        font_weight = 'bold',
        ),
    alt_box_style = dict(
        stroke_width = '2',
        rx = '2',
        ry = '2',
        stroke_dasharray = '3 4',
        ),
    alt_text_style = dict(
        font_family = 'Roboto Mono',
        dominant_baseline = 'middle',
        text_anchor = 'middle',
        font_style = 'italic',
        ),

    label_line_style = dict(
        stroke = 'black',
        stroke_width = '2',
        fill = 'none',
        )
)

class Label(dw.Group):
    '''
    Label() Class

    Usually subclassed.  Creates a colored box given the base template then 
    further styled with a style dict passed in durring instatiation.
    '''
    
    template = default_label_template #function_label.label_template
    
    def __init__(self, id=None, style=None):
        '''
        Constructor

        Args:
           id: optional id for resulting html tag
           style: dict of style to overlay on default template
        '''
        super().__init__(id=id)  #id's matter. dupes create odd problems...  Use None or a unique id.
        self.style_adders = style
        return

    @classmethod
    def set_template(cls, template):
        '''
        set_template(template) class method to set default shape and style of label
        
        Args:
            template: dict of shape and style defaults
        '''

        cls.template = template
        return

    @property
    def width(self):
        '''width property. returns width in pixels of label'''
        
        return self.template['width']

    @property
    def height(self):
        '''height property. returns height in pixels of label'''
        
        return self.template['height']
        
    @property
    def offset(self):
        '''offset property.  returns offset from xxx in pixels'''

        return self.template['offset']
    
    @property
    def spacing(self):
        '''spacing property.  returns space in pixels between adjacent labels'''
        
        return self.template['spacing']

    @property
    def vert_spacing(self):
        '''vert_spacing property.  returns space in pixels between adjacent rows of labels'''
        
        return self.template['vert_spacing']
        
    @property
    def line_style(self):
        '''line_style property.  returns style of label outline'''
        
        return self.template['label_line_style']
         
    @property
    def slant_left(self):
        '''slant_left property.  returns a left slant constant'''
        
        return -1

    @property
    def slant_right(self):
        ''' slant_right property.  Returns a right slant constant'''
        return +1

    @property
    def slant_none(self):
        '''slant_none property. Returns a no slant constant'''
        return 0
    
    def _box_generate(self, slant, is_alt):
        '''box_generate method. Generates the label outline.

        Args:
            slant: a slant constant to tip box outline left or right
            is_alt: a boolean to select alternate styling

        Returns:
              returns a drawsvg object of box outline for a label
        '''

        style = dict(self.template['box_style'])
        if is_alt:
            style = dict(self.template['alt_box_style'])

        adders = self.style_adders["box_style"] if "box_style" in self.style_adders else {}
        adders["transform"] = 'skewX({})'.format(-self.height/2*slant)
        style |= adders
        
        dw_shape = shapes.label_box(self.width, self.height, **style)

        return dw_shape

    def _text_generate(self, value, x_offset=0, is_alt=False):
        '''text_generate method.  Generates the label text

        Args:
            value:    the text to be shown on the label
            x_offset: an offset in the x direction in pixels
            is_alt:   a boolean to select alternate styling        

        Returns:
              returns a drawsvg object of text for a label
        '''

        style = dict(self.template['text_style'])
        if is_alt:
            style = dict(self.template['alt_text_style'])

        adders = dict(self.style_adders['text_style']) if 'text_style' in self.style_adders else {}

        # if x_offset != 0:
        #     adders['text_anchor'] = 'end'
            
        style |= adders

        dw_shape = shapes.label_text(str(value), self.height, x_offset, **style)

        return dw_shape

    def _caption_generate(self, value, is_alt):
        '''caption_generate method.  Generates the caption shown adjacent to a label.

        Args:
            value: the text to be shown adjacent to the label
            is_alt: a boolean to select alternate styling

        Returns:
              returns a drawsvg object of the caption for a label
        '''

        style = dict(self.text_style)

        # add a caption_text section to label template
        adders = dict()
        adders['fill'] = 'black'
        adders['text_anchor'] = 'start'

        style |= adders
        
        dw_shape = shapes.label_text(str(value), self.height, **style)
        
        return dw_shape

    def _info_generate(self, value):
        '''info_generate method.  Generates a footnote bubble at end of label.

        Args:
            value: a single charactor (such as '1') to be shown in the bubble

        Returns:
              returns a drawsvg object of the bubble for a label
        '''

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
        '''generate method. Generates a complete label.

        Args:
            text:     The text to be shown on the label
            slant:    Optional. A slant constant to tip box outline left or right
            is_alt:   Optional. A boolean to select alternate styling
            footnote: Optional single charactor (such as '1') to be shown in a footnote bubble
            caption:  Optional text to be shown adjacent to the label

        Returns:
              returns a drawsvg object of a completed label
        '''

        self.append(self._box_generate(slant, is_alt))

        x_offset = 0
        if footnote is not None:
            x_offset = self.width/2-self.height/2
            self.append(dw.Use(self._info_generate(footnote), x_offset, 0))
            x_offset = self.height/2

        self.append(self._text_generate(text, x_offset, is_alt))
                    
        if caption is not None:
            dx = self.width/2 + self.width/5
            dy = (self.height-10) / 10
            self.append(dw.Use(self._caption_generate(caption, is_alt), dx, dy))

        return self


default_function_template = dict(
    description = 'Default',
    skip = False,
    blank = False,
    box_style = dict(
        stroke = '#00B8CC',
        fill = '#88EBF7'
    ),
    text_style = dict(
        font_family = 'Roboto Mono',
        fill = 'black'
    )
)

class Function():
    '''
    Function() Base Class. Subclassed by each possible function of the target device.  

    When subclassed, the user supplies a style template as a class variable that defines 
    the visual style of the function.  The subclass also supplies properties to override 
    the base class properties to parse the function data.
    '''
    
    template = default_function_template
    
    def __init__(self, function_data):
        '''
        Args:
           function_data: An opaque data structure readable by the subclasses overloaded properties
        '''
        
        self.function_data = function_data
        return

    @property
    def text(self):
        '''text property.  parses function_data and assembles a string to be shown in function label'''
        raise NotImplementedError
        
    @property
    def name(self):
        '''name property.  parses function_data and returns the function name'''
        
        return self.function_data['name']    

    # @property
    # def type(self):
    #     return self.function_data['type']

    @property
    def is_alt(self):
        '''is_alt property.  parses function_data and returns a boolean indicating an alternate function'''
        
        return self.function_data['alt']

    @property
    def footnote(self):
        '''footnote property.  parses function_data and returns a footprint charactor if any'''
        
        return self.function_data.get('footnote', None)

    @property
    def style(self):
        return self.template

    @property
    def skip(self):
        return "skip" in self.template and self.template['skip']
        
    @property
    def blank(self):
        return "blank" in self.template and self.template['blank']

    @property
    def spacing(self):
        return Label().spacing

    # def label(self):
    #     return Label(style=self.template)

    def generate(self, slant=False):
        
        label = Label(style=self.template)
        dw_lbl = label.generate(self.text, slant=slant, is_alt=self.is_alt, footnote=self.footnote)
        
        return dw_lbl

#class Pad(dw.Group):
class Functions(dw.Group):
    '''
    Functions Base Class.  Emulates a simple list containing a single row of function labels.
    '''
    
    def __init__(self, id=None):
        '''
        Args:
        id: optional id for resulting html tag
        '''
        
        super().__init__(id=id)
        
        #self.id = id
        #self.direction = direction
        self.row = []
        #self.rows = [ [],[] ]

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

    def append(self, function):
        '''
        append() method.  Appends a function.

        Args:
           function:  A Function or subclassed Function object

        Returns:
           nothing

        Todo:
           width calculation should probably happen here so user can choose to start a new row.
        '''
        
        self.row.append(function)
        return

    def sort(self):
        '''
        sort() method.  Sorts list of functions in place by function index.

        Args:
           none.

        Returns:
           None
        '''
        
        self.row = sorted(self.row, key=lambda function: function.index)
        return self

    def split(self, function):
        # row = self.rows[0]
        # found = False
        # i = 0
        # for f in self.row:
        #     if f.index == function.index and not found:
        #         i += 1
        #         found = True
            
        #     self.rows[i].append(f)
        
        return

    def generate(self, direction, slant=0):
        '''
        generate() method.  Builds row of function labels extending from the origin.

        Args:
           direction:
           slant:

        Returns:
           drawsvg object of the finished row of function labels
        '''

        self.x = Label().width/2 * -direction

        dw_labels = dw.Group() 
        for function in self.row:
            if function.skip:
                continue

            #print(function.name)
            label = function.generate(slant)

            self.x += (label.width + label.spacing) * direction
            if not function.blank:
                dw_labels.append(dw.Use(label, self.x, self.y))

        super().append(dw.Line(0,0, self.width*direction,0, **self.line_style))
        super().append(dw_labels)
        
        return self
