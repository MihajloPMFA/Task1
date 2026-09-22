const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
        WidthType, ShadingType, AlignmentType, BorderStyle, Footer, PageNumber } = require('docx');

const CW = 9026;                       // sirina sadrzaja (A4, podrazumevane margine)
const HDR = 'D9E2F3', ZEBRA = 'F2F5FA';
const B = { style: BorderStyle.SINGLE, size: 4, color: 'AAB4C4' };
const BORDERS = { top: B, bottom: B, left: B, right: B,
                  insideHorizontal: B, insideVertical: B };

const p = (text, o = {}) => new Paragraph({
  spacing: { after: o.after === undefined ? 120 : o.after, line: 276 },
  alignment: o.align, children: [new TextRun({ text, bold: o.bold, italics: o.it,
    size: o.size || 21, color: o.color })] });

const cell = (text, { w, bold, fill, align } = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: fill ? { type: ShadingType.CLEAR, color: 'auto', fill } : undefined,
  margins: { top: 60, bottom: 60, left: 110, right: 110 },
  children: (Array.isArray(text) ? text : [text])
    .flatMap(t => String(t).split('\n'))          // nikad \n u jednom pasusu
    .map(t => new Paragraph({ alignment: align, spacing: { after: 0, line: 264 },
      children: [new TextRun({ text: t, bold, size: 20 })] })) });

function specTable(rows) {
  const w = [2500, CW - 2500];
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: w, borders: BORDERS,
    rows: [new TableRow({ tableHeader: true, children: [
        cell('Stavka', { w: w[0], bold: true, fill: HDR }),
        cell('Opis',   { w: w[1], bold: true, fill: HDR })] }),
      ...rows.map(([k, v], i) => new TableRow({ children: [
        cell(k, { w: w[0], bold: true, fill: i % 2 ? ZEBRA : undefined }),
        cell(v, { w: w[1], fill: i % 2 ? ZEBRA : undefined })] }))] });
}

function gridTable(head, rows, widths) {
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: widths, borders: BORDERS,
    rows: [new TableRow({ tableHeader: true, children:
        head.map((h, i) => cell(h, { w: widths[i], bold: true, fill: HDR })) }),
      ...rows.map((r, k) => new TableRow({ children:
        r.map((c, i) => cell(c, { w: widths[i], fill: k % 2 ? ZEBRA : undefined,
          bold: i === 0 })) }))] });
}

// ----------------------------------------------------------------- sadrzaj
const R = [
{
 id: 1, tip: 'Tabelarni (grupisani)',
 naziv: 'Programska šema sa terminima emitovanja',
 svrha: 'Prikaz usvojene programske šeme za izabranu sezonu: programske celine i svi termini emitovanja u njima, sa emisijom, trajanjem, zonom gledanosti i rednim brojem reprize. Redakciji i tehničkoj službi služi kao radni raspored, a upravi kao dokaz o usvojenoj šemi programa.',
 izvor: 'Tabele „Programska šema“, „Programska celina“, „Termin emitovanja“, „Emisija“ i „Urednik“ iz baze podataka informacionog sistema.',
 param: '—',
 ucest: 'Izveštaj se kreira pri svakom usvajanju ili izmeni programske šeme, obavezno pre početka sezone, kao i po zahtevu.',
 zagl: 'U zaglavlju se nalaze naziv izveštaja, naziv i sezona šeme, period važenja (datum od – datum do), verzija i status šeme, kao i ime urednika koji je šemu odobrio. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Tabelarni prikaz grupisan po programskoj celini (naziv celine, tip celine, datum, vreme od – vreme do). Unutar svake celine, za svaki termin: vreme početka, naziv emisije, žanr, trajanje termina, tip termina, zona gledanosti, redni broj reprize i status termina. U podnožju grupe zbir minuta po celini, a na kraju ukupan broj termina i ukupno minuta po šemi.',
 pristup: 'Urednici programa, redakcija, tehnička služba i uprava stanice.'
},
{
 id: 2, tip: 'Parametarski (tabelarni)',
 naziv: 'Evidencija emitovanog sadržaja (playout log)',
 svrha: 'Hronološka evidencija stvarno emitovanog sadržaja za period koji korisnik unese: šta je, kada i koliko dugo emitovano, po kom pravu korišćenja i uz koje smetnje. Osnova za izveštavanje regulatornom telu i za dokazivanje osnova za emitovanje.',
 izvor: 'Tabele „Zapis o emitovanju“, „Termin emitovanja“, „Emisija“, „Medijski sadržaj“, „Pokrivenost pravom“ i „Pravo korišćenja“ iz baze podataka informacionog sistema.',
 param: 'Datum od i datum do (obavezni parametri, unose se pri pokretanju izveštaja). Opciono se može zadati i status realizacije radi izdvajanja samo neuspelih emitovanja.',
 ucest: 'Izveštaj se kreira automatski na dnevnom nivou, kao i po zahtevu pravne službe i ovlašćenih regulatornih tela.',
 zagl: 'U zaglavlju su naziv izveštaja i period koji je korisnik uneo kao parametar. U podnožju su datum i vreme kreiranja, ime odgovornog lica i broj strane.',
 telo: 'Hronološki tabelarni prikaz, sortiran po datumu i stvarnom vremenu početka: datum, stvarno vreme početka, naziv emisije, naziv medijskog sadržaja, planirano trajanje termina, stvarno trajanje i odstupanje, status realizacije, broj licence i vrsta prava, operater emitovanja i napomena o smetnjama. Po danu se prikazuju zbir emitovanih minuta i broj emitovanja sa zabeleženim smetnjama.',
 pristup: 'Uprava stanice, urednici programa, tehnička služba, pravna služba i ovlašćena regulatorna tela.'
},
{
 id: 3, tip: 'Grafički (sa pratećom tabelom)',
 naziv: 'Gledanost emisija po žanru',
 svrha: 'Prikaz ostvarenog rejtinga i udela u terminu po emisiji i po žanru za izabrani period, radi ocene uspešnosti programa i donošenja odluka o izmeni programske šeme.',
 izvor: 'Tabele „Merenje gledanosti“, veza „Merena“ (ostvareni rejting i udeo u terminu), „Emisija“ i „Termin emitovanja“ iz baze podataka informacionog sistema.',
 param: '—',
 ucest: 'Izveštaj se kreira na mesečnom nivou i po završetku sezone, kao i po zahtevu sektora marketinga.',
 zagl: 'U zaglavlju su naziv izveštaja, period merenja, izvor merenja i ciljna grupa na koju se merenja odnose. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Grafički prikaz: stubasti grafikon prosečnog ostvarenog rejtinga po žanru emisije i linijski grafikon kretanja prosečnog rejtinga po datumu merenja. Ispod grafikona prateći tabelarni prikaz: naziv emisije, žanr, broj merenja, prosečan ostvareni rejting, prosečan udeo u terminu, prosečan broj gledalaca i prosečno vreme gledanja, sortirano opadajuće po rejtingu.',
 pristup: 'Uprava stanice, urednici programa i sektor marketinga i prodaje.'
},
{
 id: 4, tip: 'Tabelarni (grupisani, sa zbirovima)',
 naziv: 'Realizacija i troškovi projekta produkcije',
 svrha: 'Pregled projekata produkcije sa pripadajućim aktivnostima i nastalim troškovima, uz poređenje sa odobrenim budžetom, radi kontrole trošenja i planiranja narednih projekata.',
 izvor: 'Tabele „Projekat produkcije“, „Aktivnost produkcije“, „Trošak produkcije“, „Faktura“, „Emisija“ i „Urednik“ iz baze podataka informacionog sistema.',
 param: '—',
 ucest: 'Izveštaj se kreira na mesečnom nivou i obavezno po završetku svakog projekta produkcije.',
 zagl: 'U zaglavlju su naziv izveštaja i period na koji se odnosi. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Tabelarni prikaz grupisan po projektu (šifra i naziv projekta, vrsta produkcije, urednik, datum početka i završetka, odobren budžet, status projekta). Unutar projekta prikazuju se aktivnosti (redni broj, naziv, vrsta, lokacija snimanja, datum od – datum do, status), a ispod svake aktivnosti pripadajući troškovi (vrsta troška, opis, datum nastanka, iznos i broj fakture kojom je trošak dokumentovan). Zbir troškova daje se po aktivnosti i po projektu, uz iznos i procenat iskorišćenja odobrenog budžeta.',
 pristup: 'Urednici, rukovodilac produkcije, finansijska služba i uprava stanice.'
},
{
 id: 5, tip: 'Tabelarni (grupisani, sa zbirovima)',
 naziv: 'Angažovanje zaposlenih i zaduženje opreme na produkciji',
 svrha: 'Pregled angažovanja zaposlenih na aktivnostima produkcije i opreme rezervisane za te aktivnosti, radi obračuna angažovanja, raspodele posla i planiranja tehničkih resursa.',
 izvor: 'Tabele „Zaposleni“, „Organizaciona jedinica“, „Aktivnost produkcije“, „Projekat produkcije“, „Oprema“, veza „Angažuje“ (uloga na snimanju i broj angažovanih sati) i veza „Zadužuje“ (datum rezervacije i trajanje zaduženja) iz baze podataka informacionog sistema.',
 param: '—',
 ucest: 'Izveštaj se kreira na mesečnom nivou i po zahtevu službe za kadrove i tehničke službe.',
 zagl: 'U zaglavlju su naziv izveštaja i period na koji se odnosi. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Izveštaj ima dva dela. Prvi deo — angažovanje zaposlenih, grupisano po zaposlenom (ime, prezime, radno mesto i organizaciona jedinica), sa redovima: projekat i aktivnost, uloga na snimanju, datum od – datum do i broj angažovanih sati; zbir sati daje se po zaposlenom i ukupno. Drugi deo — zaduženja opreme: inventarski broj, naziv i model opreme, aktivnost za koju je rezervisana, datum rezervacije i trajanje zaduženja, sa ukupnim brojem dana zaduženja po komadu opreme.',
 pristup: 'Rukovodilac produkcije, tehnička služba, služba za kadrove i uprava stanice.'
},
{
 id: 6, tip: 'Parametarski (tabelarni, sa zbirovima)',
 naziv: 'Realizacija ugovora o oglašavanju i naplata po oglašivaču',
 svrha: 'Kartica jednog oglašivača koga korisnik bira pri pokretanju izveštaja: svi njegovi ugovori o oglašavanju, ugovorene stavke, stvarno emitovani spotovi i stanje naplate. Koristi se u pregovorima, pri produženju ugovora i kao osnova za opomenu.',
 izvor: 'Tabele „Klijent“, „Oglašivač“, „Ugovor“, „Ugovor o oglašavanju“, „Stavka ugovora“, „Reklamni sadržaj“, „Reklamni blok“, „Emitovanje reklame“, „Cenovnik reklamnih termina“ i „Faktura“ iz baze podataka informacionog sistema.',
 param: 'Šifra ili naziv oglašivača (obavezan parametar, bira se pri pokretanju izveštaja). Opciono se zadaje i period od – do radi ograničenja na jednu kampanju.',
 ucest: 'Izveštaj se kreira po zahtevu, po završetku svake kampanje i na mesečnom nivou za sve aktivne ugovore.',
 zagl: 'U zaglavlju su naziv izveštaja, naziv izabranog oglašivača sa PIB-om i kontakt osobom, branša i godišnji budžet oglašivača. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Tabelarni prikaz grupisan po ugovoru (broj ugovora, datum sklapanja, važi od – važi do, status i ukupna vrednost ugovora). Unutar ugovora prikazuju se stavke (opis stavke, ugovorena količina u sekundama, jedinična cena, popust i vrednost stavke), a ispod njih emitovani spotovi (datum i vreme emitovanja, reklamni blok i termin, zona iz cenovnika, trajanje spota, naplaćeni iznos i status naplate). Zbirovi po ugovoru: ugovoreno i realizovano u sekundama i u dinarima, razlika, fakturisan i naplaćen iznos sa statusom plaćanja fakture.',
 pristup: 'Sektor marketinga i prodaje, finansijska služba i uprava stanice.'
},
{
 id: 7, tip: 'Tabelarni (grupisani, sa zbirovima)',
 naziv: 'Realizacija plana nabavke sa vrednovanjem ponuda',
 svrha: 'Pregled izvršenja godišnjeg plana nabavke po stavkama i prikaz načina na koji su ponude bodovane pri izboru dobavljača — istovremeno kontrola trošenja i dokaz o transparentnosti postupka nabavke.',
 izvor: 'Tabele „Plan nabavke“, „Stavka plana nabavke“, „Zahtev za nabavku“, „Ponuda dobavljača“, „Dobavljač“, „Kriterijum vrednovanja“, „Narudžbenica“, veza „Ponuđena“ i veza „Vrednuje se“ (broj bodova i komentar ocene) iz baze podataka informacionog sistema.',
 param: '—',
 ucest: 'Izveštaj se kreira na kvartalnom nivou i obavezno na kraju kalendarske godine, kao i po zahtevu uprave.',
 zagl: 'U zaglavlju su naziv izveštaja, oznaka i godina plana nabavke, donosilac plana i status plana. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Tabelarni prikaz po stavci plana: redni broj, opis artikla, količina i jedinica mere, procenjena cena, planirani kvartal, povezani zahtev za nabavku sa statusom, iznos izdate narudžbenice i odstupanje realizovanog od procenjenog iznosa. Za stavke za koje su prikupljene ponude dodaje se pododeljak sa svim ponudama: broj ponude, naziv dobavljača, ukupna cena, rok isporuke, uslovi plaćanja, bodovi po svakom kriterijumu vrednovanja i ukupan broj bodova, uz oznaku izabrane ponude. Na kraju: ukupno planirano, ukupno naručeno i procenat izvršenja plana.',
 pristup: 'Referenti nabavke, komisija za vrednovanje ponuda, finansijska služba i uprava stanice.'
},
{
 id: 8, tip: 'Tabelarni',
 naziv: 'Prava korišćenja medijskog sadržaja i rokovi važenja',
 svrha: 'Pregled svih prava korišćenja sa rokovima važenja i iskorišćenošću dozvoljenog broja emitovanja, radi blagovremene obnove prava i sprečavanja emitovanja sadržaja bez važećeg osnova.',
 izvor: 'Tabele „Pravo korišćenja“, „Pokrivenost pravom“, „Medijski sadržaj“, „Nabavljeni sadržaj“, „Ugovor o nabavci“ i „Zapis o emitovanju“ iz baze podataka informacionog sistema.',
 param: '—',
 ucest: 'Izveštaj se kreira na mesečnom nivou, kao i automatski kada je do isteka nekog prava ostalo manje od 30 dana.',
 zagl: 'U zaglavlju su naziv izveštaja i datum na koji se stanje prava prikazuje. U podnožju su datum kreiranja, ime zaposlenog koji je izveštaj generisao i broj strane.',
 telo: 'Tabelarni prikaz sortiran rastuće po datumu isteka: broj licence, vrsta prava, nosilac prava, teritorija, važi od – važi do, broj dana do isteka, dozvoljen broj emitovanja, iskorišćen broj emitovanja i preostalo, spisak pokrivenih medijskih sadržaja sa oblašću pokrivenosti, kao i status prava (važeće, uskoro ističe, isteklo ili iskorišćeno). Prava kojima ističe rok ili je iskorišćen dozvoljen broj emitovanja izdvajaju se na početku izveštaja.',
 pristup: 'Pravna služba, urednici programa, arhiva medijskog sadržaja i uprava stanice.'
}];

const ROWS = r => [
  ['ID izveštaja', String(r.id)],
  ['Naziv', r.naziv],
  ['Tip izveštaja', r.tip],
  ['Svrha', r.svrha],
  ['Izvor podataka', r.izvor],
  ['Parametri', r.param],
  ['Učestalost i raspodela', r.ucest],
  ['Zaglavlje i podnožje', r.zagl],
  ['Telo izveštaja', r.telo],
  ['Pristup izveštaju', r.pristup]];

const OBLAST = ['Program i emitovanje', 'Program i emitovanje', 'Analitika gledanosti',
  'Produkcija', 'Produkcija i kadrovi', 'Marketing i prodaja', 'Nabavka', 'Pravo i arhiva'];

const ACCESS = [
 ['1', 'qryProgramskaSema → rptProgramskaSema', '—',
  'Grupisanje po programskoj celini; zbir trajanja termina u podnožju grupe i izveštaja.'],
 ['2', 'qryPlayoutLog → rptPlayoutLog', 'Kriterijum na polju Datum:\nBetween [Unesite datum od:] And [Unesite datum do:]',
  'Sortiranje po datumu i stvarnom vremenu; grupisanje po danu, zbir minuta i broj smetnji.'],
 ['3', 'qryGledanostPoZanru (upit sa zbirovima) → rptGledanost sa kontrolom grafikona',
  '—', 'Grupisanje po žanru, Avg ostvarenog rejtinga; grafikon se vezuje za isti upit.'],
 ['4', 'qryTroskoviProjekta → rptTroskoviProjekta', '—',
  'Dva nivoa grupisanja (projekat → aktivnost); zbir iznosa i procenat budžeta.'],
 ['5', 'qryAngazovanje i qryZaduzenjeOpreme → rptAngazovanjeIOprema (podizveštaj)',
  '—', 'Grupisanje po zaposlenom, zbir angažovanih sati; drugi deo kao podizveštaj.'],
 ['6', 'qryKarticaOglasivaca → rptKarticaOglasivaca', 'Kriterijum na polju Šifra klijenta:\n[Unesite šifru oglašivača:]\nili veza na kombinovani okvir sa forme: Forms![frmParametri]![cboOglasivac]',
  'Grupisanje po ugovoru → stavci; zbirovi sekundi i iznosa, poređenje ugovoreno/realizovano.'],
 ['7', 'qryPlanNabavke i qryVrednovanjePonuda → rptPlanNabavke (podizveštaj)', '—',
  'Grupisanje po stavci plana; ponude kao podizveštaj, zbir bodova i procenat izvršenja.'],
 ['8', 'qryPravaKoriscenja → rptPravaKoriscenja', '—',
  'Sortiranje po datumu isteka; izračunata polja za dane do isteka i preostala emitovanja, uslovno oblikovanje statusa.']];

// ----------------------------------------------------------------- dokument
const children = [];
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 160 },
  children: [new TextRun({ text: 'Uvod', size: 30, bold: true })] }));
children.push(p('Televizijska stanica svakodnevno rukuje velikim brojem podataka — od programske šeme i arhive medijskog sadržaja, preko projekata produkcije i ugovora sa oglašivačima, do nabavke opreme, prava korišćenja sadržaja i evidencije stvarno emitovanog programa. Da bi se ti podaci pretvorili u tačne i pravovremene informacije, izveštaji predstavljaju jedan od najvažnijih delova informacionog sistema.'));
children.push(p('Izveštaji omogućavaju zaposlenima i upravi da brzo i pouzdano dođu do potrebnih informacija — bilo da je reč o operativnom praćenju rasporeda emitovanja, kontroli troškova produkcije, realizaciji reklamnih kampanja, izvršenju plana nabavke ili dokazivanju osnova za emitovanje pred regulatornim telom. U nastavku su specificirani izveštaji koje informacioni sistem TV stanice generiše, sa opisom svrhe, izvora podataka, sadržaja i prava pristupa.'));
children.push(p('Sadržaj svakog izveštaja izveden je iz modela podataka (PMOV i ER dijagram) — svaka kolona u telu izveštaja odgovara konkretnom atributu ili izvedenoj vrednosti iz tabela baze podataka. Od ukupno osam izveštaja, dva su parametarska (izveštaji 2 i 6 — korisnik pri pokretanju unosi period, odnosno bira oglašivača), a jedan sadrži grafički prikaz (izveštaj 3).', { after: 240 }));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 160, after: 160 },
  children: [new TextRun({ text: 'Pregled izveštaja', size: 30, bold: true })] }));
children.push(gridTable(['ID', 'Naziv izveštaja', 'Tip', 'Poslovna oblast'],
  R.map((r, i) => [String(r.id), r.naziv, r.tip, OBLAST[i]]), [560, 4166, 2400, 1900]));

children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 },
  children: [new TextRun({ text: 'Specifikacija izveštaja', size: 30, bold: true })] }));
R.forEach((r, i) => {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_2,
    spacing: { before: i ? 300 : 40, after: 120 },
    children: [new TextRun({ text: `Izveštaj ${r.id} – ${r.naziv.toLowerCase()}`, size: 25, bold: true })] }));
  children.push(specTable(ROWS(r)));
});

children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: 'Prilog — realizacija izveštaja u Access-u', size: 30, bold: true })] }));
children.push(p('Svaki izveštaj se u Access-u realizuje kao izveštaj (Report) vezan za upit (Query) koji spaja navedene tabele. Parametarski izveštaji koriste parametar u kriterijumu upita ili referencu na kontrolu na formi, a grafički izveštaj koristi kontrolu grafikona vezanu za upit sa zbirovima.'));
children.push(gridTable(['Izveštaj', 'Upit i izveštaj u Access-u', 'Parametar', 'Grupisanje, sortiranje i zbirovi'],
  ACCESS, [900, 3100, 2400, 2626]));

const doc = new Document({
  styles: { default: { document: { run: { font: 'Calibri', size: 21 } } } },
  sections: [{
    properties: {},
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: 'Specifikacija izveštaja — informacioni sistem TV stanice · strana ', size: 17, color: '666666' }),
                 new TextRun({ children: [PageNumber.CURRENT], size: 17, color: '666666' })] })] }) },
    children }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync('Specifikacija_izvestaja.docx', b);
  console.log('napisano', b.length, 'bajtova'); });
