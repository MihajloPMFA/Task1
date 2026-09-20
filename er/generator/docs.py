# -*- coding: utf-8 -*-
"""Generise dokumentaciju preslikavanja PMOV -> relaciona sema."""
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import TABLES
BY = {t['name']: t for t in TABLES}
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- PMOV entitet -> tabela -----------------------------------------
ENT = [
 # (PMOV entitet, vrsta, tabela)
 ('ORGANIZACIONA JEDINICA','jak','ORGANIZACIONA_JEDINICA'),
 ('ZAPOSLENI','jak (nadtip)','ZAPOSLENI'),
 ('UREDNIK','podtip','UREDNIK'),
 ('NOVINAR / REPORTER','podtip','NOVINAR_REPORTER'),
 ('TEHNICKO OSOBLJE','podtip','TEHNICKO_OSOBLJE'),
 ('REFERENT','podtip','REFERENT'),
 ('SERVISERI','podtip','SERVISERI'),
 ('OPREMA','jak (nadtip)','OPREMA'),
 ('SNIMATELJSKA OPREMA','podtip','SNIMATELJSKA_OPREMA'),
 ('STUDIJSKA I EMISIONA OPREMA','podtip (i nadtip)','STUDIJSKA_I_EMISIONA_OPREMA'),
 ('AUDIO OPREMA','podtip','AUDIO_OPREMA'),
 ('SVETLOSNA OPREMA','podtip','SVETLOSNA_OPREMA'),
 ('PROJEKAT PRODUKCIJE','jak','PROJEKAT_PRODUKCIJE'),
 ('AKTIVNOST PRODUKCIJE','slab','AKTIVNOST_PRODUKCIJE'),
 ('TROSAK PRODUKCIJE','slab','TROSAK_PRODUKCIJE'),
 ('SIROVI SNIMAK','jak','SIROVI_SNIMAK'),
 ('GRAFICKI I MUZICKI ELEMENT','jak','GRAFICKI_I_MUZICKI_ELEMENT'),
 ('PROGRAMSKA SEMA','jak','PROGRAMSKA_SEMA'),
 ('PROGRAMSKA CELINA','slab','PROGRAMSKA_CELINA'),
 ('TERMIN EMITOVANJA','jak','TERMIN_EMITOVANJA'),
 ('ZAPIS O EMITOVANJU','slab','ZAPIS_O_EMITOVANJU'),
 ('EMISIJA','jak','EMISIJA'),
 ('MEDIJSKI SADRZAJ','jak (nadtip)','MEDIJSKI_SADRZAJ'),
 ('PRODUCIRANI SADRZAJ','podtip','PRODUCIRANI_SADRZAJ'),
 ('NABAVLJENI SADRZAJ','podtip','NABAVLJENI_SADRZAJ'),
 ('REKLAMNI SADRZAJ','podtip','REKLAMNI_SADRZAJ'),
 ('PRAVO KORISCENJA','jak','PRAVO_KORISCENJA'),
 ('POVRATNA INFO. GLEDALACA','jak','POVRATNA_INFO_GLEDALACA'),
 ('MERENJE GLEDANOSTI','jak','MERENJE_GLEDANOSTI'),
 ('CENOVNIK REKL. TERMINA','jak','CENOVNIK_REKL_TERMINA'),
 ('REKLAMNI BLOK','jak','REKLAMNI_BLOK'),
 ('EMITOVANJE REKLAME','slab','EMITOVANJE_REKLAME'),
 ('STAVKA UGOVORA','slab','STAVKA_UGOVORA'),
 ('UGOVOR','jak (nadtip)','UGOVOR'),
 ('UGOVOR O OGLASAVANJU','podtip','UGOVOR_O_OGLASAVANJU'),
 ('UGOVOR O PRODAJI TV SADRZAJA','podtip','UGOVOR_O_PRODAJI_TV_SADRZAJA'),
 ('UGOVOR O NABAVCI','podtip','UGOVOR_O_NABAVCI'),
 ('KLIJENT','jak (nadtip)','KLIJENT'),
 ('OGLASIVAC','podtip','OGLASIVAC'),
 ('KUPAC SADRZAJA','podtip','KUPAC_SADRZAJA'),
 ('ZAHTEV ZA NABAVKU','jak','ZAHTEV_ZA_NABAVKU'),
 ('PLAN NABAVKE','jak','PLAN_NABAVKE'),
 ('STAVKA PLANA NABAVKE','slab','STAVKA_PLANA_NABAVKE'),
 ('PONUDA DOBAVLJACA','jak','PONUDA_DOBAVLJACA'),
 ('KRITERIJUM VREDNOVANJA','jak','KRITERIJUM_VREDNOVANJA'),
 ('DOBAVLJAC','jak (nadtip)','DOBAVLJAC'),
 ('DOBAVLJAC TV SADRZAJA','podtip','DOBAVLJAC_TV_SADRZAJA'),
 ('DOBAVLJAC OPREME I MATERIJALA','podtip','DOBAVLJAC_OPREME_I_MATERIJALA'),
 ('NARUDZBENICA','jak','NARUDZBENICA'),
 ('STAVKA NARUDZBENICE','slab','STAVKA_NARUDZBENICE'),
 ('PRIJEMNICA','jak','PRIJEMNICA'),
 ('REKLAMACIJA','jak','REKLAMACIJA'),
 ('FAKTURA','jak','FAKTURA'),
 ('STAVKA FAKTURE','slab','STAVKA_FAKTURE'),
 ('NALOG ZA PLACANJE','jak','NALOG_ZA_PLACANJE'),
]

# ---- PMOV veza -> realizacija ---------------------------------------
REL = [
 # (veza, kardinalnosti, tip, realizacija)
 ('PODREDJENA','ORG. JEDINICA (0,N) - ORG. JEDINICA (0,1)','1:N rekurzivna',
  'ORGANIZACIONA_JEDINICA.SIFRA_NADREDJENE_JEDINICE -> ORGANIZACIONA_JEDINICA'),
 ('RADI U','ZAPOSLENI (1,1) - ORG. JEDINICA (0,N)','1:N',
  'ZAPOSLENI.SIFRA_JEDINICE (NOT NULL)'),
 ('ZADUZENA','ZAPOSLENI (0,N) - OPREMA (0,N)','N:M + atributi',
  'tabela ZADUZENJE_OPREME'),
 ('SERVISIRANJE','SERVISERI (0,N) - OPREMA (0,N)','N:M + atributi',
  'tabela SERVISIRANJE_OPREME'),
 ('ANGAZUJE','ZAPOSLENI (0,N) - AKTIVNOST PRODUKCIJE (0,N)','N:M + atributi',
  'tabela ANGAZOVANJE_NA_AKTIVNOSTI'),
 ('ZADUZUJE','OPREMA (0,N) - AKTIVNOST PRODUKCIJE (0,N)','N:M + atributi',
  'tabela REZERVACIJA_OPREME'),
 ('UREDJUJE','UREDNIK (0,N) - PROJEKAT PRODUKCIJE (1,1)','1:N',
  'PROJEKAT_PRODUKCIJE.SIFRA_UREDNIKA (NOT NULL)'),
 ('ODOBRAVA','UREDNIK (0,N) - PROGRAMSKA SEMA (1,1)','1:N',
  'PROGRAMSKA_SEMA.SIFRA_UREDNIKA (NOT NULL)'),
 ('SASTOJI SE OD *','PROJEKAT (1,N) - AKTIVNOST (1,1)','1:N identifikujuca',
  'AKTIVNOST_PRODUKCIJE.SIFRA_PROJEKTA u primarnom kljucu'),
 ('IZAZIVA','AKTIVNOST (0,N) - TROSAK (1,1)','1:N identifikujuca',
  'TROSAK_PRODUKCIJE.(SIFRA_PROJEKTA, RB_AKTIVNOSTI) u primarnom kljucu'),
 ('DOKUMENTOVAN','TROSAK PRODUKCIJE (0,1) - FAKTURA (0,N)','1:N',
  'TROSAK_PRODUKCIJE.BROJ_FAKTURE (NULL)'),
 ('SNIMLJEN NA','SIROVI SNIMAK (1,1) - AKTIVNOST (0,N)','1:N',
  'SIROVI_SNIMAK.(SIFRA_PROJEKTA, RB_AKTIVNOSTI) (NOT NULL)'),
 ('PROIZVODI','PROJEKAT (0,1) - EMISIJA (0,N)','1:N',
  'PROJEKAT_PRODUKCIJE.SIFRA_EMISIJE (NULL)'),
 ('MONTIRAN U','SIROVI SNIMAK (0,N) - MEDIJSKI SADRZAJ (0,N)','N:M',
  'tabela MONTAZA_SNIMKA'),
 ('UGRADJEN U','GRAF. I MUZ. ELEMENT (0,N) - MEDIJSKI SADRZAJ (0,N)','N:M + atributi',
  'tabela UGRADNJA_ELEMENTA'),
 ('SADRZI CELINE *','PROGRAMSKA SEMA (1,N) - PROGRAMSKA CELINA (1,1)','1:N identifikujuca',
  'PROGRAMSKA_CELINA.SIFRA_SEME u primarnom kljucu'),
 ('OBUHVATA','PROGRAMSKA CELINA (1,N) - TERMIN (1,1)','1:N',
  'TERMIN_EMITOVANJA.(SIFRA_SEME, RB_CELINE) (NOT NULL)'),
 ('REALIZOVAN *','TERMIN (0,N) - ZAPIS O EMITOVANJU (1,1)','1:N identifikujuca',
  'ZAPIS_O_EMITOVANJU.SIFRA_TERMINA u primarnom kljucu'),
 ('PLANIRANA','TERMIN (1,1) - EMISIJA (0,N)','1:N',
  'TERMIN_EMITOVANJA.SIFRA_EMISIJE (NOT NULL)'),
 ('EVIDENTIRA','ZAPIS O EMITOVANJU (1,1) - MEDIJSKI SADRZAJ (0,N)','1:N',
  'ZAPIS_O_EMITOVANJU.SIFRA_SADRZAJA (NOT NULL)'),
 ('CINI','EMISIJA (1,N) - MEDIJSKI SADRZAJ (0,N)','N:M + atribut',
  'tabela SADRZAJ_EMISIJE'),
 ('POKRIVA','PRAVO KORISCENJA (1,N) - MEDIJSKI SADRZAJ (0,N)','N:M + atribut',
  'tabela POKRIVENOST_PRAVOM'),
 ('MERENA','MERENJE GLEDANOSTI (1,N) - EMISIJA (0,N)','N:M + atributi',
  'tabela MERENJE_EMISIJE'),
 ('ODNOSI SE NA','POVRATNA INFO. (0,1) - EMISIJA (0,N)','1:N',
  'POVRATNA_INFO_GLEDALACA.SIFRA_EMISIJE (NULL)'),
 ('ZAKUPLJEN U','REKLAMNI BLOK (1,1) - TERMIN (0,N)','1:N',
  'REKLAMNI_BLOK.SIFRA_TERMINA (NOT NULL)'),
 ('TARIFIRAN','CENOVNIK (1,N) - REKLAMNI BLOK (1,1)','1:N',
  'REKLAMNI_BLOK.SIFRA_CENOVNIKA (NOT NULL)'),
 ('SADRZI SPOT','REKLAMNI BLOK (1,N) - EMITOVANJE REKLAME (1,1)','1:N identifikujuca',
  'EMITOVANJE_REKLAME.SIFRA_BLOKA u primarnom kljucu'),
 ('PRIKAZUJE','EMITOVANJE REKLAME (1,1) - REKLAMNI SADRZAJ (0,N)','1:N',
  'EMITOVANJE_REKLAME.SIFRA_SADRZAJA (NOT NULL)'),
 ('UGOVOREN','EMITOVANJE REKLAME (1,1) - STAVKA UGOVORA (0,N)','1:N',
  'EMITOVANJE_REKLAME.(BROJ_UGOVORA, RB_STAVKE_UGOVORA) (NOT NULL)'),
 ('PRECIZIRA','UGOVOR (1,N) - STAVKA UGOVORA (1,1)','1:N identifikujuca',
  'STAVKA_UGOVORA.BROJ_UGOVORA u primarnom kljucu'),
 ('SKLAPA','KLIJENT (0,N) - UGOVOR (0,1)','1:N',
  'UGOVOR.SIFRA_KLIJENTA (NULL)'),
 ('DOSTAVLJA','OGLASIVAC (1,N) - REKLAMNI SADRZAJ (1,1)','1:N',
  'REKLAMNI_SADRZAJ.SIFRA_OGLASIVACA (NOT NULL)'),
 ('USTUPA','UGOVOR O PRODAJI (1,N) - PRODUCIRANI SADRZAJ (0,N)','N:M + atributi',
  'tabela USTUPANJE_SADRZAJA'),
 ('UGOVARA','DOBAVLJAC (0,N) - UGOVOR O NABAVCI (1,1)','1:N',
  'UGOVOR_O_NABAVCI.SIFRA_DOBAVLJACA (NOT NULL)'),
 ('NABAVLJEN PO','NABAVLJENI SADRZAJ (1,1) - UGOVOR O NABAVCI (1,N)','1:N + atributi',
  'NABAVLJENI_SADRZAJ.BROJ_UGOVORA + kolone DATUM_PREUZIMANJA, UGOVORENA_NAKNADA'),
 ('PODNOSI','ORG. JEDINICA (0,N) - ZAHTEV ZA NABAVKU (1,1)','1:N',
  'ZAHTEV_ZA_NABAVKU.SIFRA_JEDINICE (NOT NULL)'),
 ('UVRSTEN U','ZAHTEV (0,1) - PLAN NABAVKE (0,N)','1:N',
  'ZAHTEV_ZA_NABAVKU.SIFRA_PLANA (NULL)'),
 ('SADRZI STAVKE PLANA *','PLAN NABAVKE (1,N) - STAVKA PLANA (1,1)','1:N identifikujuca',
  'STAVKA_PLANA_NABAVKE.SIFRA_PLANA u primarnom kljucu'),
 ('PONUDJENA','STAVKA PLANA (0,N) - PONUDA DOBAVLJACA (0,N)','N:M + atributi',
  'tabela PONUDJENA_STAVKA'),
 ('VREDNUJE SE','PONUDA (1,N) - KRITERIJUM (1,N)','N:M + atributi',
  'tabela OCENA_PONUDE'),
 ('DOSTAVIO','DOBAVLJAC (0,N) - PONUDA DOBAVLJACA (1,1)','1:N',
  'PONUDA_DOBAVLJACA.SIFRA_DOBAVLJACA (NOT NULL)'),
 ('NARUCENO OD','DOBAVLJAC (0,N) - NARUDZBENICA (1,1)','1:N',
  'NARUDZBENICA.SIFRA_DOBAVLJACA (NOT NULL)'),
 ('SADRZI STAVKE NARUDZBINE *','NARUDZBENICA (1,N) - STAVKA (1,1)','1:N identifikujuca',
  'STAVKA_NARUDZBENICE.BROJ_NARUDZBENICE u primarnom kljucu'),
 ('PRACENA','NARUDZBENICA (0,N) - PRIJEMNICA (1,1)','1:N',
  'PRIJEMNICA.BROJ_NARUDZBENICE (NOT NULL)'),
 ('PRIMLJENO PO','PRIJEMNICA (1,N) - STAVKA NARUDZBENICE (0,N)','N:M + atributi',
  'tabela PRIJEM_STAVKE'),
 ('REKLAMIRANA','PRIJEMNICA (0,N) - REKLAMACIJA (1,1)','1:N',
  'REKLAMACIJA.BROJ_PRIJEMNICE (NOT NULL)'),
 ('ODNOSI SE NA (reklamacija)','REKLAMACIJA (1,N) - STAVKA NARUDZBENICE (0,N)','N:M',
  'tabela REKLAMIRANA_STAVKA'),
 ('FAKTURISANA','PRIJEMNICA (0,1) - FAKTURA (0,N)','1:N',
  'PRIJEMNICA.BROJ_FAKTURE (NULL)'),
 ('SADRZI STAVKE FAKTURE *','FAKTURA (1,N) - STAVKA FAKTURE (1,1)','1:N identifikujuca',
  'STAVKA_FAKTURE.BROJ_FAKTURE u primarnom kljucu'),
 ('PLACENA','FAKTURA (0,N) - NALOG ZA PLACANJE (1,1)','1:N',
  'NALOG_ZA_PLACANJE.BROJ_FAKTURE (NOT NULL)'),
 ('IZDATA PO','UGOVOR (0,N) - FAKTURA (0,1)','1:N',
  'FAKTURA.BROJ_UGOVORA (NULL)'),
]

SPEC = [
 ('ZAPOSLENI','UREDNIK, NOVINAR / REPORTER, TEHNICKO OSOBLJE, REFERENT, SERVISERI',
  'UREDNIK, NOVINAR_REPORTER, TEHNICKO_OSOBLJE, REFERENT, SERVISERI'),
 ('OPREMA','SNIMATELJSKA OPREMA, STUDIJSKA I EMISIONA OPREMA',
  'SNIMATELJSKA_OPREMA, STUDIJSKA_I_EMISIONA_OPREMA'),
 ('STUDIJSKA I EMISIONA OPREMA','AUDIO OPREMA, SVETLOSNA OPREMA',
  'AUDIO_OPREMA, SVETLOSNA_OPREMA'),
 ('MEDIJSKI SADRZAJ','PRODUCIRANI, NABAVLJENI, REKLAMNI SADRZAJ',
  'PRODUCIRANI_SADRZAJ, NABAVLJENI_SADRZAJ, REKLAMNI_SADRZAJ'),
 ('UGOVOR','O NABAVCI, O OGLASAVANJU, O PRODAJI TV SADRZAJA',
  'UGOVOR_O_NABAVCI, UGOVOR_O_OGLASAVANJU, UGOVOR_O_PRODAJI_TV_SADRZAJA'),
 ('KLIJENT','OGLASIVAC, KUPAC SADRZAJA','OGLASIVAC, KUPAC_SADRZAJA'),
 ('DOBAVLJAC','DOBAVLJAC TV SADRZAJA, DOBAVLJAC OPREME I MATERIJALA',
  'DOBAVLJAC_TV_SADRZAJA, DOBAVLJAC_OPREME_I_MATERIJALA'),
]

def tbl(rows, head):
    w = [max(len(str(r[i])) for r in [head] + rows) for i in range(len(head))]
    out = ['| ' + ' | '.join('%-*s' % (w[i], head[i]) for i in range(len(head))) + ' |',
           '|' + '|'.join('-' * (w[i] + 2) for i in range(len(head))) + '|']
    for r in rows:
        out.append('| ' + ' | '.join('%-*s' % (w[i], str(r[i])) for i in range(len(head))) + ' |')
    return '\n'.join(out)

o = io.StringIO()
W = o.write
W('# Preslikavanje PMOV -> relaciona sema (ER model za ERwin r7.3)\n\n')
W('Izvor: `PMOV_TV_stanica_2_1_1.vsdx` (vasa verzija PMOV dijagrama).\n')
W('Iz njega je masinski procitano: **55 entiteta** (9 slabih), **45 imenovanih veza**,\n')
W('**7 specijalizacija**, **317 atributa** i **96 oznaka kardinalnosti**.\n\n')
W('Rezultat: **%d tabela**, **%d kolona**, **%d stranih kljuceva** '
  '(fajl `ER_TV_stanica.sql`).\n\n' % (
      len(TABLES), sum(len(t['cols']) for t in TABLES),
      sum(len(t['fks']) for t in TABLES)))
W('---\n\n## 1. Pravila preslikavanja koja su primenjena\n\n')
W("""1. **Jak entitet** -> tabela; njegov kljucni atribut -> primarni kljuc.
2. **Slab entitet** -> tabela ciji je primarni kljuc *kljuc vlasnika + parcijalni kljuc*
   (npr. `AKTIVNOST_PRODUKCIJE(SIFRA_PROJEKTA, RB_AKTIVNOSTI)`). Identifikujuca veza
   ne daje posebnu tabelu - ona je ugradjena u primarni kljuc.
3. **Veza 1:N** -> strani kljuc na strani sa maksimumom 1. Ako je minimum te strane 1,
   kolona je `NOT NULL`; ako je 0, kolona je nullable.
4. **Veza N:M** -> posebna (asocijativna) tabela; primarni kljuc je unija kljuceva
   oba ucesnika; atributi veze postaju kolone te tabele.
5. **Atributi veze 1:N** -> kolone tabele koja nosi strani kljuc
   (npr. `NABAVLJEN PO` -> `NABAVLJENI_SADRZAJ.DATUM_PREUZIMANJA`, `UGOVORENA_NAKNADA`).
6. **Specijalizacija** -> tabela po podtipu; primarni kljuc podtipa je istovremeno
   strani kljuc ka nadtipu. (Ista konvencija kao u vasem primeru `TV_stanica_v7.erwin`,
   gde su `REFERENT_NABAVKE`, `STUDIJSKA_OPREMA` ... zasebne tabele.)
7. **Slozeni atribut** -> razlozen na proste kolone
   (`KLIJENT.ADRESA` -> `ULICA_I_BROJ`, `GRAD`, `POSTANSKI_BROJ`).
8. **Izvedeni atributi** su zadrzani kao kolone, ali su u DDL-u oznaceni komentarom
   `izvedeni atribut` - u fizickoj bazi se racunaju, ne unose.
9. **Imena** su ASCII, velikim slovima, sa podvlakom (S->S, C->C, Z->Z, DJ za D),
   jer ERwin i vecina baza ne rukuju dobro dijakriticima. Duzina imena <= 30 znakova.

""")
W('---\n\n## 2. Entiteti -> tabele (%d)\n\n' % len(ENT))
W(tbl([(e[0], e[1], '`%s`' % e[2]) for e in ENT], ('PMOV entitet', 'Vrsta', 'Tabela')))
W('\n\n---\n\n## 3. Specijalizacije (7)\n\n')
W(tbl([('`%s`' % s[0].replace(' ', '_'), s[1], s[2]) for s in SPEC],
      ('Nadtip', 'Podtipovi u PMOV-u', 'Tabele podtipova')))
W('\n\nSvaka tabela podtipa ima primarni kljuc koji je istovremeno strani kljuc ka nadtipu,\n')
W('pa je 1:1 veza sa nadtipom garantovana.\n\n')
W('---\n\n## 4. Veze -> strani kljucevi i asocijativne tabele (%d)\n\n' % len(REL))
W(tbl([(r[0], r[1], r[2], r[3]) for r in REL],
      ('PMOV veza', 'Kardinalnosti', 'Tip', 'Realizacija u semi')))
W('\n\n`*` = veza koja **nedostaje u vasoj verziji PMOV-a**, a bez koje slab entitet ne moze\n')
W('da ima ispravan primarni kljuc - vidi odeljak 6.\n\n')
W('---\n\n## 5. Asocijativne tabele (N:M veze)\n\n')
assoc = [t for t in TABLES if t['src'].startswith('veza ')]
W(tbl([('`%s`' % t['name'], t['src'].split(':')[0].replace('veza ', ''),
        ', '.join(t['pk'])) for t in assoc],
      ('Tabela', 'PMOV veza', 'Primarni kljuc')))
W('\n\n---\n\n## 6. Sta je moralo da se doda u odnosu na vas PMOV\n\n')
W("""U verziji `PMOV_TV_stanica_2_1_1.vsdx` nedostaje **sest identifikujucih veza**
(dvostruki romb) koje su postojale u prethodnoj verziji dijagrama:

| Identifikujuca veza | Vlasnik | Slab entitet |
|---------------------|---------|--------------|
| SASTOJI SE OD | PROJEKAT PRODUKCIJE | AKTIVNOST PRODUKCIJE |
| SADRZI CELINE | PROGRAMSKA SEMA | PROGRAMSKA CELINA |
| REALIZOVAN | TERMIN EMITOVANJA | ZAPIS O EMITOVANJU |
| SADRZI STAVKE PLANA | PLAN NABAVKE | STAVKA PLANA NABAVKE |
| SADRZI STAVKE NARUDZBINE | NARUDZBENICA | STAVKA NARUDZBENICE |
| SADRZI STAVKE FAKTURE | FAKTURA | STAVKA FAKTURE |

Bez njih:

* pet slabih entiteta nema vlasnika, pa njihov parcijalni kljuc (`RB STAVKE`,
  `RB AKTIVNOSTI`, `RB CELINE`) **ne moze da bude primarni kljuc** - `RB_STAVKE = 1`
  postoji u svakoj narudzbenici;
* `STAVKA FAKTURE` u vasem dijagramu **nema nijednu vezu** - potpuno je odvojena od
  ostatka modela;
* `TROSAK PRODUKCIJE` je slab entitet nad `AKTIVNOST PRODUKCIJE`, koja je i sama slaba
  nad `PROJEKAT PRODUKCIJE`, pa lanac kljuceva puca na prvom clanu.

Zato su te sest veza **vracene u ER model** i oznacene su zvezdicom u tabeli iz
odeljka 4. To je jedino sto je dodato - nijedan entitet, atribut ni veza nisu izmisljeni.

**Nije vraceno:** entitet `ODLUKA O IZBORU DOBAVLJACA` i veza `BIRA`, koje ste obrisali.
To je sadrzinska odluka (koga bira komisija), a ne strukturna nuznost, pa nisu dirane.
Posledica: u semi ne postoji podatak o tome koja je ponuda izabrana - veza
`PONUDA_DOBAVLJACA -> NARUDZBENICA` ide samo posredno, preko dobavljaca. Ako to zelite,
dovoljno je u `NARUDZBENICA` dodati kolonu `BROJ_PONUDE` kao strani kljuc.

**Jedna izmena kardinalnosti:** `REALIZOVAN` je vracen kao `TERMIN (0,N) - ZAPIS (1,1)`
umesto `(0,1) - (1,1)`. Sa `(0,1)` bi `RB EMITOVANJA` bio suvisan (jedan zapis po terminu),
pa slab entitet ne bi imao smisla. Sa `(0,N)` jedan termin moze imati vise zapisa
(npr. prekid i nastavak emitovanja), sto je i razlog postojanja rednog broja.

""")
W('---\n\n## 7. Struktura tabela\n\n')
for t in TABLES:
    W('### `%s`\n\n' % t['name'])
    W('*PMOV:* %s\n\n' % t['src'])
    rows = []
    for c in t['cols']:
        flag = []
        if c['n'] in t['pk']:
            flag.append('PK')
        for f in t['fks']:
            if c['n'] in f['child']:
                flag.append('FK -> %s' % f['parent'])
        rows.append(('`%s`' % c['n'], c['t'], '' if c['null'] else 'NOT NULL',
                     ', '.join(flag), c['d']))
    W(tbl(rows, ('Kolona', 'Tip', 'Obavezno', 'Kljuc', 'Poreklo iz PMOV-a')))
    W('\n\n')
open(os.path.join(base, 'ER_mapiranje_PMOV.md'), 'w', encoding='utf-8').write(o.getvalue())
print('-> ER_mapiranje_PMOV.md (%d redova)' % o.getvalue().count('\n'))
