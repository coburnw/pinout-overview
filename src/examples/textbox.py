#import drawsvg as dw

#import urllib.request, urllib.parse

from PIL import ImageFont
import requests
from io import BytesIO

# family = 'Roboto'
# display = 'swap'
# text = None

# if not isinstance(family, str):
#     family = '|'.join(family)  # Request a list of families

# args = dict(family=family, display=display)

# if text is not None:
#     if not isinstance(text, str):
#         text = ''.join(text)
#     args['text'] = text

# #args.update(kwargs)

# params = urllib.parse.urlencode(args)
# url = f'https://fonts.googleapis.com/css?{params}'
# with urllib.request.urlopen(url) as r:
#     css = r.read().decode('utf-8')

# for line in css:
#     if 
# print(css)
# exit()

#return embed_css_resources(css)


#kwargs = dict(raw = True)
#font_family = dw.font_embed.download_google_font_css('Roboto', **kwargs)

font_url = "https://github.com/googlefonts/roboto/blob/master/src/hinted/Roboto-Regular.ttf?raw=true"
font_url = "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400&display=swap"
font_url = "https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmSU5vAw.ttf"
font_url = "https://fonts.googleapis.com/css2?family=Roboto"



def get_google_font(family_name, kwargs=dict()):
    google_url = "https://fonts.googleapis.com/css2"
    kwargs = dict(family=family_name)
    req = requests.get(google_url, params=kwargs)
    print(req.url)
    
    text = req.text
    start = text.rfind('url(')
    line = text[start+4:]
    end = line.find(')')
    font_url = line[:end]
    
    req = requests.get(font_url)
    print(req.url)
    font_family = req.content
    
    return font_family

if __name__ == '__main__':
    font = get_google_font('Roboto')
    
    font_data = BytesIO(font)
    font = ImageFont.truetype(font_data, 16)

    text = '''Roboto has a dual nature. 
It has a mechanical skeleton and the forms are largely geometric. 
At the same time, the font features friendly and open curves. 
While some grotesks distort their letterforms to force a rigid 
rhythm, Roboto doesn’t compromise, allowing letters to be settled 
into their natural width. This makes for a more natural reading 
rhythm more commonly found in humanist and serif types.'''

    max_length = 500

    words = text.split(' ')

    lines = []
    line = ''
    line_length = font.getlength(line)
    for word in words:
        word = word.strip()
        word_length = font.getlength(word)
        if  (line_length + word_length) < (max_length): # + word_length/2
            line += word + ' '
        else:
            lines.append(line)
            line = word + ' '

        line_length = font.getlength(line)

    for line in lines:                 
        print('{}: {}'.format(int(font.getlength(line)), line))


# <link rel="preconnect" href="https://fonts.googleapis.com">
# <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
# <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400&display=swap" rel="stylesheet">
#url(https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmSU5vAw.ttf)
