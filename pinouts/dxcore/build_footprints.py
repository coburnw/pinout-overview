import csv
import yaml
import io
import tabula

footprints = ['VQFN20','SOIC20','SOIC14']

pdf_url = 'https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/AVR32-16DD20-14-Prel-DataSheet-DS40002413.pdf'
pages = [17]
#pages = [17,18]

home = 'dd14_20'
csv_fname = 'device.csv'

if False:
    # convert PDF into CSV
    tabula.convert_into(pdf_url, csv_fname, output_format="csv", pages=pages, lattice='true')

def extract_functions(row):
    functions = []
    for column in row:
        if row[column] == '':
            pass
        elif 'VQFN' in column:
            pass
        elif 'SOIC' in column:
            pass
        else:
            is_alt = False
            if '(3)' in row[column]:
                is_alt = True
                        
            group = row[column].split('\n')
            for item in group:
                print(column, item)
                func = dict()
                col = column.rstrip('0123456789n')
                if 'USART' in col:
                    col = 'USART'
                func['type'] = col.lower()
                func['alt'] = is_alt
                func['name'] = item.replace('(3)', '').replace('(6)','').replace('\n','')
                functions.append(func)
                
    return functions

def build_footprint(footprint):
    path = '{}/{}'.format(home, csv_fname)
    with open(path) as csv_file:
        pins = dict()
        reader = csv.DictReader(csv_file, delimiter=',')

        for row in reader:
            if row[footprint] > '':
                number = row[footprint]
                funcs = extract_functions(row)
                pins['P'+number] = funcs

        pins_fname = '{}/{}_pins.yaml'.format(home,footprint).lower()
        with open(pins_fname, 'w') as stream:
            yaml.dump(pins, stream)

    return

if __name__ == '__main__':
    for footprint in footprints:
        build_footprint(footprint)
        
    print('done')
