functions_template = dict(
    usart = dict(
        description = 'UART0',
        box_style = dict(
            stroke = '#CC0092',
            fill = '#FFA3E5'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    twi = dict(
        description = 'I2C',
        skip = True,
        box_style = dict(
            stroke = '#00B8CC',
            fill = '#88EBF7'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    spi = dict(
        description = 'SPI',
        box_style = dict(
            stroke = '#00CC5F',
            fill = '#8CEEBA',
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    adc = dict(
        description = 'ADC',
        box_style = dict(
            stroke = '#0060CD',
            fill = '#A2CEFF'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    ac = dict(
        description = 'COMPARATOR',
        box_style = dict(
            stroke = '#0060CD',
            fill = '#A2CEFF'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    dac = dict(
        description = 'DAC',
        box_style = dict(
            stroke = '#0060CD',
            fill = '#A2CEFF'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    zcd = dict(
        description = 'ZeroCrossingDetector',
        box_style = dict(
            stroke = '#0060CD',
            fill = '#A2CEFF'
            ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
            )
        ),
    sys = dict(
        width = 150,
        description = 'SYSTEM',
        box_style = dict(
            stroke = '#CCAA00',
            fill = '#FFE97C'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    tca = dict(
        description = 'TCA0',
        box_style = dict(
            stroke = '#00CCA0',
            fill = '#99FFE9'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    tcb = dict(
        description = 'TCBn',
        box_style = dict(
            stroke = '#69CC00',
            fill = '#DAFFB3'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    tcd = dict(
        description = 'TCD0',
        box_style = dict(
            stroke = '#69CC00',
            fill = '#DAFFB3',
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    evsys = dict(
        description = 'Events',
        box_style = dict(
            stroke = '#9600CC',
            fill = '#E399FF'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    ccl_lut = dict(
        description = 'Logic Table',
        box_style = dict(
            stroke = '#9600CC',
            fill = '#E399FF'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    pin = dict(
        width = 80,
        description = 'PIN NAME',
        box_style = dict(
            stroke = 'black',
            fill = 'grey'
        ),
        text_style= dict(
            font_family = 'Roboto Mono',
            fill = 'white'
        )
    ),
    vss = dict(
        width = 80,
        description = 'GND',
        box_style = dict(
            stroke = 'black',
            fill = 'black'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'white'
        )
    ),
    vdd = dict(
        width = 120,
        description = '2.5V-3.6V',
        box_style = dict(
            stroke = 'red',
            fill = 'red'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    spacer = dict(
        skip = True
    )
)
