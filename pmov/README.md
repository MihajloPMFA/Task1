# PMOV – Prošireni model objekti–veze (IS Televizijske stanice)

Glavni rezultat: **`../PMOV_TV_stanica.vsdx`** – otvara se u Microsoft Visio 2013+
(jedna stranica, 112 × 106 inča).

## Sadržaj
| Fajl | Opis |
|---|---|
| `../PMOV_TV_stanica.vsdx` | PMOV dijagram za Visio |
| `PMOV_TV_stanica_pregled.png` | rasterski pregled istog dijagrama |
| `PMOV_trasabilnost.md` | veza svakog objekta/veze sa DFD i IDEF0 modelom |
| `PMOV_ispravke.md` | spisak ispravki iz revizije v1 → v2 i obrazloženja |
| `generator/` | skriptovi kojima je dijagram generisan i proveren |

## Kako je model izveden
Ulazi su BPwin modeli `DFD_16_09_2026__v12.bp1` i `IDEF0_16_09_2026__v11.bp1`.
Iz njih su izdvojeni svi objekti modela (88 procesa, 78 skladišta podataka,
8 eksternih entiteta i 647 tokova u DFD-u; 90 aktivnosti i 554 strelice u IDEF0-u),
pa su:

* **skladišta podataka i eksterni entiteti** preslikani u tipove objekata,
* **tokovi podataka** u atribute i u veze između tipova objekata,
* **mehanizmi iz IDEF0-a** (uloge, oprema, studio) u specijalizacije.

Težište je na emitovanju, produkciji, marketingu i prodaji i nabavci, uz one
elemente administracije (organizaciona struktura, fakture, nalozi za plaćanje)
bez kojih ostali procesi ne bi bili povezani.

## Generisanje i provera
```
cd generator
python3 vsdx.py ../../PMOV_TV_stanica.vsdx     # generiše .vsdx
python3 -c "import layout; S,L=layout.build_all(); print(layout.check(S,L))"   # provera preklapanja
python3 verify_vsdx.py ../../PMOV_TV_stanica.vsdx ../PMOV_TV_stanica_pregled.png 42
```
`layout.check` prijavljuje svako preklapanje oblika i svako sečenje oblika linijom;
trenutno stanje je **0 konflikata** na 588 oblika i 442 linije.

Model sadrži 37 tipova objekata (9 slabih), 16 podtipova u 6 specijalizacija,
48 tipova veza i 289 atributa.
