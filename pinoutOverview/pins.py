import drawsvg as dw

from pinoutOverview import functions

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
        return functions.Label().spacing
    
    @property
    def row_spacing(self):
        return functions.Label().height + functions.Label().vert_spacing
        
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
            row_labels = functions.Functions(r, direction)
            row = row_labels.generate(slant=slant)
            
            offset = i * self.row_spacing
            self.append(dw.Use(row, x,y+offset))
            i += 1
            
        if row_count > 1:
            self.append(dw.Line(0,y_start, 0,y+offset, **row.line_style))

        return self

class Pins():
    def __init__(self, variant_pins, rows):
        self.variant = variant_pins   # each name can be a name or a list of names that point to a row in rows
        self.rows = rows.functions.functions
        self.spacing = self.calc_spacing(self.variant['pin_map'])
        return

    def __len__(self):
        return len(self.variant.pin_map)
    
    def __getitem__(self, i):
        names = self.variant['pin_map'][i]
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
        if self.index < len(self.variant['pin_map']):
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

        pin_spacing = max_lines * (functions.Label().height + functions.Label().vert_spacing)

        return pin_spacing

