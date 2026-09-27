# Kako pokrenuti Claude lokalno i dati mu pristup Accessu i Power BI-u

Cilj: da Claude na tvom računaru može da pročita pravi SQL iz `Access_v3.accdb`
(upite `Izvestaj1`–`Izvestaj8`) i da stvarno otvori i proveri Power BI fajlove.

---

## Pre svega: dve provere arhitekture

Ovo je najčešći uzrok problema, pa proveri odmah.

**Power BI Desktop:** Help → About → piše `64-bit`.

**Access / ACE drajver:** otvori Access → File → Account → About Access → u zaglavlju piše
`32-bit` ili `64-bit`. Ako nemaš Access, proveri da li uopšte imaš ACE:

```powershell
(New-Object system.data.oledb.oledbenumerator).GetElements() |
  Select-Object -ExpandProperty SOURCES_NAME | Select-String ACE
```

Ako ništa ne vrati → skini „Microsoft Access Database Engine 2016 Redistributable".
**Uzmi istu arhitekturu kao Power BI Desktop** (dakle 64-bit u 99% slučajeva).

Ako se ispostavi da imaš 32-bitni Office a 64-bitni Power BI, javi — rešava se, ali
drugim putem (čitanje baze preko 32-bitnog PowerShell-a iz `SysWOW64`).

---

## Korak 1 — Napravi jedan radni folder

Da, tvoja pretpostavka je tačna. Napravi npr. `C:\Users\<ti>\Documents\TVStanica` i u njega:

```
TVStanica\
├─ Access_v3.accdb              <- tvoja baza
├─ TV_stanica__v3.pbix          <- primer od koleginice (koristan kao uzor)
└─ powerbi\                     <- ovaj folder iz repozitorijuma
   ├─ TV_stanica_Izvestaji.pbit
   ├─ TV_stanica_Izvestaji_ACCESS.pbit
   ├─ UPUTSTVO.md
   ├─ build\                    <- skripte generatora
   └─ csv\
```

Najlakše je da ceo `powerbi\` folder dobiješ `git clone`-om (vidi Korak 3) —
tako dobiješ i sve skripte kojima su fajlovi napravljeni.

**Šta NE ide u folder:** Power BI Desktop i Access ostaju gde su instalirani.
Njih ne premeštaš — Claude ih pokreće sa njihove sistemske putanje.

**Izbegni** `.accdb` u folderu koji sinhronizuje OneDrive/Dropbox dok je baza otvorena —
sinhronizacija zna da zaključa fajl usred čitanja.

---

## Korak 2 — Pokreni Claude Code lokalno

Dve opcije, obe rade.

### A) Kroz Claude desktop aplikaciju (najlakše, već je imaš)

Claude Code je ugrađen u desktop aplikaciju. Pokreneš novu Claude Code sesiju i izabereš
`C:\Users\<ti>\Documents\TVStanica` kao radni folder.

Tačan naziv stavke u meniju se menja kroz verzije — traži „Claude Code" ili opciju za
otvaranje foldera/projekta. Ako je ne nađeš, idi na opciju B.

### B) Kroz terminal (CLI)

Treba ti Node.js 18+ (`node --version` da proveriš). Onda u PowerShell-u:

```powershell
npm install -g @anthropic-ai/claude-code
cd C:\Users\<ti>\Documents\TVStanica
claude
```

Postoji i instalacija bez Node.js-a — uputstvo je na `code.claude.com/docs`.

Prvi put će tražiti da se prijaviš na svoj Anthropic nalog.

---

## Korak 3 — Prenesi dosadašnji rad

**Bitno:** nova sesija na desktopu **ne zna ništa** o našem dosadašnjem razgovoru.
Kreće od nule. Zato joj prenesi kontekst:

```powershell
cd C:\Users\<ti>\Documents\TVStanica
git clone -b claude/wizardly-allen-1f1xqd https://github.com/MihajloPMFA/Task1.git
```

U klonu je sve: oba `.pbit` fajla, `UPUTSTVO.md` i skripte generatora u `build/`.
Onda je dovoljno da kažeš novoj sesiji „pročitaj `powerbi/UPUTSTVO.md` i
`powerbi/build/README.md`" i zna gde smo stali.

---

## Korak 4 — Dozvole

Claude Code pita za odobrenje pre svake komande koja menja nešto ili pokreće program.
Videćeš prompt i možeš da odobriš jednokratno ili trajno za tu vrstu komande.
Komandom `/permissions` vidiš i menjaš spisak odobrenog.

Za ovaj posao će tražiti da pokreće PowerShell (čitanje baze, pokretanje Power BI-a)
i da piše fajlove u radni folder. Ništa van tog foldera mu ne treba.

---

## Korak 5 — Šta mu reći prvo

Nalepi otprilike ovo:

> U ovom folderu je `Access_v3.accdb` (baza TV stanice) i folder `powerbi/` sa Power BI
> izveštajima napravljenim iz nje. Pročitaj `powerbi/UPUTSTVO.md`.
>
> Treba mi dvoje:
> 1. Izvuci pravi SQL svih upita iz Accessa (preko DAO COM-a) i `RecordSource` izveštaja
>    `Izvestaj1`–`Izvestaj8`, pa mi reci šta svaki od njih stvarno prikazuje.
> 2. Otvori `powerbi/TV_stanica_Izvestaji.pbit` u Power BI Desktopu, proveri da li se
>    učitava bez greške i sačuvaj ga kao `.pbix`.

---

## Šta će verovatno trebati da se instalira

Ništa od ovoga nije obavezno za početak — Claude će reći kad zatreba.

| Alat | Čemu služi | Cena |
|---|---|---|
| Access Database Engine (ACE) | čitanje `.accdb` i živa veza iz Power BI-a | besplatno |
| Tabular Editor 2 | izmene modela u otvorenom `.pbix`-u | besplatno |
| pbi-tools | rastavljanje i sastavljanje `.pbix`/`.pbit` fajlova | besplatno |

---

## Granice — da ne očekuješ previše

**Power BI Desktop nema zvanični CLI ni headless režim.** Može da se pokrene i da mu se
prosledi fajl, ali „otvori ovaj izveštaj i sačuvaj kao .pbix" je u suštini klikanje po
GUI-ju. To se automatizuje, ali je osetljivo — realno ćeš ponekad ti morati da klikneš.

**Power BI Service (cloud) je odvojena priča.** Ako budeš hteo da objaviš izveštaj na
`app.powerbi.com`, to traži prijavu na tvoj Power BI nalog i ide preko `MicrosoftPowerBIMgmt`
PowerShell modula. Za rad na lokalnim fajlovima nije potrebno.

**Korporativni antivirus** ponekad blokira COM automatizaciju (`DAO.DBEngine.120`).
Ako se to desi, postoji zaobilazni put preko ODBC-a.
