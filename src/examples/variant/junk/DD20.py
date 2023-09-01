package_data = dict(
    type = 'qfn',
    
    text = 'AVR16DD20\nAVR32DD20\nAVR64DD20',
    sub_text = 'VQFN-20',
 
    vert_offset = 0,
    horiz_offset = 0,
    
    pin_map = ['PA4', 'PA5', 'PA6', 'PA7', 'PC1',
               'PC2', 'PC3', 'VDDIO2', 'PD4', 'PD5',
               'PD6', 'PD7', 'VDD', 'GND', 'PF6',
               'PF7', 'PA0', 'PA1', 'PA2', 'PA3']    
)

# layout = orthogonal, diagonal, or horizontal
page_data = dict(
    canvas_width = 2500,
    canvas_height = 1000,
    
    header_title = 'VQFN-20',
    header_subtitle = 'AVR DD Family Processor',
    
    layout = 'orthogonal',

    quad_text1 = '''## The AVR32DB28/32/48 *microcontrollers* 
    The AVR® DB family of 
    microcontrollers are using the AVR® CPU with hardware multiplier 
    running at clock speeds up to 24 MHz. They come with 32 KB of 
    Flash, 4 KB of SRAM, and 512 bytes of EEPROM. The microcontrollers 
    are available in 28-, 32- and 48- pin packages
    ''',
    quad_text2 = '''
    ''',
    quad_text3 = '''
    ''',
    quad_text4 = '''
    ''',
    
    footer_title = '',
    footer_subtitle = ''
)
