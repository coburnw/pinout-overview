import pinoutOverview as Overview


function_type_index = 0
class TestFunction(Overview.FunctionLabel):
    type_index = function_type_index

    def __init__(self, data=None):
        if data is None:
            data = dict()

        self.data = data

        super().__init__(self.name)

        self.text_style['font_family'] = 'Roboto Mono'

        return

    @property
    def name(self):
        return self.data.get('name', 'none')

    @property
    def type(self):
        return self.type_index

    @property
    def instance(self):
        return self.data.get('instance', 0)

    @property
    def footnote(self):
        return self.data.get('footnote', '')

    @property
    def text(self):
        return '{}.{}'.format(self.name, self.instance)

    @property
    def is_alt(self):
        return self.data.get('alt', False)


function_type_index += 1
class PortFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'Port'
        self.description = 'Port Pin'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'green'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class SerialFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'Serial'
        self.description = 'Serial Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'lightgrey'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class UsartFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'Usart'
        self.description = 'Usart Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'lightblue'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class SpiFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'SPI'
        self.description = 'SPI Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'blue'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class I2cFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'I2C',
        self.description = 'I2C Function',

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'darkblue'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class PwmFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'PWM'
        self.description = 'PWM Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'grey'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class TcaFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'TCA'
        self.description = 'TimerA Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'salmon'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


function_type_index += 1
class TcbFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'TCB'
        self.description = 'TimerB Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'red'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return

function_type_index += 1
class TcdFunction(TestFunction):
    type_index = function_type_index

    def __init__(self, data):
        super().__init__(data)

        self.title = 'TCD'
        self.description = 'TimerD Function'

        self.box_style['stroke'] = '#00CC5F'
        self.box_style['fill'] = 'darkred'

        self.text_style['stroke'] = 'white'
        self.text_style['fill'] = self.text_style['stroke']

        return


# simulate some function data parsed from a manufacturer source
pa3_data = dict(
    name='Port',
    instance='3',
    footnote=None,
    alt=False
)

spi_data = dict(
    name='spi',
    instance='0',
    footnote='1',
    alt=False
)

i2c_data = dict(
    name='i2c',
    instance='3',
    footnote='1',
    alt=False
)

usart_data = dict(
    name='usart',
    instance='0',
    footnote=None,
    alt=False
)

tca_data = dict(
    name='tca',
    instance='0',
    footnote=None,
    alt=False
)

tcb_data = dict(
    name='tcb',
    instance='0',
    footnote=None,
    alt=False
)

tcd_data = dict(
    name='tcd',
    instance='0',
    footnote=None,
    alt=False
)


if __name__ == '__main__':
    import drawsvg as dw

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

    pad_function = PortFunction(pa3_data)
    pad = Overview.Pad(pad_function)

    pad.append(SpiFunction(spi_data))
    pad.append(I2cFunction(i2c_data))
    pad.append(UsartFunction(usart_data))

    pad.append(TcbFunction(tcb_data))
    pad.append(TcdFunction(tcd_data))
    pad.append(TcaFunction(tca_data))

    pad.sort()
    print(pad.height)

    split_functions = Overview.Functions()
    split_functions.append(PwmFunction(None))
    pad.split(split_functions)
    print(pad.height)

    dw_pad = pad.generate(direction=-1)
    dw_page.append(dw.Use(dw_pad, x, y))

    dw_page.save_svg('junk.svg')
