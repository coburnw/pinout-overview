import drawsvg as dw

from pinoutOverview import functions

# a group of function label rows for a specific pin
class Pin(dw.Group):
    '''A group of function label rows for a specific pin

    Attributes:
       number (int): pin number, most likely 1 indexed.
       rows (list):  each item is a row of function. 

    Todo:
       * Perhaps emulate a list of rows.  Use append to fill, use split() to split on index
    '''
    
    def __init__(self, number, rows):
        super().__init__()
        self.pin_number = number
        self.pin_name = name
        self.rows = rows
        return

    @property
    def number(self):
        '''int: the number of the pin.'''
        return self.pin_number
    
    @property
    def name(self):
        '''int: the name of the pin.'''
        return self.pin_name
    
    # @property
    # def label_spacing(self):
    #     '''int: spacing in pixels between labels.'''
    #     return functions.Label().spacing
    
    # @property
    # def row_spacing(self):
    #     '''int: spacing in pixels between rows.'''
    #     return functions.Label().height + functions.Label().vert_spacing
        
    @property
    def height(self):
        '''int: height in pixels of combined rows.'''
        count = len(self.rows)
        spacing = functions.Label().height + functions.Label().vert_spacing
        return spacing * count 

    @property
    def width(self):
        '''int: width in pixels of longest row.'''
        return 0

    def split_on(self, function):
        self.functions.split(function)
        return
    
    def generate(self, direction, slant=0):
        '''generate a drawingsvg object of the pin rows

        Args:
           direction (int): determines direction of label placement, left or right.  Use constants.
           slant (optional int): determines slant of label box.  Use label constants.

        Returns:
           dw.Group (object): A drawingsvg group object of a constructed pin
        '''
        
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
            row_labels = functions.Functions(r, direction)
            row = row_labels.generate(slant=slant)
            
            offset = i * self.row_spacing
            self.append(dw.Use(row, x,y+offset))
            i += 1
            
        if row_count > 1:
            self.append(dw.Line(0,y_start, 0,y+offset, **row.line_style))

        return self

class Pins():
    '''A group of pins

    Args:
       pin_list (list): a list of pin names.
       rows (list): a list of function rows

    Todo:
       * add an item setter to allow filling of row list
    '''
    
    def __init__(self, pin_list, rows):
        self.pin_list = pin_list   # each pin can be a name or a list of names that point to a row in rows
        self.rows = rows
        self.spacing = self.calc_spacing(self.pin_list)
        return

    def __len__(self):
        return len(self.pin_list)
    
    def __getitem__(self, i):
        names = self.pin_list[i]
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
        if self.index < len(self.pin_list):
            next = self.__getitem__(self.index)
            self.index += 1
            return next
        
        raise StopIteration

    def calc_spacing(self, names):
        '''Finds maximum pin spacing in pixels
        
        Args: names (list): a list of names to scan to find max rows and calculate spacing

        Returns:
           pin_spacing (int): the maximum spacing required between pins

        Todo:
           * i think we should be using our local list rather than from an argument.
        '''
        
        max_lines = 1
        
        for i, m in enumerate(names):
                if hasattr( m, "__len__" ) and not isinstance( m, str ):
                    if len(m) > max_lines:
                        max_lines = len(m)

        pin_spacing = max_lines * (functions.Label().height + functions.Label().vert_spacing)

        return pin_spacing

