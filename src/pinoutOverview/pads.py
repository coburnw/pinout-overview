import drawsvg as dw

from pinoutOverview import FunctionLabel, Functions


# a group of function label rows for a specific pin
class Pad(dw.Group):
    """A collection of function label rows for a specific pad"""
    _functions: Functions
    _label: FunctionLabel

    def __init__(self, function_label: FunctionLabel):
        """
        Attributes:
            function_label (FunctionLabel): a function label to be used as a root for this pad.
        """

        super().__init__()

        self._label = function_label

        self._index = 0
        self._functions = Functions()

        self._rows = []
        #self._rows.append(self._functions)
        return

    def __getitem__(self, index):
        """

        Args:
            index (int): index into a list of functions

        Returns:
            Object (Function): A Function object
        """
        return self._functions[index]

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

    # @property
    # def functions(self):
    #     return self._functions

    @property
    def name(self):
        """string: the name of the pad."""
        return self._label.name
    
    @property
    def height(self):
        """int: height in pixels of combined rows of functions."""
        return self.row_spacing * len(self._rows)  # self.row_count

    @property
    def width(self):
        """int: width in pixels of longest row."""
        return 0

    @property
    def row_spacing(self):
        return FunctionLabel().height + FunctionLabel().vert_spacing

    def append(self, function: FunctionLabel):
        """Function: append a function to the list of available pad functions"""

        if function.skip:
            return

        # reset possible split
        self._rows = []

        self._functions.append(function)
        self._rows.append(self._functions)
        return

    def sort(self):
        """Function: sort the list of functions by their type_index"""
        self._functions.sort()
        return

    def split(self, split_functions: [FunctionLabel]):
        """
        Function: split functions into rows of functions

        Attributes:
            split_functions[]: a list of function class's that start a new row

        Todo: make split_functions a list of functions allowing n-row splits
        """
        self._rows = []

        split = self._functions.split(split_functions[0])
        for row in split:
            if len(row) > 0:
                self._rows.append(row)

        return

    def generate(self, direction, slant=0):
        """generate a drawsvg object of the pad function rows

        Args:
           direction (int): determines direction of label placement, left or right.  Use label constants.
           slant (int): determines slant of label box.  Use label constants.

        Returns:
           drawsvg.Group: A drawsvg group of a constructed pad with an origin of 0,0
        """
        
        x_start = self._label.width/2 * direction
        y_start = 0

        dw_label = self._label.generate(slant=slant)
        super().append(dw.Use(dw_label, x_start, y_start))

        if len(self._rows) == 0:
            return self

        # add connector to rows
        x_start = self._label.width * direction
        x_end = x_start + self._label.spacing * direction
        super().append(dw.Line(x_start, y_start, x_end, y_start, **Functions().line_style))
        x_start = x_end

        row_count = len(self._rows)
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
        offset = 0
        for function_row in self._rows:
            row = function_row.generate(direction=direction, slant=slant)
            
            offset = i * self.row_spacing
            super().append(dw.Use(row, x, y+offset))
            i += 1

        # add connector between rows
        if len(self._rows) > 1:
            super().append(dw.Line(x, y_start, x, y+offset, **row.line_style))

        return self


# look into subclassing a UserList here
# class Pads(object):
#     """A group of pads
#     """
#
#     def __init__(self):
#         self.pads = dict()
#         return
#
#     def __len__(self):
#         return len(self.pads)
#
#     def __getitem__(self, pad_name):
#         return self.pads[pad_name]
#
#     # def __setitem__(self, pad_name, function):
#     #     self.pads[pad_name] = function
#     #     return
#
#     def __iter__(self):
#         self.index = 0
#         return self
#
#     def __next__(self):
#         if self.index < len(self.pads):
#             pad = self.__getitem__(self.index)
#             self.index += 1
#             return pad
#
#         raise StopIteration
#
#     def append(self, pad_name, pad):
#         if pad_name in self.pads:
#             raise 'pad already exists in pads collection'
#
#         self.pads[pad_name] = pad
#         return
#
#     @property
#     def spacing(self):
#         """Finds maximum pin spacing in pixels
#
#         Returns:
#            pin_spacing (int): the maximum spacing required between pins
#         """
#
#         max_height = 0
#         for name, pad in self.pads.items():
#             if pad.height > max_height:
#                 max_height = pad.height
#
#         return max_height
