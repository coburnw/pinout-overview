from family.functions import function_types, function_template

pin_functions = dict(
    PA4 = [
        dict(
            alt = False,
            name = 'PA4',
            type = 'pin',
        ),
        dict(
            alt = False,
            name = 'AIN24',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,TxD',
            type = 'usart',
        ),
        dict(
            alt = False,
            name = 'MOSI',
            type = 'spi'
        ),
        dict(
            alt = False,
            name = 'WO4',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = 'WOA',
            type = 'tcd'
        )
    ],
    PD5 = [
        dict(
            alt = False,
            name = 'PD5',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'AIN5',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,RxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'MISO',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'WO5',
            type = 'tca'
        ),
        dict(
            alt = True,
            name = 'WOD',
            type = 'tcd'
        )
    ],
    PD6 = [
        dict(
            alt = False,
            name = 'PD6',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'AIN6',
            type = 'adc'
        ),
        dict(
            alt = False,
            name = 'AINP3',
            type = 'ac'
        ),
        dict(
            alt = False,
            name = 'VOUT',
            type = 'dac'
        ),
        dict(
            alt = True,
            name = '0,XCK',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '1,TxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'SCK',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = '2,OUT',
            type = 'ccl_lut'
        )
    ],
    PD7 = [
        dict(
            alt = False,
            name = 'PD7',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'VREFA',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'AIN7',
            type = 'adc'
        ),
        dict(
            alt = False,
            name = 'AINN2',
            type = 'ac'
        ),
        dict(
            alt = True,
            name = '0,XDIR',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '1,RxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'SS',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'EVOUTD',
            type = 'evsys'
        ),
    ],
    VDD = [
        dict(
            alt = False,
            name = 'VDD',
            type = 'pin'
        ),
    ],
    GND = [
        dict(
            alt = False,
            name = 'GND',
            type = 'pin'
        ),
    ],
    PF6 = [
        dict(
            alt = False,
            name = 'PF6(5)',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'RESET',
            type = 'sys'
        )
    ],
    PF7 = [
        dict(
            alt = False,
            name = 'PF7',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'UPDI',
            type = 'sys'
        ),
        dict(
            alt = True,
            name = 'SS',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'EVOUTF',
            type = 'evsys'
        )
    ],
    PA0 = [
        dict(
            alt = False,
            name = 'PA0',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'XTAL32K1',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'XTALHF1',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'EXTCLK',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = '0,TxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'MOSI',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'SDA(H)',
            type = 'twi'
        ),
        dict(
            alt = False,
            name = 'WO0',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = '0,IN0',
            type = 'ccl_lut'
        )
    ],
    PA1 = [
        dict(
            alt = False,
            name = 'PA1',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'XTAL32K2',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'XTALHF2',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = '0,RxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'MISO',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'SCL(H)',
            type = 'twi'
        ),
        dict(
            alt = False,
            name = 'WO1',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = '0,IN1',
            type = 'ccl_lut'
        )
    ],
    PA2 = [
        dict(
            alt = False,
            name = 'PA2',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'TWI',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'Fm+',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'AIN22',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,XCK',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '0,TxD',
            type = 'usart'
        ),
        dict(
            alt = False,
            name = 'SDA(H)',
            type = 'twi'
        ),
        dict(
            alt = False,
            name = 'WO2',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = '0,WO',
            type = 'tcb'
        ),
        dict(
            alt = False,
            name = 'EVOUTA',
            type = 'evsys'
        ),
        dict(
            alt = False,
            name = '0,IN2',
            type = 'ccl_lut'
        )
    ],
    PA5 = [
        dict(
            alt = False,
            name = 'PA5',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'AIN25',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,RxD',
            type = 'usart'
        ),
        dict(
            alt = False,
            name = 'MISO',
            type = 'spi'
        ),
        dict(
            alt = False,
            name = 'WO5',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = 'WOB',
            type = 'tcd'
        )
    ],
    PA3 = [
        dict(
            alt = False,
            name = 'PA3',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'TWI',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'Fm+',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'AIN23',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,XDIR',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '0,RxD',
            type = 'usart'
        ),
        dict(
            alt = False,
            name = 'SCL(H)',
            type = 'twi'
        ),
        dict(
            alt = False,
            name = 'WO3',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = '1,WO',
            type = 'tcb'
        ),
        dict(
            alt = False,
            name = '0,OUT',
            type = 'ccl_lut'
        )
    ],
    PA6 = [
        dict(
            alt = False,
            name = 'PA6',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'AIN26',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,XCK',
            type = 'usart'
        ),
        dict(
            alt = False,
            name = 'SCK',
            type = 'spi'
        ),
        dict(
            alt = False,
            name = 'WOC',
            type = 'tcd'
        ),
        dict(
            alt = True,
            name = '0,OUT',
            type = 'ccl_lut'
        )
    ],
    PA7 = [
        dict(
            alt = False,
            name = 'PA7',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'CLKOUT',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'AIN27',
            type = 'adc'
        ),
        dict(
            alt = False,
            name = 'OUT',
            type = 'ac'
        ),
        dict(
            alt = False,
            name = 'ZCOUT',
            type = 'zcd'
        ),
        dict(
            alt = True,
            name = '0,XDIR',
            type = 'usart'
        ),
        dict(
            alt = False,
            name = 'SS',
            type = 'spi'
        ),
        dict(
            alt = False,
            name = 'WOD',
            type = 'tcd'
        ),
        dict(
            alt = True,
            name = 'EVOUTA',
            type = 'evsys'
        )
    ],
    PC1 = [
        dict(
            alt = False,
            name = 'PC1',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'AIN29',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '1,RxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '0,TxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'SS',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'MISO',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'MOSI',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'WO1',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = '1,IN1',
            type = 'ccl_lut'
        )
    ],
    PC2 = [
        dict(
            alt = False,
            name = 'PC2',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'TWI',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'Fm+',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'AIN30',
            type = 'adc'
        ),
        dict(
            alt = False,
            name = 'AINN3',
            type = 'ac'
        ),
        dict(
            alt = False,
            name = 'ZCIN',
            type = 'zcd'
        ),
        dict(
            alt = True,
            name = '1,XCK',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '0,RxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'SCK',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'MISO',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'SDA(C)',
            type = 'twi'
        ),
        dict(
            alt = True,
            name = 'SDA(H)',
            type = 'twi'
        ),
        dict(
            alt = True,
            name = 'WO2',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = 'EVOUTC',
            type = 'evsys'
        ),
        dict(
            alt = False,
            name = '1,IN2',
            type = 'ccl_lut'
        )
    ],
    PC3 = [
        dict(
            alt = False,
            name = 'PC3',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'TWI',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'Fm+',
            type = 'sys'
        ),
        dict(
            alt = False,
            name = 'AIN31',
            type = 'adc'
        ),
        dict(
            alt = False,
            name = 'AINP4',
            type = 'ac'
        ),
        dict(
            alt = True,
            name = '1,XDIR',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = '0,XCK',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'SS',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'SCK',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'SCL(C)',
            type = 'twi'
        ),
        dict(
            alt = True,
            name = 'SCL(H)',
            type = 'twi'
        ),
        dict(
            alt = True,
            name = 'WO3',
            type = 'tca'
        ),
        dict(
            alt = False,
            name = '1,OUT',
            type = 'ccl_lut'
        )
    ],
    VDDIO2 = [
        dict(
            alt = False,
            name = 'VDDIO2',
            type = 'pin'
        )
    ],
    PD4 = [
        dict(
            alt = False,
            name = 'PD4',
            type = 'pin'
        ),
        dict(
            alt = False,
            name = 'AIN4',
            type = 'adc'
        ),
        dict(
            alt = True,
            name = '0,TxD',
            type = 'usart'
        ),
        dict(
            alt = True,
            name = 'MOSI',
            type = 'spi'
        ),
        dict(
            alt = True,
            name = 'WO4',
            type = 'tca'
        ),
        dict(
            alt = True,
            name = 'WOC',
            type = 'tcd'
        )
    ]
)
