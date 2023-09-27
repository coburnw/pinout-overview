import drawsvg as dw

from pinoutOverview import shapes

# default_label_template = dict(
#     width = 70,
#     height = 20,
#     spacing= 10,
#     offset= 30,
#     vert_spacing = 10,
#     center_offset = 20,
#
#     box_style = dict(
#         stroke_width = '2',
#         rx = '2',
#         ry = '2',
#         stroke_dasharray = '',
#         ),
#     text_style = dict(
#         font_family = 'Roboto Mono',
#         dominant_baseline = 'middle',
#         text_anchor = 'middle',
#         font_weight = 'bold',
#         ),
#     alt_box_style = dict(
#         stroke_width = '2',
#         rx = '2',
#         ry = '2',
#         stroke_dasharray = '3 4',
#         ),
#     alt_text_style = dict(
#         font_family = 'Roboto Mono',
#         dominant_baseline = 'middle',
#         text_anchor = 'middle',
#         font_style = 'italic',
#         ),
#
#     label_line_style = dict(
#         stroke = 'black',
#         stroke_width = '2',
#         fill = 'none',
#         )
# )


class Label(object):
    """
    Label() Class

    Usually subclassed.  Creates a colored box given the base template then
    further styled with a style dict passed in during instantiation.
    """
    
    # template = default_label_template  # function_label.label_template
    
    def __init__(self, id=None):
        """
        Constructor

        Args:
           id: optional id for resulting html tag
        """

        #super().__init__(id=id)  # id's matter. dupes create odd problems...  Use None or a unique id.

        # style attributes.  subclasses override any or all to fit desired style.
        self.width = 70
        self.height = 20
        self.spacing = 10
        self.offset = 30
        self.vert_spacing = 10
        self.center_offset = 20

        self.box_style = dict(
            fill = 'white',
            stroke = 'black',
            stroke_width='2',
            stroke_dasharray='',
            rx='2',
            ry='2',
        )
        self.alt_box_style = dict(
            stroke_width = '2',
            stroke_dasharray = '3 4',
            rx='2',
            ry='2',
        )
        self.text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black',
            stroke = 'black',
            dominant_baseline = 'middle',
            text_anchor = 'middle',
            font_weight = 'bold'
        )
        self.alt_text_style = dict(
            font_style = 'italic',
            font_weight = 'normal'
        )

        return

    @property
    def slant_left(self):
        """slant_left property.  returns a left slant constant"""
        
        return -1

    @property
    def slant_right(self):
        """ slant_right property.  Returns a right slant constant"""
        return +1

    @property
    def slant_none(self):
        """slant_none property. Returns a no slant constant"""
        return 0
    
    def _box_generate(self, slant, is_alt=False):
        """box_generate method. Generates the label outline.

        Args:
            slant: a slant constant to tip box outline left or right
            is_alt: a boolean to select alternate styling

        Returns:
              returns a drawsvg object of box outline for a label
        """

        style = dict(self.box_style)
        if is_alt:
            style |= dict(self.alt_box_style)

        adders = {'transform': 'skewX({})'.format(-self.height / 2 * slant)}
        style |= adders
        
        dw_shape = shapes.label_box(self.width, self.height, **style)

        return dw_shape

    def _text_generate(self, value, x_offset=0, is_alt=False):
        """text_generate method.  Generates the label text

        Args:
            value:    the text to be shown on the label
            x_offset: an offset in the x direction in pixels
            is_alt:   a boolean to select alternate styling        

        Returns:
              returns a drawsvg object of text for a label
        """

        style = dict(self.text_style)
        if is_alt:
            style |= dict(self.alt_text_style)

        adders = {}

        # if x_offset != 0:
        #     adders['text_anchor'] = 'end'
            
        style |= adders

        dw_shape = shapes.label_text(str(value), self.height, x_offset, **style)

        return dw_shape

    def _caption_generate(self, value, is_alt=False):
        """caption_generate method.  Generates the caption shown adjacent to a label.

        Args:
            value: the text to be shown adjacent to the label
            is_alt: a boolean to select alternate styling

        Returns:
              returns a drawsvg object of the caption for a label
        """

        style = dict(self.text_style)

        # add a caption_text section to label template
        adders = dict()
        adders['fill'] = 'black'
        adders['text_anchor'] = 'start'

        style |= adders
        
        dw_shape = shapes.label_text(str(value), self.height, **style)
        
        return dw_shape

    def _info_generate(self, value):
        """info_generate method.  Generates a footnote bubble at end of label.

        Args:
            value: a single character (such as '1') to be shown in the bubble

        Returns:
              returns a drawsvg object of the bubble for a label
        """

        style = dict(self.text_style)

        dw_group = dw.Group()
        dw_group.append(dw.Circle(0, 0, self.height/2*0.9, stroke='black', fill='white'))

        # add a caption_text section to label template
        adders = dict()
        adders['fill'] = 'blue'
        # adders['text_anchor'] = 'start'

        style |= adders
        dw_group.append(shapes.label_text(str(value), self.height, **style))
                        
        return dw_group
    
    def generate(self, text, slant=0, is_alt=False, footnote=None, caption=None):
        """generate method. Generates a complete label.

        Args:
            text (str):      The text to be shown on the label
            slant (int):     Optional. A slant constant to tip box outline left or right
            is_alt (bool):   Optional. A boolean to select alternate styling
            footnote (str):  Optional. Single character (such as '1') to be shown in a footnote bubble
            caption (str):   Optional. Text to be shown adjacent to the label

        Returns:
              returns a drawsvg object of a completed label
        """
        dw_group = dw.Group()
        dw_group.append(self._box_generate(slant, is_alt))

        x_offset = 0
        if footnote is not None:
            x_offset = self.width/2-self.height/2
            dw_group.append(dw.Use(self._info_generate(footnote), x_offset, 0))
            x_offset = self.height/2

        dw_group.append(self._text_generate(text, x_offset, is_alt))
                    
        if caption is not None:
            dx = self.width/2 + self.width/5
            dy = (self.height-10) / 10
            dw_group.append(dw.Use(self._caption_generate(caption, is_alt), dx, dy))

        return dw_group


class FunctionLabel(Label):
    """
    FunctionLabel() Base Class. Subclassed and customized by each possible function of the target device.

    When subclassed, the user overrides/amends label style in init().
    The subclass also supplies properties to override the base class properties to parse the function data.
    """

    def __init__(self, name='Default'):
        super().__init__()

        self._name = name

        self.description = 'Default Function'
        self.skip = False
        self.blank = False

        return

    def __lt__(self, other):
        return self.type_index < other.type_index

    def __eq__(self, other):
        return self.type_index == other.type_index

    @property
    def name(self):
        return self._name

    @property
    def type_index(self):
        """type_index (int):  an index used for ordering and splitting of functions in a list"""

        raise NotImplementedError

    @property
    def text(self):
        """text (str):  parses function_data and assembles a string to be shown in function label"""
        return self.name

    @property
    def is_alt(self):
        """is_alt (bool):  parses function_data and returns a boolean indicating an alternate function"""
        
        raise NotImplementedError

    @property
    def footnote(self):
        """footnote (str).  parses function_data and returns a footnote character if any"""
        
        raise NotImplementedError

    def generate(self, slant=0, legend=False):
        """
        Generate a DrawingSVG object of a function label

        Args:
            slant (int): a label constant describing direction of slant of the label.
            legend (bool): is label being used in a legend

        Returns:
            dw_lbl (drawsvg.Group): A DrawingSVG Group object of a FunctionLabel
        """

        text = self.text
        footnote = self.footnote

        if legend:
            text = self.title
            footnote = None

        dw_lbl = super().generate(text, is_alt=self.is_alt, slant=slant, footnote=footnote)
        
        return dw_lbl


class Functions(dw.Group):
    """
    Functions Base Class.  Emulates a simple list containing a single row of function labels.
    """
    
    def __init__(self, id=None):
        """
        Args:
        id: optional id for resulting html tag.  A unique id is created if None.
        """
        
        super().__init__(id=id)

        # style for line used to connect labels
        self.line_style = dict(
            stroke = 'black',
            stroke_width = '2',
            fill = 'none'
        )

        self._row = []
        self._width = 0
        self._height = 0

        # iter index
        self._index = 0

        self.x = 0
        self.y = 0
        return

    def __len__(self):
        return len(self._row)

    def __contains__(self, item):
        for function in self._row:
            if function == item:
                return True

        return False

    def __getitem__(self, index):
        """

        Args:
            index (int): index in row of functions

        Returns:
            Object (Function): A Function object
        """
        return self._row[index]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        """

        Returns:
            Object (Function): A Function object
        """
        try:
            item = self.__getitem__(self._index)
            self._index += 1
        except IndexError:
            raise StopIteration

        return item

    @property
    def height(self):
        """

        Returns:
            Maximum height in pixels of function row
        """
        return self._height
    
    @property
    def width(self):
        """

        Returns:
            Maximum width in pixels of row of functions
        """
        return self._width

    def append(self, function):
        """
        append() method.  Appends a function.

        Args:
           function (FunctionLabel):  Subclassed FunctionLabel object.
                                      When used for splitting, subclassed FunctionLabel class.

        Returns:
           nothing

        """

        # check if an instance or a class
        if isinstance(function, FunctionLabel):
            self._width += (function.width + function.spacing)
            if function.height > self._height:
                self._height = function.height

        self._row.append(function)
        return

    def sort(self):
        """
        sort() method.  Sorts list of functions in place by function type_index.

        Args:
           none.

        Returns:
           None
        """
        
        self._row = sorted(self._row, key=lambda function: function.type_index)
        return None

    def split(self, split_function: FunctionLabel):
        """
        Split a row of functions into two rows at split function

        Args:
            split_function (FunctionLabel): the split point.

        Returns:
            object (list): list of two entries of Functions objects.
                all functions with type less than split function in list entry[0] remaining in list entry[1]
                Note: either Functions object could be empty
        """

        rows = [Functions(), Functions()]
        for function in self._row:
            index = 1
            if function < split_function:
                index = 0

            rows[index].append(function)

        return rows

    def generate(self, direction, slant=0):
        """
        generate() method.  Builds row of function labels extending from the origin.

        Args:
           direction (int): label constant left or right progression of labels
           slant (int): label constant describing direction of box slant

        Returns:
           Object (drawsvg.Group): of the finished row of function labels
        """

        x = self.x
        y = self.y

        dw_labels = dw.Group()
        for function in self._row:
            if x == 0:
                x = function.width / 2 * -direction

            label = function.generate(slant)

            x += (function.width + function.spacing) * direction
            if not function.blank:
                dw_labels.append(dw.Use(label, x, y))

        super().append(dw.Line(self.x, self.y, self.width*direction, y, **self.line_style))
        super().append(dw_labels)

        return self
