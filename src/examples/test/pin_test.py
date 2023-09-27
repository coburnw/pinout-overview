if __name__ == '__main__':
    import os
    import pprint
    import importlib
    
    import drawsvg as dw

    from pinoutOverview import pads as Pins

    package = importlib.import_module('templates.qfn')
    variant = importlib.import_module('variants.dd14_20')

    # list of pin names in order of pin numbers.
    dd20 = ['PA4', 'PA5', 'PA6', 'PA7', 'PC1', 'PC2', 'PC3', 'VDDIO2', 'PD4', 'PD5',
            'PD6', 'PD7', 'VDD', 'GND', 'PF6', 'PF7', 'PA0', 'PA1', 'PA2', 'PA3']
    
    dd14 = ['GND', 'PF6', 'PF7', 'PA0', 'PA1', 'PC1', 'PC2',
            'PC3', 'VDDIO2', 'PD4', 'PD5', 'PD6', 'PD7', 'VDD']
    
    Pins.Label(style=None, template=package.label_template)
    Pins.Function(function=None, type_templates=variant.functions_template)
    pins = Pins.Pins(names=dd14, rows=variant.pins)
    
    x_max = 1500
    y_max = 1000
    dw_page = dw.Drawing(x_max, y_max, origin='center', displayInline=True)
    dw_page.embed_google_font("Roboto Mono")

    # svg coordinates: +x to the right, +y to the bottom
    x_direction = -1  # +1 right, -1 left
    y_direction = 1   # +1 down
    x = -600 * x_direction
    y = -400 * y_direction
    
    dw_page.append(dw.Line(x_max,y, -x_max,y, stroke='black'))
    dw_page.append(dw.Line(x,y_max, x,-y_max, stroke='red'))

    dw_pins = dw.Group()
    for pin in pins:
        dw_pin = pin.generate(x_direction, slant=Pins.Label().slant_none)
        dw_pins.append(dw.Use(dw_pin, x,y))
        dw_pins.append(dw.Circle(x,y, 2, stroke='black'))
        y += pins.spacing * y_direction 

    dw_page.append(dw_pins)
    dw_page.save_svg('junk.svg')
