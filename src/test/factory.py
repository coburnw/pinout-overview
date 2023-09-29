# https://stackoverflow.com/a/5961102
# Note python3 has a different declaration

class ShapeFactory(type):
    def __call__(cls, *args):
        print('factory')
        desc = args[0]
        if cls is Shape:
            if desc == 'big':   return Rectangle(desc)
            if desc == 'small': return Triangle(desc)
        return type.__call__(cls, desc)

class Shape(metaclass=ShapeFactory):
    def __init__(self, desc):
        print("init called")
        self.desc = desc

class Triangle(Shape):
    @property
    def number_of_edges(self): return 3

class Rectangle(Shape):
    @property
    def number_of_edges(self): return 4

if __name__ == '__main__':
    shape = Shape('big')
    print(shape.number_of_edges)