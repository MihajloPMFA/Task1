-- =====================================================================
--  ER model informacionog sistema TV stanice
--  Relaciona sema izvedena iz PMOV dijagrama PMOV_TV_stanica_2_1_1.vsdx
--
--  Namena: reverzni inzenjering u CA ERwin Data Modeler r7.3
--          (File > New > Logical/Physical  ->  Tools > Reverse Engineer
--           -> Reverse Engineer From: Script File -> ovaj .sql fajl)
--
--  69 tabela, 405 kolona, 84 stranih kljuceva
-- =====================================================================


-- =====================================================================
-- CELINA: ORGANIZACIJA I KADROVI (7 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- ORGANIZACIONA_JEDINICA
-- PMOV: jak entitet ORGANIZACIONA JEDINICA + rekurzivna veza PODREDJENA (0,N)-(0,1)
-- ---------------------------------------------------------------------
CREATE TABLE ORGANIZACIONA_JEDINICA
(
    SIFRA_JEDINICE             CHAR(18)      NOT NULL,                  /* PK - SIFRA JEDINICE */
    SIFRA_NADREDJENE_JEDINICE  CHAR(18),                                /* FK - veza PODREDJENA (nadredjena jedinica) */
    NAZIV_JEDINICE             VARCHAR(60)   NOT NULL,                  /* NAZIV JEDINICE */
    TIP_JEDINICE               VARCHAR(30),                             /* TIP JEDINICE */
    OPIS_DELATNOSTI            VARCHAR(255),                            /* OPIS DELATNOSTI */
    DATUM_OSNIVANJA            DATE,                                    /* DATUM OSNIVANJA */
    BROJ_ZAPOSLENIH            INTEGER,                                 /* BROJ ZAPOSLENIH - izvedeni atribut */
    CONSTRAINT PK_ORGANIZACIONA_JEDINICA PRIMARY KEY (SIFRA_JEDINICE)
);

-- ---------------------------------------------------------------------
-- ZAPOSLENI
-- PMOV: jak entitet ZAPOSLENI + veza RADI U: ZAPOSLENI (1,1) - ORGANIZACIONA JEDINICA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE ZAPOSLENI
(
    SIFRA_ZAPOSLENOG   CHAR(18)       NOT NULL,              /* PK - SIFRA ZAPOSLENOG */
    SIFRA_JEDINICE     CHAR(18)       NOT NULL,              /* FK - veza RADI U */
    JMBG               CHAR(13)       NOT NULL,              /* JMBG */
    IME                VARCHAR(30)    NOT NULL,              /* IME */
    PREZIME            VARCHAR(30)    NOT NULL,              /* PREZIME */
    RADNO_MESTO        VARCHAR(60),                          /* RADNO MESTO */
    DATUM_ZAPOSLENJA   DATE,                                 /* DATUM ZAPOSLENJA */
    OSNOVNA_ZARADA     DECIMAL(12,2),                        /* OSNOVNA ZARADA */
    STATUS_ZAPOSLENJA  VARCHAR(20),                          /* STATUS ZAPOSLENJA */
    CONSTRAINT PK_ZAPOSLENI PRIMARY KEY (SIFRA_ZAPOSLENOG)
);

-- ---------------------------------------------------------------------
-- UREDNIK
-- PMOV: podtip ZAPOSLENI -> UREDNIK (specijalizacija)
-- ---------------------------------------------------------------------
CREATE TABLE UREDNIK
(
    SIFRA_ZAPOSLENOG  CHAR(18)     NOT NULL,               /* PK = FK ka ZAPOSLENI */
    NIVO_OVLASCENJA   VARCHAR(30),                         /* NIVO OVLASCENJA */
    REDAKCIJA         VARCHAR(60),                         /* REDAKCIJA */
    CONSTRAINT PK_UREDNIK PRIMARY KEY (SIFRA_ZAPOSLENOG)
);

-- ---------------------------------------------------------------------
-- NOVINAR_REPORTER
-- PMOV: podtip ZAPOSLENI -> NOVINAR / REPORTER
-- ---------------------------------------------------------------------
CREATE TABLE NOVINAR_REPORTER
(
    SIFRA_ZAPOSLENOG         CHAR(18)     NOT NULL,                 /* PK = FK ka ZAPOSLENI */
    OBLAST_IZVESTAVANJA      VARCHAR(60),                           /* OBLAST IZVESTAVANJA */
    BROJ_NOVINARSKE_LEGITIM  VARCHAR(20),                           /* BROJ NOVINARSKE LEGITIMACIJE */
    CONSTRAINT PK_NOVINAR_REPORTER PRIMARY KEY (SIFRA_ZAPOSLENOG)
);

-- ---------------------------------------------------------------------
-- TEHNICKO_OSOBLJE
-- PMOV: podtip ZAPOSLENI -> TEHNICKO OSOBLJE
-- ---------------------------------------------------------------------
CREATE TABLE TEHNICKO_OSOBLJE
(
    SIFRA_ZAPOSLENOG  CHAR(18)     NOT NULL,                        /* PK = FK ka ZAPOSLENI */
    SPECIJALIZACIJA   VARCHAR(60),                                  /* SPECIJALIZACIJA */
    TIP_EKIPE         VARCHAR(30),                                  /* TIP EKIPE */
    CONSTRAINT PK_TEHNICKO_OSOBLJE PRIMARY KEY (SIFRA_ZAPOSLENOG)
);

-- ---------------------------------------------------------------------
-- REFERENT
-- PMOV: podtip ZAPOSLENI -> REFERENT
-- ---------------------------------------------------------------------
CREATE TABLE REFERENT
(
    SIFRA_ZAPOSLENOG  CHAR(18)     NOT NULL,                /* PK = FK ka ZAPOSLENI */
    TIP_REFERENTA     VARCHAR(30),                          /* TIP REFERENTA */
    NIVO_OVLASCENJA   VARCHAR(30),                          /* NIVO OVLASCENJA */
    CONSTRAINT PK_REFERENT PRIMARY KEY (SIFRA_ZAPOSLENOG)
);

-- ---------------------------------------------------------------------
-- SERVISERI
-- PMOV: podtip ZAPOSLENI -> SERVISERI
-- ---------------------------------------------------------------------
CREATE TABLE SERVISERI
(
    SIFRA_ZAPOSLENOG  CHAR(18)     NOT NULL,                 /* PK = FK ka ZAPOSLENI */
    LICENCA           VARCHAR(60),                           /* LICENCA */
    CONSTRAINT PK_SERVISERI PRIMARY KEY (SIFRA_ZAPOSLENOG)
);


-- =====================================================================
-- CELINA: OPREMA (7 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- OPREMA
-- PMOV: jak entitet OPREMA
-- ---------------------------------------------------------------------
CREATE TABLE OPREMA
(
    INVENTARSKI_BROJ  CHAR(18)       NOT NULL,            /* PK - INVENTARSKI BROJ */
    NAZIV_OPREME      VARCHAR(60)    NOT NULL,            /* NAZIV OPREME */
    MODEL_OPREME      VARCHAR(60),                        /* MODEL (MODEL je rezervisana rec -> MODEL_OPREME) */
    PROIZVODJAC       VARCHAR(60),                        /* PROIZVODJAC */
    STATUS_OPREME     VARCHAR(20),                        /* STATUS OPREME */
    DATUM_NABAVKE     DATE,                               /* DATUM NABAVKE */
    GARANCIJA_DO      DATE,                               /* GARANCIJA DO */
    NABAVNA_VREDNOST  DECIMAL(12,2),                      /* NABAVNA VREDNOST */
    CONSTRAINT PK_OPREMA PRIMARY KEY (INVENTARSKI_BROJ)
);

-- ---------------------------------------------------------------------
-- SNIMATELJSKA_OPREMA
-- PMOV: podtip OPREMA -> SNIMATELJSKA OPREMA
-- ---------------------------------------------------------------------
CREATE TABLE SNIMATELJSKA_OPREMA
(
    INVENTARSKI_BROJ           CHAR(18)     NOT NULL,                  /* PK = FK ka OPREMA */
    TIP_MEMORIJSKOG_SKLADISTA  VARCHAR(30),                            /* TIP MEMORIJSKOG SKLADISTA */
    REZOLUCIJA                 VARCHAR(20),                            /* REZOLUCIJA */
    TIP_KAMERE                 VARCHAR(30),                            /* TIP KAMERE */
    CONSTRAINT PK_SNIMATELJSKA_OPREMA PRIMARY KEY (INVENTARSKI_BROJ)
);

-- ---------------------------------------------------------------------
-- STUDIJSKA_I_EMISIONA_OPREMA
-- PMOV: podtip OPREMA -> STUDIJSKA I EMISIONA OPREMA
-- ---------------------------------------------------------------------
CREATE TABLE STUDIJSKA_I_EMISIONA_OPREMA
(
    INVENTARSKI_BROJ    CHAR(18)     NOT NULL,                                 /* PK = FK ka OPREMA */
    LOKACIJA_U_STUDIJU  VARCHAR(60),                                           /* LOKACIJA U STUDIJU */
    CONSTRAINT PK_STUDIJSKA_I_EMISIONA_OPREMA PRIMARY KEY (INVENTARSKI_BROJ)
);

-- ---------------------------------------------------------------------
-- AUDIO_OPREMA
-- PMOV: podtip STUDIJSKA I EMISIONA OPREMA -> AUDIO OPREMA
-- ---------------------------------------------------------------------
CREATE TABLE AUDIO_OPREMA
(
    INVENTARSKI_BROJ  CHAR(18)     NOT NULL,                    /* PK = FK ka STUDIJSKA_I_EMISIONA_OPREMA */
    TIP               VARCHAR(30),                              /* TIP */
    FREKVENCIJA       VARCHAR(20),                              /* FREKVENCIJA */
    CONSTRAINT PK_AUDIO_OPREMA PRIMARY KEY (INVENTARSKI_BROJ)
);

-- ---------------------------------------------------------------------
-- SVETLOSNA_OPREMA
-- PMOV: podtip STUDIJSKA I EMISIONA OPREMA -> SVETLOSNA OPREMA
-- ---------------------------------------------------------------------
CREATE TABLE SVETLOSNA_OPREMA
(
    INVENTARSKI_BROJ  CHAR(18)     NOT NULL,                        /* PK = FK ka STUDIJSKA_I_EMISIONA_OPREMA */
    SNAGA             VARCHAR(20),                                  /* SNAGA */
    TIP_SVETLOSTI     VARCHAR(30),                                  /* TIP SVETLOSTI */
    CONSTRAINT PK_SVETLOSNA_OPREMA PRIMARY KEY (INVENTARSKI_BROJ)
);

-- ---------------------------------------------------------------------
-- ZADUZENJE_OPREME
-- PMOV: veza ZADUZENA: ZAPOSLENI (0,N) - OPREMA (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE ZADUZENJE_OPREME
(
    SIFRA_ZAPOSLENOG     CHAR(18)      NOT NULL,                                                       /* PK/FK ka ZAPOSLENI */
    INVENTARSKI_BROJ     CHAR(18)      NOT NULL,                                                       /* PK/FK ka OPREMA */
    DATUM_ZADUZENJA      DATE          NOT NULL,                                                       /* PK - atribut veze DATUM ZADUZENJA */
    DATUM_RAZDUZENJA     DATE,                                                                         /* atribut veze DATUM RAZDUZENJA */
    STANJE_PRI_VRACANJU  VARCHAR(255),                                                                 /* atribut veze STANJE PRI VRACANJU */
    CONSTRAINT PK_ZADUZENJE_OPREME PRIMARY KEY (SIFRA_ZAPOSLENOG, INVENTARSKI_BROJ, DATUM_ZADUZENJA)
);

-- ---------------------------------------------------------------------
-- SERVISIRANJE_OPREME
-- PMOV: veza SERVISIRANJE: SERVISERI (0,N) - OPREMA (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE SERVISIRANJE_OPREME
(
    SIFRA_ZAPOSLENOG  CHAR(18)       NOT NULL,                                                          /* PK/FK ka SERVISERI */
    INVENTARSKI_BROJ  CHAR(18)       NOT NULL,                                                          /* PK/FK ka OPREMA */
    DATUM_SERVISA     DATE           NOT NULL,                                                          /* PK - atribut veze DATUM SERVISA */
    OPIS_RADOVA       VARCHAR(255),                                                                     /* atribut veze OPIS RADOVA */
    TROSAK            DECIMAL(12,2),                                                                    /* atribut veze TROSAK */
    CONSTRAINT PK_SERVISIRANJE_OPREME PRIMARY KEY (SIFRA_ZAPOSLENOG, INVENTARSKI_BROJ, DATUM_SERVISA)
);


-- =====================================================================
-- CELINA: PRODUKCIJA (7 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- PROJEKAT_PRODUKCIJE
-- PMOV: jak entitet PROJEKAT PRODUKCIJE + UREDJUJE: UREDNIK (0,N)-(1,1) + PROIZVODI: PROJEKAT (0,1)-EMISIJA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE PROJEKAT_PRODUKCIJE
(
    SIFRA_PROJEKTA    CHAR(18)       NOT NULL,                       /* PK - SIFRA PROJEKTA */
    SIFRA_UREDNIKA    CHAR(18)       NOT NULL,                       /* FK - veza UREDJUJE */
    SIFRA_EMISIJE     CHAR(18),                                      /* FK - veza PROIZVODI */
    NAZIV_PROJEKTA    VARCHAR(60)    NOT NULL,                       /* NAZIV PROJEKTA */
    DATUM_POCETKA     DATE,                                          /* DATUM POCETKA */
    DATUM_ZAVRSETKA   DATE,                                          /* DATUM ZAVRSETKA */
    ODOBREN_BUDZET    DECIMAL(12,2),                                 /* ODOBREN BUDZET */
    STATUS_PROJEKTA   VARCHAR(20),                                   /* STATUS PROJEKTA */
    VRSTA_PRODUKCIJE  VARCHAR(30),                                   /* VRSTA PRODUKCIJE */
    OPIS_PROJEKTA     VARCHAR(255),                                  /* OPIS PROJEKTA */
    CONSTRAINT PK_PROJEKAT_PRODUKCIJE PRIMARY KEY (SIFRA_PROJEKTA)
);

-- ---------------------------------------------------------------------
-- AKTIVNOST_PRODUKCIJE
-- PMOV: slab entitet AKTIVNOST PRODUKCIJE; identifikujuca veza SASTOJI SE OD: PROJEKAT (1,N) - AKTIVNOST (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE AKTIVNOST_PRODUKCIJE
(
    SIFRA_PROJEKTA     CHAR(18)     NOT NULL,                                        /* PK/FK - identifikujuci vlasnik */
    RB_AKTIVNOSTI      INTEGER      NOT NULL,                                        /* PK - parcijalni kljuc RB AKTIVNOSTI */
    NAZIV_AKTIVNOSTI   VARCHAR(60)  NOT NULL,                                        /* NAZIV AKTIVNOSTI */
    DATUM_OD           DATE,                                                         /* DATUM OD */
    DATUM_DO           DATE,                                                         /* DATUM DO */
    VRSTA_AKTIVNOSTI   VARCHAR(30),                                                  /* VRSTA AKTIVNOSTI */
    LOKACIJA_SNIMANJA  VARCHAR(60),                                                  /* LOKACIJA SNIMANJA */
    STATUS_AKTIVNOSTI  VARCHAR(20),                                                  /* STATUS AKTIVNOSTI */
    CONSTRAINT PK_AKTIVNOST_PRODUKCIJE PRIMARY KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI)
);

-- ---------------------------------------------------------------------
-- TROSAK_PRODUKCIJE
-- PMOV: slab entitet TROSAK PRODUKCIJE; identifikujuca veza IZAZIVA: AKTIVNOST (0,N) - TROSAK (1,1); DOKUMENTOVAN: TROSAK (0,1) - FAKTURA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE TROSAK_PRODUKCIJE
(
    SIFRA_PROJEKTA  CHAR(18)       NOT NULL,                                                 /* PK/FK - identifikujuci vlasnik */
    RB_AKTIVNOSTI   INTEGER        NOT NULL,                                                 /* PK/FK - identifikujuci vlasnik */
    RB_TROSKA       INTEGER        NOT NULL,                                                 /* PK - parcijalni kljuc RB TROSKA */
    BROJ_FAKTURE    CHAR(18),                                                                /* FK - veza DOKUMENTOVAN */
    VRSTA_TROSKA    VARCHAR(30),                                                             /* VRSTA TROSKA */
    IZNOS           DECIMAL(12,2)  NOT NULL,                                                 /* IZNOS */
    DATUM_NASTANKA  DATE,                                                                    /* DATUM NASTANKA */
    OPIS_TROSKA     VARCHAR(255),                                                            /* OPIS TROSKA */
    CONSTRAINT PK_TROSAK_PRODUKCIJE PRIMARY KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI, RB_TROSKA)
);

-- ---------------------------------------------------------------------
-- ANGAZOVANJE_NA_AKTIVNOSTI
-- PMOV: veza ANGAZUJE: ZAPOSLENI (0,N) - AKTIVNOST PRODUKCIJE (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE ANGAZOVANJE_NA_AKTIVNOSTI
(
    SIFRA_PROJEKTA         CHAR(18)     NOT NULL,                                                           /* PK/FK ka AKTIVNOST_PRODUKCIJE */
    RB_AKTIVNOSTI          INTEGER      NOT NULL,                                                           /* PK/FK ka AKTIVNOST_PRODUKCIJE */
    SIFRA_ZAPOSLENOG       CHAR(18)     NOT NULL,                                                           /* PK/FK ka ZAPOSLENI */
    ULOGA_NA_SNIMANJU      VARCHAR(60),                                                                     /* atribut veze ULOGA NA SNIMANJU */
    DATUM_OD               DATE,                                                                            /* atribut veze DATUM OD */
    DATUM_DO               DATE,                                                                            /* atribut veze DATUM DO */
    BROJ_ANGAZOVANIH_SATI  INTEGER,                                                                         /* atribut veze BROJ ANGAZOVANIH SATI */
    CONSTRAINT PK_ANGAZOVANJE_NA_AKTIVNOSTI PRIMARY KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI, SIFRA_ZAPOSLENOG)
);

-- ---------------------------------------------------------------------
-- REZERVACIJA_OPREME
-- PMOV: veza ZADUZUJE: OPREMA (0,N) - AKTIVNOST PRODUKCIJE (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE REZERVACIJA_OPREME
(
    SIFRA_PROJEKTA      CHAR(18)  NOT NULL,                                                          /* PK/FK ka AKTIVNOST_PRODUKCIJE */
    RB_AKTIVNOSTI       INTEGER   NOT NULL,                                                          /* PK/FK ka AKTIVNOST_PRODUKCIJE */
    INVENTARSKI_BROJ    CHAR(18)  NOT NULL,                                                          /* PK/FK ka OPREMA */
    DATUM_REZERVACIJE   DATE,                                                                        /* atribut veze DATUM REZERVACIJE */
    TRAJANJE_ZADUZENJA  INTEGER,                                                                     /* atribut veze TRAJANJE ZADUZENJA (dana) */
    CONSTRAINT PK_REZERVACIJA_OPREME PRIMARY KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI, INVENTARSKI_BROJ)
);

-- ---------------------------------------------------------------------
-- SIROVI_SNIMAK
-- PMOV: jak entitet SIROVI SNIMAK + veza SNIMLJEN NA: SIROVI SNIMAK (1,1) - AKTIVNOST PRODUKCIJE (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE SIROVI_SNIMAK
(
    SIFRA_SNIMKA     CHAR(18)     NOT NULL,                  /* PK - SIFRA SNIMKA */
    SIFRA_PROJEKTA   CHAR(18)     NOT NULL,                  /* FK - veza SNIMLJEN NA */
    RB_AKTIVNOSTI    INTEGER      NOT NULL,                  /* FK - veza SNIMLJEN NA */
    DATUM_SNIMANJA   DATE,                                   /* DATUM SNIMANJA */
    TRAJANJE         INTEGER,                                /* TRAJANJE (sekundi) */
    FORMAT_SNIMKA    VARCHAR(30),                            /* FORMAT SNIMKA */
    LOKACIJA_SNIMKA  VARCHAR(60),                            /* LOKACIJA SNIMKA */
    OCENA_KVALITETA  VARCHAR(20),                            /* OCENA KVALITETA */
    CONSTRAINT PK_SIROVI_SNIMAK PRIMARY KEY (SIFRA_SNIMKA)
);

-- ---------------------------------------------------------------------
-- GRAFICKI_I_MUZICKI_ELEMENT
-- PMOV: jak entitet GRAFICKI I MUZICKI ELEMENT
-- ---------------------------------------------------------------------
CREATE TABLE GRAFICKI_I_MUZICKI_ELEMENT
(
    SIFRA_ELEMENTA    CHAR(18)      NOT NULL,                               /* PK - SIFRA ELEMENTA */
    NAZIV_ELEMENTA    VARCHAR(60)   NOT NULL,                               /* NAZIV ELEMENTA */
    TIP_ELEMENTA      VARCHAR(30),                                          /* TIP ELEMENTA */
    AUTOR             VARCHAR(60),                                          /* AUTOR */
    FORMAT_ELEMENTA   VARCHAR(30),                                          /* FORMAT (FORMAT je rezervisana rec -> FORMAT_ELEMENTA) */
    USLOV_KORISCENJA  VARCHAR(255),                                         /* USLOV KORISCENJA */
    CONSTRAINT PK_GRAFICKI_I_MUZICKI_ELEMENT PRIMARY KEY (SIFRA_ELEMENTA)
);


-- =====================================================================
-- CELINA: PROGRAM I EMITOVANJE (17 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- PROGRAMSKA_SEMA
-- PMOV: jak entitet PROGRAMSKA SEMA + veza ODOBRAVA: UREDNIK (0,N) - PROGRAMSKA SEMA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE PROGRAMSKA_SEMA
(
    SIFRA_SEME       CHAR(18)     NOT NULL,                  /* PK - ID SEME */
    SIFRA_UREDNIKA   CHAR(18)     NOT NULL,                  /* FK - veza ODOBRAVA */
    NAZIV_SEME       VARCHAR(60)  NOT NULL,                  /* NAZIV SEME */
    SEZONA           VARCHAR(20),                            /* SEZONA */
    VERZIJA_SEME     VARCHAR(20),                            /* VERZIJA SEME */
    DATUM_OD         DATE,                                   /* DATUM OD */
    DATUM_DO         DATE,                                   /* DATUM DO */
    STATUS_SEME      VARCHAR(20),                            /* STATUS SEME */
    DATUM_USVAJANJA  DATE,                                   /* DATUM USVAJANJA */
    CONSTRAINT PK_PROGRAMSKA_SEMA PRIMARY KEY (SIFRA_SEME)
);

-- ---------------------------------------------------------------------
-- PROGRAMSKA_CELINA
-- PMOV: slab entitet PROGRAMSKA CELINA; identifikujuca veza SADRZI CELINE: PROGRAMSKA SEMA (1,N) - PROGRAMSKA CELINA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE PROGRAMSKA_CELINA
(
    SIFRA_SEME    CHAR(18)     NOT NULL,                                  /* PK/FK - identifikujuci vlasnik */
    RB_CELINE     INTEGER      NOT NULL,                                  /* PK - parcijalni kljuc RB CELINE */
    NAZIV_CELINE  VARCHAR(60)  NOT NULL,                                  /* NAZIV CELINE */
    TIP_CELINE    VARCHAR(30),                                            /* TIP CELINE */
    DATUM         DATE,                                                   /* DATUM */
    VREME_OD      TIME,                                                   /* VREME OD */
    VREME_DO      TIME,                                                   /* VREME DO */
    CONSTRAINT PK_PROGRAMSKA_CELINA PRIMARY KEY (SIFRA_SEME, RB_CELINE)
);

-- ---------------------------------------------------------------------
-- TERMIN_EMITOVANJA
-- PMOV: jak entitet TERMIN EMITOVANJA + OBUHVATA: PROGRAMSKA CELINA (1,N)-(1,1) + PLANIRANA: TERMIN (1,1) - EMISIJA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE TERMIN_EMITOVANJA
(
    SIFRA_TERMINA       CHAR(18)     NOT NULL,                    /* PK - SIFRA TERMINA */
    SIFRA_SEME          CHAR(18)     NOT NULL,                    /* FK - veza OBUHVATA */
    RB_CELINE           INTEGER      NOT NULL,                    /* FK - veza OBUHVATA */
    SIFRA_EMISIJE       CHAR(18)     NOT NULL,                    /* FK - veza PLANIRANA */
    DATUM               DATE         NOT NULL,                    /* DATUM */
    VREME_POCETKA       TIME         NOT NULL,                    /* VREME POCETKA */
    TRAJANJE_TERMINA    INTEGER,                                  /* TRAJANJE TERMINA (minuta) */
    TIP_TERMINA         VARCHAR(30),                              /* TIP TERMINA */
    ZONA_GLEDANOSTI     VARCHAR(20),                              /* ZONA GLEDANOSTI */
    STATUS_TERMINA      VARCHAR(20),                              /* STATUS TERMINA */
    REDNI_BROJ_REPRIZE  INTEGER,                                  /* REDNI BROJ REPRIZE */
    CONSTRAINT PK_TERMIN_EMITOVANJA PRIMARY KEY (SIFRA_TERMINA)
);

-- ---------------------------------------------------------------------
-- EMISIJA
-- PMOV: jak entitet EMISIJA
-- ---------------------------------------------------------------------
CREATE TABLE EMISIJA
(
    SIFRA_EMISIJE         CHAR(18)      NOT NULL,       /* PK - SIFRA EMISIJE */
    NAZIV_EMISIJE         VARCHAR(60)   NOT NULL,       /* NAZIV EMISIJE */
    ZANR                  VARCHAR(30),                  /* ZANR */
    FORMAT_EMISIJE        VARCHAR(30),                  /* FORMAT EMISIJE */
    PREDVIDJENO_TRAJANJE  INTEGER,                      /* PREDVIDJENO TRAJANJE (minuta) */
    CILJNA_PUBLIKA        VARCHAR(60),                  /* CILJNA PUBLIKA */
    STATUS_EMISIJE        VARCHAR(20),                  /* STATUS EMISIJE */
    PROGRAMSKI_ELABORAT   VARCHAR(255),                 /* PROGRAMSKI ELABORAT */
    CONSTRAINT PK_EMISIJA PRIMARY KEY (SIFRA_EMISIJE)
);

-- ---------------------------------------------------------------------
-- MEDIJSKI_SADRZAJ
-- PMOV: jak entitet MEDIJSKI SADRZAJ (nadtip)
-- ---------------------------------------------------------------------
CREATE TABLE MEDIJSKI_SADRZAJ
(
    SIFRA_SADRZAJA     CHAR(18)     NOT NULL,                     /* PK - SIFRA SADRZAJA */
    NAZIV_SADRZAJA     VARCHAR(60)  NOT NULL,                     /* NAZIV SADRZAJA */
    TRAJANJE           INTEGER,                                   /* TRAJANJE (sekundi) */
    FORMAT_ZAPISA      VARCHAR(30),                               /* FORMAT ZAPISA */
    DATUM_ARHIVIRANJA  DATE,                                      /* DATUM ARHIVIRANJA */
    LOKACIJA_U_ARHIVI  VARCHAR(60),                               /* LOKACIJA U ARHIVI */
    CONSTRAINT PK_MEDIJSKI_SADRZAJ PRIMARY KEY (SIFRA_SADRZAJA)
);

-- ---------------------------------------------------------------------
-- PRODUCIRANI_SADRZAJ
-- PMOV: podtip MEDIJSKI SADRZAJ -> PRODUCIRANI SADRZAJ
-- ---------------------------------------------------------------------
CREATE TABLE PRODUCIRANI_SADRZAJ
(
    SIFRA_SADRZAJA    CHAR(18)     NOT NULL,                         /* PK = FK ka MEDIJSKI_SADRZAJ */
    DATUM_PRODUKCIJE  DATE,                                          /* DATUM PRODUKCIJE */
    VERZIJA_MASTERA   VARCHAR(20),                                   /* VERZIJA MASTERA */
    CONSTRAINT PK_PRODUCIRANI_SADRZAJ PRIMARY KEY (SIFRA_SADRZAJA)
);

-- ---------------------------------------------------------------------
-- NABAVLJENI_SADRZAJ
-- PMOV: podtip MEDIJSKI SADRZAJ -> NABAVLJENI SADRZAJ + veza NABAVLJEN PO: NABAVLJENI SADRZAJ (1,1) - UGOVOR O NABAVCI (1,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE NABAVLJENI_SADRZAJ
(
    SIFRA_SADRZAJA     CHAR(18)       NOT NULL,                     /* PK = FK ka MEDIJSKI_SADRZAJ */
    BROJ_UGOVORA       CHAR(18)       NOT NULL,                     /* FK - veza NABAVLJEN PO */
    ZEMLJA_POREKLA     VARCHAR(60),                                 /* ZEMLJA POREKLA */
    CENA_NABAVKE       DECIMAL(12,2),                               /* CENA NABAVKE */
    DATUM_PREUZIMANJA  DATE,                                        /* atribut veze NABAVLJEN PO: DATUM PREUZIMANJA */
    UGOVORENA_NAKNADA  DECIMAL(12,2),                               /* atribut veze NABAVLJEN PO: UGOVORENA NAKNADA */
    CONSTRAINT PK_NABAVLJENI_SADRZAJ PRIMARY KEY (SIFRA_SADRZAJA)
);

-- ---------------------------------------------------------------------
-- REKLAMNI_SADRZAJ
-- PMOV: podtip MEDIJSKI SADRZAJ -> REKLAMNI SADRZAJ + veza DOSTAVLJA: OGLASIVAC (1,N) - REKLAMNI SADRZAJ (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE REKLAMNI_SADRZAJ
(
    SIFRA_SADRZAJA    CHAR(18)     NOT NULL,                      /* PK = FK ka MEDIJSKI_SADRZAJ */
    SIFRA_OGLASIVACA  CHAR(18)     NOT NULL,                      /* FK - veza DOSTAVLJA */
    DATUM_PRIJEMA     DATE,                                       /* DATUM PRIJEMA */
    STATUS            VARCHAR(20),                                /* STATUS */
    CONSTRAINT PK_REKLAMNI_SADRZAJ PRIMARY KEY (SIFRA_SADRZAJA)
);

-- ---------------------------------------------------------------------
-- ZAPIS_O_EMITOVANJU
-- PMOV: slab entitet ZAPIS O EMITOVANJU; identifikujuca veza REALIZOVAN: TERMIN (0,N) - ZAPIS (1,1); EVIDENTIRA: ZAPIS (1,1) - MEDIJSKI SADRZAJ (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE ZAPIS_O_EMITOVANJU
(
    SIFRA_TERMINA          CHAR(18)      NOT NULL,                                /* PK/FK - identifikujuci vlasnik */
    RB_EMITOVANJA          INTEGER       NOT NULL,                                /* PK - parcijalni kljuc RB EMITOVANJA */
    SIFRA_SADRZAJA         CHAR(18)      NOT NULL,                                /* FK - veza EVIDENTIRA */
    STATUS_REALIZACIJE     VARCHAR(20),                                           /* STATUS REALIZACIJE */
    STVARNO_VREME_POCETKA  TIME,                                                  /* STVARNO VREME POC. */
    STVARNO_TRAJANJE       INTEGER,                                               /* STVARNO TRAJANJE (minuta, isto kao TRAJANJE_TERMINA) */
    NAPOMENA_O_SMETNJAMA   VARCHAR(255),                                          /* NAPOMENA O SMETNJAMA */
    OPERATER_EMITOVANJA    VARCHAR(60),                                           /* OPERATER EMITOVANJA */
    CONSTRAINT PK_ZAPIS_O_EMITOVANJU PRIMARY KEY (SIFRA_TERMINA, RB_EMITOVANJA)
);

-- ---------------------------------------------------------------------
-- MONTAZA_SNIMKA
-- PMOV: veza MONTIRAN U: SIROVI SNIMAK (0,N) - MEDIJSKI SADRZAJ (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE MONTAZA_SNIMKA
(
    SIFRA_SADRZAJA  CHAR(18)  NOT NULL,                                       /* PK/FK ka MEDIJSKI_SADRZAJ */
    SIFRA_SNIMKA    CHAR(18)  NOT NULL,                                       /* PK/FK ka SIROVI_SNIMAK */
    CONSTRAINT PK_MONTAZA_SNIMKA PRIMARY KEY (SIFRA_SADRZAJA, SIFRA_SNIMKA)
);

-- ---------------------------------------------------------------------
-- UGRADNJA_ELEMENTA
-- PMOV: veza UGRADJEN U: GRAFICKI I MUZICKI ELEMENT (0,N) - MEDIJSKI SADRZAJ (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE UGRADNJA_ELEMENTA
(
    SIFRA_SADRZAJA       CHAR(18)     NOT NULL,                                    /* PK/FK ka MEDIJSKI_SADRZAJ */
    SIFRA_ELEMENTA       CHAR(18)     NOT NULL,                                    /* PK/FK ka GRAFICKI_I_MUZICKI_ELEMENT */
    VREME_POJAVLJIVANJA  TIME,                                                     /* atribut veze VREME POJAVLJIVANJA */
    NACIN_KORISCENJA     VARCHAR(60),                                              /* atribut veze NACIN KORISCENJA */
    CONSTRAINT PK_UGRADNJA_ELEMENTA PRIMARY KEY (SIFRA_SADRZAJA, SIFRA_ELEMENTA)
);

-- ---------------------------------------------------------------------
-- SADRZAJ_EMISIJE
-- PMOV: veza CINI: EMISIJA (1,N) - MEDIJSKI SADRZAJ (0,N), sa atributom veze
-- ---------------------------------------------------------------------
CREATE TABLE SADRZAJ_EMISIJE
(
    SIFRA_EMISIJE         CHAR(18)  NOT NULL,                                   /* PK/FK ka EMISIJA */
    SIFRA_SADRZAJA        CHAR(18)  NOT NULL,                                   /* PK/FK ka MEDIJSKI_SADRZAJ */
    REDNI_BROJ_U_EMISIJI  INTEGER,                                              /* atribut veze REDNI BROJ U EMISIJI */
    CONSTRAINT PK_SADRZAJ_EMISIJE PRIMARY KEY (SIFRA_EMISIJE, SIFRA_SADRZAJA)
);

-- ---------------------------------------------------------------------
-- PRAVO_KORISCENJA
-- PMOV: jak entitet PRAVO KORISCENJA
-- ---------------------------------------------------------------------
CREATE TABLE PRAVO_KORISCENJA
(
    BROJ_LICENCE            CHAR(18)     NOT NULL,              /* PK - BROJ LICENCE */
    VRSTA_PRAVA             VARCHAR(30),                        /* VRSTA PRAVA */
    DATUM_OD                DATE,                               /* DATUM OD */
    DATUM_DO                DATE,                               /* DATUM DO */
    DOZVOLJENO_EMITOVANJA   INTEGER,                            /* DOZVOLJENO EMITOVANJA */
    ISKORISCENO_EMITOVANJA  INTEGER,                            /* ISKORISCENO EMITOVANJA - izvedeni atribut */
    TERITORIJA              VARCHAR(60),                        /* TERITORIJA */
    NOSILAC_PRAVA           VARCHAR(60),                        /* NOSILAC PRAVA */
    CONSTRAINT PK_PRAVO_KORISCENJA PRIMARY KEY (BROJ_LICENCE)
);

-- ---------------------------------------------------------------------
-- POKRIVENOST_PRAVOM
-- PMOV: veza POKRIVA: PRAVO KORISCENJA (1,N) - MEDIJSKI SADRZAJ (0,N), sa atributom veze
-- ---------------------------------------------------------------------
CREATE TABLE POKRIVENOST_PRAVOM
(
    BROJ_LICENCE         CHAR(18)     NOT NULL,                                   /* PK/FK ka PRAVO_KORISCENJA */
    SIFRA_SADRZAJA       CHAR(18)     NOT NULL,                                   /* PK/FK ka MEDIJSKI_SADRZAJ */
    OBLAST_POKRIVENOSTI  VARCHAR(60),                                             /* atribut veze OBLAST POKRIVENOSTI */
    CONSTRAINT PK_POKRIVENOST_PRAVOM PRIMARY KEY (BROJ_LICENCE, SIFRA_SADRZAJA)
);

-- ---------------------------------------------------------------------
-- POVRATNA_INFO_GLEDALACA
-- PMOV: jak entitet POVRATNA INFO. GLEDALACA + veza ODNOSI SE NA: POVRATNA INFO (0,1) - EMISIJA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE POVRATNA_INFO_GLEDALACA
(
    BROJ_PRIJAVE     CHAR(18)      NOT NULL,                           /* PK - BROJ PRIJAVE */
    SIFRA_EMISIJE    CHAR(18),                                         /* FK - veza ODNOSI SE NA */
    DATUM_PRIJEMA    DATE,                                             /* DATUM PRIJEMA */
    VRSTA_PRIJAVE    VARCHAR(30),                                      /* VRSTA PRIJAVE */
    KANAL_PRIJEMA    VARCHAR(30),                                      /* KANAL PRIJEMA */
    SADRZAJ_PRIJAVE  VARCHAR(255),                                     /* SADRZAJ PRIJAVE */
    STATUS_OBRADE    VARCHAR(20),                                      /* STATUS OBRADE */
    DATUM_ODGOVORA   DATE,                                             /* DATUM ODGOVORA */
    PROFIL_GLEDAOCA  VARCHAR(60),                                      /* PROFIL GLEDAOCA */
    CONSTRAINT PK_POVRATNA_INFO_GLEDALACA PRIMARY KEY (BROJ_PRIJAVE)
);

-- ---------------------------------------------------------------------
-- MERENJE_GLEDANOSTI
-- PMOV: jak entitet MERENJE GLEDANOSTI
-- ---------------------------------------------------------------------
CREATE TABLE MERENJE_GLEDANOSTI
(
    SIFRA_MERENJA      CHAR(18)      NOT NULL,                     /* PK - SIFRA MERENJA */
    DATUM_MERENJA      DATE,                                       /* DATUM MERENJA */
    IZVOR_MERENJA      VARCHAR(60),                                /* IZVOR MERENJA */
    CILJNA_GRUPA       VARCHAR(60),                                /* CILJNA GRUPA */
    RATING             DECIMAL(5,2),                               /* RATING */
    SHARE_UDEO         DECIMAL(5,2),                               /* SHARE (SHARE je rezervisana rec -> SHARE_UDEO) */
    BROJ_GLEDALACA     INTEGER,                                    /* BROJ GLEDALACA */
    PROSECNO_GLEDANJE  INTEGER,                                    /* PROSECNO GLEDANJE (minuta) */
    CONSTRAINT PK_MERENJE_GLEDANOSTI PRIMARY KEY (SIFRA_MERENJA)
);

-- ---------------------------------------------------------------------
-- MERENJE_EMISIJE
-- PMOV: veza MERENA: MERENJE GLEDANOSTI (1,N) - EMISIJA (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE MERENJE_EMISIJE
(
    SIFRA_MERENJA     CHAR(18)      NOT NULL,                                  /* PK/FK ka MERENJE_GLEDANOSTI */
    SIFRA_EMISIJE     CHAR(18)      NOT NULL,                                  /* PK/FK ka EMISIJA */
    OSTVARENI_RATING  DECIMAL(5,2),                                            /* atribut veze OSTVARENI RATING */
    UDEO_U_TERMINU    DECIMAL(5,2),                                            /* atribut veze UDEO U TERMINU */
    CONSTRAINT PK_MERENJE_EMISIJE PRIMARY KEY (SIFRA_MERENJA, SIFRA_EMISIJE)
);


-- =====================================================================
-- CELINA: MARKETING I PRODAJA (12 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- CENOVNIK_REKL_TERMINA
-- PMOV: jak entitet CENOVNIK REKL. TERMINA
-- ---------------------------------------------------------------------
CREATE TABLE CENOVNIK_REKL_TERMINA
(
    SIFRA_CENOVNIKA       CHAR(18)       NOT NULL,                      /* PK - SIFRA CENOVNIKA */
    VAZI_OD               DATE,                                         /* VAZI OD */
    VAZI_DO               DATE,                                         /* VAZI DO */
    ZONA                  VARCHAR(30),                                  /* ZONA */
    CENA_PO_SEKUNDI       DECIMAL(12,2),                                /* CENA PO SEKUNDI */
    TIP_CENOVNOG_PAKETA   VARCHAR(30),                                  /* TIP CENOVNOG PAKETA */
    OPIS_CENOVNOG_PAKETA  VARCHAR(255),                                 /* OPIS CENOVNOG PAKETA */
    CONSTRAINT PK_CENOVNIK_REKL_TERMINA PRIMARY KEY (SIFRA_CENOVNIKA)
);

-- ---------------------------------------------------------------------
-- REKLAMNI_BLOK
-- PMOV: jak entitet REKLAMNI BLOK + ZAKUPLJEN U: BLOK (1,1) - TERMIN (0,N) + TARIFIRAN: CENOVNIK (1,N) - BLOK (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE REKLAMNI_BLOK
(
    SIFRA_BLOKA         CHAR(18)      NOT NULL,             /* PK - SIFRA BLOKA */
    SIFRA_TERMINA       CHAR(18)      NOT NULL,             /* FK - veza ZAKUPLJEN U */
    SIFRA_CENOVNIKA     CHAR(18)      NOT NULL,             /* FK - veza TARIFIRAN */
    DATUM               DATE,                               /* DATUM */
    VREME_POCETKA       TIME,                               /* VREME POCETKA */
    TRAJANJE_BLOKA      INTEGER,                            /* TRAJANJE BLOKA (sekundi) */
    ZAKUPLJENO_SEKUNDI  INTEGER,                            /* ZAKUPLJENO SEKUNDI - izvedeni atribut */
    SLOBODNO_SEKUNDI    INTEGER,                            /* SLOBODNO SEKUNDI - izvedeni atribut */
    ISKORISCENOST       DECIMAL(5,2),                       /* ISKORISCENOST - izvedeni atribut */
    STATUS_BLOKA        VARCHAR(20),                        /* STATUS BLOKA */
    CONSTRAINT PK_REKLAMNI_BLOK PRIMARY KEY (SIFRA_BLOKA)
);

-- ---------------------------------------------------------------------
-- EMITOVANJE_REKLAME
-- PMOV: slab entitet EMITOVANJE REKLAME; identifikujuca veza SADRZI SPOT: REKLAMNI BLOK (1,N) - (1,1); PRIKAZUJE: (1,1) - REKLAMNI SADRZAJ (0,N); UGOVOREN: (1,1) - STAVKA UGOVORA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE EMITOVANJE_REKLAME
(
    SIFRA_BLOKA        CHAR(18)       NOT NULL,                              /* PK/FK - identifikujuci vlasnik */
    RB_U_BLOKU         INTEGER        NOT NULL,                              /* PK - parcijalni kljuc RB U BLOKU */
    SIFRA_SADRZAJA     CHAR(18)       NOT NULL,                              /* FK - veza PRIKAZUJE */
    BROJ_UGOVORA       CHAR(18)       NOT NULL,                              /* FK - veza UGOVOREN */
    RB_STAVKE_UGOVORA  INTEGER        NOT NULL,                              /* FK - veza UGOVOREN */
    DATUM_EMITOVANJA   DATE,                                                 /* DATUM EMITOVANJA */
    VREME_EMITOVANJA   TIME,                                                 /* VREME EMITOVANJA */
    TRAJANJE_SPOTA     INTEGER,                                              /* TRAJANJE SPOTA (sekundi) */
    NAPLACENI_IZNOS    DECIMAL(12,2),                                        /* NAPLACENI IZNOS */
    STATUS_NAPLATE     VARCHAR(20),                                          /* STATUS NAPLATE */
    CONSTRAINT PK_EMITOVANJE_REKLAME PRIMARY KEY (SIFRA_BLOKA, RB_U_BLOKU)
);

-- ---------------------------------------------------------------------
-- KLIJENT
-- PMOV: jak entitet KLIJENT (nadtip); ADRESA je slozeni atribut
-- ---------------------------------------------------------------------
CREATE TABLE KLIJENT
(
    SIFRA_KLIJENTA  CHAR(18)     NOT NULL,               /* PK - SIFRA KLIJENTA */
    NAZIV_KLIJENTA  VARCHAR(60)  NOT NULL,               /* NAZIV KLIJENTA */
    PIB             CHAR(9),                             /* PIB */
    MATICNI_BROJ    CHAR(8),                             /* MATICNI BROJ */
    ULICA_I_BROJ    VARCHAR(60),                         /* ADRESA / ULICA I BROJ (slozeni atribut) */
    GRAD            VARCHAR(30),                         /* ADRESA / GRAD (slozeni atribut) */
    POSTANSKI_BROJ  CHAR(5),                             /* ADRESA / POSTANSKI BROJ (slozeni atribut) */
    KONTAKT_OSOBA   VARCHAR(60),                         /* KONTAKT OSOBA */
    CONSTRAINT PK_KLIJENT PRIMARY KEY (SIFRA_KLIJENTA)
);

-- ---------------------------------------------------------------------
-- OGLASIVAC
-- PMOV: podtip KLIJENT -> OGLASIVAC
-- ---------------------------------------------------------------------
CREATE TABLE OGLASIVAC
(
    SIFRA_KLIJENTA   CHAR(18)       NOT NULL,              /* PK = FK ka KLIJENT */
    BRANSA           VARCHAR(60),                          /* BRANSA */
    GODISNJI_BUDZET  DECIMAL(12,2),                        /* GODISNJI BUDZET */
    CONSTRAINT PK_OGLASIVAC PRIMARY KEY (SIFRA_KLIJENTA)
);

-- ---------------------------------------------------------------------
-- KUPAC_SADRZAJA
-- PMOV: podtip KLIJENT -> KUPAC SADRZAJA
-- ---------------------------------------------------------------------
CREATE TABLE KUPAC_SADRZAJA
(
    SIFRA_KLIJENTA         CHAR(18)     NOT NULL,               /* PK = FK ka KLIJENT */
    TIP_MEDIJA             VARCHAR(30),                         /* TIP MEDIJA */
    TERITORIJA_EMITOVANJA  VARCHAR(60),                         /* TERITORIJA EMITOVANJA */
    CONSTRAINT PK_KUPAC_SADRZAJA PRIMARY KEY (SIFRA_KLIJENTA)
);

-- ---------------------------------------------------------------------
-- UGOVOR
-- PMOV: jak entitet UGOVOR (nadtip) + veza SKLAPA: KLIJENT (0,N) - UGOVOR (0,1)
-- ---------------------------------------------------------------------
CREATE TABLE UGOVOR
(
    BROJ_UGOVORA     CHAR(18)       NOT NULL,         /* PK - BROJ UGOVORA */
    SIFRA_KLIJENTA   CHAR(18),                        /* FK - veza SKLAPA */
    DATUM_SKLAPANJA  DATE,                            /* DATUM SKLAPANJA */
    VAZI_OD          DATE,                            /* VAZI OD */
    VAZI_DO          DATE,                            /* VAZI DO */
    UKUPNA_VREDNOST  DECIMAL(12,2),                   /* UKUPNA VREDNOST - izvedeni atribut */
    STATUS_UGOVORA   VARCHAR(20),                     /* STATUS UGOVORA */
    CONSTRAINT PK_UGOVOR PRIMARY KEY (BROJ_UGOVORA)
);

-- ---------------------------------------------------------------------
-- STAVKA_UGOVORA
-- PMOV: slab entitet STAVKA UGOVORA; identifikujuca veza PRECIZIRA: UGOVOR (1,N) - STAVKA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE STAVKA_UGOVORA
(
    BROJ_UGOVORA      CHAR(18)       NOT NULL,                           /* PK/FK - identifikujuci vlasnik */
    RB_STAVKE         INTEGER        NOT NULL,                           /* PK - parcijalni kljuc RB STAVKE */
    OPIS_STAVKE       VARCHAR(255),                                      /* OPIS STAVKE */
    KOLICINA_SEKUNDE  INTEGER,                                           /* KOLICINA / SEKUNDE */
    JEDINICNA_CENA    DECIMAL(12,2),                                     /* JEDINICNA CENA */
    POPUST            DECIMAL(5,2),                                      /* POPUST */
    VREDNOST_STAVKE   DECIMAL(12,2),                                     /* VREDNOST STAVKE - izvedeni atribut */
    CONSTRAINT PK_STAVKA_UGOVORA PRIMARY KEY (BROJ_UGOVORA, RB_STAVKE)
);

-- ---------------------------------------------------------------------
-- UGOVOR_O_OGLASAVANJU
-- PMOV: podtip UGOVOR -> UGOVOR O OGLASAVANJU
-- ---------------------------------------------------------------------
CREATE TABLE UGOVOR_O_OGLASAVANJU
(
    BROJ_UGOVORA       CHAR(18)      NOT NULL,                      /* PK = FK ka UGOVOR */
    UGOVORENI_TERMINI  VARCHAR(255),                                /* UGOVORENI TERMINI */
    CONSTRAINT PK_UGOVOR_O_OGLASAVANJU PRIMARY KEY (BROJ_UGOVORA)
);

-- ---------------------------------------------------------------------
-- UGOVOR_O_PRODAJI_TV_SADRZAJA
-- PMOV: podtip UGOVOR -> UGOVOR O PRODAJI TV SADRZAJA
-- ---------------------------------------------------------------------
CREATE TABLE UGOVOR_O_PRODAJI_TV_SADRZAJA
(
    BROJ_UGOVORA            CHAR(18)      NOT NULL,                        /* PK = FK ka UGOVOR */
    PRENOS_VLASNISTVA       VARCHAR(20),                                   /* PRENOS VLASNISTVA */
    OBIM_USTUPLJENIH_PRAVA  VARCHAR(255),                                  /* OBIM USTUPLJENIH PRAVA */
    CONSTRAINT PK_UGOVOR_O_PRODAJI_TV_SADRZAJ PRIMARY KEY (BROJ_UGOVORA)
);

-- ---------------------------------------------------------------------
-- UGOVOR_O_NABAVCI
-- PMOV: podtip UGOVOR -> UGOVOR O NABAVCI + veza UGOVARA: DOBAVLJAC (0,N) - UGOVOR O NABAVCI (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE UGOVOR_O_NABAVCI
(
    BROJ_UGOVORA        CHAR(18)      NOT NULL,                 /* PK = FK ka UGOVOR */
    SIFRA_DOBAVLJACA    CHAR(18)      NOT NULL,                 /* FK - veza UGOVARA */
    VRSTA_REKLAMIRANJA  VARCHAR(30),                            /* VRSTA REKLAMIRANJA */
    ROK_ISPORUKE        DATE,                                   /* ROK ISPORUKE */
    USLOVI_PLACANJA     VARCHAR(255),                           /* USLOVI PLACANJA */
    CONSTRAINT PK_UGOVOR_O_NABAVCI PRIMARY KEY (BROJ_UGOVORA)
);

-- ---------------------------------------------------------------------
-- USTUPANJE_SADRZAJA
-- PMOV: veza USTUPA: UGOVOR O PRODAJI TV SADRZAJA (1,N) - PRODUCIRANI SADRZAJ (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE USTUPANJE_SADRZAJA
(
    BROJ_UGOVORA    CHAR(18)       NOT NULL,                                      /* PK/FK ka UGOVOR_O_PRODAJI_TV_SADRZAJA */
    SIFRA_SADRZAJA  CHAR(18)       NOT NULL,                                      /* PK/FK ka PRODUCIRANI_SADRZAJ */
    UGOVORENA_CENA  DECIMAL(12,2),                                                /* atribut veze UGOVORENA CENA */
    OBIM_USTUPANJA  VARCHAR(255),                                                 /* atribut veze OBIM USTUPANJA */
    CONSTRAINT PK_USTUPANJE_SADRZAJA PRIMARY KEY (BROJ_UGOVORA, SIFRA_SADRZAJA)
);


-- =====================================================================
-- CELINA: NABAVKA (16 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- PLAN_NABAVKE
-- PMOV: jak entitet PLAN NABAVKE
-- ---------------------------------------------------------------------
CREATE TABLE PLAN_NABAVKE
(
    SIFRA_PLANA      CHAR(18)       NOT NULL,              /* PK - SIFRA PLANA */
    GODINA_PLANA     INTEGER,                              /* GODINA PLANA */
    DATUM_DONOSENJA  DATE,                                 /* DATUM DONOSENJA */
    STATUS_PLANA     VARCHAR(20),                          /* STATUS PLANA */
    UKUPNA_VREDNOST  DECIMAL(12,2),                        /* UKUPNA VREDNOST - izvedeni atribut */
    DONOSILAC_PLANA  VARCHAR(60),                          /* DONOSILAC PLANA */
    CONSTRAINT PK_PLAN_NABAVKE PRIMARY KEY (SIFRA_PLANA)
);

-- ---------------------------------------------------------------------
-- ZAHTEV_ZA_NABAVKU
-- PMOV: jak entitet ZAHTEV ZA NABAVKU + PODNOSI: ORG. JEDINICA (0,N) - ZAHTEV (1,1) + UVRSTEN U: ZAHTEV (0,1) - PLAN (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE ZAHTEV_ZA_NABAVKU
(
    BROJ_ZAHTEVA         CHAR(18)       NOT NULL,                /* PK - BROJ ZAHTEVA */
    SIFRA_JEDINICE       CHAR(18)       NOT NULL,                /* FK - veza PODNOSI */
    SIFRA_PLANA          CHAR(18),                               /* FK - veza UVRSTEN U */
    DATUM_ZAHTEVA        DATE,                                   /* DATUM ZAHTEVA */
    VRSTA_NABAVKE        VARCHAR(30),                            /* VRSTA NABAVKE */
    PREDMET_ZAHTEVA      VARCHAR(255),                           /* PREDMET ZAHTEVA */
    OBRAZLOZENJE         VARCHAR(255),                           /* OBRAZLOZENJE */
    STATUS_ZAHTEVA       VARCHAR(20),                            /* STATUS ZAHTEVA */
    PRIORITET            VARCHAR(20),                            /* PRIORITET */
    PROCENJENA_VREDNOST  DECIMAL(12,2),                          /* PROCENJENA VREDNOST */
    CONSTRAINT PK_ZAHTEV_ZA_NABAVKU PRIMARY KEY (BROJ_ZAHTEVA)
);

-- ---------------------------------------------------------------------
-- STAVKA_PLANA_NABAVKE
-- PMOV: slab entitet STAVKA PLANA NABAVKE; identifikujuca veza SADRZI STAVKE PLANA: PLAN (1,N) - STAVKA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE STAVKA_PLANA_NABAVKE
(
    SIFRA_PLANA        CHAR(18)       NOT NULL,                               /* PK/FK - identifikujuci vlasnik */
    RB_STAVKE          INTEGER        NOT NULL,                               /* PK - parcijalni kljuc RB STAVKE */
    OPIS_ARTIKLA       VARCHAR(255),                                          /* OPIS ARTIKLA */
    KOLICINA           INTEGER,                                               /* KOLICINA */
    JEDINICA_MERE      VARCHAR(20),                                           /* JEDINICA MERE */
    PROCENJENA_CENA    DECIMAL(12,2),                                         /* PROCENJENA CENA */
    PLANIRANI_KVARTAL  VARCHAR(20),                                           /* PLANIRANI KVARTAL */
    CONSTRAINT PK_STAVKA_PLANA_NABAVKE PRIMARY KEY (SIFRA_PLANA, RB_STAVKE)
);

-- ---------------------------------------------------------------------
-- DOBAVLJAC
-- PMOV: jak entitet DOBAVLJAC (nadtip)
-- ---------------------------------------------------------------------
CREATE TABLE DOBAVLJAC
(
    SIFRA_DOBAVLJACA  CHAR(18)      NOT NULL,                /* PK - SIFRA DOBAVLJACA */
    NAZIV_DOBAVLJACA  VARCHAR(60)   NOT NULL,                /* NAZIV DOBAVLJACA */
    PIB               CHAR(9),                               /* PIB */
    MATICNI_BROJ      CHAR(8),                               /* MATICNI BROJ */
    ADRESA            VARCHAR(60),                           /* ADRESA */
    OCENA_DOBAVLJACA  DECIMAL(5,2),                          /* OCENA DOBAVLJACA - izvedeni atribut */
    CONSTRAINT PK_DOBAVLJAC PRIMARY KEY (SIFRA_DOBAVLJACA)
);

-- ---------------------------------------------------------------------
-- DOBAVLJAC_TV_SADRZAJA
-- PMOV: podtip DOBAVLJAC -> DOBAVLJAC TV SADRZAJA
-- ---------------------------------------------------------------------
CREATE TABLE DOBAVLJAC_TV_SADRZAJA
(
    SIFRA_DOBAVLJACA  CHAR(18)      NOT NULL,                            /* PK = FK ka DOBAVLJAC */
    VRSTA_SADRZAJA    VARCHAR(30),                                       /* VRSTA SADRZAJA */
    KATALOG_PONUDE    VARCHAR(255),                                      /* KATALOG PONUDE */
    CONSTRAINT PK_DOBAVLJAC_TV_SADRZAJA PRIMARY KEY (SIFRA_DOBAVLJACA)
);

-- ---------------------------------------------------------------------
-- DOBAVLJAC_OPREME_I_MATERIJALA
-- PMOV: podtip DOBAVLJAC -> DOBAVLJAC OPREME I MATERIJALA
-- ---------------------------------------------------------------------
CREATE TABLE DOBAVLJAC_OPREME_I_MATERIJALA
(
    SIFRA_DOBAVLJACA  CHAR(18)      NOT NULL,                                  /* PK = FK ka DOBAVLJAC */
    ASORTIMAN         VARCHAR(255),                                            /* ASORTIMAN */
    OVLASCENI_SERVIS  VARCHAR(20),                                             /* OVLASCENI SERVIS */
    CONSTRAINT PK_DOBAVLJAC_OPREME_I_MATERIJA PRIMARY KEY (SIFRA_DOBAVLJACA)
);

-- ---------------------------------------------------------------------
-- PONUDA_DOBAVLJACA
-- PMOV: jak entitet PONUDA DOBAVLJACA + veza DOSTAVIO: DOBAVLJAC (0,N) - PONUDA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE PONUDA_DOBAVLJACA
(
    BROJ_PONUDE       CHAR(18)       NOT NULL,                  /* PK - BROJ PONUDE */
    SIFRA_DOBAVLJACA  CHAR(18)       NOT NULL,                  /* FK - veza DOSTAVIO */
    DATUM_PRIJEMA     DATE,                                     /* DATUM PRIJEMA */
    VAZI_DO           DATE,                                     /* VAZI DO */
    UKUPNA_CENA       DECIMAL(12,2),                            /* UKUPNA CENA */
    ROK_ISPORUKE      DATE,                                     /* ROK ISPORUKE */
    USLOVI_PLACANJA   VARCHAR(255),                             /* USLOVI PLACANJA */
    STATUS_PONUDE     VARCHAR(20),                              /* STATUS PONUDE */
    UKUPNO_BODOVA     DECIMAL(5,2),                             /* UKUPNO BODOVA - izvedeni atribut */
    CONSTRAINT PK_PONUDA_DOBAVLJACA PRIMARY KEY (BROJ_PONUDE)
);

-- ---------------------------------------------------------------------
-- PONUDJENA_STAVKA
-- PMOV: veza PONUDJENA: STAVKA PLANA NABAVKE (0,N) - PONUDA DOBAVLJACA (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE PONUDJENA_STAVKA
(
    SIFRA_PLANA     CHAR(18)       NOT NULL,                                           /* PK/FK ka STAVKA_PLANA_NABAVKE */
    RB_STAVKE       INTEGER        NOT NULL,                                           /* PK/FK ka STAVKA_PLANA_NABAVKE */
    BROJ_PONUDE     CHAR(18)       NOT NULL,                                           /* PK/FK ka PONUDA_DOBAVLJACA */
    PONUDJENA_CENA  DECIMAL(12,2),                                                     /* atribut veze PONUDJENA CENA */
    ROK_ZA_STAVKU   DATE,                                                              /* atribut veze ROK ZA STAVKU */
    CONSTRAINT PK_PONUDJENA_STAVKA PRIMARY KEY (SIFRA_PLANA, RB_STAVKE, BROJ_PONUDE)
);

-- ---------------------------------------------------------------------
-- KRITERIJUM_VREDNOVANJA
-- PMOV: jak entitet KRITERIJUM VREDNOVANJA
-- ---------------------------------------------------------------------
CREATE TABLE KRITERIJUM_VREDNOVANJA
(
    SIFRA_KRITERIJUMA  CHAR(18)      NOT NULL,                             /* PK - SIFRA KRITERIJUMA */
    NAZIV_KRITERIJUMA  VARCHAR(60)   NOT NULL,                             /* NAZIV KRITERIJUMA */
    NACIN_BODOVANJA    VARCHAR(60),                                        /* NACIN BODOVANJA */
    OPIS_KRITERIJUMA   VARCHAR(255),                                       /* OPIS KRITERIJUMA */
    CONSTRAINT PK_KRITERIJUM_VREDNOVANJA PRIMARY KEY (SIFRA_KRITERIJUMA)
);

-- ---------------------------------------------------------------------
-- OCENA_PONUDE
-- PMOV: veza VREDNUJE SE: PONUDA DOBAVLJACA (1,N) - KRITERIJUM VREDNOVANJA (1,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE OCENA_PONUDE
(
    BROJ_PONUDE        CHAR(18)      NOT NULL,                                /* PK/FK ka PONUDA_DOBAVLJACA */
    SIFRA_KRITERIJUMA  CHAR(18)      NOT NULL,                                /* PK/FK ka KRITERIJUM_VREDNOVANJA */
    BROJ_BODOVA        DECIMAL(5,2),                                          /* atribut veze BROJ BODOVA */
    KOMENTAR_OCENE     VARCHAR(255),                                          /* atribut veze KOMENTAR OCENE */
    CONSTRAINT PK_OCENA_PONUDE PRIMARY KEY (BROJ_PONUDE, SIFRA_KRITERIJUMA)
);

-- ---------------------------------------------------------------------
-- NARUDZBENICA
-- PMOV: jak entitet NARUDZBENICA + veza NARUCENO OD: DOBAVLJAC (0,N) - NARUDZBENICA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE NARUDZBENICA
(
    BROJ_NARUDZBENICE  CHAR(18)       NOT NULL,                  /* PK - BROJ NARUDZBENICE */
    SIFRA_DOBAVLJACA   CHAR(18)       NOT NULL,                  /* FK - veza NARUCENO OD */
    DATUM_IZDAVANJA    DATE,                                     /* DATUM IZDAVANJA */
    ROK_ISPORUKE       DATE,                                     /* ROK ISPORUKE */
    MESTO_ISPORUKE     VARCHAR(60),                              /* MESTO ISPORUKE */
    UKUPAN_IZNOS       DECIMAL(12,2),                            /* UKUPAN IZNOS - izvedeni atribut */
    STATUS_NARUDZBINE  VARCHAR(20),                              /* STATUS NARUDZBINE */
    CONSTRAINT PK_NARUDZBENICA PRIMARY KEY (BROJ_NARUDZBENICE)
);

-- ---------------------------------------------------------------------
-- STAVKA_NARUDZBENICE
-- PMOV: slab entitet STAVKA NARUDZBENICE; identifikujuca veza SADRZI STAVKE NARUDZBINE: NARUDZBENICA (1,N) - STAVKA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE STAVKA_NARUDZBENICE
(
    BROJ_NARUDZBENICE  CHAR(18)       NOT NULL,                                    /* PK/FK - identifikujuci vlasnik */
    RB_STAVKE          INTEGER        NOT NULL,                                    /* PK - parcijalni kljuc RB STAVKE */
    NAZIV_ARTIKLA      VARCHAR(60),                                                /* NAZIV ARTIKLA */
    KOLICINA           INTEGER,                                                    /* KOLICINA */
    JEDINICNA_CENA     DECIMAL(12,2),                                              /* JEDINICNA CENA */
    STATUS_STAVKE      VARCHAR(20),                                                /* STATUS STAVKE */
    VREDNOST_STAVKE    DECIMAL(12,2),                                              /* VREDNOST STAVKE - izvedeni atribut */
    CONSTRAINT PK_STAVKA_NARUDZBENICE PRIMARY KEY (BROJ_NARUDZBENICE, RB_STAVKE)
);

-- ---------------------------------------------------------------------
-- PRIJEMNICA
-- PMOV: jak entitet PRIJEMNICA + PRACENA: NARUDZBENICA (0,N) - PRIJEMNICA (1,1) + FAKTURISANA: PRIJEMNICA (0,1) - FAKTURA (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE PRIJEMNICA
(
    BROJ_PRIJEMNICE      CHAR(18)      NOT NULL,             /* PK - BROJ PRIJEMNICE */
    BROJ_NARUDZBENICE    CHAR(18)      NOT NULL,             /* FK - veza PRACENA */
    BROJ_FAKTURE         CHAR(18),                           /* FK - veza FAKTURISANA */
    DATUM_PRIJEMA        DATE,                               /* DATUM PRIJEMA */
    BROJ_OTPREMNICE      VARCHAR(30),                        /* BROJ OTPREMNICE */
    PRIMIO_MAGACIONER    VARCHAR(60),                        /* PRIMIO (MAGACIONER) */
    ISPRAVNOST_ISPORUKE  VARCHAR(20),                        /* ISPRAVNOST ISPORUKE */
    NAPOMENA             VARCHAR(255),                       /* NAPOMENA */
    CONSTRAINT PK_PRIJEMNICA PRIMARY KEY (BROJ_PRIJEMNICE)
);

-- ---------------------------------------------------------------------
-- PRIJEM_STAVKE
-- PMOV: veza PRIMLJENO PO: PRIJEMNICA (1,N) - STAVKA NARUDZBENICE (0,N), sa atributima veze
-- ---------------------------------------------------------------------
CREATE TABLE PRIJEM_STAVKE
(
    BROJ_PRIJEMNICE       CHAR(18)      NOT NULL,                                             /* PK/FK ka PRIJEMNICA */
    BROJ_NARUDZBENICE     CHAR(18)      NOT NULL,                                             /* PK/FK ka STAVKA_NARUDZBENICE */
    RB_STAVKE             INTEGER       NOT NULL,                                             /* PK/FK ka STAVKA_NARUDZBENICE */
    PRIMLJENA_KOLICINA    INTEGER,                                                            /* atribut veze PRIMLJENA KOLICINA */
    UTVRDJENO_ODSTUPANJE  VARCHAR(255),                                                       /* atribut veze UTVRDJENO ODSTUPANJE */
    CONSTRAINT PK_PRIJEM_STAVKE PRIMARY KEY (BROJ_PRIJEMNICE, BROJ_NARUDZBENICE, RB_STAVKE)
);

-- ---------------------------------------------------------------------
-- REKLAMACIJA
-- PMOV: jak entitet REKLAMACIJA + veza REKLAMIRANA: PRIJEMNICA (0,N) - REKLAMACIJA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE REKLAMACIJA
(
    BROJ_REKLAMACIJE    CHAR(18)       NOT NULL,               /* PK - BROJ REKLAMACIJE */
    BROJ_PRIJEMNICE     CHAR(18)       NOT NULL,               /* FK - veza REKLAMIRANA */
    DATUM_REKLAMACIJE   DATE,                                  /* DATUM REKLAMACIJE */
    RAZLOG_REKLAMACIJE  VARCHAR(60),                           /* RAZLOG REKLAMACIJE */
    OPIS_NEDOSTATKA     VARCHAR(255),                          /* OPIS NEDOSTATKA */
    STATUS_REKLAMACIJE  VARCHAR(20),                           /* STATUS REKLAMACIJE */
    DATUM_RESENJA       DATE,                                  /* DATUM RESENJA */
    REKLAMIRANI_IZNOS   DECIMAL(12,2),                         /* REKLAMIRANI IZNOS */
    NACIN_RESAVANJA     VARCHAR(60),                           /* NACIN RESAVANJA */
    CONSTRAINT PK_REKLAMACIJA PRIMARY KEY (BROJ_REKLAMACIJE)
);

-- ---------------------------------------------------------------------
-- REKLAMIRANA_STAVKA
-- PMOV: veza ODNOSI SE NA: REKLAMACIJA (1,N) - STAVKA NARUDZBENICE (0,N)
-- ---------------------------------------------------------------------
CREATE TABLE REKLAMIRANA_STAVKA
(
    BROJ_REKLAMACIJE   CHAR(18)  NOT NULL,                                                          /* PK/FK ka REKLAMACIJA */
    BROJ_NARUDZBENICE  CHAR(18)  NOT NULL,                                                          /* PK/FK ka STAVKA_NARUDZBENICE */
    RB_STAVKE          INTEGER   NOT NULL,                                                          /* PK/FK ka STAVKA_NARUDZBENICE */
    CONSTRAINT PK_REKLAMIRANA_STAVKA PRIMARY KEY (BROJ_REKLAMACIJE, BROJ_NARUDZBENICE, RB_STAVKE)
);


-- =====================================================================
-- CELINA: FINANSIJE (3 tabela)
-- =====================================================================

-- ---------------------------------------------------------------------
-- FAKTURA
-- PMOV: jak entitet FAKTURA + veza IZDATA PO: UGOVOR (0,N) - FAKTURA (0,1)
-- ---------------------------------------------------------------------
CREATE TABLE FAKTURA
(
    BROJ_FAKTURE       CHAR(18)       NOT NULL,        /* PK - BROJ FAKTURE */
    BROJ_UGOVORA       CHAR(18),                       /* FK - veza IZDATA PO */
    DATUM_IZDAVANJA    DATE,                           /* DATUM IZDAVANJA */
    ROK_PLACANJA       DATE,                           /* ROK PLACANJA */
    SMER               VARCHAR(20),                    /* SMER (ULAZNA/IZLAZNA) */
    OSNOVICA           DECIMAL(12,2),                  /* OSNOVICA - izvedeni atribut */
    IZNOS_PDV          DECIMAL(12,2),                  /* IZNOS PDV - izvedeni atribut */
    STATUS_PLACANJA    VARCHAR(20),                    /* STATUS PLACANJA */
    IZNOS_ZA_PLACANJE  DECIMAL(12,2),                  /* IZNOS ZA PLACANJE - izvedeni atribut */
    CONSTRAINT PK_FAKTURA PRIMARY KEY (BROJ_FAKTURE)
);

-- ---------------------------------------------------------------------
-- STAVKA_FAKTURE
-- PMOV: slab entitet STAVKA FAKTURE; identifikujuca veza SADRZI STAVKE FAKTURE: FAKTURA (1,N) - STAVKA (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE STAVKA_FAKTURE
(
    BROJ_FAKTURE     CHAR(18)       NOT NULL,                            /* PK/FK - identifikujuci vlasnik */
    RB_STAVKE        INTEGER        NOT NULL,                            /* PK - parcijalni kljuc RB STAVKE */
    OPIS_STAVKE      VARCHAR(255),                                       /* OPIS STAVKE */
    KOLICINA         INTEGER,                                            /* KOLICINA */
    JEDINICNA_CENA   DECIMAL(12,2),                                      /* JEDINICNA CENA */
    STOPA_PDV        DECIMAL(5,2),                                       /* STOPA PDV */
    VREDNOST_STAVKE  DECIMAL(12,2),                                      /* VREDNOST STAVKE - izvedeni atribut */
    CONSTRAINT PK_STAVKA_FAKTURE PRIMARY KEY (BROJ_FAKTURE, RB_STAVKE)
);

-- ---------------------------------------------------------------------
-- NALOG_ZA_PLACANJE
-- PMOV: jak entitet NALOG ZA PLACANJE + veza PLACENA: FAKTURA (0,N) - NALOG (1,1)
-- ---------------------------------------------------------------------
CREATE TABLE NALOG_ZA_PLACANJE
(
    BROJ_NALOGA        CHAR(18)       NOT NULL,                 /* PK - BROJ NALOGA */
    BROJ_FAKTURE       CHAR(18)       NOT NULL,                 /* FK - veza PLACENA */
    DATUM_NALOGA       DATE,                                    /* DATUM NALOGA */
    IZNOS_NALOGA       DECIMAL(12,2),                           /* IZNOS NALOGA */
    SVRHA_PLACANJA     VARCHAR(255),                            /* SVRHA PLACANJA */
    DATUM_REALIZACIJE  DATE,                                    /* DATUM REALIZACIJE */
    STATUS_NALOGA      VARCHAR(20),                             /* STATUS NALOGA */
    RACUN_PRIMAOCA     VARCHAR(30),                             /* RACUN PRIMAOCA */
    ODOBRIO            VARCHAR(60),                             /* ODOBRIO */
    CONSTRAINT PK_NALOG_ZA_PLACANJE PRIMARY KEY (BROJ_NALOGA)
);


-- =====================================================================
-- STRANI KLJUCEVI (veze iz PMOV dijagrama)
-- =====================================================================

ALTER TABLE ORGANIZACIONA_JEDINICA
    ADD CONSTRAINT FK_ORGJED_PODREDJENA FOREIGN KEY (SIFRA_NADREDJENE_JEDINICE)
    REFERENCES ORGANIZACIONA_JEDINICA (SIFRA_JEDINICE);

ALTER TABLE ZAPOSLENI
    ADD CONSTRAINT FK_ZAPOSLENI_RADI_U FOREIGN KEY (SIFRA_JEDINICE)
    REFERENCES ORGANIZACIONA_JEDINICA (SIFRA_JEDINICE);

ALTER TABLE UREDNIK
    ADD CONSTRAINT FK_UREDNIK_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE NOVINAR_REPORTER
    ADD CONSTRAINT FK_NOVINAR_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE TEHNICKO_OSOBLJE
    ADD CONSTRAINT FK_TEHOSOB_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE REFERENT
    ADD CONSTRAINT FK_REFERENT_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE SERVISERI
    ADD CONSTRAINT FK_SERVISERI_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE SNIMATELJSKA_OPREMA
    ADD CONSTRAINT FK_SNIMOPR_OPREMA FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES OPREMA (INVENTARSKI_BROJ);

ALTER TABLE STUDIJSKA_I_EMISIONA_OPREMA
    ADD CONSTRAINT FK_STUDOPR_OPREMA FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES OPREMA (INVENTARSKI_BROJ);

ALTER TABLE AUDIO_OPREMA
    ADD CONSTRAINT FK_AUDIOOPR_STUDOPR FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES STUDIJSKA_I_EMISIONA_OPREMA (INVENTARSKI_BROJ);

ALTER TABLE SVETLOSNA_OPREMA
    ADD CONSTRAINT FK_SVETLOPR_STUDOPR FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES STUDIJSKA_I_EMISIONA_OPREMA (INVENTARSKI_BROJ);

ALTER TABLE ZADUZENJE_OPREME
    ADD CONSTRAINT FK_ZADUZ_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE ZADUZENJE_OPREME
    ADD CONSTRAINT FK_ZADUZ_OPREMA FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES OPREMA (INVENTARSKI_BROJ);

ALTER TABLE SERVISIRANJE_OPREME
    ADD CONSTRAINT FK_SERVIS_SERVISERI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES SERVISERI (SIFRA_ZAPOSLENOG);

ALTER TABLE SERVISIRANJE_OPREME
    ADD CONSTRAINT FK_SERVIS_OPREMA FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES OPREMA (INVENTARSKI_BROJ);

ALTER TABLE PROJEKAT_PRODUKCIJE
    ADD CONSTRAINT FK_PROJEKAT_UREDJUJE FOREIGN KEY (SIFRA_UREDNIKA)
    REFERENCES UREDNIK (SIFRA_ZAPOSLENOG);

ALTER TABLE PROJEKAT_PRODUKCIJE
    ADD CONSTRAINT FK_PROJEKAT_PROIZVODI FOREIGN KEY (SIFRA_EMISIJE)
    REFERENCES EMISIJA (SIFRA_EMISIJE);

ALTER TABLE AKTIVNOST_PRODUKCIJE
    ADD CONSTRAINT FK_AKTIVNOST_PROJEKAT FOREIGN KEY (SIFRA_PROJEKTA)
    REFERENCES PROJEKAT_PRODUKCIJE (SIFRA_PROJEKTA);

ALTER TABLE TROSAK_PRODUKCIJE
    ADD CONSTRAINT FK_TROSAK_IZAZIVA FOREIGN KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI)
    REFERENCES AKTIVNOST_PRODUKCIJE (SIFRA_PROJEKTA, RB_AKTIVNOSTI);

ALTER TABLE TROSAK_PRODUKCIJE
    ADD CONSTRAINT FK_TROSAK_DOKUMENTOVAN FOREIGN KEY (BROJ_FAKTURE)
    REFERENCES FAKTURA (BROJ_FAKTURE);

ALTER TABLE ANGAZOVANJE_NA_AKTIVNOSTI
    ADD CONSTRAINT FK_ANGAZ_AKTIVNOST FOREIGN KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI)
    REFERENCES AKTIVNOST_PRODUKCIJE (SIFRA_PROJEKTA, RB_AKTIVNOSTI);

ALTER TABLE ANGAZOVANJE_NA_AKTIVNOSTI
    ADD CONSTRAINT FK_ANGAZ_ZAPOSLENI FOREIGN KEY (SIFRA_ZAPOSLENOG)
    REFERENCES ZAPOSLENI (SIFRA_ZAPOSLENOG);

ALTER TABLE REZERVACIJA_OPREME
    ADD CONSTRAINT FK_REZERV_AKTIVNOST FOREIGN KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI)
    REFERENCES AKTIVNOST_PRODUKCIJE (SIFRA_PROJEKTA, RB_AKTIVNOSTI);

ALTER TABLE REZERVACIJA_OPREME
    ADD CONSTRAINT FK_REZERV_OPREMA FOREIGN KEY (INVENTARSKI_BROJ)
    REFERENCES OPREMA (INVENTARSKI_BROJ);

ALTER TABLE SIROVI_SNIMAK
    ADD CONSTRAINT FK_SNIMAK_SNIMLJEN_NA FOREIGN KEY (SIFRA_PROJEKTA, RB_AKTIVNOSTI)
    REFERENCES AKTIVNOST_PRODUKCIJE (SIFRA_PROJEKTA, RB_AKTIVNOSTI);

ALTER TABLE PROGRAMSKA_SEMA
    ADD CONSTRAINT FK_PSEMA_ODOBRAVA FOREIGN KEY (SIFRA_UREDNIKA)
    REFERENCES UREDNIK (SIFRA_ZAPOSLENOG);

ALTER TABLE PROGRAMSKA_CELINA
    ADD CONSTRAINT FK_PCELINA_PSEMA FOREIGN KEY (SIFRA_SEME)
    REFERENCES PROGRAMSKA_SEMA (SIFRA_SEME);

ALTER TABLE TERMIN_EMITOVANJA
    ADD CONSTRAINT FK_TERMIN_OBUHVATA FOREIGN KEY (SIFRA_SEME, RB_CELINE)
    REFERENCES PROGRAMSKA_CELINA (SIFRA_SEME, RB_CELINE);

ALTER TABLE TERMIN_EMITOVANJA
    ADD CONSTRAINT FK_TERMIN_PLANIRANA FOREIGN KEY (SIFRA_EMISIJE)
    REFERENCES EMISIJA (SIFRA_EMISIJE);

ALTER TABLE PRODUCIRANI_SADRZAJ
    ADD CONSTRAINT FK_MSPROD_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE NABAVLJENI_SADRZAJ
    ADD CONSTRAINT FK_MSNAB_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE NABAVLJENI_SADRZAJ
    ADD CONSTRAINT FK_MSNAB_NABAVLJEN_PO FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR_O_NABAVCI (BROJ_UGOVORA);

ALTER TABLE REKLAMNI_SADRZAJ
    ADD CONSTRAINT FK_MSREK_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE REKLAMNI_SADRZAJ
    ADD CONSTRAINT FK_MSREK_DOSTAVLJA FOREIGN KEY (SIFRA_OGLASIVACA)
    REFERENCES OGLASIVAC (SIFRA_KLIJENTA);

ALTER TABLE ZAPIS_O_EMITOVANJU
    ADD CONSTRAINT FK_ZAPISEM_REALIZOVAN FOREIGN KEY (SIFRA_TERMINA)
    REFERENCES TERMIN_EMITOVANJA (SIFRA_TERMINA);

ALTER TABLE ZAPIS_O_EMITOVANJU
    ADD CONSTRAINT FK_ZAPISEM_EVIDENTIRA FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE MONTAZA_SNIMKA
    ADD CONSTRAINT FK_MONTAZA_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE MONTAZA_SNIMKA
    ADD CONSTRAINT FK_MONTAZA_SNIMAK FOREIGN KEY (SIFRA_SNIMKA)
    REFERENCES SIROVI_SNIMAK (SIFRA_SNIMKA);

ALTER TABLE UGRADNJA_ELEMENTA
    ADD CONSTRAINT FK_UGRADNJA_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE UGRADNJA_ELEMENTA
    ADD CONSTRAINT FK_UGRADNJA_ELEMENT FOREIGN KEY (SIFRA_ELEMENTA)
    REFERENCES GRAFICKI_I_MUZICKI_ELEMENT (SIFRA_ELEMENTA);

ALTER TABLE SADRZAJ_EMISIJE
    ADD CONSTRAINT FK_SADREM_EMISIJA FOREIGN KEY (SIFRA_EMISIJE)
    REFERENCES EMISIJA (SIFRA_EMISIJE);

ALTER TABLE SADRZAJ_EMISIJE
    ADD CONSTRAINT FK_SADREM_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE POKRIVENOST_PRAVOM
    ADD CONSTRAINT FK_POKRIV_PRAVO FOREIGN KEY (BROJ_LICENCE)
    REFERENCES PRAVO_KORISCENJA (BROJ_LICENCE);

ALTER TABLE POKRIVENOST_PRAVOM
    ADD CONSTRAINT FK_POKRIV_MSADRZAJ FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES MEDIJSKI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE POVRATNA_INFO_GLEDALACA
    ADD CONSTRAINT FK_POVRINF_EMISIJA FOREIGN KEY (SIFRA_EMISIJE)
    REFERENCES EMISIJA (SIFRA_EMISIJE);

ALTER TABLE MERENJE_EMISIJE
    ADD CONSTRAINT FK_MERENJEEM_MERENJE FOREIGN KEY (SIFRA_MERENJA)
    REFERENCES MERENJE_GLEDANOSTI (SIFRA_MERENJA);

ALTER TABLE MERENJE_EMISIJE
    ADD CONSTRAINT FK_MERENJEEM_EMISIJA FOREIGN KEY (SIFRA_EMISIJE)
    REFERENCES EMISIJA (SIFRA_EMISIJE);

ALTER TABLE REKLAMNI_BLOK
    ADD CONSTRAINT FK_RBLOK_ZAKUPLJEN_U FOREIGN KEY (SIFRA_TERMINA)
    REFERENCES TERMIN_EMITOVANJA (SIFRA_TERMINA);

ALTER TABLE REKLAMNI_BLOK
    ADD CONSTRAINT FK_RBLOK_TARIFIRAN FOREIGN KEY (SIFRA_CENOVNIKA)
    REFERENCES CENOVNIK_REKL_TERMINA (SIFRA_CENOVNIKA);

ALTER TABLE EMITOVANJE_REKLAME
    ADD CONSTRAINT FK_EMREK_SADRZI_SPOT FOREIGN KEY (SIFRA_BLOKA)
    REFERENCES REKLAMNI_BLOK (SIFRA_BLOKA);

ALTER TABLE EMITOVANJE_REKLAME
    ADD CONSTRAINT FK_EMREK_PRIKAZUJE FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES REKLAMNI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE EMITOVANJE_REKLAME
    ADD CONSTRAINT FK_EMREK_UGOVOREN FOREIGN KEY (BROJ_UGOVORA, RB_STAVKE_UGOVORA)
    REFERENCES STAVKA_UGOVORA (BROJ_UGOVORA, RB_STAVKE);

ALTER TABLE OGLASIVAC
    ADD CONSTRAINT FK_OGLASIVAC_KLIJENT FOREIGN KEY (SIFRA_KLIJENTA)
    REFERENCES KLIJENT (SIFRA_KLIJENTA);

ALTER TABLE KUPAC_SADRZAJA
    ADD CONSTRAINT FK_KUPACSAD_KLIJENT FOREIGN KEY (SIFRA_KLIJENTA)
    REFERENCES KLIJENT (SIFRA_KLIJENTA);

ALTER TABLE UGOVOR
    ADD CONSTRAINT FK_UGOVOR_SKLAPA FOREIGN KEY (SIFRA_KLIJENTA)
    REFERENCES KLIJENT (SIFRA_KLIJENTA);

ALTER TABLE STAVKA_UGOVORA
    ADD CONSTRAINT FK_STUGOV_PRECIZIRA FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR (BROJ_UGOVORA);

ALTER TABLE UGOVOR_O_OGLASAVANJU
    ADD CONSTRAINT FK_UGOGL_UGOVOR FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR (BROJ_UGOVORA);

ALTER TABLE UGOVOR_O_PRODAJI_TV_SADRZAJA
    ADD CONSTRAINT FK_UGPROD_UGOVOR FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR (BROJ_UGOVORA);

ALTER TABLE UGOVOR_O_NABAVCI
    ADD CONSTRAINT FK_UGNAB_UGOVOR FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR (BROJ_UGOVORA);

ALTER TABLE UGOVOR_O_NABAVCI
    ADD CONSTRAINT FK_UGNAB_UGOVARA FOREIGN KEY (SIFRA_DOBAVLJACA)
    REFERENCES DOBAVLJAC (SIFRA_DOBAVLJACA);

ALTER TABLE USTUPANJE_SADRZAJA
    ADD CONSTRAINT FK_USTUP_UGPROD FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR_O_PRODAJI_TV_SADRZAJA (BROJ_UGOVORA);

ALTER TABLE USTUPANJE_SADRZAJA
    ADD CONSTRAINT FK_USTUP_MSPROD FOREIGN KEY (SIFRA_SADRZAJA)
    REFERENCES PRODUCIRANI_SADRZAJ (SIFRA_SADRZAJA);

ALTER TABLE ZAHTEV_ZA_NABAVKU
    ADD CONSTRAINT FK_ZAHNAB_PODNOSI FOREIGN KEY (SIFRA_JEDINICE)
    REFERENCES ORGANIZACIONA_JEDINICA (SIFRA_JEDINICE);

ALTER TABLE ZAHTEV_ZA_NABAVKU
    ADD CONSTRAINT FK_ZAHNAB_UVRSTEN_U FOREIGN KEY (SIFRA_PLANA)
    REFERENCES PLAN_NABAVKE (SIFRA_PLANA);

ALTER TABLE STAVKA_PLANA_NABAVKE
    ADD CONSTRAINT FK_STPLAN_PLAN FOREIGN KEY (SIFRA_PLANA)
    REFERENCES PLAN_NABAVKE (SIFRA_PLANA);

ALTER TABLE DOBAVLJAC_TV_SADRZAJA
    ADD CONSTRAINT FK_DOBTVSAD_DOBAVLJAC FOREIGN KEY (SIFRA_DOBAVLJACA)
    REFERENCES DOBAVLJAC (SIFRA_DOBAVLJACA);

ALTER TABLE DOBAVLJAC_OPREME_I_MATERIJALA
    ADD CONSTRAINT FK_DOBOPR_DOBAVLJAC FOREIGN KEY (SIFRA_DOBAVLJACA)
    REFERENCES DOBAVLJAC (SIFRA_DOBAVLJACA);

ALTER TABLE PONUDA_DOBAVLJACA
    ADD CONSTRAINT FK_PONUDA_DOSTAVIO FOREIGN KEY (SIFRA_DOBAVLJACA)
    REFERENCES DOBAVLJAC (SIFRA_DOBAVLJACA);

ALTER TABLE PONUDJENA_STAVKA
    ADD CONSTRAINT FK_PONSTAV_STPLAN FOREIGN KEY (SIFRA_PLANA, RB_STAVKE)
    REFERENCES STAVKA_PLANA_NABAVKE (SIFRA_PLANA, RB_STAVKE);

ALTER TABLE PONUDJENA_STAVKA
    ADD CONSTRAINT FK_PONSTAV_PONUDA FOREIGN KEY (BROJ_PONUDE)
    REFERENCES PONUDA_DOBAVLJACA (BROJ_PONUDE);

ALTER TABLE OCENA_PONUDE
    ADD CONSTRAINT FK_OCENA_PONUDA FOREIGN KEY (BROJ_PONUDE)
    REFERENCES PONUDA_DOBAVLJACA (BROJ_PONUDE);

ALTER TABLE OCENA_PONUDE
    ADD CONSTRAINT FK_OCENA_KRITERIJUM FOREIGN KEY (SIFRA_KRITERIJUMA)
    REFERENCES KRITERIJUM_VREDNOVANJA (SIFRA_KRITERIJUMA);

ALTER TABLE NARUDZBENICA
    ADD CONSTRAINT FK_NARUDZB_NARUCENO_OD FOREIGN KEY (SIFRA_DOBAVLJACA)
    REFERENCES DOBAVLJAC (SIFRA_DOBAVLJACA);

ALTER TABLE STAVKA_NARUDZBENICE
    ADD CONSTRAINT FK_STNARUD_NARUDZBENICA FOREIGN KEY (BROJ_NARUDZBENICE)
    REFERENCES NARUDZBENICA (BROJ_NARUDZBENICE);

ALTER TABLE PRIJEMNICA
    ADD CONSTRAINT FK_PRIJEMN_PRACENA FOREIGN KEY (BROJ_NARUDZBENICE)
    REFERENCES NARUDZBENICA (BROJ_NARUDZBENICE);

ALTER TABLE PRIJEMNICA
    ADD CONSTRAINT FK_PRIJEMN_FAKTURISANA FOREIGN KEY (BROJ_FAKTURE)
    REFERENCES FAKTURA (BROJ_FAKTURE);

ALTER TABLE PRIJEM_STAVKE
    ADD CONSTRAINT FK_PRIJSTAV_PRIJEMNICA FOREIGN KEY (BROJ_PRIJEMNICE)
    REFERENCES PRIJEMNICA (BROJ_PRIJEMNICE);

ALTER TABLE PRIJEM_STAVKE
    ADD CONSTRAINT FK_PRIJSTAV_STNARUD FOREIGN KEY (BROJ_NARUDZBENICE, RB_STAVKE)
    REFERENCES STAVKA_NARUDZBENICE (BROJ_NARUDZBENICE, RB_STAVKE);

ALTER TABLE REKLAMACIJA
    ADD CONSTRAINT FK_REKLAMAC_PRIJEMNICA FOREIGN KEY (BROJ_PRIJEMNICE)
    REFERENCES PRIJEMNICA (BROJ_PRIJEMNICE);

ALTER TABLE REKLAMIRANA_STAVKA
    ADD CONSTRAINT FK_REKSTAV_REKLAMACIJA FOREIGN KEY (BROJ_REKLAMACIJE)
    REFERENCES REKLAMACIJA (BROJ_REKLAMACIJE);

ALTER TABLE REKLAMIRANA_STAVKA
    ADD CONSTRAINT FK_REKSTAV_STNARUD FOREIGN KEY (BROJ_NARUDZBENICE, RB_STAVKE)
    REFERENCES STAVKA_NARUDZBENICE (BROJ_NARUDZBENICE, RB_STAVKE);

ALTER TABLE FAKTURA
    ADD CONSTRAINT FK_FAKTURA_IZDATA_PO FOREIGN KEY (BROJ_UGOVORA)
    REFERENCES UGOVOR (BROJ_UGOVORA);

ALTER TABLE STAVKA_FAKTURE
    ADD CONSTRAINT FK_STFAKT_FAKTURA FOREIGN KEY (BROJ_FAKTURE)
    REFERENCES FAKTURA (BROJ_FAKTURE);

ALTER TABLE NALOG_ZA_PLACANJE
    ADD CONSTRAINT FK_NALOG_PLACENA FOREIGN KEY (BROJ_FAKTURE)
    REFERENCES FAKTURA (BROJ_FAKTURE);

