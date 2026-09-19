# PMOV v2 – spisak ispravki posle revizije modela

Sve izmene su primenjene nad `PMOV_TV_stanica.vsdx`. Provera rasporeda i dalje
prijavljuje **0 preklapanja** oblika i linija (542 oblika, 435 linija).

## A. Otklonjene kontradikcije

| # | Šta je bilo | Šta je sada | Zašto |
|---|---|---|---|
| A1 | `OBUHVATA` (PROGRAMSKA CELINA → TERMIN EMITOVANJA) nacrtana kao **identifikujuća** (dupli romb), a TERMIN je jak entitet sa ključem `ŠIFRA TERMINA` | romb je **jednostruk** | identifikujuća veza sme imati samo slab entitet sa parcijalnim ključem na strani deteta |
| A2 | `SKLAPA` KLIJENT (1,N) — UGOVOR **(1,1)** | KLIJENT **(0,N)** — UGOVOR **(0,1)** | UGOVOR O NABAVCI je podtip UGOVORA i nasleđivao je obavezu da ima klijenta, iako preko `UGOVARA` ima dobavljača |
| A3 | `NAPLAĆUJE` UGOVOR **(1,N)** — FAKTURA (0,N) | UGOVOR **(0,N)** — FAKTURA **(0,1)** | nabavni ugovor ne izdaje izlaznu fakturu; faktura pripada najviše jednom ugovoru |
| A4 | `MONTIRAN U` SIROVI SNIMAK (0,N) — MEDIJSKI SADRŽAJ **(1,1)** | MEDIJSKI SADRŽAJ **(0,N)** | kupljeni i reklamni sadržaj nemaju sirove snimke, a montirana emisija ih ima više |
| A5 | `POKRIVENO` MEDIJSKI SADRŽAJ **(1,N)** — PRAVO **(1,1)** | MEDIJSKI SADRŽAJ **(0,N)** — PRAVO **(1,N)** | sopstvena vest nema zasebnu licencu; jedna licenca pokriva više sadržaja |
| A6 | `PLAĆENA` FAKTURA **(1,N)** — NALOG (1,1) | FAKTURA **(0,N)** | entitet ima atribut `STATUS PLAĆANJA`, dakle neplaćena faktura mora biti moguća |
| A7 | `UGOVARA` DOBAVLJAČ **(1,N)** — UGOVOR O NABAVCI (1,1) | DOBAVLJAČ **(0,N)** | registrovan dobavljač može biti bez ugovora |

## B. Ispravljene obrnute strane kardinalnosti

| Veza | Bilo | Sada |
|---|---|---|
| `PRIKAZUJE` EMITOVANJE REKLAME — REKLAMNI SADRŽAJ | (1,N) — (1,1) | **(1,1) — (0,N)** |
| `ODNOSI SE NA` POVRATNA INFO — EMISIJA | (0,N) — (0,1) | **(0,1) — (0,N)** |
| `REALIZOVAN` TERMIN — ZAPIS O EMITOVANJU | (1,N) — (1,1) | **(0,1) — (1,1)** |

## C. Opuštene prestroge minimalne kardinalnosti (1 → 0)

`RADI U` (ORG. JEDINICA), `IZAZIVA` (AKTIVNOST), `ZAKUPLJEN U` (TERMIN),
`MERENA` (EMISIJA), `UVRŠTEN U` (ZAHTEV ZA NABAVKU), `PONUĐENA` (PONUDA),
`BIRA` (PONUDA), `DOSTAVIO` (DOBAVLJAČ), `NARUČENO OD` (DOBAVLJAČ),
`PRAĆENA` (NARUDŽBENICA), `PRIMLJENO PO` (STAVKA NARUDŽBENICE),
`FAKTURISANA` (PRIJEMNICA), `PROIZVODI` (PROJEKAT).

Svaka od njih je ranije tvrdila da nešto mora postojati od prvog trenutka
(dobavljač bez ponude, narudžbenica pre isporuke, nova emisija bez merenja…).

## D. Strukturne izmene

- **`PODNOSI` (POVRATNA INFORMACIJA ↔ MERENJE GLEDANOSTI) je obrisana.** Veza nije
  imala uporište u DFD-u i naziv joj je bio besmislen u datom smeru.
- **`PLANIRANA` je premeštena sa ZAPIS O EMITOVANJU na TERMIN EMITOVANJA**
  (TERMIN (1,1) — EMISIJA (0,N)). Plan „koja emisija ide u koji termin" sada visi o
  terminu, a ZAPIS O EMITOVANJU beleži samo realizaciju. Time nestaje i redundantni
  trougao ZAPIS–EMISIJA–MEDIJSKI SADRŽAJ, pa veza `EMITUJE` više nije izvediva iz
  ostalih.
- **Dodata veza `TIČE SE`** REKLAMACIJA (1,N) — STAVKA NARUDŽBENICE (0,N): ranije se
  nije videlo šta se tačno reklamira, iako REKLAMACIJA ima `REKLAMIRANI IZNOS`.
- **`PROIZVODI`** sada dozvoljava da emisija nastane iz više projekata (npr. po epizodi).

## E. Jedinstveni nazivi veza

`SADRŽI` se javljalo 4 puta, `OBUHVATA` 2 puta. Novi nazivi:
`SADRŽI CELINE`, `SADRŽI STAVKE PLANA`, `SADRŽI STAVKE NARUDŽBINE`,
`SADRŽI STAVKE FAKTURE`, `PRIMLJENO PO`.

## F. Uklonjen skriveni strani ključ

`NABAVLJENI SADRŽAJ.IZVOR NABAVKE` → zamenjen sa `ZEMLJA POREKLA`. Dobavljač se
sada dobija putanjom NABAVLJENI SADRŽAJ → `NABAVLJEN PO` → UGOVOR O NABAVCI →
`UGOVARA` → DOBAVLJAČ, pa je atribut bio redundantan.

## G. Dopunjena PMOV notacija

- **Kompozitni atribut**: `KLIJENT.ADRESA` → ULICA I BROJ, GRAD, POŠTANSKI BROJ.
- **Višeznačni atributi** (dvostruka elipsa): `EMISIJA.ŽANR`, `KLIJENT.KONTAKT OSOBA`.
- **Totalnost specijalizacije**: dvostruka linija od nadtipa ka rombu **S** za totalne,
  jednostruka za parcijalne.
- **Disjunktnost**: slovo `d` (disjunktna) odnosno `o` (preklapajuća) u kružiću.

| Specijalizacija | Vrsta |
|---|---|
| ZAPOSLENI → UREDNIK, NOVINAR/REPORTER, SNIMATELJ, REFERENT | parcijalna, disjunktna |
| OPREMA → SNIMATELJSKA, STUDIJSKA I EMISIONA | parcijalna, disjunktna |
| MEDIJSKI SADRŽAJ → PRODUCIRANI, NABAVLJENI, REKLAMNI | totalna, disjunktna |
| UGOVOR → O OGLAŠAVANJU, O PRODAJI TV SADRŽAJA, O NABAVCI | totalna, disjunktna |
| KLIJENT → OGLAŠIVAČ, KUPAC SADRŽAJA | totalna, preklapajuća |
| DOBAVLJAČ → TV SADRŽAJA, OPREME I MATERIJALA | totalna, preklapajuća |

Legenda na dijagramu je proširena novim simbolima, a zatim naknadno uklonjena sa
crteža na zahtev (opis notacije ostaje u ovom dokumentu).

---

## Šta NIJE promenjeno i zašto

Ovo su svesno ostavljene stvari — treba ih znati odbraniti, ne sakriti:

1. **Pet atributa tipa „ko je uradio"** ostaju atributi, a ne veze:
   `ZAPIS O EMITOVANJU.OPERATER EMITOVANJA`, `PLAN NABAVKE.DONOSILAC PLANA`,
   `ODLUKA O IZBORU.DONOSILAC ODLUKE`, `NALOG ZA PLAĆANJE.ODOBRIO`,
   `PRIJEMNICA.PRIMIO (MAGACIONER)`.
   Razlog: entitet ZAPOSLENI je u gornjoj traci dijagrama i sva četiri njegova
   priključka su zauzeta; povezivanje bi zahtevalo linije preko celog crteža.
   Modelarski stav koji se može braniti: sistem beleži ime osobe upisano na
   dokumentu, a ne vodi referencu na kadrovsku evidenciju.
2. **`FAKTURA.SMER (ULAZNA/IZLAZNA)`** ostaje atribut umesto specijalizacije.
   Kontradikcija je uklonjena tako što su obe veze (`FAKTURISANA`, `NAPLAĆUJE`)
   sada opcione, pa ulazna faktura nema ugovor, a izlazna nema prijemnicu.
3. **Trougao `ANGAŽUJE` / `ZADUŽUJE` / `ZADUŽENA`** nije pretvoren u ternarnu vezu.
   Posledica: ne vidi se ko je zadužio koju opremu za koju aktivnost.
4. **Podtipovi bez sopstvenih veza** (npr. UGOVOR O OGLAŠAVANJU, KUPAC SADRŽAJA)
   zadržani su jer ih razlikuju sopstveni atributi, što je dovoljan razlog za podtip.
5. **DOZVOLA ZA EMITOVANJE / REGULATORNO TELO** i dalje nisu modelovani.
6. **PRODUCIRANI SADRŽAJ nema direktnu vezu ka PROJEKAT PRODUKCIJE** — veza
   `PROIZVODI` ide na EMISIJU, a sadržaj se dobija preko `ČINI`.
