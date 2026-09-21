import os, sys
from playwright.sync_api import sync_playwright
BASE = os.path.dirname(os.path.abspath(__file__))
SHOTS = [('f1', 'Forma_1_Projekat_produkcije'),
         ('f2', 'Forma_2_Zakup_reklamnog_termina'),
         ('f3', 'Forma_3_Vrednovanje_ponuda')]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1460, 'height': 1000}, device_scale_factor=2)
    pg.goto('file://' + os.path.join(BASE, 'forme.html'))
    pg.wait_for_timeout(300)
    for sel, name in SHOTS:
        el = pg.query_selector('#' + sel)
        box = el.bounding_box()
        out = os.path.join(BASE, name + '.png')
        el.screenshot(path=out)
        print('%-36s %4d x %4d css px -> %s' % (name, box['width'], box['height'], out))
    b.close()
