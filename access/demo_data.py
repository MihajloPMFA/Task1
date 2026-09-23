# -*- coding: utf-8 -*-
"""Demo podaci - redosled postuje strane kljuceve.  (tabela, kolone, redovi)
Datumi su u Jet formatu #m/d/yyyy#, vreme #hh:nn:ss#, decimale sa tackom."""

D = [
('ORGANIZACIONA_JEDINICA', 'SIFRA_JEDINICE,SIFRA_NADREDJENE_JEDINICE,NAZIV_JEDINICE,TIP_JEDINICE,DATUM_OSNIVANJA', [
 ("'OJ-01'", 'Null', "'Uprava stanice'", "'Uprava'", '#3/1/2004#'),
 ("'OJ-02'", "'OJ-01'", "'Redakcija programa'", "'Redakcija'", '#3/1/2004#'),
 ("'OJ-03'", "'OJ-01'", "'Tehnička služba'", "'Tehnika'", '#3/1/2004#'),
 ("'OJ-04'", "'OJ-01'", "'Marketing i prodaja'", "'Komercijala'", '#5/1/2006#'),
 ("'OJ-05'", "'OJ-01'", "'Služba nabavke'", "'Nabavka'", '#5/1/2006#'),
 ("'OJ-06'", "'OJ-01'", "'Finansijska služba'", "'Finansije'", '#5/1/2006#')]),

('ZAPOSLENI', 'SIFRA_ZAPOSLENOG,SIFRA_JEDINICE,JMBG,IME,PREZIME,RADNO_MESTO,DATUM_ZAPOSLENJA,OSNOVNA_ZARADA,STATUS_ZAPOSLENJA', [
 ("'ZAP-001'", "'OJ-02'", "'0101985800012'", "'Milica'", "'Jovanović'", "'Urednik programa'", '#2/1/2012#', '142000', "'Aktivan'"),
 ("'ZAP-002'", "'OJ-02'", "'1203979800031'", "'Dragan'", "'Stanković'", "'Glavni urednik'", '#9/15/2008#', '168000', "'Aktivan'"),
 ("'ZAP-003'", "'OJ-02'", "'2207990805044'", "'Ana'", "'Ilić'", "'Novinar'", '#4/1/2018#', '96000', "'Aktivan'"),
 ("'ZAP-004'", "'OJ-02'", "'0512988800017'", "'Marko'", "'Petrović'", "'Reporter'", '#10/1/2016#', '92000', "'Aktivan'"),
 ("'ZAP-005'", "'OJ-03'", "'1809983800022'", "'Nenad'", "'Kovač'", "'Snimatelj'", '#6/1/2014#', '88000', "'Aktivan'"),
 ("'ZAP-006'", "'OJ-03'", "'3001992805019'", "'Jelena'", "'Marić'", "'Ton majstor'", '#3/1/2019#', '84000', "'Aktivan'"),
 ("'ZAP-007'", "'OJ-03'", "'1104980800026'", "'Vladimir'", "'Đurić'", "'Operater emitovanja'", '#1/15/2011#', '90000', "'Aktivan'"),
 ("'ZAP-008'", "'OJ-05'", "'2506987800033'", "'Nikola'", "'Antić'", "'Referent nabavke'", '#8/1/2015#', '95000', "'Aktivan'"),
 ("'ZAP-009'", "'OJ-04'", "'0703991800011'", "'Stefan'", "'Perić'", "'Referent marketinga'", '#2/1/2017#', '98000', "'Aktivan'"),
 ("'ZAP-010'", "'OJ-03'", "'1502975800044'", "'Goran'", "'Lukić'", "'Serviser opreme'", '#5/1/2010#', '86000', "'Aktivan'")]),

('UREDNIK', 'SIFRA_ZAPOSLENOG,NIVO_OVLASCENJA,REDAKCIJA', [
 ("'ZAP-001'", "'Urednik emisije'", "'Dokumentarni program'"),
 ("'ZAP-002'", "'Glavni urednik'", "'Informativni program'")]),
('NOVINAR_REPORTER', 'SIFRA_ZAPOSLENOG,OBLAST_IZVESTAVANJA,BROJ_NOVINARSKE_LEGITIM', [
 ("'ZAP-003'", "'Unutrašnja politika'", "'NL-2018-114'"),
 ("'ZAP-004'", "'Ekologija i regioni'", "'NL-2016-087'")]),
('TEHNICKO_OSOBLJE', 'SIFRA_ZAPOSLENOG,SPECIJALIZACIJA,TIP_EKIPE', [
 ("'ZAP-005'", "'Kamera'", "'Terenska'"),
 ("'ZAP-006'", "'Ton'", "'Terenska'"),
 ("'ZAP-007'", "'Emitovanje'", "'Studijska'")]),
('REFERENT', 'SIFRA_ZAPOSLENOG,TIP_REFERENTA,NIVO_OVLASCENJA', [
 ("'ZAP-008'", "'Nabavka'", "'Do 5.000.000 RSD'"),
 ("'ZAP-009'", "'Marketing'", "'Do 3.000.000 RSD'")]),
('SERVISERI', 'SIFRA_ZAPOSLENOG,LICENCA', [("'ZAP-010'", "'Ovlašćeni serviser Sony/Canon'")]),

('OPREMA', 'INVENTARSKI_BROJ,NAZIV_OPREME,MODEL_OPREME,PROIZVODJAC,STATUS_OPREME,DATUM_NABAVKE,GARANCIJA_DO,NABAVNA_VREDNOST', [
 ("'INV-0101'", "'Studijska kamera'", "'PXW-Z750'", "'Sony'", "'U upotrebi'", '#4/12/2023#', '#4/12/2026#', '1850000'),
 ("'INV-0102'", "'Studijska kamera'", "'PXW-Z750'", "'Sony'", "'U upotrebi'", '#4/12/2023#', '#4/12/2026#', '1850000'),
 ("'INV-0103'", "'Reportažna kamera'", "'XF605'", "'Canon'", "'U upotrebi'", '#9/3/2024#', '#9/3/2027#', '640000'),
 ("'INV-0104'", "'Bežični mikrofonski set'", "'UWP-D21'", "'Sony'", "'U upotrebi'", '#2/20/2024#', '#2/20/2026#', '145000'),
 ("'INV-0105'", "'LED panel rasvete'", "'Forza 500B'", "'Nanlite'", "'U upotrebi'", '#6/10/2024#', '#6/10/2026#', '210000'),
 ("'INV-0106'", "'Miks pult'", "'Wing'", "'Behringer'", "'Na servisu'", '#11/5/2022#', '#11/5/2024#', '380000')]),
('SNIMATELJSKA_OPREMA', 'INVENTARSKI_BROJ,TIP_MEMORIJSKOG_SKLADISTA,REZOLUCIJA,TIP_KAMERE', [
 ("'INV-0103'", "'CFexpress'", "'4K UHD'", "'Reportažna'")]),
('STUDIJSKA_I_EMISIONA_OPREMA', 'INVENTARSKI_BROJ,LOKACIJA_U_STUDIJU', [
 ("'INV-0101'", "'Studio 1'"), ("'INV-0102'", "'Studio 2'"),
 ("'INV-0104'", "'Studio 2'"), ("'INV-0105'", "'Studio 2'"), ("'INV-0106'", "'Režija 1'")]),
('AUDIO_OPREMA', 'INVENTARSKI_BROJ,TIP,FREKVENCIJA', [
 ("'INV-0104'", "'Bežični mikrofon'", "'566-608 MHz'"),
 ("'INV-0106'", "'Miks pult'", "'20 Hz - 20 kHz'")]),
('SVETLOSNA_OPREMA', 'INVENTARSKI_BROJ,SNAGA,TIP_SVETLOSTI', [
 ("'INV-0105'", "'500 W'", "'LED bi-color'")]),

('EMISIJA', 'SIFRA_EMISIJE,NAZIV_EMISIJE,ZANR,FORMAT_EMISIJE,PREDVIDJENO_TRAJANJE,CILJNA_PUBLIKA,STATUS_EMISIJE', [
 ("'EM-001'", "'Dnevnik u 19'", "'Informativni'", "'Studijska'", '42', "'Opšta populacija'", "'Aktivna'"),
 ("'EM-002'", "'Jutarnji program'", "'Jutarnji'", "'Studijska'", '180', "'Opšta populacija'", "'Aktivna'"),
 ("'EM-003'", "'Panorama magazin'", "'Magazin'", "'Kombinovana'", '60', "'25-54'", "'Aktivna'"),
 ("'EM-004'", "'Sportski žurnal'", "'Sportski'", "'Studijska'", '25', "'18-49'", "'Aktivna'"),
 ("'EM-005'", "'Reke Vojvodine'", "'Dokumentarni'", "'Terenska'", '25', "'35+'", "'U produkciji'"),
 ("'EM-006'", "'Kulturni pregled'", "'Kulturni'", "'Kombinovana'", '45', "'35+'", "'Aktivna'"),
 ("'EM-007'", "'Dečije carstvo'", "'Dečiji'", "'Studijska'", '30', "'4-12'", "'Aktivna'")]),
]

D += [
('PROGRAMSKA_SEMA', 'SIFRA_SEME,SIFRA_UREDNIKA,NAZIV_SEME,SEZONA,VERZIJA_SEME,DATUM_OD,DATUM_DO,STATUS_SEME,DATUM_USVAJANJA', [
 ("'PS-2026-J'", "'ZAP-002'", "'Jesenja šema 2026'", "'Jesen 2026'", "'v1.2'", '#9/1/2026#', '#12/15/2026#', "'Usvojena'", '#8/20/2026#')]),
('PROGRAMSKA_CELINA', 'SIFRA_SEME,RB_CELINE,NAZIV_CELINE,TIP_CELINE,DATUM,VREME_OD,VREME_DO', [
 ("'PS-2026-J'", '1', "'Jutarnji blok'", "'Jutarnji'", '#9/14/2026#', '#07:00:00#', '#10:00:00#'),
 ("'PS-2026-J'", '2', "'Popodnevni blok'", "'Popodnevni'", '#9/14/2026#', '#16:00:00#', '#19:00:00#'),
 ("'PS-2026-J'", '3', "'Udarni termin'", "'Prime time'", '#9/14/2026#', '#19:00:00#', '#23:00:00#')]),
('TERMIN_EMITOVANJA', 'SIFRA_TERMINA,SIFRA_SEME,RB_CELINE,SIFRA_EMISIJE,DATUM,VREME_POCETKA,TRAJANJE_TERMINA,TIP_TERMINA,ZONA_GLEDANOSTI,STATUS_TERMINA,REDNI_BROJ_REPRIZE', [
 ("'TR-0001'", "'PS-2026-J'", '1', "'EM-002'", '#9/14/2026#', '#07:00:00#', '180', "'Premijera'", "'C'", "'Realizovan'", '0'),
 ("'TR-0002'", "'PS-2026-J'", '2', "'EM-007'", '#9/14/2026#', '#16:00:00#', '30', "'Premijera'", "'B'", "'Realizovan'", '0'),
 ("'TR-0003'", "'PS-2026-J'", '2', "'EM-006'", '#9/14/2026#', '#16:30:00#', '45', "'Premijera'", "'B'", "'Realizovan'", '0'),
 ("'TR-0004'", "'PS-2026-J'", '3', "'EM-001'", '#9/14/2026#', '#19:00:00#', '42', "'Premijera'", "'A'", "'Realizovan'", '0'),
 ("'TR-0005'", "'PS-2026-J'", '3', "'EM-003'", '#9/14/2026#', '#20:00:00#', '60', "'Premijera'", "'A'", "'Otkazan'", '0'),
 ("'TR-0006'", "'PS-2026-J'", '3', "'EM-004'", '#9/14/2026#', '#22:15:00#', '25', "'Premijera'", "'B'", "'Realizovan'", '0'),
 ("'TR-0007'", "'PS-2026-J'", '3', "'EM-001'", '#9/15/2026#', '#19:00:00#', '42', "'Premijera'", "'A'", "'Realizovan'", '0'),
 ("'TR-0008'", "'PS-2026-J'", '3', "'EM-005'", '#9/15/2026#', '#20:00:00#', '25', "'Premijera'", "'A'", "'Realizovan'", '0'),
 ("'TR-0009'", "'PS-2026-J'", '1', "'EM-002'", '#9/15/2026#', '#07:00:00#', '180', "'Premijera'", "'C'", "'Realizovan'", '0'),
 ("'TR-0010'", "'PS-2026-J'", '2', "'EM-006'", '#9/15/2026#', '#16:30:00#', '45', "'Repriza'", "'B'", "'Realizovan'", '1')]),

('MEDIJSKI_SADRZAJ', 'SIFRA_SADRZAJA,NAZIV_SADRZAJA,TRAJANJE,FORMAT_ZAPISA,DATUM_ARHIVIRANJA,LOKACIJA_U_ARHIVI', [
 ("'MS-0001'", "'Dnevnik 14.09.2026'", '42', "'MXF 1080i'", '#9/14/2026#', "'ARH/2026/09/A-114'"),
 ("'MS-0002'", "'Jutarnji program 14.09.2026'", '180', "'MXF 1080i'", '#9/14/2026#', "'ARH/2026/09/A-115'"),
 ("'MS-0003'", "'Kulturni pregled - epizoda 12'", '45', "'MXF 1080i'", '#9/14/2026#', "'ARH/2026/09/A-116'"),
 ("'MS-0004'", "'Dečije carstvo - epizoda 30'", '30', "'MXF 1080i'", '#9/14/2026#', "'ARH/2026/09/A-117'"),
 ("'MS-0005'", "'Sportski žurnal 14.09.2026'", '25', "'MXF 1080i'", '#9/14/2026#', "'ARH/2026/09/A-118'"),
 ("'MS-0006'", "'Reke Vojvodine - epizoda 1'", '25', "'MXF 2160p'", '#9/10/2026#', "'ARH/2026/09/D-021'"),
 ("'MS-0007'", "'Dnevnik 15.09.2026'", '42', "'MXF 1080i'", '#9/15/2026#', "'ARH/2026/09/A-119'"),
 ("'MS-0008'", "'Spot Delta Market - Jesenja akcija'", '30', "'MP4 1080p'", '#9/1/2026#', "'ARH/REK/2026/S-4417'"),
 ("'MS-0009'", "'Spot NIS Petrol - Zimska priprema'", '30', "'MP4 1080p'", '#9/1/2026#', "'ARH/REK/2026/S-4290'"),
 ("'MS-0010'", "'Strani dokumentarac - Divlja Evropa'", '50', "'MXF 1080p'", '#7/15/2026#', "'ARH/NAB/2026/N-008'")]),
('PRODUCIRANI_SADRZAJ', 'SIFRA_SADRZAJA,DATUM_PRODUKCIJE,VERZIJA_MASTERA', [
 ("'MS-0001'", '#9/14/2026#', "'v1'"), ("'MS-0003'", '#9/12/2026#', "'v2'"),
 ("'MS-0006'", '#9/9/2026#', "'v3'"), ("'MS-0007'", '#9/15/2026#', "'v1'")]),

('KLIJENT', 'SIFRA_KLIJENTA,NAZIV_KLIJENTA,PIB,MATICNI_BROJ,ULICA_I_BROJ,GRAD,POSTANSKI_BROJ,KONTAKT_OSOBA', [
 ("'KL-001'", "'Delta Market d.o.o.'", "'100234567'", "'07123456'", "'Bulevar oslobođenja 12'", "'Novi Sad'", "'21000'", "'Ivana Simić'"),
 ("'KL-002'", "'NIS Petrol a.d.'", "'100112233'", "'20011223'", "'Narodnog fronta 12'", "'Novi Sad'", "'21000'", "'Petar Vuković'"),
 ("'KL-003'", "'Telekom Srbija a.d.'", "'100445566'", "'17162543'", "'Takovska 2'", "'Beograd'", "'11000'", "'Maja Nikolić'"),
 ("'KL-004'", "'RTV Kanal Plus'", "'101778899'", "'08877665'", "'Trg slobode 3'", "'Subotica'", "'24000'", "'Zoran Balint'")]),
('OGLASIVAC', 'SIFRA_KLIJENTA,BRANSA,GODISNJI_BUDZET', [
 ("'KL-001'", "'Maloprodaja'", '24000000'),
 ("'KL-002'", "'Naftna industrija'", '18000000'),
 ("'KL-003'", "'Telekomunikacije'", '31000000')]),
('KUPAC_SADRZAJA', 'SIFRA_KLIJENTA,TIP_MEDIJA,TERITORIJA_EMITOVANJA', [
 ("'KL-004'", "'Regionalna TV'", "'Severna Bačka'")]),

('DOBAVLJAC', 'SIFRA_DOBAVLJACA,NAZIV_DOBAVLJACA,PIB,MATICNI_BROJ,ADRESA,OCENA_DOBAVLJACA', [
 ("'DOB-01'", "'AV Studio d.o.o.'", "'102334455'", "'20334455'", "'Cara Dušana 45, Novi Sad'", '9.1'),
 ("'DOB-02'", "'TechnoMedia d.o.o.'", "'103445566'", "'21445566'", "'Vojvode Stepe 88, Beograd'", '7.8'),
 ("'DOB-03'", "'Panorama Oprema d.o.o.'", "'104556677'", "'22556677'", "'Industrijska 7, Zrenjanin'", '7.2'),
 ("'DOB-04'", "'Global Media Rights Ltd'", "'105667788'", "'23667788'", "'Praha 3, Češka'", '8.4')]),
('DOBAVLJAC_OPREME_I_MATERIJALA', 'SIFRA_DOBAVLJACA,ASORTIMAN,OVLASCENI_SERVIS', [
 ("'DOB-01'", "'Kamere, stativi, optika'", "'Da'"),
 ("'DOB-02'", "'Emisiona i studijska oprema'", "'Da'"),
 ("'DOB-03'", "'Rasveta i potrošni materijal'", "'Ne'")]),
('DOBAVLJAC_TV_SADRZAJA', 'SIFRA_DOBAVLJACA,VRSTA_SADRZAJA,KATALOG_PONUDE', [
 ("'DOB-04'", "'Dokumentarni program'", "'Katalog 2026 - Divlja Evropa'")]),
]

D += [
('UGOVOR', 'BROJ_UGOVORA,SIFRA_KLIJENTA,DATUM_SKLAPANJA,VAZI_OD,VAZI_DO,UKUPNA_VREDNOST,STATUS_UGOVORA', [
 ("'UG-2026-0087'", "'KL-001'", '#8/20/2026#', '#9/1/2026#', '#12/31/2026#', '18720000', "'Aktivan'"),
 ("'UG-2026-0044'", "'KL-002'", '#7/10/2026#', '#8/1/2026#', '#12/31/2026#', '10980000', "'Aktivan'"),
 ("'UG-2026-0031'", "'KL-003'", '#6/1/2026#', '#7/1/2026#', '#12/31/2026#', '14850000', "'Aktivan'"),
 ("'UG-2026-0110'", "'KL-004'", '#9/1/2026#', '#9/15/2026#', '#3/15/2027#', '2400000', "'Aktivan'"),
 ("'UG-2026-0120'", 'Null', '#7/1/2026#', '#7/1/2026#', '#6/30/2027#', '3600000', "'Aktivan'")]),
('UGOVOR_O_OGLASAVANJU', 'BROJ_UGOVORA,UGOVORENI_TERMINI', [
 ("'UG-2026-0087'", "'Zona A, radnim danima 19-23h'"),
 ("'UG-2026-0044'", "'Zona A i B, vikendom'"),
 ("'UG-2026-0031'", "'Zona A, svakodnevno'")]),
('UGOVOR_O_PRODAJI_TV_SADRZAJA', 'BROJ_UGOVORA,PRENOS_VLASNISTVA,OBIM_USTUPLJENIH_PRAVA', [
 ("'UG-2026-0110'", "'Ne'", "'Emitovanje, 6 meseci, Severna Bačka'")]),
('UGOVOR_O_NABAVCI', 'BROJ_UGOVORA,SIFRA_DOBAVLJACA,VRSTA_REKLAMIRANJA,ROK_ISPORUKE,USLOVI_PLACANJA', [
 ("'UG-2026-0120'", "'DOB-04'", "'Pisana reklamacija u roku od 8 dana'", '#7/15/2026#', "'60 dana odloženo'")]),
('NABAVLJENI_SADRZAJ', 'SIFRA_SADRZAJA,BROJ_UGOVORA,ZEMLJA_POREKLA,CENA_NABAVKE,DATUM_PREUZIMANJA,UGOVORENA_NAKNADA', [
 ("'MS-0010'", "'UG-2026-0120'", "'Češka'", '1200000', '#7/15/2026#', '1200000')]),
('REKLAMNI_SADRZAJ', 'SIFRA_SADRZAJA,SIFRA_OGLASIVACA,DATUM_PRIJEMA,STATUS', [
 ("'MS-0008'", "'KL-001'", '#9/1/2026#', "'Proveren'"),
 ("'MS-0009'", "'KL-002'", '#9/1/2026#', "'Proveren'")]),

('CENOVNIK_REKL_TERMINA', 'SIFRA_CENOVNIKA,VAZI_OD,VAZI_DO,ZONA,CENA_PO_SEKUNDI,TIP_CENOVNOG_PAKETA', [
 ("'CN-2026-03'", '#9/1/2026#', '#12/31/2026#', "'A'", '4500', "'Udarni termin'"),
 ("'CN-2026-04'", '#9/1/2026#', '#12/31/2026#', "'B'", '2200', "'Dnevni termin'"),
 ("'CN-2026-05'", '#9/1/2026#', '#12/31/2026#', "'C'", '1100', "'Noćni termin'")]),
('REKLAMNI_BLOK', 'SIFRA_BLOKA,SIFRA_TERMINA,SIFRA_CENOVNIKA,DATUM,VREME_POCETKA,TRAJANJE_BLOKA,ZAKUPLJENO_SEKUNDI,SLOBODNO_SEKUNDI,ISKORISCENOST,STATUS_BLOKA', [
 ("'RB-1187'", "'TR-0004'", "'CN-2026-03'", '#9/14/2026#', '#19:42:00#', '180', '150', '30', '83.33', "'Popunjen'"),
 ("'RB-1188'", "'TR-0006'", "'CN-2026-04'", '#9/14/2026#', '#22:40:00#', '120', '60', '60', '50.00', "'Delimično'"),
 ("'RB-1189'", "'TR-0007'", "'CN-2026-03'", '#9/15/2026#', '#19:42:00#', '180', '120', '60', '66.67', "'Delimično'")]),
('STAVKA_UGOVORA', 'BROJ_UGOVORA,RB_STAVKE,OPIS_STAVKE,KOLICINA_SEKUNDE,JEDINICNA_CENA,POPUST,VREDNOST_STAVKE', [
 ("'UG-2026-0087'", '1', "'TV spot 30 sekundi, jesenja kampanja'", '1800', '4500', '10.00', '7290000'),
 ("'UG-2026-0087'", '2', "'TV spot 15 sekundi, podrška kampanji'", '900', '4500', '10.00', '3645000'),
 ("'UG-2026-0044'", '1', "'TV spot 30 sekundi, zimska priprema'", '1200', '4500', '5.00', '5130000'),
 ("'UG-2026-0031'", '1', "'TV spot 30 sekundi, godišnji zakup'", '2400', '4500', '15.00', '9180000')]),
('EMITOVANJE_REKLAME', 'SIFRA_BLOKA,RB_U_BLOKU,SIFRA_SADRZAJA,BROJ_UGOVORA,RB_STAVKE_UGOVORA,DATUM_EMITOVANJA,VREME_EMITOVANJA,TRAJANJE_SPOTA,NAPLACENI_IZNOS,STATUS_NAPLATE', [
 ("'RB-1187'", '1', "'MS-0008'", "'UG-2026-0087'", '1', '#9/14/2026#', '#19:42:10#', '30', '121500', "'Fakturisano'"),
 ("'RB-1187'", '2', "'MS-0009'", "'UG-2026-0044'", '1', '#9/14/2026#', '#19:42:45#', '30', '128250', "'Naplaćeno'"),
 ("'RB-1187'", '3', "'MS-0008'", "'UG-2026-0087'", '2', '#9/14/2026#', '#19:43:20#', '15', '60750', "'Fakturisano'"),
 ("'RB-1188'", '1', "'MS-0009'", "'UG-2026-0044'", '1', '#9/14/2026#', '#22:40:15#', '30', '62700', "'Naplaćeno'"),
 ("'RB-1189'", '1', "'MS-0008'", "'UG-2026-0087'", '1', '#9/15/2026#', '#19:42:10#', '30', '121500', "'Nenaplaćeno'"),
 ("'RB-1189'", '2', "'MS-0008'", "'UG-2026-0087'", '2', '#9/15/2026#', '#19:42:45#', '15', '60750', "'Nenaplaćeno'")]),
('FAKTURA', 'BROJ_FAKTURE,BROJ_UGOVORA,DATUM_IZDAVANJA,ROK_PLACANJA,SMER,OSNOVICA,IZNOS_PDV,STATUS_PLACANJA,IZNOS_ZA_PLACANJE', [
 ("'FA-2026-0301'", "'UG-2026-0087'", '#9/30/2026#', '#10/30/2026#', "'Izlazna'", '182250', '36450', "'Neplaćena'", '218700'),
 ("'FA-2026-0302'", "'UG-2026-0044'", '#9/30/2026#', '#10/15/2026#', "'Izlazna'", '190950', '38190', "'Plaćena'", '229140'),
 ("'FA-2026-0410'", 'Null', '#5/20/2026#', '#6/20/2026#', "'Ulazna'", '186000', '37200', "'Plaćena'", '223200'),
 ("'FA-2026-0411'", 'Null', '#6/8/2026#', '#7/8/2026#', "'Ulazna'", '92000', '18400', "'Plaćena'", '110400')]),

('PROJEKAT_PRODUKCIJE', 'SIFRA_PROJEKTA,SIFRA_UREDNIKA,SIFRA_EMISIJE,NAZIV_PROJEKTA,DATUM_POCETKA,DATUM_ZAVRSETKA,ODOBREN_BUDZET,STATUS_PROJEKTA,VRSTA_PRODUKCIJE,OPIS_PROJEKTA', [
 ("'PRJ-2026-014'", "'ZAP-001'", "'EM-005'", "'Dokumentarni serijal Reke Vojvodine'", '#3/1/2026#', '#6/30/2026#', '1800000', "'U realizaciji'", "'Sopstvena produkcija'", "'Šestodelni serijal, snimanje u tri etape.'"),
 ("'PRJ-2026-021'", "'ZAP-002'", "'EM-003'", "'Panorama magazin - jesenja sezona'", '#8/1/2026#', '#12/15/2026#', '1200000', "'U realizaciji'", "'Sopstvena produkcija'", "'Nedeljni magazin, 16 epizoda.'")]),
('AKTIVNOST_PRODUKCIJE', 'SIFRA_PROJEKTA,RB_AKTIVNOSTI,NAZIV_AKTIVNOSTI,DATUM_OD,DATUM_DO,VRSTA_AKTIVNOSTI,LOKACIJA_SNIMANJA,STATUS_AKTIVNOSTI', [
 ("'PRJ-2026-014'", '1', "'Istraživanje i scenario'", '#3/1/2026#', '#3/20/2026#', "'Priprema'", "'Redakcija, Novi Sad'", "'Završena'"),
 ("'PRJ-2026-014'", '2', "'Snimanje - gornji tok Tise'", '#4/6/2026#', '#4/12/2026#', "'Terensko snimanje'", "'Kanjiža / Senta'", "'Završena'"),
 ("'PRJ-2026-014'", '3', "'Snimanje - Dunav kod Apatina'", '#5/4/2026#', '#5/11/2026#', "'Terensko snimanje'", "'Apatin'", "'U toku'"),
 ("'PRJ-2026-014'", '4', "'Montaža i postprodukcija'", '#5/25/2026#', '#6/19/2026#', "'Postprodukcija'", "'Montaža 1'", "'Planirana'"),
 ("'PRJ-2026-021'", '1', "'Priprema sezone'", '#8/1/2026#', '#8/20/2026#', "'Priprema'", "'Redakcija, Novi Sad'", "'Završena'"),
 ("'PRJ-2026-021'", '2', "'Studijsko snimanje epizoda 1-8'", '#9/1/2026#', '#10/20/2026#', "'Studijsko snimanje'", "'Studio 2'", "'U toku'")]),
('TROSAK_PRODUKCIJE', 'SIFRA_PROJEKTA,RB_AKTIVNOSTI,RB_TROSKA,BROJ_FAKTURE,VRSTA_TROSKA,IZNOS,DATUM_NASTANKA,OPIS_TROSKA', [
 ("'PRJ-2026-014'", '1', '1', 'Null', "'Honorari'", '180000', '#3/25/2026#', "'Autorski honorar za scenario'"),
 ("'PRJ-2026-014'", '2', '1', "'FA-2026-0410'", "'Putni troškovi'", '223200', '#4/15/2026#', "'Smeštaj i prevoz ekipe'"),
 ("'PRJ-2026-014'", '2', '2', 'Null', "'Honorari'", '240000', '#4/20/2026#', "'Angažovanje terenske ekipe'"),
 ("'PRJ-2026-014'", '3', '1', "'FA-2026-0411'", "'Putni troškovi'", '110400', '#5/12/2026#', "'Smeštaj i prevoz ekipe'"),
 ("'PRJ-2026-014'", '3', '2', 'Null', "'Zakup opreme'", '150000', '#5/10/2026#', "'Zakup dodatne optike'"),
 ("'PRJ-2026-014'", '4', '1', 'Null', "'Postprodukcija'", '340000', '#6/10/2026#', "'Montaža, grafika i ton'"),
 ("'PRJ-2026-021'", '1', '1', 'Null', "'Honorari'", '120000', '#8/18/2026#', "'Priprema formata i najave'"),
 ("'PRJ-2026-021'", '2', '1', 'Null', "'Scenografija'", '260000', '#9/5/2026#', "'Izrada scenografije u Studiju 2'")]),
('ANGAZOVANJE_NA_AKTIVNOSTI', 'SIFRA_PROJEKTA,RB_AKTIVNOSTI,SIFRA_ZAPOSLENOG,ULOGA_NA_SNIMANJU,DATUM_OD,DATUM_DO,BROJ_ANGAZOVANIH_SATI', [
 ("'PRJ-2026-014'", '1', "'ZAP-003'", "'Autor i novinar'", '#3/1/2026#', '#3/20/2026#', '96'),
 ("'PRJ-2026-014'", '2', "'ZAP-003'", "'Novinar na terenu'", '#4/6/2026#', '#4/12/2026#', '56'),
 ("'PRJ-2026-014'", '2', "'ZAP-005'", "'Snimatelj'", '#4/6/2026#', '#4/12/2026#', '56'),
 ("'PRJ-2026-014'", '2', "'ZAP-006'", "'Ton majstor'", '#4/6/2026#', '#4/12/2026#', '48'),
 ("'PRJ-2026-014'", '3', "'ZAP-004'", "'Reporter'", '#5/4/2026#', '#5/11/2026#', '64'),
 ("'PRJ-2026-014'", '3', "'ZAP-005'", "'Snimatelj'", '#5/4/2026#', '#5/11/2026#', '64'),
 ("'PRJ-2026-021'", '2', "'ZAP-005'", "'Snimatelj'", '#9/1/2026#', '#10/20/2026#', '120'),
 ("'PRJ-2026-021'", '2', "'ZAP-006'", "'Ton majstor'", '#9/1/2026#', '#10/20/2026#', '110')]),
('REZERVACIJA_OPREME', 'SIFRA_PROJEKTA,RB_AKTIVNOSTI,INVENTARSKI_BROJ,DATUM_REZERVACIJE,TRAJANJE_ZADUZENJA', [
 ("'PRJ-2026-014'", '2', "'INV-0103'", '#4/5/2026#', '8'),
 ("'PRJ-2026-014'", '2', "'INV-0104'", '#4/5/2026#', '8'),
 ("'PRJ-2026-014'", '3', "'INV-0103'", '#5/3/2026#', '9'),
 ("'PRJ-2026-021'", '2', "'INV-0101'", '#9/1/2026#', '50'),
 ("'PRJ-2026-021'", '2', "'INV-0105'", '#9/1/2026#', '50')]),
]

D += [
('ZAPIS_O_EMITOVANJU', 'SIFRA_TERMINA,RB_EMITOVANJA,SIFRA_SADRZAJA,STATUS_REALIZACIJE,STVARNO_VREME_POCETKA,STVARNO_TRAJANJE,NAPOMENA_O_SMETNJAMA,OPERATER_EMITOVANJA', [
 ("'TR-0001'", '1', "'MS-0002'", "'Realizovano'", '#07:00:05#', '180', 'Null', "'Vladimir Đurić'"),
 ("'TR-0002'", '1', "'MS-0004'", "'Realizovano'", '#16:00:00#', '30', 'Null', "'Vladimir Đurić'"),
 ("'TR-0003'", '1', "'MS-0003'", "'Realizovano'", '#16:30:10#', '47', "'Produžen intervju sa gostom'", "'Vladimir Đurić'"),
 ("'TR-0004'", '1', "'MS-0001'", "'Realizovano'", '#19:00:02#', '44', "'Produžen zbog vanredne vesti'", "'Vladimir Đurić'"),
 ("'TR-0005'", '1', "'MS-0010'", "'Otkazano'", '#20:00:00#', '0', "'Kvar emisione opreme - miks pult'", "'Vladimir Đurić'"),
 ("'TR-0006'", '1', "'MS-0005'", "'Realizovano'", '#22:15:00#', '22', "'Skraćen zbog prenosa utakmice'", "'Vladimir Đurić'"),
 ("'TR-0007'", '1', "'MS-0007'", "'Realizovano'", '#19:00:01#', '42', 'Null', "'Vladimir Đurić'"),
 ("'TR-0008'", '1', "'MS-0006'", "'Realizovano'", '#20:00:00#', '25', 'Null', "'Vladimir Đurić'"),
 ("'TR-0009'", '1', "'MS-0002'", "'Realizovano'", '#07:00:00#', '176', "'Prekid signala u trajanju 3 min'", "'Vladimir Đurić'"),
 ("'TR-0010'", '1', "'MS-0003'", "'Realizovano'", '#16:30:00#', '45', 'Null', "'Vladimir Đurić'")]),

('PRAVO_KORISCENJA', 'BROJ_LICENCE,VRSTA_PRAVA,DATUM_OD,DATUM_DO,DOZVOLJENO_EMITOVANJA,ISKORISCENO_EMITOVANJA,TERITORIJA,NOSILAC_PRAVA', [
 ("'LIC-2026-001'", "'Emitovanje - sopstvena produkcija'", '#1/1/2026#', '#12/31/2030#', '999', '12', "'Srbija'", "'TV Panorama'"),
 ("'LIC-2026-014'", "'Emitovanje - kupljeni format'", '#7/15/2026#', '#10/15/2026#', '6', '5', "'Srbija'", "'Global Media Rights Ltd'"),
 ("'LIC-2026-022'", "'Muzička prava'", '#1/1/2026#', '#12/31/2026#', '999', '48', "'Srbija'", "'SOKOJ'"),
 ("'LIC-2025-088'", "'Emitovanje - arhivski materijal'", '#6/1/2025#', '#9/30/2026#', '20', '20', "'Srbija'", "'Filmski centar'")]),
('POKRIVENOST_PRAVOM', 'BROJ_LICENCE,SIFRA_SADRZAJA,OBLAST_POKRIVENOSTI', [
 ("'LIC-2026-001'", "'MS-0001'", "'Linearno emitovanje'"),
 ("'LIC-2026-001'", "'MS-0003'", "'Linearno emitovanje'"),
 ("'LIC-2026-001'", "'MS-0006'", "'Linearno emitovanje i internet'"),
 ("'LIC-2026-001'", "'MS-0007'", "'Linearno emitovanje'"),
 ("'LIC-2026-014'", "'MS-0010'", "'Linearno emitovanje'"),
 ("'LIC-2026-022'", "'MS-0002'", "'Muzika u jutarnjem programu'")]),

('MERENJE_GLEDANOSTI', 'SIFRA_MERENJA,DATUM_MERENJA,IZVOR_MERENJA,CILJNA_GRUPA,RATING,SHARE_UDEO,BROJ_GLEDALACA,PROSECNO_GLEDANJE', [
 ("'MG-0914'", '#9/14/2026#', "'Nielsen'", "'4+'", '6.80', '22.40', '470000', '28'),
 ("'MG-0915'", '#9/15/2026#', "'Nielsen'", "'4+'", '6.40', '21.10', '442000', '26'),
 ("'MG-0916'", '#9/16/2026#', "'Nielsen'", "'4+'", '7.10', '23.80', '491000', '31')]),
('MERENJE_EMISIJE', 'SIFRA_MERENJA,SIFRA_EMISIJE,OSTVARENI_RATING,UDEO_U_TERMINU', [
 ("'MG-0914'", "'EM-001'", '9.40', '31.20'), ("'MG-0914'", "'EM-002'", '4.10', '18.60'),
 ("'MG-0914'", "'EM-003'", '7.80', '25.40'), ("'MG-0914'", "'EM-004'", '7.10', '24.10'),
 ("'MG-0914'", "'EM-006'", '6.20', '19.80'), ("'MG-0914'", "'EM-007'", '5.10', '17.20'),
 ("'MG-0915'", "'EM-001'", '9.10', '30.40'), ("'MG-0915'", "'EM-002'", '3.90', '17.90'),
 ("'MG-0915'", "'EM-005'", '6.90', '22.60'), ("'MG-0915'", "'EM-006'", '6.00', '19.10'),
 ("'MG-0916'", "'EM-001'", '9.70', '32.10'), ("'MG-0916'", "'EM-003'", '8.00', '26.20'),
 ("'MG-0916'", "'EM-004'", '7.30', '24.80'), ("'MG-0916'", "'EM-005'", '7.20', '23.40')]),

('PLAN_NABAVKE', 'SIFRA_PLANA,GODINA_PLANA,DATUM_DONOSENJA,STATUS_PLANA,UKUPNA_VREDNOST,DONOSILAC_PLANA', [
 ("'PN-2026'", '2026', '#12/20/2025#', "'Usvojen'", '14450000', "'Uprava stanice'")]),
('STAVKA_PLANA_NABAVKE', 'SIFRA_PLANA,RB_STAVKE,OPIS_ARTIKLA,KOLICINA,JEDINICA_MERE,PROCENJENA_CENA,PLANIRANI_KVARTAL', [
 ("'PN-2026'", '1', "'Studijske kamere i stativi'", '2', "'kom'", '4200000', "'Q2'"),
 ("'PN-2026'", '2', "'Rasveta studija 2'", '6', "'kom'", '1850000', "'Q2'"),
 ("'PN-2026'", '3', "'Audio miks pult'", '1', "'kom'", '2400000', "'Q3'"),
 ("'PN-2026'", '4', "'Servis emisione opreme'", '1', "'usluga'", '1200000', "'Q1-Q4'"),
 ("'PN-2026'", '5', "'Prava emitovanja - strani format'", '1', "'licenca'", '3600000', "'Q3'"),
 ("'PN-2026'", '6', "'Potrošni materijal'", '1', "'paket'", '780000', "'Q1-Q4'"),
 ("'PN-2026'", '7', "'Kancelarijski materijal'", '1', "'paket'", '420000', "'Q1-Q4'")]),
('ZAHTEV_ZA_NABAVKU', 'BROJ_ZAHTEVA,SIFRA_JEDINICE,SIFRA_PLANA,DATUM_ZAHTEVA,VRSTA_NABAVKE,PREDMET_ZAHTEVA,STATUS_ZAHTEVA,PRIORITET,PROCENJENA_VREDNOST', [
 ("'ZN-2026-0042'", "'OJ-03'", "'PN-2026'", '#3/10/2026#', "'Oprema'", "'Zamena dve studijske kamere i stativa - Studio 2'", "'Realizovan'", "'Visok'", '4200000'),
 ("'ZN-2026-0051'", "'OJ-03'", "'PN-2026'", '#4/2/2026#', "'Oprema'", "'Rasveta studija 2 - LED paneli'", "'Realizovan'", "'Srednji'", '1850000'),
 ("'ZN-2026-0067'", "'OJ-03'", "'PN-2026'", '#6/18/2026#', "'Oprema'", "'Audio miks pult za režiju 1'", "'U postupku'", "'Visok'", '2400000')]),
('PONUDA_DOBAVLJACA', 'BROJ_PONUDE,SIFRA_DOBAVLJACA,DATUM_PRIJEMA,VAZI_DO,UKUPNA_CENA,ROK_ISPORUKE,USLOVI_PLACANJA,STATUS_PONUDE,UKUPNO_BODOVA', [
 ("'PD-2026-0113'", "'DOB-01'", '#3/25/2026#', '#4/30/2026#', '4480000', '#4/20/2026#', "'Avans 50%'", "'Nije izabrana'", '7.60'),
 ("'PD-2026-0114'", "'DOB-02'", '#3/26/2026#', '#4/30/2026#', '3950000', '#5/5/2026#', "'60 dana odloženo'", "'Izabrana'", '9.15'),
 ("'PD-2026-0115'", "'DOB-03'", '#3/27/2026#', '#4/30/2026#', '4180000', '#5/15/2026#', "'45 dana odloženo'", "'Nije izabrana'", '7.15')]),
('KRITERIJUM_VREDNOVANJA', 'SIFRA_KRITERIJUMA,NAZIV_KRITERIJUMA,NACIN_BODOVANJA,OPIS_KRITERIJUMA', [
 ("'KR-01'", "'Ponuđena cena'", "'Najniža cena = 10 bodova'", "'Ponder 40%'"),
 ("'KR-02'", "'Rok isporuke'", "'Kraći rok = više bodova'", "'Ponder 20%'"),
 ("'KR-03'", "'Uslovi plaćanja'", "'Duže odloženo = više bodova'", "'Ponder 15%'"),
 ("'KR-04'", "'Garantni rok i servis'", "'Duža garancija = više bodova'", "'Ponder 15%'"),
 ("'KR-05'", "'Dosadašnja ocena dobavljača'", "'Iz evidencije reklamacija'", "'Ponder 10%'")]),
('OCENA_PONUDE', 'BROJ_PONUDE,SIFRA_KRITERIJUMA,BROJ_BODOVA,KOMENTAR_OCENE', [
 ("'PD-2026-0113'", "'KR-01'", '7.00', 'Null'), ("'PD-2026-0113'", "'KR-02'", '9.00', "'Najkraći rok'"),
 ("'PD-2026-0113'", "'KR-03'", '6.00', 'Null'), ("'PD-2026-0113'", "'KR-04'", '8.00', 'Null'),
 ("'PD-2026-0113'", "'KR-05'", '9.00', "'14 isporuka bez reklamacije'"),
 ("'PD-2026-0114'", "'KR-01'", '10.00', "'Najniža cena'"), ("'PD-2026-0114'", "'KR-02'", '7.00', 'Null'),
 ("'PD-2026-0114'", "'KR-03'", '9.00', 'Null'), ("'PD-2026-0114'", "'KR-04'", '9.00', "'36 meseci, ovlašćeni servis'"),
 ("'PD-2026-0114'", "'KR-05'", '8.00', 'Null'),
 ("'PD-2026-0115'", "'KR-01'", '8.00', 'Null'), ("'PD-2026-0115'", "'KR-02'", '6.00', 'Null'),
 ("'PD-2026-0115'", "'KR-03'", '8.00', 'Null'), ("'PD-2026-0115'", "'KR-04'", '5.00', "'Bez ovlašćenog servisa'"),
 ("'PD-2026-0115'", "'KR-05'", '7.00', 'Null')]),
('PONUDJENA_STAVKA', 'SIFRA_PLANA,RB_STAVKE,BROJ_PONUDE,PONUDJENA_CENA,ROK_ZA_STAVKU', [
 ("'PN-2026'", '1', "'PD-2026-0113'", '4480000', '#4/20/2026#'),
 ("'PN-2026'", '1', "'PD-2026-0114'", '3950000', '#5/5/2026#'),
 ("'PN-2026'", '1', "'PD-2026-0115'", '4180000', '#5/15/2026#')]),
('NARUDZBENICA', 'BROJ_NARUDZBENICE,SIFRA_DOBAVLJACA,DATUM_IZDAVANJA,ROK_ISPORUKE,MESTO_ISPORUKE,UKUPAN_IZNOS,STATUS_NARUDZBINE', [
 ("'NR-2026-0211'", "'DOB-02'", '#4/5/2026#', '#5/5/2026#', "'TV Panorama, Novi Sad'", '3950000', "'Isporučena'"),
 ("'NR-2026-0238'", "'DOB-03'", '#4/20/2026#', '#5/20/2026#', "'TV Panorama, Novi Sad'", '2080000', "'Isporučena'")]),
]
