import requests
import os


link = 'https://thewheelshop.ca/collections/4x100-wheels/products/fast-wheels-jet-15x6-0-4x100mm-40-56-6-gloss-black?_pos=29&_fid=e88b71c2d&_ss=c'

res = requests.get(link)
if res.status_code != 200:
    print('it broked')
    exit(0)

with open('bleh.html', 'w') as f:
    f.write(res.text)