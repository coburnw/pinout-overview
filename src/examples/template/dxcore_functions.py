
# pip install v-palette
# for palette colors selection, view  https://github.com/villoro/vpalette

from v_palette import get_colors

palette = 'flat'
function_types = dict(
    serial = dict(
        description = 'SERIAL INTERFACE',
        box_style = dict(
            stroke = get_colors(('blue', 700), palette=palette),
            fill = get_colors(('blue', 500), palette=palette)
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white', 500), palette=palette)
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
    analog = dict(
        description = 'ANALOG',
        box_style = dict(
            stroke = get_colors(('brown', 700), palette=palette),
            fill = get_colors(('brown', 500), palette=palette)
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white', 200), palette=palette)
        )
    ),
    ain = dict(
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
    other = dict(
        width = 150,
        description = 'SYSTEM',
        box_style = dict(
            stroke = get_colors(('sunflower', 500), palette=palette),
            fill = get_colors(('sunflower', 500), palette=palette)
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('black', 500), palette=palette)
        )
    ),
    clock = dict(
        width = 150,
        description = 'CLOCK',
        box_style = dict(
            stroke = '#CCAA00',
            fill = '#FFE97C'
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = 'black'
        )
    ),
    pwm = dict(
        description = 'PWM',
        box_style = dict(
            stroke = get_colors(('purple', 700), palette=palette),
            fill = get_colors(('purple', 500), palette=palette),
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white', 200), palette=palette)
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
    logic = dict(
        description = 'Logic System',
        box_style = dict(
            stroke = get_colors(('belize-hole',700), palette=palette),
            fill = get_colors(('belize-hole',600), palette=palette)
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white',200), palette=palette)
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
    ccl = dict(
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

    vddio = dict(
        width = 80,
        description = 'MULTI-VOLTAGE PIN',
        box_style = dict(
            stroke = get_colors(('green', 900), palette=palette),
            fill = get_colors(('green', 500), palette=palette)
        ),
        text_style= dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('black', 800), palette=palette)
        )
    ),
    pin = dict(
        width = 80,
        description = 'PORT PIN',
        box_style = dict(
            stroke = get_colors(('green', 900), palette=palette),
            fill = get_colors(('green', 700), palette=palette)
        ),
        text_style= dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white', 200), palette=palette)
        )
    ),
    vss = dict(
        width = 80,
        description = 'GROUND',
        box_style = dict(
            stroke = get_colors(('black', 200), palette=palette),
            fill = get_colors(('black', 200), palette=palette)
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white', 200), palette=palette)
        )
    ),
    vdd = dict(
        width = 120,
        description = 'POWER',
        box_style = dict(
            stroke = get_colors(('red', 200), palette=palette),
            fill = get_colors(('red', 200), palette=palette)
        ),
        text_style = dict(
            font_family = 'Roboto Mono',
            fill = get_colors(('white', 200), palette=palette)
        )
    ),
    spacer = dict(
        skip = True
    )
)
