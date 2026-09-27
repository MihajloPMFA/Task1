# TV stanica — 5 izveštaja u Power BI-u

Napravljeno na osnovu baze `Access_v3.accdb`, po ugledu na strukturu koju je koristila koleginica
(5 stranica, kartica sa KPI pokazateljima, grafikoni + tabela + slicer-i na svakoj strani).

---

## 1. Koji fajl da otvoriš

U folderu se nalaze **dva** fajla. Oba sadrže **iste izveštaje** — razlika je samo odakle vuku podatke.

| Fajl | Podaci | Kada ga koristiš |
|---|---|---|
| **`TV_stanica_Izvestaji.pbit`** | Ugrađeni u sam fajl | **Počni od ovoga.** Ne traži ništa spolja. |
| `TV_stanica_Izvestaji_ACCESS.pbit` | Čita uživo iz `.accdb` | Kad hoćeš da se izveštaji osvežavaju kad promeniš bazu. |

Otvaranje: dupli klik na fajl (otvara se u **Power BI Desktop**-u), pa **File → Save As → `.pbix`**
da dobiješ običan Power BI fajl za dalji rad.

> `.pbit` je Power BI *template*. Ponaša se kao `.pbix`, samo što pri otvaranju prvo napuni podatke.
> Power BI Desktop se skida besplatno sa microsoft.com ili iz Microsoft Store-a.

---

## 2. Da li moram da spajam Access sa Power BI-em?

**Ne moraš.** Ovo je bila i suština tvog pitanja, pa evo oba scenarija:

### Varijanta A — `TV_stanica_Izvestaji.pbit` (preporučeno)

**Ništa ne povezuješ.** Svih 1.671 red iz 29 tabela je već izvučen iz Accessa i zapakovan
unutar samog `.pbit` fajla (isti mehanizam koji Power BI koristi za „Enter data").

- Ne treba ti `.accdb` fajl na računaru
- Ne treba ti Access instaliran
- Ne treba ti nikakav drajver
- Radi na bilo kom računaru, odmah

Mana: ako promeniš nešto u Accessu, izveštaji se **neće** sami ažurirati.

### Varijanta B — `TV_stanica_Izvestaji_ACCESS.pbit`

Ovde se Power BI **stvarno povezuje** na Access bazu. Pri otvaranju te pita za putanju do `.accdb`
fajla (parametar `PutanjaDoBaze`) — upišeš npr. `C:\Baze\Access_v3.accdb` i klikneš **Load**.

Za ovo ti treba **Microsoft Access Database Engine** (ACE OLEDB drajver):
- Ako već imaš instaliran Microsoft Access → **imaš ga**, ništa ne radiš.
- Ako nemaš → skini „Microsoft Access Database Engine 2016 Redistributable" sa Microsoft sajta.
- **Bitno:** drajver i Power BI Desktop moraju biti iste arhitekture (64-bit uz 64-bit).
  Ovo je najčešći razlog greške „The 'Microsoft.ACE.OLEDB.12.0' provider is not registered".

Prednost: klikneš **Refresh** u Power BI-u i izveštaji pokupe sve izmene iz Accessa.

Ako se predomisliš, putanju posle menjaš u **Transform data → Manage Parameters**.

---

## 3. Šta je u izveštajima

Svaka stranica ima naslov, karticu sa 4 KPI pokazatelja, 4 grafikona, jednu tabelu i 2 slicer-a
(filtera) sa desne strane.

**1 · Program i gledanost** — `EMISIJA`, `MERENJE_EMISIJE`, `MERENJE_GLEDANOSTI`,
`TERMIN_EMITOVANJA`, `POVRATNA_INFO_GLEDALACA`
Prosečan rejting i share, ukupno gledalaca, broj emitovanja; kretanje rejtinga kroz vreme,
gledanost po žanru, rang emisija po rejtingu, matrica emisija × kvartal, prijave gledalaca.

**2 · Oglašavanje i prihod od reklama** — `OGLASIVAC`, `KLIJENT`, `REKLAMNI_SADRZAJ`,
`EMITOVANJE_REKLAME`, `REKLAMNI_BLOK`
Prihod od reklama, broj emitovanja spotova, budžeti oglašivača, iskorišćenost blokova;
prihod po branši, po statusu naplate, najveći oglašivači, prihod po satu emitovanja.

**3 · Finansije: ugovori i fakture** — `UGOVOR`, `STAVKA_UGOVORA`, `FAKTURA`,
`STAVKA_FAKTURE`, `NALOG_ZA_PLACANJE`
Vrednost ugovora, iznos faktura, nalozi za plaćanje; ugovori vs. fakture po kvartalu,
fakture po statusu plaćanja, najveći klijenti, pregled faktura sa osnovicom i PDV-om.

**4 · Ljudski resursi i produkcija** — `ZAPOSLENI`, `ORGANIZACIONA_JEDINICA`,
`ANGAZOVANJE_NA_AKTIVNOSTI`, `AKTIVNOST_PRODUKCIJE`, `PROJEKAT_PRODUKCIJE`, `TROSAK_PRODUKCIJE`
Broj zaposlenih, masa zarada, angažovani sati, trošak produkcije; sati po zaposlenom i po ulozi,
zaposleni po organizacionoj jedinici, matrica projekat × vrsta troška.

**5 · Oprema, servisiranje i nabavka** — `OPREMA`, `SERVISIRANJE_OPREME`, `ZADUZENJE_OPREME`,
`NARUDZBENICA`, `REKLAMACIJA`, `PONUDA_DOBAVLJACA`, `DOBAVLJAC`
Nabavna vrednost opreme, trošak servisa, broj servisiranja i reklamacija; servisiranja po opremi,
struktura po statusu, trošak servisa po mesecu, evidencija servisa, narudžbenice po dobavljaču.

---

## 4. Kako je model napravljen

- **30 tabela**: 28 iz Accessa + `Kalendar` (dimenzija datuma, 2026–2027) + `_Mere` (32 DAX mere).
- **29 veza**, od toga 28 aktivnih. Veza `TERMIN_EMITOVANJA[DATUM] → Kalendar[Datum]` je namerno
  ostavljena **neaktivna** — inače bi postojala dva puta od `EMISIJA` do `Kalendar`, što Power BI
  prijavljuje kao dvosmislenost.
- Kompozitni ključ `(SIFRA_PROJEKTA, RB_AKTIVNOSTI)` je spojen u jednu kolonu `KLJUC_AKTIVNOSTI`,
  jer Power BI ne podržava veze preko više kolona.
- Neka polja su namerno **denormalizovana** umesto povezana (`UGOVOR.NAZIV_KLIJENTA`,
  `FAKTURA.NAZIV_KLIJENTA`, `SERVISIRANJE_OPREME.SERVISER`, `ZADUZENJE_OPREME.ZADUZENI`),
  da bi svaka od 5 tema mogla da ima svoju aktivnu vezu ka `Kalendar`-u.
- Uz svaki datum dodate su kolone `Godina`, `Kvartal`, `Mesec`, `MesecBr`; `Mesec` je sortiran
  po `MesecBr` pa ide hronološki, a ne azbučno.

### Napomena o novčanim iznosima

Access tip **Currency** interno čuva vrednosti kao ceo broj pomnožen sa 10.000
(npr. `1917110000` = `191.711,00`). Pri izvozu su sve takve kolone podeljene sa 10.000,
tako da su iznosi u izveštajima **stvarni**, u dinarima.

Provera ispravnosti: za svaku fakturu važi `OSNOVICA + IZNOS_PDV = IZNOS_ZA_PLACANJE`,
uz stopu PDV-a od 20%.

---

## 5. Ako nešto ne radi

**`.pbit` se ne otvara / prijavljuje grešku pri učitavanju**
U folderu `csv/` su iste tabele kao `.csv` (UTF-8, separator `;`), sa već izračunatim kolonama.
U Power BI-u: **Get data → Text/CSV**, ili **Folder** pa učitaj sve odjednom. Veze i mere
tada praviš ručno — spisak je u odeljku 4 ovog dokumenta.

**Greška „provider is not registered" (samo varijanta B)**
Fali ACE OLEDB drajver ili je pogrešne arhitekture — vidi odeljak 2.

**Grafikon prikazuje isti broj u svim kategorijama**
Znači da slicer filtrira tabelu koja nije povezana sa merom. Proveri u
**Model view** da li je veza aktivna (puna linija) ili neaktivna (isprekidana).

---

*Izvorne skripte kojima su fajlovi generisani su u folderu `build/`.*
