// Gradi Uputstvo_izvestaji_Access.docx iz uputstvo_podaci.json
const fs = require('fs');
const d = require('docx');
const {Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
       WidthType, AlignmentType, ShadingType, BorderStyle, PageBreak, PageOrientation,
       TableOfContents, LevelFormat, convertMillimetersToTwip} = d;

const P = JSON.parse(fs.readFileSync(__dirname + '/uputstvo_podaci.json', 'utf8'));
const SEK = P.sekcije, RED = P.red;
const CM = P.twip_cm;
const cm = t => (t / CM).toFixed(2);

const TAMNA = '1B2A41', SIVA = '5A6475', LINIJA = 'C8CEDA', ZAG = 'E8ECF3', BLOK = 'F4F6FA';
const SIRINA = 9639;

const deca = [];
const dodaj = x => { if (Array.isArray(x)) x.forEach(y => deca.push(y)); else deca.push(x); };

// ---------------------------------------------------------------- gradivni blokovi
function h1(t, prelom) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, pageBreakBefore: !!prelom,
    spacing: {before: 240, after: 160},
    children: [new TextRun({text: t, bold: true, size: 30, color: TAMNA, font: 'Segoe UI'})]
  });
}
function h2(t) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: {before: 220, after: 100},
    children: [new TextRun({text: t, bold: true, size: 24, color: TAMNA, font: 'Segoe UI'})]
  });
}
function h3(t) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3, spacing: {before: 180, after: 80},
    children: [new TextRun({text: t, bold: true, size: 21, color: TAMNA, font: 'Segoe UI'})]
  });
}
function p(t, o) {
  o = o || {};
  const runs = Array.isArray(t) ? t : [new TextRun({text: t, size: o.size || 20,
                                                    italics: !!o.italics,
                                                    color: o.color || '000000',
                                                    font: 'Segoe UI'})];
  return new Paragraph({children: runs, spacing: {after: o.after === undefined ? 100 : o.after},
                        alignment: o.align});
}
function korak(t, nivo) {
  return new Paragraph({
    numbering: {reference: 'koraci', level: nivo || 0},
    spacing: {after: 60},
    children: Array.isArray(t) ? t : [new TextRun({text: t, size: 20, font: 'Segoe UI'})]
  });
}
function tacka(t) {
  return new Paragraph({
    numbering: {reference: 'tacke', level: 0}, spacing: {after: 50},
    children: Array.isArray(t) ? t : [new TextRun({text: t, size: 20, font: 'Segoe UI'})]
  });
}
function kod(tekst, naslov) {
  const out = [];
  if (naslov) out.push(p([new TextRun({text: naslov, bold: true, size: 18,
                                       color: SIVA, font: 'Segoe UI'})], {after: 40}));
  const linije = tekst.split('\n');
  linije.forEach((l, i) => out.push(new Paragraph({
    shading: {type: ShadingType.CLEAR, fill: BLOK, color: 'auto'},
    spacing: {after: i === linije.length - 1 ? 140 : 0, line: 210},
    indent: {left: 113, right: 113},
    children: [new TextRun({text: l || ' ', font: 'Consolas', size: 15})]
  })));
  return out;
}
function celija(t, sirina, o) {
  o = o || {};
  return new TableCell({
    width: {size: sirina, type: WidthType.DXA},
    shading: o.fill ? {type: ShadingType.CLEAR, fill: o.fill, color: 'auto'} : undefined,
    margins: {top: 40, bottom: 40, left: 70, right: 70},
    children: String(t).split('\n').map(x => new Paragraph({
      spacing: {after: 0}, alignment: o.align,
      children: [new TextRun({text: x, bold: !!o.bold, size: o.size || 16,
                              font: o.mono ? 'Consolas' : 'Segoe UI',
                              color: o.color || '000000'})]
    }))
  });
}
function tabela(zaglavlja, redovi, sirine, opcije) {
  opcije = opcije || {};
  const ivica = {style: BorderStyle.SINGLE, size: 2, color: LINIJA};
  const rows = [new TableRow({
    tableHeader: true,
    children: zaglavlja.map((t, i) => celija(t, sirine[i], {fill: ZAG, bold: true, size: 16}))
  })];
  redovi.forEach(r => rows.push(new TableRow({
    children: r.map((t, i) => celija(t, sirine[i], {
      align: (opcije.desno || []).includes(i) ? AlignmentType.RIGHT : undefined,
      mono: (opcije.mono || []).includes(i), size: opcije.size || 16}))
  })));
  return new Table({
    columnWidths: sirine, width: {size: sirine.reduce((a, b) => a + b, 0), type: WidthType.DXA},
    borders: {top: ivica, bottom: ivica, left: ivica, right: ivica,
              insideHorizontal: ivica, insideVertical: ivica},
    rows: rows
  });
}
function razmak(v) { return new Paragraph({spacing: {after: v || 120}, children: []}); }

// ---------------------------------------------------------------- naslovna
dodaj(new Paragraph({
  spacing: {before: 1800, after: 120}, alignment: AlignmentType.CENTER,
  children: [new TextRun({text: 'Uputstvo za kreiranje izveštaja', bold: true,
                          size: 44, color: TAMNA, font: 'Segoe UI'})]
}));
dodaj(new Paragraph({
  spacing: {after: 300}, alignment: AlignmentType.CENTER,
  children: [new TextRun({text: 'u programu Microsoft Access', size: 30,
                          color: SIVA, font: 'Segoe UI'})]
}));
dodaj(p([new TextRun({text: 'Informacioni sistem TV stanice - TV Panorama', size: 22,
                      color: TAMNA, font: 'Segoe UI'})], {align: AlignmentType.CENTER}));
dodaj(p([new TextRun({text: 'Osam izveštaja iz Specifikacije izveštaja, korak po korak',
                      size: 20, color: SIVA, font: 'Segoe UI'})],
        {align: AlignmentType.CENTER, after: 600}));
dodaj(tabela(['Izveštaj', 'Naziv', 'Tip', 'Upit', 'Ime izveštaja'],
  P.izvestaji.map(z => [String(z.broj), z.spec['Naziv'], z.spec['Tip izveštaja'],
                        z.upit, z.ime]),
  [700, 3100, 2000, 1970, 1869], {mono: [3, 4]}));
dodaj(new Paragraph({children: [new PageBreak()]}));
dodaj(h1('Sadržaj'));
dodaj(new TableOfContents('Sadržaj', {hyperlink: true, headingStyleRange: '1-3'}));

// ---------------------------------------------------------------- 1. priprema
dodaj(h1('1. Šta je potrebno pre početka', true));
dodaj(p('Uputstvo pretpostavlja da već imaš Access bazu informacionog sistema TV stanice ' +
        '(Access_v1.accdb) sa 69 tabela, 84 veze i unetim podacima. Izveštaji se prave nad ' +
        'tim tabelama - ništa u njima se ne menja, ne dodaje i ne briše.'));
dodaj(tacka('Otvori bazu i, ako se pojavi žuta traka sa upozorenjem, klikni Enable Content.'));
dodaj(tacka('Proveri da u oknu objekata postoje tabele TERMIN_EMITOVANJA, ZAPIS_O_EMITOVANJU, ' +
            'PROJEKAT_PRODUKCIJE, UGOVOR, PLAN_NABAVKE i ostale - upiti se oslanjaju na njih.'));
dodaj(tacka('Napravi rezervnu kopiju baze pre nego što počneš.'));
dodaj(p([new TextRun({text: 'Imena u uputstvu su ista kao u VBA modulu modIzvestaji: upiti nose ' +
                            'prefiks qIzv, izveštaji rptIzv. Ako si već pokrenuo taj modul, ' +
                            'objekti postoje i ovo uputstvo služi kao dokumentacija kako su ' +
                            'napravljeni - ili kao uputstvo da ih napraviš rukom.',
                      size: 20, italics: true, color: SIVA, font: 'Segoe UI'})]));

// ---------------------------------------------------------------- 2. kako citati
dodaj(h1('2. Kako se čitaju koraci'));
dodaj(h2('2.1 Mere'));
dodaj(p('Sve pozicije i dimenzije date su u centimetrima, onako kako ih Access prikazuje u ' +
        'prozoru svojstava (Property Sheet). Svojstva su:'));
dodaj(tabela(['Kolona u uputstvu', 'Svojstvo u Access-u', 'Značenje'],
  [['Levo', 'Left', 'udaljenost leve ivice kontrole od leve ivice sekcije'],
   ['Gore', 'Top', 'udaljenost gornje ivice kontrole od vrha sekcije'],
   ['Širina', 'Width', 'širina kontrole'],
   ['Visina', 'Height', 'visina kontrole']],
  [2100, 2400, 5139]));
dodaj(razmak());
dodaj(p('Ako Access prikazuje inče umesto centimetara: File > Options > Client Settings > ' +
        'Measurement units > Centimeters.'));
dodaj(h2('2.2 Sekcije izveštaja'));
dodaj(p('Access sekcije nose engleska imena; u uputstvu su na srpskom:'));
dodaj(tabela(['U uputstvu', 'U Access-u', 'Kada se štampa'],
  RED.map(k => [SEK[k][0], SEK[k][1],
    k === 'acHeader' ? 'jednom, na početku izveštaja' :
    k === 'acPageHeader' ? 'na vrhu svake strane' :
    k === 'acDetail' ? 'za svaki red podataka' :
    k === 'acFooter' ? 'jednom, na kraju izveštaja' :
    k === 'acPageFooter' ? 'na dnu svake strane' :
    k.indexOf('Header') > 0 ? 'na početku svake grupe' : 'na kraju svake grupe']),
  [2300, 2600, 4739]));
dodaj(razmak());
dodaj(h2('2.3 Vrste kontrola'));
dodaj(tabela(['U uputstvu', 'Alatka u Access-u (Design > Controls)', 'Šta se postavlja'],
  [['Natpis', 'Label (Aa)', 'svojstvo Caption - tekst koji piše na izveštaju'],
   ['Polje', 'Text Box (ab|)', 'svojstvo Control Source - polje upita ili izraz'],
   ['Linija', 'Line', 'samo pozicija i dužina (Visina ostaje 0)'],
   ['Grafikon', 'Chart / Unbound Object Frame', 'MSGraph objekat nad upitom'],
   ['Podizveštaj', 'Subform/Subreport', 'svojstvo Source Object - drugi izveštaj']],
  [1700, 3200, 4739]));
dodaj(razmak());
dodaj(h2('2.4 Stil i format'));
dodaj(p('Kolona Stil u tabelama kontrola sadrži veličinu slova u pt, podebljanje, ' +
        'poravnanje teksta (Text Align) i, gde je potrebno, Format. Na primer ' +
        '"9pt, bold, desno, #,##0.00" znači: Font Size = 9, Font Weight = Bold, ' +
        'Text Align = Right, Format = #,##0.00.'));
dodaj(tabela(['Format', 'Prikazuje'],
  [['#,##0.00', 'iznos sa dve decimale i razdvojenim hiljadama (npr. 613.131,00)'],
   ['#,##0', 'ceo broj sa razdvojenim hiljadama'],
   ['0', 'ceo broj bez razdvajanja'],
   ['0.00', 'broj sa dve decimale (rejting, bodovi)'],
   ['0.0', 'broj sa jednom decimalom (popust, prosečno gledanje)'],
   ['0.0%', 'procenat sa jednom decimalom'],
   ['dd.mm.yyyy', 'datum (npr. 06.01.2026)'],
   ['hh:nn', 'vreme, sat i minut (npr. 09:07)'],
   ['dddd', 'naziv dana u nedelji'],
   ['dd.mm.yyyy. hh:nn', 'datum i vreme kreiranja izveštaja']],
  [2300, 7339]));

// ---------------------------------------------------------------- 3. opsti postupak
dodaj(h1('3. Opšti postupak (čita se jednom)', true));
dodaj(p('Svaki od osam izveštaja pravi se po istom postupku. U poglavljima 5-12 dat je samo ' +
        'sadržaj koji je za taj izveštaj različit.'));

dodaj(h2('3.1 Kreiranje upita'));
dodaj(korak('Create > Query Design.'));
dodaj(korak('Ako se otvori prozor Add Tables, zatvori ga bez dodavanja tabela.'));
dodaj(korak('Design > SQL View (ili desni klik na jezičak upita > SQL View).'));
dodaj(korak('Obriši ono što je u prozoru i nalepi SQL iz uputstva.'));
dodaj(korak('Ctrl+S i upiši ime upita (npr. qIzv1_Sema).'));
dodaj(korak('Dvokliktni na upit da proveriš da vraća redove, pa ga zatvori.'));
dodaj(p([new TextRun({text: 'Upiti se prave pre izveštaja. Pomoćni upiti iz poglavlja 4 ' +
                            'moraju postojati pre upita qIzv6_Kartica i qIzv7_Stavke, jer se ' +
                            'oni na njih pozivaju.', size: 20, italics: true,
                      color: SIVA, font: 'Segoe UI'})]));

dodaj(h2('3.2 Kreiranje izveštaja i izvor podataka'));
dodaj(korak('Create > Report Design. Otvara se prazan izveštaj u dizajnu.'));
dodaj(korak('Ako prozor svojstava nije vidljiv: Design > Property Sheet (ili F4).'));
dodaj(korak('U prozoru svojstava, u padajućoj listi na vrhu izaberi Report.'));
dodaj(korak('Na kartici Data postavi Record Source na upit iz uputstva.'));

dodaj(h2('3.3 Grupisanje i sortiranje'));
dodaj(korak('Design > Group & Sort. Na dnu se otvara okno Group, Sort, and Total.'));
dodaj(korak('Klikni Add a group i izaberi polje iz uputstva. Nivoi se dodaju u navedenom ' +
            'redosledu - prvi dodati je grupa 1, drugi grupa 2.'));
dodaj(korak('Na svakom nivou klikni More i postavi with a header section / ' +
            'without a header section i with a footer section / without a footer section ' +
            'tačno kako piše u tabeli za taj izveštaj.'));
dodaj(korak('Nivoi označeni kao "samo sortiranje" dodaju se preko Add a sort i ostaju bez ' +
            'zaglavlja i podnožja - služe da se redovi unutar grupe poređaju.'));

dodaj(h2('3.4 Prikaz zaglavlja i podnožja izveštaja'));
dodaj(korak('Desni klik na sivu površinu izveštaja > Report Header/Footer (ako sekcije nisu ' +
            'vidljive).'));
dodaj(korak('Desni klik > Page Header/Footer za zaglavlje i podnožje strane.'));
dodaj(korak('Visinu sekcije postavi tako što klikneš na njenu traku sa imenom i u prozoru ' +
            'svojstava upišeš Height iz tabele "Sekcije i visine".'));
dodaj(korak('Gde u tabeli piše "raste" postavi i Can Grow = Yes i Can Shrink = Yes.'));

dodaj(h2('3.5 Dodavanje kontrole i precizno pozicioniranje'));
dodaj(korak('Izaberi alatku (Label, Text Box ili Line) sa Design > Controls i nacrtaj je ' +
            'unutar prave sekcije - pozicija u tom trenutku nije važna.'));
dodaj(korak([new TextRun({text: 'Ako si dodao Text Box, Access uz njega napravi i prikačeni ' +
                                'natpis. Klikni na taj natpis i pritisni Delete', size: 20,
                          font: 'Segoe UI'}),
             new TextRun({text: ' - natpisi se u ovim izveštajima dodaju odvojeno, sa svojim ' +
                                'pozicijama.', size: 20, font: 'Segoe UI'})]));
dodaj(korak('U prozoru svojstava, kartica Format, upiši Left, Top, Width i Height iz tabele.'));
dodaj(korak('Za Natpis postavi Caption na tekst iz kolone "Izvor ili tekst".'));
dodaj(korak('Za Polje postavi Control Source (kartica Data) na vrednost iz kolone ' +
            '"Izvor ili tekst". Ako vrednost počinje znakom =, to je izraz i upisuje se ceo, ' +
            'sa znakom jednakosti.'));
dodaj(korak('Postavi Font Size, Font Weight (Bold ili Normal) i Text Align po koloni Stil, ' +
            'a Format ako je naveden.'));
dodaj(p([new TextRun({text: 'Podrazumevana svojstva za svako Polje u ovim izveštajima: ',
                      size: 20, bold: true, font: 'Segoe UI'}),
         new TextRun({text: 'Border Style = Transparent i Can Grow = No. Za sitne natpise ' +
                            'koji nisu podebljani koristi se siva boja teksta (Fore Color ' +
                            '#46505F); to je samo estetika i može se preskočiti.',
                      size: 20, font: 'Segoe UI'})]));
dodaj(p([new TextRun({text: 'Savet: ', size: 20, bold: true, font: 'Segoe UI'}),
         new TextRun({text: 'kad napraviš prvu kontrolu u nekoj sekciji i podesiš joj font, ' +
                            'kopiraj je (Ctrl+C, Ctrl+V) za ostale u istoj sekciji - onda samo ' +
                            'menjaš Left, Top, Width i tekst.', size: 20, font: 'Segoe UI'})]));

dodaj(h2('3.6 Podešavanje strane'));
dodaj(korak('Page Setup > Page Setup. Kartica Page: Paper Size = A4.'));
dodaj(korak('Orientation postavi na Landscape (pejzaž) ili Portrait (portret) po tabeli ' +
            '"Podešavanja izveštaja".'));
dodaj(korak('Kartica Print Options: leva i desna margina 0,64 cm, gornja i donja 0,71 cm.'));
dodaj(korak('Širinu izveštaja postavi tako što u prozoru svojstava izabereš Report i upišeš ' +
            'Width iz tabele. Širina mora biti manja od (širina papira - leva - desna margina), ' +
            'inače Access štampa prazne strane.'));

dodaj(h2('3.7 Podnožje strane'));
dodaj(p('Podnožje strane isto je u svih osam izveštaja: linija, datum i vreme kreiranja, ' +
        'ime korisnika koji je izveštaj napravio i broj strane. Tačne pozicije date su u ' +
        'tabeli za svaki izveštaj, jer zavise od širine izveštaja.'));
dodaj(p([new TextRun({text: 'Izraz =CurrentUser() vraća "Admin" ako baza nema korisničke ' +
                            'naloge. Ako želiš svoje ime, umesto Polja stavi Natpis sa ' +
                            'tekstom "Izradio: Ime Prezime".', size: 20, italics: true,
                      color: SIVA, font: 'Segoe UI'})]));

dodaj(h2('3.8 Čuvanje i provera'));
dodaj(korak('Ctrl+S i upiši ime izveštaja (npr. rptIzv1).'));
dodaj(korak('Design > View > Print Preview i proveri da se podaci prikazuju i da nema ' +
            'praznih strana.'));
dodaj(korak('Ako se pojavi prazna strana između strana sa podacima, širina izveštaja je ' +
            'prevelika - smanji je ili smanji margine.'));
dodaj(korak('Zatvori izveštaj.'));

// ---------------------------------------------------------------- 4. pomocni upiti
dodaj(h1('4. Pomoćni upiti (prvo ovi)', true));
dodaj(p('Četiri upita se ne koriste direktno kao izvor nekog izveštaja, ali se na njih ' +
        'pozivaju upiti izveštaja 6 i 7. Njihova svrha je da se vrednosti koje se ponavljaju ' +
        '(fakture po ugovoru, zahtev po planu, narudžbenice po dobavljaču, izabrana ponuda po ' +
        'stavci) svedu na jedan red, da spajanje tabela ne bi umnožilo redove i pokvarilo ' +
        'zbirove. Napravi ih po postupku 3.1.'));
P.pomocni.forEach(pa => { dodaj(h3(pa[0])); dodaj(kod(pa[1])); });

// ---------------------------------------------------------------- kontrole -> tabela
const STIL_KOL = [400, 760, 3480, 690, 690, 690, 690, 2229];
function stilOpis(k) {
  if (k.vrsta === 'Linija') return '';
  const c = [k.vel + 'pt'];
  c.push(k.bold ? 'bold' : 'normal');
  if (k.por && k.por !== 'levo') c.push(k.por);
  if (k.fmt) c.push('format ' + k.fmt);
  return c.join(', ');
}
function imeSekcije(k, grupe) {
  let ime = SEK[k][0] + ' (' + SEK[k][1] + ')';
  const m = k.match(/acGroupLevel(\d)/);
  if (m) {
    const gr = grupe[Number(m[1]) - 1];
    if (gr) ime += ' - grupa po ' + gr.polje;
  }
  return ime;
}
function tabelaKontrola(z, pre) {
  const out = [];
  let n = 0;
  RED.forEach(sek => {
    const lista = z.kontrole[sek];
    if (!lista || !lista.length) return;
    const v = z.visine[sek];
    n += 1;
    out.push(h3(pre + '.' + n + ' ' + imeSekcije(sek, z.grupe)));
    if (v) out.push(p('Visina sekcije: ' + cm(v.visina) + ' cm' +
                      (v.raste ? '   (Can Grow = Yes, Can Shrink = Yes)' : ''),
                      {size: 18, color: SIVA, after: 80}));
    out.push(tabela(['#', 'Kontrola', 'Izvor ili tekst', 'Levo', 'Gore', 'Širina', 'Visina',
                     'Stil'],
      lista.map((k, i) => [String(i + 1), k.vrsta, k.sadrzaj, cm(k.x), cm(k.y), cm(k.w),
                           k.vrsta === 'Linija' ? '0' : cm(k.h), stilOpis(k)]),
      STIL_KOL, {desno: [3, 4, 5, 6], mono: [2]}));
    out.push(razmak(140));
  });
  return out;
}
function tabelaPodesavanja(z) {
  const r = [['Ime izveštaja', z.ime],
             ['Record Source (izvor podataka)', z.upit],
             ['Caption (naslov u naslovnoj traci)', z.naslov],
             ['Orientation', z.pejzaz ? 'Landscape (pejzaž)' : 'Portrait (portret)'],
             ['Width (širina izveštaja)', cm(z.sirina) + ' cm'],
             ['Paper Size', 'A4']];
  return tabela(['Svojstvo', 'Vrednost'], r, [3600, 6039], {mono: []});
}
function tabelaGrupa(z) {
  if (!z.grupe.length) return [p('Ovaj izveštaj nema grupisanje - svi redovi idu u sekciju ' +
                                 'Detalji, u redosledu koji daje upit.')];
  const r = z.grupe.map((g, i) => {
    const samoSort = !g.zaglavlje && !g.podnozje;
    return [samoSort ? 'samo sortiranje' : 'grupa ' + (i + 1), g.polje,
            g.zaglavlje ? 'with a header section' : 'without a header section',
            g.podnozje ? 'with a footer section' : 'without a footer section'];
  });
  return [tabela(['Nivo', 'Polje (group on)', 'Zaglavlje', 'Podnožje'], r,
                 [1700, 2900, 2500, 2539], {mono: [1]})];
}
function tabelaSekcija(z) {
  const r = RED.filter(k => z.visine[k]).map(k =>
    [imeSekcije(k, z.grupe), cm(z.visine[k].visina) + ' cm',
     z.visine[k].raste ? 'Can Grow = Yes, Can Shrink = Yes' : '-']);
  return tabela(['Sekcija', 'Height', 'Napomena'], r, [4300, 1600, 3739]);
}

// ---------------------------------------------------------------- 5-12. izvestaji
const SPEC_RED = ['Tip izveštaja', 'Svrha', 'Izvor podataka', 'Parametri',
                  'Učestalost i raspodela', 'Zaglavlje i podnožje', 'Telo izveštaja',
                  'Pristup izveštaju'];
P.izvestaji.forEach((z, idx) => {
  const pog = idx + 5;
  dodaj(h1(pog + '. Izveštaj ' + z.broj + ' - ' + z.spec['Naziv'], true));

  dodaj(h2(pog + '.1 Zahtev iz specifikacije'));
  dodaj(tabela(['Stavka', 'Opis'],
    SPEC_RED.filter(k => z.spec[k]).map(k => [k, z.spec[k]]), [2400, 7239]));
  dodaj(razmak(140));

  let pod = pog + 2;
  if (z.pod) {
    dodaj(h2(pog + '.2 Podizveštaj ' + z.pod.ime + ' - pravi se prvi'));
    dodaj(p('Glavni izveštaj ga ugrađuje, pa mora da postoji pre njega. Postupak je isti, ' +
            'samo bez podešavanja strane (podizveštaj se štampa unutar glavnog).'));
    dodaj(h3(pog + '.2.1 Upit ' + z.pod.upit));
    dodaj(kod(z.pod.sql));
    dodaj(h3(pog + '.2.2 Podešavanja'));
    dodaj(tabelaPodesavanja(z.pod));
    dodaj(razmak(140));
    dodaj(h3(pog + '.2.3 Grupisanje i sortiranje'));
    dodaj(tabelaGrupa(z.pod));
    dodaj(razmak(140));
    dodaj(h3(pog + '.2.4 Sekcije i visine'));
    dodaj(tabelaSekcija(z.pod));
    dodaj(razmak(140));
    dodaj(tabelaKontrola(z.pod, pog + '.2.5'));
    dodaj(p('Sačuvaj podizveštaj kao ' + z.pod.ime + ' i zatvori ga.'));
    pod = pog + 3;
  }

  dodaj(h2(pog + '.' + (z.pod ? 3 : 2) + ' Upit ' + z.upit));
  dodaj(kod(z.sql));
  if (z.grafikoni.length) {
    dodaj(p('Grafikoni na ovom izveštaju koriste svoje upite:'));
    z.grafikoni.forEach(gr => { dodaj(h3('Upit ' + gr.upit)); dodaj(kod(gr.sql)); });
  }

  const b = z.pod ? 4 : 3;
  dodaj(h2(pog + '.' + b + ' Podešavanja izveštaja'));
  dodaj(tabelaPodesavanja(z));
  dodaj(razmak(140));
  dodaj(h2(pog + '.' + (b + 1) + ' Grupisanje i sortiranje'));
  dodaj(tabelaGrupa(z));
  dodaj(razmak(140));
  dodaj(h2(pog + '.' + (b + 2) + ' Sekcije i visine'));
  dodaj(tabelaSekcija(z));
  dodaj(razmak(140));
  dodaj(h2(pog + '.' + (b + 3) + ' Kontrole po sekcijama'));
  dodaj(tabelaKontrola(z, pog + '.' + (b + 3)));

  let k = b + 4;
  if (z.grafikoni.length) {
    dodaj(h2(pog + '.' + k + ' Grafikoni'));
    dodaj(p('Grafikon se dodaje u ' + imeSekcije(z.grafikoni[0].sek, z.grupe) + '.'));
    dodaj(korak('Design > Controls > Chart (u starijim verzijama: Insert Chart) i nacrtaj ' +
                'okvir u toj sekciji. Ako se pokrene čarobnjak, izaberi upit iz tabele ispod ' +
                'i tip Column Chart, pa Finish.'));
    dodaj(korak('U prozoru svojstava grafikona postavi Row Source Type = Table/Query i ' +
                'Row Source na upit iz tabele.'));
    dodaj(korak('Postavi Left, Top, Width i Height iz tabele.'));
    dodaj(korak('Za drugi grafikon (kretanje po datumu) desni klik na grafikon > ' +
                'Chart Object > Edit, pa Chart > Chart Type > Line. Zatim klik van grafikona.'));
    dodaj(razmak(80));
    dodaj(tabela(['#', 'Upit (Row Source)', 'Levo', 'Gore', 'Širina', 'Visina', 'Tip'],
      z.grafikoni.map((gr, i) => [String(i + 1), gr.upit, cm(gr.x), cm(gr.y), cm(gr.w),
                                  cm(gr.h), i === 0 ? 'stubasti (Column)' : 'linijski (Line)']),
      [400, 2700, 690, 690, 690, 690, 3779], {desno: [2, 3, 4, 5], mono: [1]}));
    dodaj(razmak(140));
    dodaj(p([new TextRun({text: 'Ako MSGraph nije registrovan na računaru, grafikon se ne može ' +
                                'dodati. Izveštaj i tada radi - ostaje prateća tabela, koju ' +
                                'specifikacija takođe zahteva.', size: 20, italics: true,
                          color: SIVA, font: 'Segoe UI'})]));
    k += 1;
  }
  if (z.podizvestaji.length) {
    dodaj(h2(pog + '.' + k + ' Ugradnja podizveštaja'));
    z.podizvestaji.forEach(pd => {
      dodaj(korak('Design > Controls > Subform/Subreport i nacrtaj okvir u sekciji ' +
                  imeSekcije(pd.sek, z.grupe) + '. Ako se pokrene čarobnjak, klikni Cancel.'));
      dodaj(korak('Obriši prikačeni natpis koji je Access napravio.'));
      dodaj(korak('U prozoru svojstava postavi Source Object = Report.' + pd.izvestaj + '.'));
      if (pd.master) {
        dodaj(korak('Postavi Link Master Fields = ' + pd.master.replace(/;/g, '; ') +
                    ' i Link Child Fields = ' + pd.dete.replace(/;/g, '; ') +
                    ' - tako se ispod svake stavke prikazuju samo njene ponude.'));
      } else {
        dodaj(korak('Link Master Fields i Link Child Fields ostavi prazne - prikazuje se cela ' +
                    'lista.'));
      }
      dodaj(korak('Postavi Left = ' + cm(pd.x) + ' cm, Top = ' + cm(pd.y) + ' cm, Width = ' +
                  cm(pd.w) + ' cm, Height = ' + cm(pd.h) + ' cm, Can Grow = Yes, ' +
                  'Can Shrink = Yes.'));
    });
    k += 1;
  }
  dodaj(h2(pog + '.' + k + ' Čuvanje'));
  dodaj(p('Ctrl+S, ime izveštaja: ' + z.ime + '. Zatim Print Preview i provera da se podaci ' +
          'prikazuju i da nema praznih strana.'));
});

// ---------------------------------------------------------------- 13. provera
dodaj(h1('13. Provera i česti problemi', true));
dodaj(h2('13.1 Kontrolna lista'));
dodaj(tabela(['Gotovo kada', 'Kako se proverava'],
  [['postoje 4 pomoćna upita', 'okno objekata > Queries: qIzv6_Fakture, qIzv7_Zahtev, ' +
    'qIzv7_Narudzbe, qIzv7_Izabrana'],
   ['postoji 12 upita izveštaja', 'svaki qIzv... upit otvoren dvoklikom vraća redove'],
   ['postoje 2 podizveštaja', 'rptIzv5_Oprema i rptIzv7_Ponude'],
   ['postoji 8 izveštaja', 'rptIzv1 do rptIzv8'],
   ['dva izveštaja traže parametre', 'rptIzv2 pita datum od i datum do, rptIzv6 šifru ili ' +
    'naziv oglašivača'],
   ['izveštaj 3 ima grafikone', 'u zaglavlju izveštaja dva grafikona iznad tabele'],
   ['zbirovi se pojavljuju', 'u podnožjima grupa i u podnožju izveštaja'],
   ['nema praznih strana', 'Print Preview, pregled svih strana']],
  [3000, 6639]));
dodaj(razmak());
dodaj(h2('13.2 Česti problemi'));
dodaj(tabela(['Simptom', 'Uzrok i rešenje'],
  [['#Name? u polju', 'Control Source ne postoji u upitu ili je ime pogrešno napisano. ' +
    'Otvori upit i proveri tačno ime kolone.'],
   ['#Error u polju sa procentom', 'Izraz koristi zapetu kao razdvajač argumenata. Na srpskom ' +
    'regionalnom podešavanju zameni zapete tačkom-zapetom: IIf(a; b; c).'],
   ['Prazna strana između strana', 'Širina izveštaja je veća od širine papira umanjene za ' +
    'margine. Smanji Width ili margine.'],
   ['Zbir se duplira', 'Umesto Sum upotrebi Max za vrednost koja je konstantna u grupi ' +
    '(npr. odobren budžet, ugovoreno sekundi).'],
   ['Izveštaj je prazan', 'Record Source je prazan ili upit ne vraća redove. Otvori upit ' +
    'zasebno.'],
   ['Access traži parametar koji nije očekivan', 'Ime kolone u Control Source je pogrešno, pa ' +
    'ga Access tumači kao parametar.'],
   ['Grupa se ne prikazuje', 'U Group & Sort nivo je dodat bez zaglavlja. Klikni More > ' +
    'with a header section.'],
   ['Podizveštaj prikazuje sve redove', 'Nisu postavljeni Link Master Fields i ' +
    'Link Child Fields.']],
  [2600, 7039]));
dodaj(razmak());
dodaj(h2('13.3 Brži put'));
dodaj(p('Ako ti ne treba ručno sastavljanje, isti ovi izveštaji prave se automatski: uvezi VBA ' +
        'modul TV_Stanica_Izvestaji.bas (Alt+F11 > File > Import File) i pokreni proceduru ' +
        'KreirajIzvestaje. Modul na kraju sam proveri sve što je napravio i prikaže šta radi, ' +
        'a šta ne. Postojeće tabele, forme i upiti se ne menjaju.'));

// ---------------------------------------------------------------- dokument
const doc = new Document({
  creator: 'TV Panorama', title: 'Uputstvo za kreiranje izveštaja u Microsoft Access-u',
  description: 'Osam izveštaja iz Specifikacije izveštaja, korak po korak',
  numbering: {
    config: [
      {reference: 'koraci', levels: [
        {level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.START,
         style: {paragraph: {indent: {left: 420, hanging: 280}}}}]},
      {reference: 'tacke', levels: [
        {level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.START,
         style: {paragraph: {indent: {left: 420, hanging: 280}}}}]}
    ]
  },
  styles: {default: {document: {run: {font: 'Segoe UI', size: 20}}}},
  sections: [{
    properties: {page: {margin: {top: 1134, right: 1134, bottom: 1134, left: 1134}}},
    footers: {},
    children: deca
  }]
});
Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(__dirname + '/Uputstvo_izvestaji_Access.docx', b);
  console.log('Uputstvo_izvestaji_Access.docx  ' + Math.round(b.length / 1024) + ' KB');
});
