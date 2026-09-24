# Projekat iz Dizajniranja softvera — Upravljanje coworking prostorom

![.NET](https://img.shields.io/badge/.NET-8.0-512BD4)
![C#](https://img.shields.io/badge/language-C%23-239120)
![UI](https://img.shields.io/badge/UI-Windows%20Forms-0078D4)
![DB](https://img.shields.io/badge/DB-SQL%20Server%20%7C%20PostgreSQL-CC2927)

Desktop (Windows Forms) aplikacija za administraciju **coworking prostora**: vođenje evidencije korisnika i tipova članstva, lokacija i resursa (radna mesta, sale za sastanke, privatne kancelarije), kao i kreiranje i validaciju rezervacija. Projekat je rađen kao seminarski/projektni rad iz predmeta **Dizajniranje softvera**, pa je akcenat, pored funkcionalnosti, na primeni **projektnih obrazaca (design patterns)** i na slojevitoj arhitekturi u kojoj je pristup bazi potpuno izolovan od korisničkog interfejsa.

Aplikacija radi nad **dve različite baze podataka** (Microsoft SQL Server i PostgreSQL) — konkretna baza se bira isključivo kroz konfiguracioni fajl, bez ikakve promene koda.

---

## Sadržaj

- [Funkcionalnosti](#funkcionalnosti)
- [Tehnologije i okruženje](#tehnologije-i-okruženje)
- [Arhitektura i primenjeni projektni obrasci](#arhitektura-i-primenjeni-projektni-obrasci)
- [Struktura projekta](#struktura-projekta)
- [Model podataka](#model-podataka)
- [Baza podataka — priprema](#baza-podataka--priprema)
- [Konfiguracija (`Config.json`)](#konfiguracija-configjson)
- [Pokretanje aplikacije](#pokretanje-aplikacije)
- [Prijava na sistem](#prijava-na-sistem)
- [Mesečni CSV izveštaji](#mesečni-csv-izveštaji)
- [Poznata ograničenja i moguća poboljšanja](#poznata-ograničenja-i-moguća-poboljšanja)
- [Autor](#autor)

---

## Funkcionalnosti

- **Prijava administratora** (`LoginForm`) i registracija novog administratora (`SignupForm`); lozinke se čuvaju kao **SHA-256** heš.
- **CRUD nad svim entitetima** kroz jedinstven glavni prozor sa menijem:
  - *Korisnici* — podaci o korisniku, tip članstva, period članstva, status naloga, preostali broj sati za rezervacije,
  - *Lokacije* — adresa, grad, radno vreme, maksimalan broj korisnika,
  - *Tipovi članstva* — naziv paketa, cena, trajanje, mesečni limit sati, dozvola za korišćenje sala,
  - *Resursi* → *Radna mesta*, *Sale*, *Kancelarije* — sa specifičnim atributima (kapacitet, broj računara, projektor, TV, tabla, oprema za online sastanke…),
  - *Rezervacije* — korisnik, resurs, vreme početka i završetka, status.
- **Uređivanje direktno u tabeli** (`DataGridView`) uz potvrdu izmene, brisanje tasterom `Delete`, odustajanje tasterom `Esc`.
- **Pretraga** po svim relevantnim kolonama za svaku od evidencija (`selectBySearch`).
- **Validacija rezervacije kroz lanac pravila** (Chain of Responsibility) — rezervacija se upisuje samo ako prođe sve provere:
  1. `AvailabilityHandler` — resurs nije već zauzet u traženom intervalu i nije prekoračen maksimalan broj korisnika na lokaciji,
  2. `WorkingHoursHandler` — interval rezervacije je unutar radnog vremena lokacije,
  3. `MembershipHoursHandler` — korisnik ima dovoljno preostalih sati i pravo na tip resursa (npr. sale za sastanke), nakon čega se preostali sati umanjuju.
- **Automatsko osvežavanje prikaza** — svaki repozitorijum nakon izmene obaveštava pretplaćene kontrole (Observer), pa se svi otvoreni ekrani osvežavaju sami; dodatno periodično osvežavanje radi `BasicDelayNotifier`.
- **Periodično generisanje mesečnih CSV izveštaja** o iskorišćenosti po korisniku i po resursu.

---

## Tehnologije i okruženje

| | |
|---|---|
| Jezik | C# (`nullable` i `implicit usings` uključeni) |
| Platforma | .NET 8 — `net8.0-windows` (**aplikacija radi samo na Windows-u**) |
| Korisnički interfejs | Windows Forms (`UseWindowsForms`) |
| Razvojno okruženje | Visual Studio 2022 (v17.14) — workload *.NET desktop development* |
| Baze podataka | Microsoft SQL Server i PostgreSQL |
| NuGet paketi | `Microsoft.Data.SqlClient` 6.1.4, `Npgsql` 10.0.1 |
| Veličina koda | ~8.200 linija u 83 `.cs` fajla |

Za pokretanje je dovoljan .NET 8 SDK (ili Visual Studio 2022 koji ga sadrži) i pristup jednoj od dve podržane baze.

---

## Arhitektura i primenjeni projektni obrasci

Arhitektura je podeljena na tri sloja: **GUI** (Windows Forms), **Back** (poslovna logika i pristup podacima) i **baza podataka** (tabele + uskladištene procedure). GUI nikada ne formira SQL i ne zna koja se baza koristi — komunicira isključivo sa `Back` fasadom.

```
GUI (Forms / UserControls)
        │  Back fasada  +  Observer (automatsko osvežavanje)
        ▼
Repozitorijumi  ──►  iDBadapter  ──►  MSSQLadapter / PostgresSQLadapter
        │                                      │
Chain of Responsibility                 Singleton konekcije
(validacija rezervacija)                       │
                                      Builder + Factory (connection string)
                                               ▼
                                   SQL Server  /  PostgreSQL
```

| Obrazac | Realizacija u kodu |
|---|---|
| **Singleton** | `Back/Config/Config.cs` (konfiguracija), `Back/KonekcijeKaBazama/MSSQLsinglton.cs`, `Back/KonekcijeKaBazama/PostgreSQLsinglton.cs` (konekcije), `UpisUCSV/CSVTimer.cs` (tajmer izveštaja) |
| **Adapter** | `Back/Adapters/iDBadapter.cs` sa implementacijama `MSSQLadapter` i `PostgresSQLadapter` — jedinstven interfejs `fetch` / `exec` / `callProcedure` nad dva različita provajdera |
| **Factory** | `Back/Adapters/AdapterFactory.cs` (bira adapter po `dbType`), `Back/Config/ConnectionStringFactory.cs`, `Back/Notifiers/NotifierFactory.cs` |
| **Builder** | `Back/Config/PostgresConnectionStringBuilder.cs` i `Back/Config/SQLServerStringBuilder.cs` — fluentno građenje i validacija connection string-a |
| **Repository** | `Back/Repositories/iRepository<T>` i osam repozitorijuma (`UserRepository`, `ReservationRepository`, `LocationRepository`, `SubscriptionRepository`, `SalaRepository`, `KancelarijaRepository`, `RadnoMestoRepository`, `AdminRepository`) |
| **Facade** | `Back/Back.cs` — jedna tačka pristupa svim repozitorijumima (`b.Korisnik`, `b.Rezervacija`, `b.Lokacija`, …) |
| **Observer** | `Back/Observer/ObserverPublisher.cs` i `iObserverSubscriber.cs`; repozitorijumi pozivaju `notify()` nakon izmene, a `UserControl`-i se pretplaćuju i osvežavaju prikaz (obaveštenje se prosleđuje preko `SynchronizationContext`, tj. bezbedno za UI nit) |
| **Chain of Responsibility** | `ChainOfResponsibilities/` — `IHandler`, `BaseHandler`, `AvailabilityHandler` → `WorkingHoursHandler` → `MembershipHoursHandler` |
| **Strategy / apstrakcija notifikacija** | `Back/Notifiers/INotifier.cs` sa implementacijama `PostgresNotifier` (PostgreSQL `LISTEN/NOTIFY`), `SqlServerNotifier` (`SqlDependency`, zahteva Service Broker) i `BasicDelayNotifier` (periodično osvežavanje na 15 s) |

---

## Struktura projekta

```
.
├── Projekat/
│   ├── Projekat.sln                  # Visual Studio solution
│   ├── Config.json                   # konfiguracija (kopija na nivou solution-a)
│   └── Projekat/
│       ├── Projekat.csproj           # net8.0-windows, WinForms, NuGet reference
│       ├── Config.json               # konfiguracija koja se kopira u izlazni direktorijum
│       ├── Back/
│       │   ├── Back.cs               # fasada + Observer
│       │   ├── Adapters/             # iDBadapter, MSSQLadapter, PostgresSQLadapter, AdapterFactory
│       │   ├── Config/               # Config (singleton), ConnectionStringFactory, builder-i
│       │   ├── KonekcijeKaBazama/    # singleton konekcije ka SQL Server-u i PostgreSQL-u
│       │   ├── Models/               # domenski model (Model, Korisnik, Resurs, Rezervacija…)
│       │   ├── Notifiers/            # INotifier + implementacije
│       │   ├── Observer/             # ObserverPublisher, iObserverSubscriber
│       │   └── Repositories/         # iRepository<T> + repozitorijumi
│       ├── ChainOfResponsibilities/  # validacija rezervacija
│       ├── GUI/
│       │   ├── Program.cs            # ulazna tačka aplikacije
│       │   ├── Form1.cs              # glavni prozor sa menijem
│       │   ├── Login/                # LoginForm, SignupForm
│       │   ├── Korisnik/             # KorisniciControl, AddUserForm
│       │   ├── Lokacija/             # LokacijeControl, AddLokacija
│       │   ├── Clanstvo/             # TipoviClanstvaControl, AddClanstvo
│       │   ├── RadnoMesto/           # RadnaMestaControl, AddRadnoMesto
│       │   ├── Sala/                 # SaleControl, AddSale
│       │   ├── PrivatneKancelarije/  # KancelarijeControl, AddKancelarije
│       │   └── Rezervacija/          # RezervacijeControl, AddRezervacije
│       ├── UpisUCSV/                 # CSVTimer (singleton) i Upis (generisanje izveštaja)
│       └── Properties/               # resursi
├── BAZA_TSQL_7_3_2026.sql            # najnovija T-SQL skripta (tabele, prikazi, procedure)
├── ProjekatBazaV2.sql                # starija verzija skripte (sadrži i triger BrisanjeClanstva)
└── BAZA_TSQL.sql                     # prva verzija skripte
```

---

## Model podataka

Svi domenski objekti nasleđuju apstraktnu klasu `Model` (nosi `id` i konverziju u `DataRow`):

- **`Korisnik`** — ime, prezime, e-mail, telefon, tip članstva (`Clanstvo`), datum početka i isteka članstva, status naloga, preostali broj sati za rezervaciju.
- **`Clanstvo`** — naziv paketa, cena, trajanje, maksimalan broj sati mesečno, dozvola za korišćenje sala za sastanke.
- **`Lokacija`** — naziv, adresa, grad, radno vreme (format `HH:mm-HH:mm`), maksimalan broj korisnika.
- **`Resurs`** (apstraktan: naziv, tip, opis, `Lokacija`) → **`RadnoMesto`**, **`Sala`**, **`PrivatnaKancelarija`**.
- **`Rezervacija`** — korisnik, resurs, datum i vreme početka/završetka, status (`aktivna`, …).
- **`Admin`** — korisničko ime i SHA-256 heš lozinke.

Mapiranje `DataRow` → model radi se statičkim `FromDataRow` metodama, uz nazive kolona iz baze (npr. `"ID korisnika"`, `"Datum pocetka clanstva"`).

---

## Baza podataka — priprema

Nazivi tabela i kolona sadrže razmake i dijakritički „očišćene“ srpske nazive, pa se svuda koriste **dvostruki navodnici** kao ograničivači identifikatora; zbog toga SQL Server konekcija pri otvaranju postavlja `SET QUOTED_IDENTIFIER ON` (vidi `MSSQLsinglton`).

### Microsoft SQL Server

1. Otvoriti **`BAZA_TSQL_7_3_2026.sql`** (najnovija skripta) u SQL Server Management Studio-u i izvršiti je. Skripta kreira:
   - bazu **`DSProjekat`**,
   - tabele: `Korisnici`, `Tipovi clanstva`, `Lokacije`, `Resursi`, `Radna mesta`, `Sale`, `Privatne kancelarije`, `Rezervacije`, `Admins`,
   - prikaze: `AllPrimaryKeys`, `AllColumnsView`,
   - uskladištene procedure koje aplikacija poziva: `insertIntoKorisnici`, `insertIntoLokacije`, `insertIntoTipoviClanstva`, `insertIntoRadnaMesta`, `insertIntoSale`, `insertIntoPrivatenKancelarije`, `insertIntoRezervacije` i odgovarajuće `Update...` procedure.
   - *Napomena:* skripta sadrži apsolutne putanje do `.mdf`/`.ldf` fajlova i kreiranje login-a — prilagoditi ih svojoj instanci pre izvršavanja.
2. Starija skripta `ProjekatBazaV2.sql` dodatno sadrži triger **`BrisanjeClanstva`** (`INSTEAD OF DELETE` nad `Tipovi clanstva`) koji korisnicima obrisanog paketa postavlja `Tip clanstva` na `NULL` i upisuje datum isteka — ako se želi to ponašanje, triger treba preneti u aktuelnu bazu.

### PostgreSQL

Aplikacija u potpunosti podržava PostgreSQL (`PostgresSQLadapter`, `Npgsql`, `CALL "procedura"(...)`), ali **DDL skripta za PostgreSQL nije deo repozitorijuma** — priložene skripte su T-SQL. Za rad nad PostgreSQL-om potrebno je kreirati istu strukturu (tabele sa identičnim nazivima kolona i procedure istih imena i potpisa) ili u `Config.json` izabrati `"dbType": "SqlServer"`.

> Metoda `Back.refreshDataBase()` poziva procedure `checkKorisnici` i `checkRezervacije` (održavanje statusa članstva i rezervacija). One nisu obuhvaćene priloženim skriptama; ako ne postoje u bazi, poziv se tiho ignoriše i ostatak aplikacije radi normalno.

---

## Konfiguracija (`Config.json`)

Konfiguracija se čita iz fajla `Config.json` **iz radnog direktorijuma aplikacije** (fajl je u `.csproj` označen sa `CopyToOutputDirectory=PreserveNewest`, pa se kopira pored `.exe`). Pri zatvaranju aplikacije konfiguracija se ponovo upisuje u isti fajl (pamti se, između ostalog, vreme poslednjeg generisanja CSV izveštaja).

```json
{
  "name": "Projekat",
  "dbString": "Host=localhost;Port=5432;Username=<korisnik>;Password=<lozinka>;Database=DSProjekat;",
  "dbType": "Postgres",
  "dt": 1,
  "lastCSVupdate": "2026-01-01T12:00:00",
  "databases": {
    "postgres": {
      "host": "localhost",
      "port": 5432,
      "username": "<korisnik>",
      "password": "<lozinka>",
      "database": "DSProjekat",
      "quoteIdentifiers": false,
      "useSsl": false
    },
    "sqlserver": {
      "host": "localhost",
      "port": 1433,
      "username": "<korisnik>",
      "password": "<lozinka>",
      "database": "DSProjekat",
      "encrypt": true,
      "integratedSecurity": false
    }
  }
}
```

| Polje | Značenje |
|---|---|
| `name` | Naslov glavnog prozora aplikacije |
| `dbType` | **Izbor baze: `Postgres` ili `SqlServer`** — jedina promena potrebna za prelazak sa jedne baze na drugu |
| `databases.postgres` / `databases.sqlserver` | Parametri iz kojih builder-i grade i validiraju connection string |
| `quoteIdentifiers` | Da li se korisničko ime i naziv baze navode pod dvostrukim navodnicima (PostgreSQL) |
| `integratedSecurity` | Windows autentifikacija za SQL Server (tada `username`/`password` nisu obavezni) |
| `dbString` | „Sirov“ connection string; koriste ga `PostgresNotifier`/`SqlServerNotifier` |
| `dt` | Interval generisanja CSV izveštaja (u kodu: `dt * 36.000.000 ms`, tj. `dt = 1` ≈ 10 h) |
| `lastCSVupdate` | Vreme poslednjeg generisanja izveštaja (aplikacija ga sama ažurira) |

> **Napomena o bezbednosti:** `Config.json` sadrži pristupne podatke za bazu u čistom tekstu. Preporučuje se da se lokalna kopija sa stvarnim kredencijalima **ne commit-uje** (dodati `Config.json` u `.gitignore`), a da se u repozitorijumu drži samo primer (`Config.example.json`) sa popunjenim placeholder-ima.

---

## Pokretanje aplikacije

### Visual Studio 2022

1. Instalirati Visual Studio 2022 sa workload-om **.NET desktop development** (uključuje .NET 8 SDK).
2. Otvoriti `Projekat/Projekat.sln`.
3. Pripremiti bazu (videti [Baza podataka — priprema](#baza-podataka--priprema)) i podesiti `Projekat/Projekat/Config.json`.
4. Pokrenuti sa `F5` (Debug) ili `Ctrl+F5` (bez debagovanja). NuGet paketi se povlače automatski pri prvom build-u.

### .NET CLI (Windows)

```bash
# iz korena repozitorijuma
dotnet restore Projekat/Projekat.sln
dotnet build   Projekat/Projekat.sln -c Release
dotnet run --project Projekat/Projekat/Projekat.csproj
```

Objavljivanje samostalne verzije:

```bash
dotnet publish Projekat/Projekat/Projekat.csproj -c Release -r win-x64 --self-contained false -o publish
```

Pored dobijenog `.exe` fajla mora se nalaziti i `Config.json`.

> Projekat cilja `net8.0-windows` i koristi Windows Forms, pa se **ne može pokrenuti na Linux-u ili macOS-u** (build i pokretanje zahtevaju Windows).

---

## Prijava na sistem

Aplikacija se pokreće ekranom za prijavu (`LoginForm`). Nalozi se nalaze u tabeli `Admins`, a lozinka se proverava kao **SHA-256** heš (heksadecimalni zapis velikim slovima).

Novi administrator se dodaje iz glavnog prozora, meni **Dodaj admina** (`SignupForm`). Pošto ekran za prijavu trenutno sadrži samo polja za korisničko ime i lozinku — metoda `Signup_Click` postoji u kodu, ali odgovarajuća kontrola nije postavljena na formu — **prvi administrator se upisuje direktno u bazu**, npr. na SQL Server-u:

```sql
INSERT INTO [Admins] ([username], [password])
VALUES (N'admin', CONVERT(NVARCHAR(65), HASHBYTES('SHA2_256', N'vasa_lozinka'), 2));
```

Nakon prijave, svi dalji nalozi mogu se kreirati kroz aplikaciju.

---

## Mesečni CSV izveštaji

`CSVTimer` (singleton) se inicijalizuje pri pokretanju aplikacije i na svakih `dt` intervala (kao i pri startu, ako je od poslednjeg upisa prošlo dovoljno vremena) poziva `Upis.upis()`, koji u **radnom direktorijumu aplikacije** generiše dva fajla:

| Fajl | Sadržaj |
|---|---|
| `monthly_users_report_<yyyy_MM>.csv` | ID korisnika, ime, prezime, e-mail, ukupan broj iskorišćenih sati |
| `monthly_resources_report_<yyyy_MM>.csv` | ID resursa, naziv, tip, ukupan broj sati, broj rezervacija |

Izveštaji se sortiraju opadajuće po broju sati, a vrednosti se pravilno „escape“-uju (`UTF-8`, dvostruki navodnici gde je potrebno).

---

## Poznata ograničenja i moguća poboljšanja

- **Kredencijali u `Config.json`** — nalaze se u čistom tekstu; preporuka: izmestiti ih u promenljive okruženja ili *user secrets*, a fajl sa stvarnim vrednostima izuzeti iz verzionisanja.
- **SQL upiti se grade konkatenacijom stringova** (uključujući `WHERE` filtere i argumente procedura), što ostavlja prostor za SQL injection i probleme sa formatiranjem; preporuka: prelazak na parametrizovane upite (`DbParameter`).
- **Nedostaje DDL skripta za PostgreSQL**, iako je `Postgres` podrazumevani `dbType`.
- **Procedure `checkKorisnici` i `checkRezervacije`** koje poziva `Back.refreshDataBase()` nisu deo priloženih skripti.
- **Notifikacije iz baze** (`PostgresNotifier` — `LISTEN/NOTIFY`, `SqlServerNotifier` — `SqlDependency`) su implementirane, ali je njihovo uključivanje u `Back` trenutno zakomentarisano; aktivno je periodično osvežavanje preko `BasicDelayNotifier` (15 s).
- **Konekcija je singleton koji se otvara i zatvara po upitu** — jednostavno za potrebe projekta, ali nije bezbedno za paralelan rad; realan sistem bi koristio *connection pooling* i konekciju po jedinici rada.
- **Nema automatizovanih testova** — sloj repozitorijuma i lanac validacije rezervacija su dobri kandidati za unit testove (uz *mock* `iDBadapter`).
- U repozitorijumu se nalaze i **`Projekat.zip`** (arhivirana kopija izvornog koda) i **`Projekat.csproj.user`** (lokalna VS podešavanja); mogu se ukloniti, a `.gitignore` proširiti (`.vs` i `bin`/`obj` su već pokriveni).

---

## Autor

Projektni rad iz predmeta **Dizajniranje softvera**.
