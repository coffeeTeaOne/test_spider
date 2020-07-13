import requests
from fontTools.ttLib import TTFont


urls = ['https://industrydown1.fang.com/3fang/land-egg/1.3.5/font/my_default_a.6ce68cf0.ttf',
        'https://industrydown1.fang.com/3fang/land-egg/1.3.5/font/my_default_b.d6b75413.ttf',
        'https://industrydown1.fang.com/3fang/land-egg/1.3.5/font/my_default_c.580b51a2.ttf'
        ]

for url in urls:
    ttf_content = requests.get(url)
    new_font_name ='./' +  url.split('/')[-1]
    with open(new_font_name, 'wb') as f:
       f.write(ttf_content.content)




    font = TTFont(url.split('/')[-1])
    font.saveXML(f"./{url.split('/')[-1].split('.ttf')[0]}.xml")