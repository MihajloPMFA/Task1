# Bankomati i Menjačnice — web aplikacija za pronalaženje i ocenjivanje objekata

![PHP](https://img.shields.io/badge/PHP-8.2-777BB4)
![MariaDB](https://img.shields.io/badge/MariaDB-10.4-003545)
![PDO](https://img.shields.io/badge/DB%20sloj-PDO-4F5D95)
![Leaflet](https://img.shields.io/badge/mape-Leaflet%201.9.4-199900)

Web aplikacija za pretragu, prikaz na mapi i ocenjivanje **bankomata i menjačnica** u Srbiji. Korisnici pronalaze najbliže objekte prema svojoj lokaciji, filtriraju ih po tipu, gradu, banci, valuti i naknadi, dobijaju rutu do izabranog objekta, ostavljaju recenzije i ocene, čuvaju objekte i predlažu nove. Administratori kroz poseban panel odobravaju ili odbijaju korisničke zahteve, održavaju bazu objekata (uključujući radno vreme i valute), moderiraju recenzije i upravljaju korisnicima.

Projekat je rađen kao projektni rad iz predmeta **Web programiranje 1** i implementiran je u čistom PHP-u (bez framework-a), sa PDO pristupom MySQL/MariaDB bazi i dinamičkim osvežavanjem stranica preko AJAX-a (`XMLHttpRequest`), bez ijedne JS biblioteke osim Leaflet-a za mape.

---

## Sadržaj

- [Funkcionalnosti](#funkcionalnosti)
- [Tehnologije i okruženje](#tehnologije-i-okruženje)
- [Arhitektura](#arhitektura)
- [Struktura projekta](#struktura-projekta)
- [Model podataka](#model-podataka)
- [Instalacija i pokretanje](#instalacija-i-pokretanje)
- [Nalozi i prijava](#nalozi-i-prijava)
- [Tok obrade zahteva](#tok-obrade-zahteva)
- [Poznata ograničenja i moguća poboljšanja](#poznata-ograničenja-i-moguća-poboljšanja)
- [Autor](#autor)

---

## Funkcionalnosti

### Korisnički deo

- **Registracija i prijava** — validacija na klijentu i serveru, lozinke hešovane sa `password_hash()` (bcrypt), opcija **„Zapamti me" (30 dana)** preko HMAC-potpisanog kolačića.
- **Početna strana** — traži lokaciju korisnika (`navigator.geolocation`) i prikazuje najbliže bankomate i menjačnice, rangirane po vazdušnoj udaljenosti (Haversine formula izračunata u JavaScript-u).
- **Interaktivna mapa** (Leaflet + OpenStreetMap):
  - markeri svih aktivnih objekata sa popup-om i statusom „otvoreno / zatvoreno" prema radnom vremenu za tekući dan,
  - filtriranje po pretrazi (naziv, adresa, grad), tipu, gradu, banci, valuti i opciji *bez naknade*,
  - sortiranje po nazivu ili prosečnoj oceni,
  - **izračunavanje rute** do objekta (Leaflet Routing Machine + OSRM) u tri režima: automobil, bicikl, pešice, sa prikazom dužine i trajanja.
- **Stranica objekta** — svi podaci o objektu, galerija slika, mini-mapa, radno vreme po danima, podržane valute (za menjačnice), informacija o naknadi, link za navigaciju:
  - **recenzije** — dodavanje i izmena sopstvene recenzije (ocena 1–5 + komentar, jedna recenzija po objektu),
  - **označavanje recenzije kao korisne**,
  - **čuvanje objekta** (lajk/„Sačuvaj"),
  - **prijava da objekat ne postoji** — objekat prelazi u status `prijavljen` i kreira se zahtev za uklanjanje,
  - automatsko beleženje pregleda u istoriju.
- **Predlaganje novog objekta** — forma sa izborom tačne lokacije klikom na mapu, unosom radnog vremena po danima (uključujući *neprekidno 24h* i *zatvoreno*) i liste valuta za menjačnice; objekat se upisuje sa statusom `na_cekanju` i kreira se zahtev tipa `dodavanje`.
- **Moj profil** — pet sekcija: sačuvani objekti, istorija pregleda, moje recenzije, moji podaci (izmena imena i prezimena) i podešavanja (promena lozinke, brisanje naloga).

### Administratorski deo

- **Dashboard** — statistike (broj aktivnih objekata, bankomata, menjačnica, objekata na čekanju i prijavljenih, zahteva na čekanju, korisnika, recenzija) i pregledna mapa svih objekata sa bojom markera po statusu.
- **Objekti** — lista sa filtrima po statusu i tipu, detalji objekta, ručno dodavanje i izmena objekta (uz izbor lokacije na mapi), promena statusa, uređivanje radnog vremena i dodavanje/brisanje valuta; uključena je i administratorska mapa sa istim filtrima kao korisnička.
- **Zahtevi** — pregled zahteva (`dodavanje`, `izmena`, `uklanjanje`) sa filtrom po statusu, prikaz predloženih podataka (JSON), te **odobravanje ili odbijanje sa komentarom**; obrada zahteva u transakciji menja status objekta i kreira notifikaciju podnosiocu.
- **Recenzije** — pregled svih recenzija sa filtrom po objektu i tekstualnom pretragom (po korisniku, komentaru ili nazivu objekta) i brisanje neprikladnih recenzija.
- **Korisnici** — pretraga i filtriranje po roli, broj recenzija i zahteva po korisniku, aktivacija/deaktivacija naloga i brisanje korisnika (sa zaštitom od brisanja administratorskih naloga i sopstvenog naloga).

---

## Tehnologije i okruženje

| | |
|---|---|
| Serverski jezik | PHP 8.2 (bez framework-a), sesije (`$_SESSION`) |
| Pristup bazi | PDO (`pdo_mysql`), isključivo pripremljeni upiti |
| Baza podataka | MySQL / MariaDB 10.4 (InnoDB, `utf8mb4_unicode_ci`) |
| Okruženje za razvoj | XAMPP (Apache + MariaDB + PHP) i phpMyAdmin 5.2 |
| Frontend | HTML5, CSS3 (ručno pisan, responzivan — hamburger meni na ≤700px), vanilla JavaScript + AJAX (`XMLHttpRequest`) |
| Mape i rute | [Leaflet](https://leafletjs.com/) 1.9.4, Leaflet Routing Machine 3.2.12, OpenStreetMap tile-ovi, OSRM servis za rute |
| Geolokacija | HTML5 Geolocation API (`getCurrentPosition`, `watchPosition`) |
| Veličina koda | 26 PHP fajlova (~5.000 linija) + ~3.000 linija CSS-a, 12 stranica/modula |

Aplikacija ne koristi Composer ni build alate — dovoljno je kopirati fajlove na server sa PHP-om i uvesti bazu. Leaflet se učitava sa CDN-a, pa je za rad mape i ruta potrebna internet konekcija.

---

## Arhitektura

Aplikacija je organizovana **modularno**: svaka stranica je poseban folder sa tri fajla, uvek po istom principu.

```
<modul>/
├── index.php   # kontroler + prikaz (HTML/JS) + AJAX endpoint-i
├── db.php      # klasa sa SQL upitima, nasleđuje DBKonekcija
└── style.css   # stilovi te stranice
```

- **Sloj pristupa podacima** — `zajednicki/db_konekcija.php` sadrži klasu `DBKonekcija` koja otvara PDO konekciju i postavlja `ERRMODE_EXCEPTION`. Svaki modul definiše svoju klasu koja je **nasleđuje** (`AuthDB`, `MapaDB`, `ObjekatDB`, `ProfilDB`, `NoviZahtevDB`, `HeroPageDB`, `AdminPocetakDB`, `AdminObjektiDB`, `AdminZahteviDB`, `AdminRecenzijeDB`, `AdminKorisniciDB`) i drži isključivo upite — u `index.php` fajlovima nema SQL-a.
- **AJAX endpoint-i u istom fajlu** — na početku svakog `index.php` nalazi se blok koji, ako je prisutan određeni GET parametar (npr. `?objekti`, `?recenzije`, `?approve`), vraća JSON ili kratak `OK` / `ERROR: ...` odgovor i prekida izvršavanje. Stranice se tako osvežavaju bez ponovnog učitavanja.
- **Autorizacija** — svaka strana na početku proverava sesiju; administratorske strane dodatno zahtevaju `$_SESSION['role'] === 'admin'`, u suprotnom preusmeravaju na prijavu. Nakon prijave korisnik se rutira na korisnički, a administrator na admin deo.
- **Zajedničke komponente** — `korisnik/zajednicki/navbar.php` i `admin/zajednicki/navbar.php` (navigacija sa responzivnim sidebar-om).
- **Integritet podataka** — strani ključevi sa `ON DELETE CASCADE`, `UNIQUE` ograničenja (jedna recenzija po korisniku i objektu, jedan lajk, jedno radno vreme po danu), **transakcije** za sve operacije koje menjaju više tabela (predlaganje objekta, obrada zahteva, izmena radnog vremena, brisanje naloga) i **trigeri** koji automatski preračunavaju prosečnu ocenu objekta.

---

## Struktura projekta

```
.
├── zajednicki/
│   └── db_konekcija.php          # klasa DBKonekcija (PDO) — nasleđuju je svi moduli
├── korisnik/
│   ├── auth/                     # prijava, registracija, odjava, „Zapamti me"
│   ├── pocetak/                  # početna strana sa najbližim objektima
│   ├── mapa/                     # mapa sa filtrima, pretragom i rutiranjem
│   ├── objekat/                  # detalji objekta, recenzije, lajkovi, prijava
│   ├── novi_zahtev/              # forma za predlaganje novog objekta
│   ├── profil/                   # sačuvano, istorija, recenzije, podešavanja
│   └── zajednicki/navbar.php     # korisnička navigacija
├── admin/
│   ├── pocetak/                  # dashboard sa statistikama i mapom
│   ├── objekti/                  # lista, filtri, mapa, status, radno vreme, valute
│   │   └── dodaj/                # forma za dodavanje i izmenu objekta
│   ├── zahtevi/                  # obrada zahteva (odobri / odbij)
│   ├── recenzije/                # moderacija recenzija
│   ├── korisnici/                # upravljanje korisnicima
│   └── zajednicki/navbar.php     # admin navigacija
└── projekatwp1.sql               # kompletan dump baze (struktura + demo podaci)
```

---

## Model podataka

Baza `projekatwp1` sadrži deset tabela:

| Tabela | Opis |
|---|---|
| `korisnici` | Korisnici i administratori (`role` = `korisnik` \| `admin`), bcrypt heš lozinke, `isActive`, `isEmailVerified`, `deactivatedAt`; e-mail je jedinstven |
| `objekat` | Bankomati i menjačnice: naziv, opis, država, grad, adresa, geografske koordinate, `type` (`bankomat` \| `menjacnica`), `banka`, `naknadaInfo`, telefon, sajt, `averageRating`, `status` (`aktivan`, `na_cekanju`, `odbijen`, `prijavljen`, `uklonjen`), kreirao/odobrio korisnik |
| `radnovreme` | Radno vreme po danu nedelje (`openTime`, `closeTime`, `isClosed`, `is24h`); jedinstveno po objektu i danu |
| `valute` | Valute koje menjačnica podržava (`kod`, `tip` = `kupovina` \| `prodaja` \| `oba`) |
| `recenzije` | Ocena (1–5) i komentar; jedinstveno po paru korisnik–objekat |
| `korisnerecenzije` | Oznake „ova recenzija mi je korisna" |
| `svidjanja` | Sačuvani (lajkovani) objekti po korisniku |
| `istorijapregleda` | Istorija pregleda objekata |
| `zahtevi` | Zahtevi korisnika: `tip` (`dodavanje`, `izmena`, `uklanjanje`), `status` (`na_cekanju`, `odobren`, `odbijen`), `predlozeniPodaci` (JSON, uz `json_valid` proveru), komentar administratora, vreme obrade |
| `notifikacije` | Obaveštenja korisniku o obradi zahteva (naslov, tekst, tip, `isRead`, pošiljalac) |

**Trigeri** — tri trigera nad tabelom `recenzije` (`AFTER INSERT`, `AFTER UPDATE`, `AFTER DELETE`) automatski preračunavaju `objekat.averageRating` kao zaokruženu prosečnu ocenu, tako da aplikacija nikada ne mora da je ažurira ručno.

Dump sadrži i **demo podatke**: 8 korisnika (2 administratora), 14 objekata u 5 gradova, radno vreme za sve objekte, 24 recenzije, valute, lajkovi, istorija pregleda, 6 zahteva u različitim statusima i notifikacije.

---

## Instalacija i pokretanje

### Potrebno

- PHP **8.0+** sa uključenim `pdo_mysql` ekstenzijom
- MySQL **5.7+** ili MariaDB **10.4+**
- Apache (ili bilo koji web server sa PHP-om) — najlakše preko **XAMPP**-a
- Internet konekcija (Leaflet i OSM tile-ovi se učitavaju sa CDN-a)

### Koraci (XAMPP na Windows-u)

1. **Kopirati projekat** u `htdocs`, npr. u `C:\xampp\htdocs\projekat`.
2. **Pokrenuti Apache i MySQL** iz XAMPP Control Panel-a.
3. **Uvesti bazu** — otvoriti `http://localhost/phpmyadmin`, izabrati *Import* i uvesti `projekatwp1.sql`. Skripta sama kreira bazu `projekatwp1` sa strukturom, trigerima i demo podacima.
4. **Proveriti pristupne podatke** u `zajednicki/db_konekcija.php` — podrazumevano je XAMPP-ova konfiguracija:

   ```php
   const DB_HOST = 'localhost';
   const DB_NAME = 'projekatwp1';
   const DB_USER = 'root';
   const DB_PASS = '';
   ```

   Ako vaš MySQL ima lozinku ili drugi port, promeniti ove konstante.
5. **Otvoriti aplikaciju** na adresi:

   ```
   http://localhost/projekat/korisnik/auth/index.php
   ```

   > Projekat nema `index.php` u korenu, pa je ulazna tačka strana za prijavu. Po želji se u koren može dodati fajl koji preusmerava na nju.

### Napomena za Linux/macOS

Kod referencira tabele sa velikim početnim slovom (`Korisnici`, `Objekat`, `RadnoVreme`, …), dok ih dump kreira malim slovima. Na Windows-u to radi jer MySQL tamo ne razlikuje veličinu slova u nazivima tabela, ali na Linux-u i macOS-u podrazumevano razlikuje, pa upiti prijave grešku „table doesn't exist". Rešenja: uvesti bazu na sistemu gde nazivi nisu osetljivi na veličinu slova, postaviti `lower_case_table_names=1` pri inicijalizaciji MySQL servera, ili uskladiti nazive u kodu sa nazivima u bazi.

---

## Nalozi i prijava

Demo nalozi iz dump-a (kolona `role` određuje gde se korisnik preusmerava posle prijave):

| E-mail | Rola |
|---|---|
| `admin@example.com` | administrator |
| `admin2@example.com` | administrator |
| `petar@example.com`, `milica@example.com`, `stefan@example.com`, `jovana@example.com` | korisnik |

Lozinke demo naloga čuvaju se kao bcrypt heš i **njihov tekst nije deo repozitorijuma**. Da biste se prijavili kao administrator, postavite novu lozinku — heš se generiše u PHP-u:

```bash
php -r "echo password_hash('vasa_lozinka', PASSWORD_BCRYPT), PHP_EOL;"
```

pa dobijeni heš upišite u bazu:

```sql
UPDATE korisnici SET passwordHash = '<dobijeni_hes>' WHERE email = 'admin@example.com';
```

Novi **korisnički** nalog možete napraviti i kroz samu aplikaciju (link *Registrujte se* na strani za prijavu) — registracija uvek dodeljuje rolu `korisnik`, pa se administratorska rola postavlja direktno u bazi.

---

## Tok obrade zahteva

```
Korisnik predloži objekat            Korisnik prijavi da objekat ne postoji
        │                                          │
        ▼                                          ▼
objekat → status 'na_cekanju'            objekat → status 'prijavljen'
zahtev  → tip 'dodavanje'                zahtev  → tip 'uklanjanje'
        │                                          │
        └──────────────► Admin panel → Zahtevi ◄───┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
            ODOBRENO                         ODBIJENO
   dodavanje → 'aktivan'            dodavanje → 'odbijen'
   izmena    → primeni JSON         uklanjanje → vrati 'aktivan'
   uklanjanje→ 'uklonjen'                      │
                 │                             │
                 └──── zahtev: status, admin, komentar, vreme obrade
                                   +
                       notifikacija podnosiocu zahteva
```

Cela obrada izvršava se u transakciji, a kod odobravanja izmene primenjuju se samo polja sa bele liste dozvoljenih kolona.

---

## Poznata ograničenja i moguća poboljšanja

- **Akcije koje menjaju podatke izvršavaju se preko GET zahteva** (npr. `?dodaj_recenziju`, `?toggle_svidjanje`, `?approve`, `?add`). Funkcionalno je ispravno, ali bi trebalo prebaciti na POST i dodati **CSRF tokene**, jer je u ovom obliku moguće izvršiti akciju običnim otvaranjem URL-a.
- **Kredencijali baze su tvrdo upisani** u `zajednicki/db_konekcija.php`; bolje ih je izmestiti u konfiguracioni fajl izvan verzionisanja ili u promenljive okruženja.
- **Tajni ključ za „Zapamti me" kolačić je konstanta u kodu** (`USER_RM_SECRET`), kolačić nema `Secure` zastavicu i ne vezuje se za uređaj ni sesiju; robusnije rešenje je token po uređaju sačuvan u bazi, sa mogućnošću povlačenja.
- **Nema upload-a slika** — tabela `slike` se samo čita, a putanje iz demo podataka (`/uploads/...`) ne postoje u repozitorijumu, pa se galerije prikazuju bez slika dok se fajlovi ne dodaju. Formular za administratorski upload slika je logičan sledeći korak.
- **Notifikacije se upisuju, ali se ne prikazuju** — tabela `notifikacije` se popunjava pri odobravanju zahteva, dok korisnički interfejs još ne sadrži stranu ili brojač obaveštenja.
- **Zahtev tipa `izmena` može se samo obraditi, ne i podneti** iz korisničkog dela — administratorska logika i struktura baze ga podržavaju (i postoji u demo podacima), ali forma za predlaganje izmene postojećeg objekta nije implementirana.
- **Polje `isEmailVerified` se ne koristi** — nema slanja verifikacionog e-maila, kao ni funkcije „zaboravljena lozinka".
- **Osetljivost naziva tabela na veličinu slova** — videti napomenu u sekciji o instalaciji.
- **Stilovi se dupliraju** — svaki modul ima svoj `style.css` sa ponovljenim pravilima; izdvajanje zajedničke osnove u jedan fajl smanjilo bi količinu koda.

---

## Autor

Projektni rad iz predmeta **Web programiranje 1**.
