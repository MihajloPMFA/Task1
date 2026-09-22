const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
        LevelFormat, Footer, PageNumber, convertInchesToTwip } = require('docx');

const SEK = [
['Planiranje programa i emitovanje', [
 'Programska šema se gradi kao povezana celina — sezona, programske celine i termini u njima — pa sistem sam sprečava preklapanje termina i praznine u rasporedu.',
 'Svaki termin nosi zonu gledanosti i redni broj reprize, pa se premijere i reprize planiraju i broje odvojeno, bez ručno vođenih beležaka.',
 'Šema se ne emituje dok je urednik ne odobri, a svaka izmena ostaje zabeležena kroz verziju šeme i datum usvajanja.',
 'Stvarno emitovanje se upisuje uz planirani termin (stvarno vreme početka, stvarno trajanje i napomena o smetnjama), pa se odstupanje od šeme vidi istog dana, a ne na kraju meseca.']],

['Produkcija sadržaja', [
 'Projekat produkcije objedinjuje sve što uz njega ide — aktivnosti, angažovanu ekipu, zaduženu opremu, sirove snimke i troškove — umesto da se ti podaci vode odvojeno i nepovezano.',
 'Svaki trošak se vezuje za konkretnu aktivnost, pa se u svakom trenutku vidi koliko je od odobrenog budžeta potrošeno i na čemu.',
 'Angažovanje se evidentira sa ulogom na snimanju i brojem sati, što je osnova i za raspodelu posla i za obračun angažovanja.',
 'Montirani medijski sadržaj zadržava vezu sa sirovim snimcima i ugrađenim grafičkim i muzičkim elementima, pa se uvek zna od čega je nastao i pod kojim uslovima se elementi smeju koristiti.']],

['Arhiva, medijski sadržaj i prava korišćenja', [
 'Jedinstvena arhiva sa formatom zapisa, datumom arhiviranja i lokacijom u arhivi — sadržaj se pronalazi pretragom, a ne obilaskom uređaja i diskova.',
 'Pravo korišćenja vodi rok važenja, teritoriju i dozvoljen broj emitovanja, a sistem broji iskorišćena emitovanja i upozorava pre isteka ili iscrpljenja prava.',
 'Podela na producirani, nabavljeni i reklamni sadržaj omogućava da se svakoj vrsti prate podaci koji joj zaista pripadaju — verzija mastera, zemlja porekla i cena nabavke, odnosno status provere spota.',
 'Nabavljeni sadržaj ostaje vezan za ugovor o nabavci po kojem je pribavljen, sa datumom preuzimanja i ugovorenom naknadom.']],

['Marketing, prodaja i naplata', [
 'Zakup reklamnog prostora se vodi po ugovoru i stavci ugovora, pa se u svakom trenutku vidi koliko je sekundi ugovoreno, koliko iskorišćeno i koliko preostaje do kraja kampanje.',
 'Reklamni blok zna svoje trajanje, zakupljene i slobodne sekunde, pa se prekoračenje sprečava pri zakazivanju spota, a ne posle emitovanja.',
 'Iznos spota se izvodi iz cenovnika koji važi za zonu i termin, uz ugovoreni popust — bez ručnog računanja i bez razlika u tumačenju cene.',
 'Emitovani spot nosi status naplate i vezu sa fakturom izdatom po ugovoru, pa se nenaplaćene kampanje vide bez naknadnog upoređivanja spiskova.']],

['Nabavka i odnosi sa dobavljačima', [
 'Put od zahteva organizacione jedinice, preko plana nabavke i prikupljenih ponuda, do narudžbenice i prijemnice vodi se kao jedan povezan tok, a ne kao niz odvojenih dokumenata.',
 'Ponude se boduju po unapred utvrđenim kriterijumima, pa izbor dobavljača ostaje dokumentovan i proverljiv.',
 'Prijem robe se evidentira po stavkama, sa primljenom količinom i utvrđenim odstupanjem, što je neposredna osnova za reklamaciju.',
 'Reklamacije se vezuju za konkretnu stavku narudžbenice i ulaze u ocenu dobavljača, pa se pri sledećoj nabavci zna sa kim se posluje.']],

['Oprema i tehnički resursi', [
 'Evidencija opreme po inventarskom broju sa statusom, garancijom i nabavnom vrednošću, uz podelu na snimateljsku i studijsku i emisionu opremu sa podacima koji svakoj vrsti pripadaju.',
 'Rezervacija opreme za aktivnost produkcije sprečava da dva snimanja računaju na isti komad opreme u istom terminu.',
 'Zaduženje opreme zaposlenom beleži i stanje pri vraćanju, pa se odgovornost za oštećenje ne utvrđuje naknadno i po sećanju.',
 'Istorija servisiranja sa opisom radova i troškom pokazuje koja oprema najviše opterećuje održavanje i kada je vreme za zamenu.']],

['Analitika i odlučivanje', [
 'Merenja gledanosti se vezuju za konkretnu emisiju, pa se ostvareni rejting i udeo u terminu porede sa terminom, žanrom i ciljnom publikom.',
 'Povratne informacije gledalaca se vode sa kanalom prijema, statusom obrade i datumom odgovora — vidi se i šta je stiglo i da li je odgovoreno.',
 'Troškovi produkcije i prihod od oglašavanja mogu se dovesti do iste emisije, pa se isplativost programa procenjuje na podacima, a ne na utisku.',
 'Izveštaji se generišu iz baze umesto ručnim prikupljanjem iz nepovezanih tabela, pa su uvek zasnovani na istom i aktuelnom podatku.']],

['Organizacija, zaposleni i kontrola pristupa', [
 'Organizaciona struktura se vodi hijerarhijski, pa se isti izveštaj može napraviti i za pojedinačnu službu i za stanicu u celini.',
 'Podela zaposlenih na urednike, novinare i reportere, tehničko osoblje, referente i servisere nosi podatke koji su svakoj ulozi zaista potrebni.',
 'Nivo ovlašćenja referenta i urednika određuje šta ko sme da odobri, pa se kontrola odobravanja i trošenja ne oslanja na usmeni dogovor.',
 'Podaci o emitovanju, ugovorima i nabavci ostaju na jednom mestu sa istorijom, umesto da zavise od pojedinca koji ih je vodio.']]];

const children = [];
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { after: 200 },
  children: [new TextRun({ text: 'Prednosti i koristi kreiranog informacionog sistema',
    size: 30, bold: true })] }));

const intro = t => new Paragraph({ spacing: { after: 140, line: 276 },
  alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: t, size: 21 })] });

children.push(intro('Kreiranje informacionog sistema TV stanice donosi niz prednosti koje unapređuju svakodnevni rad redakcije, produkcije, tehničke službe, marketinga i nabavke, uz istovremeno bolje iskustvo za oglašivače, dobavljače i gledaoce. Koristi koje slede nisu opšte, već proizlaze iz modela podataka izrađenog za ovu stanicu — iz veza između programske šeme i stvarnog emitovanja, projekta produkcije i njegovih troškova, ugovora o oglašavanju i emitovanih spotova, plana nabavke i prijema robe.'));
children.push(intro('Najvažnije koristi grupisane su po poslovnim oblastima informacionog sistema:'));

SEK.forEach(([naslov, tacke], i) => {
  children.push(new Paragraph({ heading: HeadingLevel.HEADING_2,
    spacing: { before: i ? 260 : 160, after: 110 },
    children: [new TextRun({ text: naslov, size: 25, bold: true })] }));
  tacke.forEach(t => children.push(new Paragraph({
    numbering: { reference: 'tacke', level: 0 },
    spacing: { after: 90, line: 276 }, alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({ text: t, size: 21 })] })));
});

const doc = new Document({
  styles: { default: { document: { run: { font: 'Calibri', size: 21 } } } },
  numbering: { config: [{ reference: 'tacke', levels: [{
    level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: convertInchesToTwip(0.28),
                                    hanging: convertInchesToTwip(0.18) } } } }] }] },
  sections: [{
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: 'Prednosti i koristi kreiranog IS-a · strana ', size: 17, color: '666666' }),
                 new TextRun({ children: [PageNumber.CURRENT], size: 17, color: '666666' })] })] }) },
    children }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync('Prednosti_i_koristi_IS.docx', b);
  console.log('napisano', b.length, 'bajtova · sekcija:', SEK.length,
              '· tacaka:', SEK.reduce((n, s) => n + s[1].length, 0)); });
