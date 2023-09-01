import csv
import io

from pinoutOverview import config


pdf_url = 'https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/AVR32-16DD20-14-Prel-DataSheet-DS40002413.pdf'
pages = [17]
#pages = [17,18]

home = 'dd14_20'
csv_fname = 'variants.csv'

if False:
    import tabula
    # convert PDF into CSV
    tabula.convert_into(pdf_url, csv_fname, output_format="csv", pages=pages, lattice='true')

def build_family_functions(family_name, csv_rows):
    family_functions = config.FamilyFunctions()
    family_functions.styles = 'dxcore_functions'

    functions = dict()
    for row in csv_rows:
        pin_name = ''
        suffix = ''
        # if split is not None:
        #     suffix = 'a'
            
        for column in row:
            if 'PIN' in column:
                pin_name = row[column]

            if pin_name == '':
                # ignore any columns which occur before pin_name column
                continue

            if row[column] == '':
                continue

            # if split is not None:
            #     if split in column:
            #         suffix = 'b'
                    
            is_alt = False
            if '(3)' in row[column]:
                is_alt = True

            group = row[column].split('\n')
            for item in group:
                #print(column, item)
                col = column.rstrip('0123456789n')
                if 'USART' in col:
                    col = 'USART'

                func_name = item.replace('(3)', '').replace('(6)','').replace('\n','')
                func_type = col.lower()
                is_alt = is_alt

                if 'twi' in func_name.lower():
                    continue
                
                if 'xtal' in func_name.lower():
                    func_name = 'XTAL'

                family_functions.append(pin_name+suffix, func_name, func_type, is_alt)
                
    family_functions.save(family_name)

    return pin_name, functions

def extract_pin_map(package, csv_rows):
    pin_map = dict()
    print(package)
    for row in csv_rows:
        pin_number = row[package].strip()
        if pin_number == '':
            continue

        pin_number = int(pin_number)
        pin_name = row['PIN'].strip()
        pin_map[pin_number] = pin_name

    pins = []
    ol = sorted(pin_map.items())
    for key, value in ol:
        pins.append(value)

    return pins

def build_variant_config(variant_name, package_type, csv_rows):
    variant = config.VariantConfig()
    variant.family = family_name
    pkg_name, pkg_type = package_type
    variant_name = '{}_{}'.format(variant_name, pkg_type)
    
    variant.pins = dict(
        pin_map = extract_pin_map(pkg_name, csv_rows),
        split = 'tca'
        )

    variant.package = dict(
        type = pkg_type,
        pin_count = len(variant.pins['pin_map']),
        text1 = 'AVR16DD20\nAVR32DD20\nAVR64DD20',
        text2 = pkg_name
    )

    # add a template entry to page
    variant.page = dict(
        header = dict(
            text1 = 'big title',
            text2 = 'sub title'
        ),
        quadrant = dict(
            text1 = 'sldkfjlksjlkjsadfdjalksfdslkjalksf',
            text2 = 'jsadklfdslkjalksfsldkfjlksjlk',
            text3 = 'jalksfsldkfjlkjalksfksjlkjsadklfdsl',
            text4 = 'fdslkjalksfsldkfjlksjlkjsadkl'
        )
    )

    variant.save(variant_name)

    return

if __name__ == '__main__':

    # use qfn package only!
    packages = [('VQFN20','qfn'),('VQFN20','qfp'),('SOIC20','sop')]
    
    atp_path = 'atpack'
    family_name = 'dd14_20'
    variant_name = 'DD20'
    
    path = '{}/{}.csv'.format(atp_path, family_name)
    with open(path, newline='') as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=',')
        print('opened {}'.format(path))
        build_family_functions(family_name, csv_rows)

        for package in packages:
            csv_file.seek(0)
            csv_rows = csv.DictReader(csv_file, delimiter=',')
            build_variant_config(variant_name, package, csv_rows)
        
    print('done')
