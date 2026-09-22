# Korisnički interfejs — TV Panorama

Dva kompleta ekrana u istom dizajn sistemu: **tri forme** (unos) i **tri izveštaja**
(analitika, tab *Izveštaji*). Zajednički stilovi su u `ui.css`.

---

## Deo 1 — forme

Tri ekrana iz istog sistema koji je modelovan u PMOV-u i ER šemi. Svako polje na
formama odgovara konkretnoj koloni iz `er/ER_TV_stanica.sql` — tabele ispod.

| Fajl | Ekran | Oblast |
|------|-------|--------|
| `Forma_1_Projekat_produkcije.png` | Projekat produkcije (master–detail sa karticama) | Produkcija |
| `Forma_2_Zakup_reklamnog_termina.png` | Zakup reklamnog termina (rezervacija + obračun) | Marketing i prodaja |
| `Forma_3_Vrednovanje_ponuda.png` | Vrednovanje ponuda dobavljača (matrica ocenjivanja) | Nabavka |
| `forme.html` | izvor formi — otvara se u pregledaču, lako se menja |

Ekrani su namerno različitog tipa da pokriju tri obrasca koja se u ovom sistemu
najviše ponavljaju: **zaglavlje + stavke**, **unos sa živim obračunom** i
**poređenje po kriterijumima**.

---

## Dizajn sistem

| | |
|---|---|
| Boje | osnovna `#1650c9`, tamna navigacija `#0d1526`, podloga `#f4f6f9`, linije `#e3e8ef` |
| Status | uspeh `#0b7a44`, upozorenje `#9a5b00`, greška `#b52a2a`, neutralno `#5b6b81` |
| Tipografija | Liberation Sans / Arial; naslov 21px, naslov kartice 13px, polje 13,5px, labela 11,5px |
| Razmaci | skala 4 / 8 / 12 / 16 / 24 px |
| Radijusi | polje i dugme 8px, kartica 10px, oznaka 99px |
| Obavezna polja | crvena zvezdica uz labelu; polje u fokusu ima plavi prsten |
| Polja koja sistem popunjava | siva podloga + oznaka `AUTO` (šifra, redni broj, izvedene vrednosti) |

---

## Forma 1 — Projekat produkcije

Zaglavlje projekta + kartice za stavke koje u modelu vise o njemu.

| Polje na formi | ER tabela i kolona |
|---|---|
| Šifra projekta *(auto)* | `PROJEKAT_PRODUKCIJE.SIFRA_PROJEKTA` |
| Naziv projekta | `.NAZIV_PROJEKTA` |
| Emisija | `.SIFRA_EMISIJE` → `EMISIJA` (veza PROIZVODI, zato „najviše jednu“) |
| Urednik | `.SIFRA_UREDNIKA` → `UREDNIK` (veza UREĐUJE, obavezno) |
| Vrsta produkcije | `.VRSTA_PRODUKCIJE` |
| Datum početka / završetka | `.DATUM_POCETKA`, `.DATUM_ZAVRSETKA` |
| Odobren budžet | `.ODOBREN_BUDZET` |
| Opis projekta | `.OPIS_PROJEKTA` |
| Oznaka statusa u naslovu | `.STATUS_PROJEKTA` |
| Kartica **Aktivnosti** | `AKTIVNOST_PRODUKCIJE` — `RB_AKTIVNOSTI`, `NAZIV_AKTIVNOSTI`, `VRSTA_AKTIVNOSTI`, `LOKACIJA_SNIMANJA`, `DATUM_OD`, `DATUM_DO`, `STATUS_AKTIVNOSTI` |
| Kartica **Angažovana ekipa** | `ANGAZOVANJE_NA_AKTIVNOSTI` (veza ANGAŽUJE) |
| Kartica **Zadužena oprema** | `REZERVACIJA_OPREME` (veza ZADUŽUJE) |
| Kartica **Troškovi** | `TROSAK_PRODUKCIJE` (veza IZAZIVA) |
| Kartica **Sirovi snimci** | `SIROVI_SNIMAK` (veza SNIMLJEN NA) |
| Traka „Utrošeno … od …“ | `SUM(TROSAK_PRODUKCIJE.IZNOS)` prema `.ODOBREN_BUDZET` |

Kartice nisu ukras: `AKTIVNOST_PRODUKCIJE` je slab entitet čiji je vlasnik baš
projekat, pa stavke ne mogu ni da postoje bez otvorenog zaglavlja.

## Forma 2 — Zakup reklamnog termina

Levo unos, desno ono što sistem sam izračuna — popunjenost bloka i iznos.

| Polje na formi | ER tabela i kolona |
|---|---|
| Ugovor o oglašavanju | `UGOVOR_O_OGLASAVANJU.BROJ_UGOVORA` |
| Oglašivač *(readonly)* | `OGLASIVAC` → `KLIJENT.NAZIV_KLIJENTA`, `.PIB` (veza SKLAPA) |
| Stavka ugovora | `STAVKA_UGOVORA` — `RB_STAVKE`, `KOLICINA_SEKUNDE`, `POPUST` |
| „Ugovoreno / iskorišćeno / preostalo“ | `KOLICINA_SEKUNDE` minus zbir `EMITOVANJE_REKLAME.TRAJANJE_SPOTA` |
| Reklamni sadržaj + oznaka „Proveren“ | `REKLAMNI_SADRZAJ.SIFRA_SADRZAJA`, `.STATUS` |
| Datum emitovanja | `REKLAMNI_BLOK.DATUM` |
| Termin emitovanja | `TERMIN_EMITOVANJA` (veza ZAKUPLJEN U) |
| Reklamni blok | `REKLAMNI_BLOK.SIFRA_BLOKA` |
| Trajanje spota | `EMITOVANJE_REKLAME.TRAJANJE_SPOTA` |
| Redni broj u bloku *(auto)* | `EMITOVANJE_REKLAME.RB_U_BLOKU` — parcijalni ključ slabog entiteta |
| Zona gledanosti *(readonly)* | `TERMIN_EMITOVANJA.ZONA_GLEDANOSTI` |
| Traka popunjenosti | `REKLAMNI_BLOK.TRAJANJE_BLOKA`, `.ZAKUPLJENO_SEKUNDI`, `.SLOBODNO_SEKUNDI`, `.ISKORISCENOST` |
| Spisak spotova u bloku | `EMITOVANJE_REKLAME` (veza SADRŽI SPOT) |
| Obračun | `CENOVNIK_REKL_TERMINA.ZONA`, `.CENA_PO_SEKUNDI` (veza TARIFIRAN) × trajanje − popust → `EMITOVANJE_REKLAME.NAPLACENI_IZNOS` |

Redni broj je siv i nosi oznaku `AUTO` zato što je deo primarnog ključa
`EMITOVANJE_REKLAME(SIFRA_BLOKA, RB_U_BLOKU)` — korisnik ga ne sme birati.

## Forma 3 — Vrednovanje ponuda dobavljača

Veza `VREDNUJE SE` je N:M sa atributom `BROJ_BODOVA`, pa je prirodan oblik forme
matrica: redovi su kriterijumi, kolone su ponude, ćelije su ocene.

| Deo forme | ER tabela i kolona |
|---|---|
| Traka zaglavlja | `ZAHTEV_ZA_NABAVKU` — `BROJ_ZAHTEVA`, `PREDMET_ZAHTEVA`, `SIFRA_JEDINICE`, `PROCENJENA_VREDNOST`, `PRIORITET` |
| „Plan nabavke · stavka“ | `PLAN_NABAVKE` + `STAVKA_PLANA_NABAVKE` (veze UVRŠTEN U, SADRŽI STAVKE PLANA) |
| Redovi matrice | `KRITERIJUM_VREDNOVANJA.NAZIV_KRITERIJUMA`, `.NACIN_BODOVANJA` |
| Kolone matrice | `PONUDA_DOBAVLJACA.BROJ_PONUDE` + `DOBAVLJAC.NAZIV_DOBAVLJACA` (veza DOSTAVIO) |
| Polja za ocenu | `OCENA_PONUDE.BROJ_BODOVA` (atribut veze VREDNUJE SE) |
| Redovi ispod ocena | `PONUDA_DOBAVLJACA.UKUPNA_CENA`, `.ROK_ISPORUKE`, `.USLOVI_PLACANJA` |
| „Dosadašnja ocena dobavljača“ | `DOBAVLJAC.OCENA_DOBAVLJACA` (izvedeno iz `REKLAMACIJA`) |
| „Ukupno bodova“ | `PONUDA_DOBAVLJACA.UKUPNO_BODOVA` — izvedeni atribut |
| „Izabrana ponuda“ | `PONUDA_DOBAVLJACA.STATUS_PONUDE` |
| Obrazloženje izbora | `OCENA_PONUDE.KOMENTAR_OCENE` |
| „Ponude važe do“ | `PONUDA_DOBAVLJACA.VAZI_DO` |
| Dugme „Kreiraj narudžbenicu“ | prelazak na `NARUDZBENICA` (veza NARUČENO OD) |

> Napomena: u vašoj verziji PMOV-a obrisani su entitet `ODLUKA O IZBORU DOBAVLJAČA`
> i veza `BIRA`, pa izbor ponude ovde stoji kao `STATUS_PONUDE`. Ako se odluka vrati
> u model, ovaj deo forme postaje zaseban zapis sa datumom i komisijom.

---

## Kako se menjaju

Sve tri forme su jedan HTML fajl sa zajedničkim dizajn sistemom u `:root`.
Promena boje, razmaka ili teksta je izmena u `forme.html`, a zatim:

```
python3 ui/shot.py
```

što ponovo napravi sve tri slike u 2× rezoluciji (2880 px široke).


---

## Deo 2 — izveštaji (tab *Izveštaji*)

Ista navigacija, isti dizajn sistem, aktivna stavka **Izveštaji**.

| Fajl | Izveštaj | Oblast | Tip |
|------|----------|--------|-----|
| `Izvestaj_1_Realizacija_seme_i_gledanost.png` | Realizacija programske šeme i gledanost | Program i emitovanje | kontrolna tabla |
| `Izvestaj_2_Prihodi_od_oglasavanja.png` | Prihodi od oglašavanja | Marketing i prodaja | kontrolna tabla |
| `Izvestaj_3_Realizacija_plana_nabavke.png` | Realizacija plana nabavke | Nabavka | overen dokument za štampu |
| `izvestaji.html` | izvor sva tri izveštaja |
| `gen_izvestaji.py` | generiše `izvestaji.html` — grafikoni su inline SVG sa izračunatim koordinatama |
| `ui.css` | zajednički dizajn sistem za forme i izveštaje |

Treći je namerno drugačiji: izveštaj koji se overava i štampa, sa zaglavljem,
brojem izveštaja, periodom, napomenama i mestom za potpise — za razliku od prva
dva koja su ekrani za rad.

### Odakle dolaze podaci

| Izveštaj | ER tabele i kolone |
|---|---|
| **1 — Realizacija šeme** | `TERMIN_EMITOVANJA` (planirani termini), `ZAPIS_O_EMITOVANJU` (`STATUS_REALIZACIJE`, `STVARNO_TRAJANJE`, `NAPOMENA_O_SMETNJAMA`), `MERENJE_EMISIJE.OSTVARENI_RATING` i `.UDEO_U_TERMINU` (atributi veze MERENA), `EMISIJA.NAZIV_EMISIJE`, `PROGRAMSKA_SEMA` |
| **2 — Prihodi od oglašavanja** | `EMITOVANJE_REKLAME` (`NAPLACENI_IZNOS`, `STATUS_NAPLATE`, `TRAJANJE_SPOTA`), `FAKTURA` (`IZNOS_ZA_PLACANJE`, `STATUS_PLACANJA`), `UGOVOR_O_OGLASAVANJU`, `OGLASIVAC` → `KLIJENT.NAZIV_KLIJENTA`, `REKLAMNI_BLOK.ISKORISCENOST` po `TERMIN_EMITOVANJA.ZONA_GLEDANOSTI` |
| **3 — Plan nabavke** | `PLAN_NABAVKE`, `STAVKA_PLANA_NABAVKE` (`PROCENJENA_CENA`, `PLANIRANI_KVARTAL`), `NARUDZBENICA.UKUPAN_IZNOS`, `PRIJEM_STAVKE`, `FAKTURA`, `REKLAMACIJA` (napomene), `ZAHTEV_ZA_NABAVKU.STATUS_ZAHTEVA` |

### Odluke o grafikonima

Forma grafikona je birana prema poslu koji podatak obavlja, a ne prema izgledu:

| Grafikon | Forma | Zašto |
|---|---|---|
| Rejting po danu | linija, jedna serija | trend kroz vreme; jedna serija ne traži legendu — naslov kaže šta je nacrtano |
| Najgledanije emisije | vodoravne trake, **jedna boja** | poređenje veličine; boja po vrednosti bi dva puta kodirala istu stvar |
| Fakturisano po mesecima | složeni stubovi, dve serije | deo–celina (naplaćeno + za naplatu = fakturisano); ista jedinica, **jedna osa** |
| Popunjenost po zoni | merači | jedan odnos prema cilju — nije grafikon nego tri broja |
| Odstupanje od plana | divergentne trake | polaritet oko nule: plavo ispod plana, crveno iznad |

Paleta je **proverena skriptom**, ne na oko, nad podlogom `#ffffff`:

```
#2a78d6, #eb6834   -> sve provere PASS (CVD ΔE 24,7 · normalan vid ΔE 33,6 · kontrast ≥ 3:1)
#2a78d6 <-> #e34948 -> sve provere PASS (divergentni par, neutralna sredina)
```

Primenjena pravila: nikad dve y-ose; trake najviše 24px debele sa 4px zaobljenim
krajem podatka i ravnim dnom na osnovici; linija 2px; 2px razmak u boji podloge
između segmenata složenog stuba; mreža tanka i puna (nikad isprekidana);
legenda čim ima dve serije; oznake vrednosti samo na krajnjoj, najvišoj i
najnižoj tački — nikad na svakoj; tekst uvek u bojama teksta, nikad u boji
serije. Sve vrednosti koje grafikon ne ispisuje stoje u tabeli ispod njega.

### Kako se menjaju

```
python3 ui/gen_izvestaji.py   # ponovo napravi izvestaji.html (podaci i grafikoni)
python3 ui/shot.py            # napravi svih 6 slika u 2x rezoluciji
```

Podaci za grafikone su liste na vrhu `gen_izvestaji.py` (`REJTING`, `TOP`,
`NAPL`, `DUG`, `ODST`) — promena vrednosti automatski pomera i marke i oznake.
Prosečan rejting u KPI polju se računa iz iste liste, pa izveštaj ne može da
protivreči svom grafikonu.
