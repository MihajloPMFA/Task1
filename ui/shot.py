import os, sys
from playwright.sync_api import sync_playwright
BASE = os.path.dirname(os.path.abspath(__file__))
PAGES = [('forme.html', [('f1', 'Forma_1_Projekat_produkcije'),
                         ('f2', 'Forma_2_Zakup_reklamnog_termina'),
                         ('f3', 'Forma_3_Vrednovanje_ponuda')]),
         ('izvestaji.html', [('r1', 'Izvestaj_1_Realizacija_seme_i_gledanost'),
                             ('r2', 'Izvestaj_2_Prihodi_od_oglasavanja'),
                             ('r3', 'Izvestaj_3_Realizacija_plana_nabavke')])]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1460, 'height': 1000}, device_scale_factor=2)
    for page, shots in PAGES:
        pg.goto('file://' + os.path.join(BASE, page))
        pg.wait_for_timeout(250)
        for sel, name in shots:
            el = pg.query_selector('#' + sel)
            box = el.bounding_box()
            out = os.path.join(BASE, name + '.png')
            el.screenshot(path=out)
            print('%-42s %4d x %4d css px' % (name, box['width'], box['height']))
    b.close()
