import tabula

# convert PDF into CSV
tabula.convert_into("AVR16_32DD14_20_p17.pdf", "table.csv", output_format="csv", pages='all', lattice='true')
