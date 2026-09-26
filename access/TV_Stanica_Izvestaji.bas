Attribute VB_Name = "modIzvestaji"
Option Compare Database
Option Explicit

' =====================================================================
'  TV PANORAMA - osam izvestaja iz Specifikacije izvestaja
'
'  Modul se uvozi u POSTOJECU bazu (Access_v1.accdb) i dodaje SAMO nove
'  objekte:
'     - upite sa prefiksom  qIzv...
'     - izvestaje sa prefiksom  rptIzv...
'     - jednu formu  frmIzvestaji  (meni za pokretanje izvestaja)
'
'  Postojece tabele, forme i upiti se NE MENJAJU.  Procedure koje brisu
'  proveravaju prefiks imena, pa ne mogu obrisati nista tudje.
'
'  KAKO SE KORISTI
'    1. Otvori svoju bazu (Access_v1.accdb).
'    2. Alt+F11  ->  File  ->  Import File...  ->  izaberi ovaj .bas
'    3. Tools -> References...  ->  ukljuci "Microsoft Office x.0 Access
'       database engine Object Library" (DAO), ako vec nije ukljucena.
'    4. Klikni bilo gde u proceduru KreirajIzvestaje i pritisni F5.
'
'  NAPOMENA O SRPSKIM SLOVIMA
'    Fajl je namerno ciste ASCII sadrzine da bi se uvozio bez obzira na
'    kodnu stranu Windows-a.  Slova c, c, s, z, d se sastavljaju u funkciji
'    T() preko ChrW, pa su natpisi u bazi ispravni.
' =====================================================================

Private Const APP_NAZIV As String = "TV Panorama"
Private Const P_UPIT As String = "qIzv"
Private Const P_IZV As String = "rptIzv"
Private Const P_FORMA As String = "frmIzvestaji"

Private gUpit As Long, gIzv As Long, gForm As Long, gGreske As Long
Private gOk As Long, gPrazno As Long, gLose As Long
Private gPoruke As String

' ---------------------------------------------------------------- srpska slova
Private Function Z(ByVal s As String, ByVal marker As String, ByVal kod As Long) As String
    ' vbBinaryCompare je obavezan: uz Option Compare Database Replace ne razlikuje
    ' velika i mala slova.
    Z = Replace(s, marker, ChrW(kod), 1, -1, vbBinaryCompare)
End Function

Private Function T(ByVal s As String) As String
    If InStr(1, s, "~", vbBinaryCompare) = 0 Then
        T = s
        Exit Function
    End If
    s = Z(s, "~C", 268): s = Z(s, "~c", 269)
    s = Z(s, "~K", 262): s = Z(s, "~k", 263)
    s = Z(s, "~S", 352): s = Z(s, "~s", 353)
    s = Z(s, "~Z", 381): s = Z(s, "~z", 382)
    s = Z(s, "~D", 272): s = Z(s, "~d", 273)
    T = s
End Function

Private Sub Beleska(ByVal s As String)
    Debug.Print s
    gPoruke = gPoruke & s & vbCrLf
End Sub

' ---------------------------------------------------------------- javne pomocne
Public Function Generisao() As String
    Dim s As String
    On Error Resume Next
    s = CurrentUser()
    If Len(s) = 0 Or s = "Admin" Then s = Environ$("USERNAME")
    If Len(s) = 0 Then s = "Admin"
    Err.Clear
    Generisao = T("Izradio: ") & s
End Function

Public Function Spisak(ByVal sql As String) As String
    ' Vrati vrednosti prve kolone upita, razdvojene zapetom.
    Dim db As DAO.Database, rs As DAO.Recordset, s As String
    On Error GoTo Greska
    Set db = CurrentDb
    Set rs = db.OpenRecordset(sql)
    Do While Not rs.EOF
        If Len(s) > 0 Then s = s & ", "
        s = s & Nz(rs(0), "")
        rs.MoveNext
    Loop
    rs.Close
    Spisak = s
    Exit Function
Greska:
    Spisak = ""
    Err.Clear
End Function

Public Function Zaglavlje3() As String
    ' Period merenja, izvori i ciljne grupe - zaglavlje izvestaja 3.
    Dim od As String, dd As String
    On Error Resume Next
    od = Format(DMin("DATUM_MERENJA", "MERENJE_GLEDANOSTI"), "dd.mm.yyyy.")
    dd = Format(DMax("DATUM_MERENJA", "MERENJE_GLEDANOSTI"), "dd.mm.yyyy.")
    Err.Clear
    Zaglavlje3 = T("Period merenja: ") & od & " - " & dd & _
        T("     Izvori merenja: ") & _
        Spisak("SELECT DISTINCT IZVOR_MERENJA FROM MERENJE_GLEDANOSTI" & _
               " ORDER BY IZVOR_MERENJA") & _
        T("     Ciljne grupe: ") & _
        Spisak("SELECT DISTINCT CILJNA_GRUPA FROM MERENJE_GLEDANOSTI" & _
               " ORDER BY CILJNA_GRUPA")
End Function

Public Function OtvoriIzvestaj(ByVal ime As String)
    On Error Resume Next
    DoCmd.OpenReport ime, acViewPreview
    Err.Clear
End Function

' ---------------------------------------------------------------- brisanje
' Brise se samo ono sto je ovaj modul i napravio - proverava se prefiks.
Private Sub ObrisiUpit(ByVal ime As String)
    If Left(ime, Len(P_UPIT)) <> P_UPIT Then
        Beleska "  ODBIJENO brisanje upita " & ime & " (nije qIzv...)"
        Exit Sub
    End If
    On Error Resume Next
    CurrentDb.QueryDefs.Delete ime
    Err.Clear
End Sub

Private Sub ObrisiIzvestaj(ByVal ime As String)
    If Left(ime, Len(P_IZV)) <> P_IZV Then
        Beleska "  ODBIJENO brisanje izvestaja " & ime & " (nije rptIzv...)"
        Exit Sub
    End If
    On Error Resume Next
    DoCmd.DeleteObject acReport, ime
    Err.Clear
End Sub

Private Sub ObrisiFormu(ByVal ime As String)
    If Left(ime, Len(P_FORMA)) <> P_FORMA Then
        Beleska "  ODBIJENO brisanje forme " & ime & " (nije frmIzvestaji)"
        Exit Sub
    End If
    On Error Resume Next
    DoCmd.DeleteObject acForm, ime
    Err.Clear
End Sub

' ---------------------------------------------------------------- upiti
Private Sub Upit(ByVal ime As String, ByVal sql As String)
    Dim db As DAO.Database
    ObrisiUpit ime
    Set db = CurrentDb
    On Error GoTo Greska
    db.CreateQueryDef ime, T(sql)
    db.QueryDefs.Refresh
    gUpit = gUpit + 1
    Exit Sub
Greska:
    gGreske = gGreske + 1
    Beleska "  upit " & ime & " nije napravljen: " & Err.Description
    Err.Clear
End Sub

' ---------------------------------------------------------------- izvestaji
Private Function Poc(ByVal izvor As String) As String
    Dim rpt As Report
    Set rpt = CreateReport()
    rpt.RecordSource = izvor
    Poc = rpt.Name
End Function

Private Sub Gr(ByVal r As String, ByVal izraz As String, ByVal zagl As Boolean, _
               ByVal podn As Boolean)
    On Error GoTo Greska
    CreateGroupLevel r, izraz, zagl, podn
    Exit Sub
Greska:
    gGreske = gGreske + 1
    Beleska "  grupa " & izraz & " u " & r & ": " & Err.Description
    Err.Clear
End Sub

Private Sub Sek(ByVal r As String, ByVal s As Integer, ByVal h As Long, _
                Optional ByVal rast As Boolean = False)
    On Error Resume Next
    Reports(r).Section(s).Visible = True
    Reports(r).Section(s).Height = h
    Reports(r).Section(s).CanGrow = rast
    Reports(r).Section(s).CanShrink = rast
    Err.Clear
End Sub

Private Function Lab(ByVal r As String, ByVal s As Integer, ByVal x As Long, _
                     ByVal y As Long, ByVal w As Long, ByVal h As Long, _
                     ByVal tekst As String, Optional ByVal vel As Long = 9, _
                     Optional ByVal bold As Boolean = False, _
                     Optional ByVal por As Integer = 1) As Control
    Dim ctl As Control
    On Error GoTo Greska
    Set ctl = CreateReportControl(r, acLabel, s, , , x, y, w, h)
    ctl.Caption = T(tekst)
    ctl.FontSize = vel
    ctl.FontBold = bold
    ctl.TextAlign = por
    If Not bold And vel <= 9 Then ctl.ForeColor = RGB(70, 80, 95)
    Set Lab = ctl
    Exit Function
Greska:
    gGreske = gGreske + 1
    Beleska "  natpis """ & tekst & """ u " & r & ": " & Err.Description
    Err.Clear
End Function

Private Function Txt(ByVal r As String, ByVal s As Integer, ByVal x As Long, _
                     ByVal y As Long, ByVal w As Long, ByVal h As Long, _
                     ByVal izv As String, Optional ByVal vel As Long = 9, _
                     Optional ByVal bold As Boolean = False, _
                     Optional ByVal por As Integer = 1, _
                     Optional ByVal fmt As String = "") As Control
    Dim ctl As Control
    On Error GoTo Greska
    Set ctl = CreateReportControl(r, acTextBox, s, , , x, y, w, h)
    ctl.ControlSource = T(izv)
    ctl.FontSize = vel
    ctl.FontBold = bold
    ctl.TextAlign = por
    ctl.BorderStyle = 0
    ctl.CanGrow = False
    If Len(fmt) > 0 Then ctl.Format = fmt
    Set Txt = ctl
    Exit Function
Greska:
    gGreske = gGreske + 1
    Beleska "  polje " & izv & " u " & r & ": " & Err.Description
    Err.Clear
End Function

Private Sub Lin(ByVal r As String, ByVal s As Integer, ByVal x As Long, _
                ByVal y As Long, ByVal w As Long)
    On Error Resume Next
    CreateReportControl r, acLine, s, , , x, y, w, 0
    Err.Clear
End Sub

Private Sub Podnozje(ByVal r As String, ByVal sirina As Long)
    Sek r, acPageFooter, 360
    Lin r, acPageFooter, 0, 40, sirina
    Txt r, acPageFooter, 0, 100, 3400, 240, "=Now()", 8, False, 1, "dd.mm.yyyy. hh:nn"
    Txt r, acPageFooter, 3500, 100, 4600, 240, "=Generisao()", 8, False, 1
    Txt r, acPageFooter, sirina - 3100, 100, 3000, 240, _
        "=""Strana "" & [Page] & "" od "" & [Pages]", 8, False, 3
End Sub

Private Sub Grafikon(ByVal r As String, ByVal s As Integer, ByVal x As Long, _
                     ByVal y As Long, ByVal w As Long, ByVal h As Long, _
                     ByVal upit As String)
    Dim ctl As Control
    On Error GoTo Greska
    Set ctl = CreateReportControl(r, acObjectFrame, s, , , x, y, w, h)
    ctl.Class = "MSGraph.Chart.8"
    ctl.RowSourceType = "Table/Query"
    ctl.RowSource = upit
    Beleska "  grafikon nad " & upit & " dodat"
    Exit Sub
Greska:
    Beleska "  grafikon nad " & upit & " nije dodat (" & Err.Description & _
            ") - izvestaj radi i bez njega"
    Err.Clear
End Sub

Private Sub Pod(ByVal r As String, ByVal s As Integer, ByVal x As Long, _
                ByVal y As Long, ByVal w As Long, ByVal h As Long, _
                ByVal podizvestaj As String, Optional ByVal masterPolja As String = "", _
                Optional ByVal childPolja As String = "")
    Dim ctl As Control
    On Error GoTo Greska
    Set ctl = CreateReportControl(r, acSubform, s, , , x, y, w, h)
    ctl.SourceObject = "Report." & podizvestaj
    If Len(masterPolja) > 0 Then
        ctl.LinkMasterFields = masterPolja
        ctl.LinkChildFields = childPolja
    End If
    ctl.CanGrow = True
    ctl.CanShrink = True
    Beleska "  podizvestaj " & podizvestaj & " ugradjen u " & r
    Exit Sub
Greska:
    gGreske = gGreske + 1
    Beleska "  podizvestaj " & podizvestaj & " nije ugradjen: " & Err.Description
    Err.Clear
End Sub

Private Sub Kraj(ByVal priv As String, ByVal ime As String, ByVal naslov As String, _
                 ByVal sirina As Long, ByVal pejzaz As Boolean)
    Dim rpt As Report
    On Error GoTo Greska
    Set rpt = Reports(priv)
    rpt.Width = sirina
    rpt.Caption = T(naslov)
    On Error Resume Next
    rpt.Printer.PaperSize = 9
    rpt.Printer.TopMargin = 400
    rpt.Printer.BottomMargin = 400
    rpt.Printer.LeftMargin = 360
    rpt.Printer.RightMargin = 360
    If pejzaz Then rpt.Printer.Orientation = 2 Else rpt.Printer.Orientation = 1
    Err.Clear
    On Error GoTo Greska
    DoCmd.Close acReport, priv, acSaveYes
    DoCmd.Rename ime, acReport, priv
    gIzv = gIzv + 1
    Beleska "  izvestaj " & ime & " napravljen"
    Exit Sub
Greska:
    gGreske = gGreske + 1
    Beleska "  izvestaj " & ime & " nije dovrsen: " & Err.Description
    Err.Clear
    On Error Resume Next
    DoCmd.Close acReport, priv, acSaveNo
    Err.Clear
End Sub

' ================================================================
'  PROVERA - otvara svaki upit i svaki izvestaj i kaze sta radi
'  a sta ne.  Pokrece se i sama na kraju procedure KreirajIzvestaje.
' ================================================================
Private Function ImaParametre(ByVal izvestaj As String) As Boolean
    ImaParametre = (izvestaj = "rptIzv2" Or izvestaj = "rptIzv6")
End Function

Private Function ProveriUpit(ByVal ime As String) As String
    Dim db As DAO.Database, qd As DAO.QueryDef, rs As DAO.Recordset
    Dim i As Long, n As Long, par As String
    On Error GoTo Greska
    Set db = CurrentDb
    Set qd = db.QueryDefs(ime)
    For i = 0 To qd.Parameters.Count - 1
        If qd.Parameters(i).Type = dbDate Then
            If InStr(1, qd.Parameters(i).Name, "do:", vbBinaryCompare) > 0 Then
                qd.Parameters(i) = DateSerial(2100, 12, 31)
            Else
                qd.Parameters(i) = DateSerial(1900, 1, 1)
            End If
        Else
            qd.Parameters(i) = Nz(DMin("SIFRA_KLIJENTA", "OGLASIVAC"), "")
        End If
        par = par & " [" & qd.Parameters(i).Name & "=" & qd.Parameters(i) & "]"
    Next i
    Set rs = qd.OpenRecordset(dbOpenSnapshot)
    n = 0
    If Not rs.EOF Then
        rs.MoveLast
        n = rs.RecordCount
    End If
    rs.Close
    If n > 0 Then
        gOk = gOk + 1
        ProveriUpit = "  U REDU  " & ime & " - " & n & T(" redova") & par
    Else
        gPrazno = gPrazno + 1
        ProveriUpit = "  PRAZNO  " & ime & T(" - upit radi, ali ne vraca ni jedan red") & par
    End If
    Exit Function
Greska:
    gLose = gLose + 1
    ProveriUpit = "  GRESKA  " & ime & " - " & Err.Description
    Err.Clear
End Function

Private Function ProveriIzvestaj(ByVal ime As String) As String
    Dim rpt As Report, ima As Boolean
    On Error GoTo Greska
    If ImaParametre(ime) Then
        gOk = gOk + 1
        ProveriIzvestaj = "  U REDU  " & ime & _
            T(" - parametarski; pokreni ga rucno i unesi vrednosti")
        Exit Function
    End If
    DoCmd.OpenReport ime, acViewPreview, , , acHidden
    Set rpt = Reports(ime)
    ima = (rpt.HasData <> 0)
    DoCmd.Close acReport, ime, acSaveNo
    If ima Then
        gOk = gOk + 1
        ProveriIzvestaj = "  U REDU  " & ime & T(" - otvara se i ima podatke")
    Else
        gPrazno = gPrazno + 1
        ProveriIzvestaj = "  PRAZNO  " & ime & T(" - otvara se, ali nema podataka")
    End If
    Exit Function
Greska:
    gLose = gLose + 1
    ProveriIzvestaj = "  GRESKA  " & ime & " - " & Err.Description
    Err.Clear
    On Error Resume Next
    DoCmd.Close acReport, ime, acSaveNo
    Err.Clear
End Function

Private Function ProveriSve() As String
    Dim db As DAO.Database, i As Long, s As String, ime As String
    gOk = 0: gPrazno = 0: gLose = 0
    Set db = CurrentDb
    s = T("UPITI") & vbCrLf
    For i = 0 To db.QueryDefs.Count - 1
        ime = db.QueryDefs(i).Name
        If Left(ime, Len(P_UPIT)) = P_UPIT Then s = s & ProveriUpit(ime) & vbCrLf
    Next i
    s = s & vbCrLf & T("IZVESTAJI") & vbCrLf
    For i = 0 To CurrentProject.AllReports.Count - 1
        ime = CurrentProject.AllReports(i).Name
        If Left(ime, Len(P_IZV)) = P_IZV Then s = s & ProveriIzvestaj(ime) & vbCrLf
    Next i
    ProveriSve = s
End Function

Public Sub Provera()
    Dim s As String
    On Error Resume Next
    DoCmd.SetWarnings False
    Err.Clear
    s = ProveriSve()
    DoCmd.SetWarnings True
    Debug.Print s
    gPoruke = gPoruke & vbCrLf & s
    MsgBox T("Provera upita i izvestaja") & vbCrLf & vbCrLf & _
           T("u redu: ") & gOk & vbCrLf & _
           T("prazno (radi, ali bez podataka): ") & gPrazno & vbCrLf & _
           T("greska: ") & gLose & vbCrLf & vbCrLf & _
           T("Detaljan spisak je u Immediate prozoru (Ctrl+G),") & vbCrLf & _
           T("a ispisuje se i procedurom Dnevnik."), vbInformation, APP_NAZIV
End Sub

' ---------------------------------------------- upiti (1)
Private Sub Upiti1()
    Dim s As String
    ' qIzv1_Sema
    s = "SELECT PS.SIFRA_SEME, PS.NAZIV_SEME, PS.SEZONA, PS.VERZIJA_SEME, PS.STATUS_SEME, PS.DATUM_OD AS SEMA_OD, PS.DATUM_DO AS SEMA_DO, PS.DATUM_USVAJANJA, (Z.PREZIME & "" "" & "
    s = s & "Z.IME) AS UREDNIK_NAZIV, UR.REDAKCIJA, PC.RB_CELINE, PC.NAZIV_CELINE, PC.TIP_CELINE, PC.DATUM AS DATUM_CELINE, PC.VREME_OD, PC.VREME_DO, (PS.SIFRA_SEME & ""-"" & "
    s = s & "Format(PC.RB_CELINE,""000"")) AS CELINA_KLJUC, TE.SIFRA_TERMINA, TE.DATUM AS DATUM_TERMINA, TE.VREME_POCETKA, E.NAZIV_EMISIJE, E.ZANR, TE.TRAJANJE_TERMINA, TE.TIP_TERMINA, "
    s = s & "TE.ZONA_GLEDANOSTI, TE.REDNI_BROJ_REPRIZE, TE.STATUS_TERMINA FROM ((((PROGRAMSKA_SEMA AS PS INNER JOIN PROGRAMSKA_CELINA AS PC ON PS.SIFRA_SEME = PC.SIFRA_SEME) INNER "
    s = s & "JOIN TERMIN_EMITOVANJA AS TE ON (PC.SIFRA_SEME = TE.SIFRA_SEME) AND (PC.RB_CELINE = TE.RB_CELINE)) INNER JOIN EMISIJA AS E ON TE.SIFRA_EMISIJE = E.SIFRA_EMISIJE) INNER "
    s = s & "JOIN UREDNIK AS UR ON PS.SIFRA_UREDNIKA = UR.SIFRA_ZAPOSLENOG) INNER JOIN ZAPOSLENI AS Z ON UR.SIFRA_ZAPOSLENOG = Z.SIFRA_ZAPOSLENOG ORDER BY PS.SIFRA_SEME, PC.RB_CELINE, "
    s = s & "TE.VREME_POCETKA; "
    Upit "qIzv1_Sema", s
    ' qIzv2_Playout
    s = "PARAMETERS [Datum od:] DateTime, [Datum do:] DateTime; SELECT TE.DATUM, ZE.RB_EMITOVANJA, ZE.STVARNO_VREME_POCETKA, E.NAZIV_EMISIJE, MS.NAZIV_SADRZAJA, "
    s = s & "TE.TRAJANJE_TERMINA, ZE.STVARNO_TRAJANJE, (Nz(ZE.STVARNO_TRAJANJE,0) - Nz(TE.TRAJANJE_TERMINA,0)) AS ODSTUPANJE, ZE.STATUS_REALIZACIJE, PK.BROJ_LICENCE, PK.VRSTA_PRAVA, "
    s = s & "ZE.OPERATER_EMITOVANJA, ZE.NAPOMENA_O_SMETNJAMA, IIf(Len(Nz(ZE.NAPOMENA_O_SMETNJAMA,"""")) > 0, 1, 0) AS IMA_SMETNJU, [Datum od:] AS PAR_OD, [Datum do:] AS PAR_DO FROM "
    s = s & "((((ZAPIS_O_EMITOVANJU AS ZE INNER JOIN TERMIN_EMITOVANJA AS TE ON ZE.SIFRA_TERMINA = TE.SIFRA_TERMINA) INNER JOIN EMISIJA AS E ON TE.SIFRA_EMISIJE = E.SIFRA_EMISIJE) "
    s = s & "INNER JOIN MEDIJSKI_SADRZAJ AS MS ON ZE.SIFRA_SADRZAJA = MS.SIFRA_SADRZAJA) LEFT JOIN POKRIVENOST_PRAVOM AS PP ON MS.SIFRA_SADRZAJA = PP.SIFRA_SADRZAJA) LEFT JOIN "
    s = s & "PRAVO_KORISCENJA AS PK ON PP.BROJ_LICENCE = PK.BROJ_LICENCE WHERE TE.DATUM BETWEEN [Datum od:] AND [Datum do:] ORDER BY TE.DATUM, ZE.STVARNO_VREME_POCETKA; "
    Upit "qIzv2_Playout", s
    ' qIzv3_Emisije
    s = "SELECT E.NAZIV_EMISIJE, E.ZANR, Count(ME.SIFRA_MERENJA) AS BROJ_MERENJA, Round(Avg(ME.OSTVARENI_RATING),2) AS PROSECAN_REJTING, Round(Avg(ME.UDEO_U_TERMINU),2) AS "
    s = s & "PROSECAN_UDEO, Round(Avg(MG.BROJ_GLEDALACA),0) AS PROSECAN_BROJ_GLEDALACA, Round(Avg(MG.PROSECNO_GLEDANJE),1) AS PROSECNO_GLEDANJE FROM (EMISIJA AS E INNER JOIN "
    s = s & "MERENJE_EMISIJE AS ME ON E.SIFRA_EMISIJE = ME.SIFRA_EMISIJE) INNER JOIN MERENJE_GLEDANOSTI AS MG ON ME.SIFRA_MERENJA = MG.SIFRA_MERENJA GROUP BY E.NAZIV_EMISIJE, E.ZANR "
    s = s & "ORDER BY Avg(ME.OSTVARENI_RATING) DESC; "
    Upit "qIzv3_Emisije", s
    ' qIzv3_RejtingPoZanru
    s = "SELECT E.ZANR, Round(Avg(ME.OSTVARENI_RATING),2) AS PROSECAN_REJTING FROM EMISIJA AS E INNER JOIN MERENJE_EMISIJE AS ME ON E.SIFRA_EMISIJE = ME.SIFRA_EMISIJE GROUP BY "
    s = s & "E.ZANR ORDER BY E.ZANR; "
    Upit "qIzv3_RejtingPoZanru", s
End Sub

' ---------------------------------------------- upiti (2)
Private Sub Upiti2()
    Dim s As String
    ' qIzv3_RejtingPoDatumu
    s = "SELECT MG.DATUM_MERENJA, Round(Avg(ME.OSTVARENI_RATING),2) AS PROSECAN_REJTING FROM MERENJE_GLEDANOSTI AS MG INNER JOIN MERENJE_EMISIJE AS ME ON MG.SIFRA_MERENJA = "
    s = s & "ME.SIFRA_MERENJA GROUP BY MG.DATUM_MERENJA ORDER BY MG.DATUM_MERENJA; "
    Upit "qIzv3_RejtingPoDatumu", s
    ' qIzv4_Troskovi
    s = "SELECT PP.SIFRA_PROJEKTA, PP.NAZIV_PROJEKTA, PP.VRSTA_PRODUKCIJE, PP.STATUS_PROJEKTA, PP.DATUM_POCETKA, PP.DATUM_ZAVRSETKA, PP.ODOBREN_BUDZET, (Z.PREZIME & "" "" & Z.IME) "
    s = s & "AS UREDNIK_NAZIV, E.NAZIV_EMISIJE, AP.RB_AKTIVNOSTI, AP.NAZIV_AKTIVNOSTI, AP.VRSTA_AKTIVNOSTI, AP.LOKACIJA_SNIMANJA, AP.DATUM_OD, AP.DATUM_DO, AP.STATUS_AKTIVNOSTI, "
    s = s & "(PP.SIFRA_PROJEKTA & ""-"" & Format(AP.RB_AKTIVNOSTI,""000"")) AS AKT_KLJUC, TP.RB_TROSKA, TP.VRSTA_TROSKA, TP.OPIS_TROSKA, TP.DATUM_NASTANKA, TP.IZNOS, TP.BROJ_FAKTURE, "
    s = s & "FA.STATUS_PLACANJA FROM ((((PROJEKAT_PRODUKCIJE AS PP INNER JOIN AKTIVNOST_PRODUKCIJE AS AP ON PP.SIFRA_PROJEKTA = AP.SIFRA_PROJEKTA) INNER JOIN ZAPOSLENI AS Z ON "
    s = s & "PP.SIFRA_UREDNIKA = Z.SIFRA_ZAPOSLENOG) LEFT JOIN EMISIJA AS E ON PP.SIFRA_EMISIJE = E.SIFRA_EMISIJE) LEFT JOIN TROSAK_PRODUKCIJE AS TP ON (AP.SIFRA_PROJEKTA = "
    s = s & "TP.SIFRA_PROJEKTA) AND (AP.RB_AKTIVNOSTI = TP.RB_AKTIVNOSTI)) LEFT JOIN FAKTURA AS FA ON TP.BROJ_FAKTURE = FA.BROJ_FAKTURE ORDER BY PP.SIFRA_PROJEKTA, AP.RB_AKTIVNOSTI, "
    s = s & "TP.RB_TROSKA; "
    Upit "qIzv4_Troskovi", s
    ' qIzv5_Angazovanje
    s = "SELECT Z.SIFRA_ZAPOSLENOG, Z.IME, Z.PREZIME, Z.RADNO_MESTO, OJ.NAZIV_JEDINICE, (Z.PREZIME & "" "" & Z.IME & "" ("" & Z.SIFRA_ZAPOSLENOG & "")"") AS ZAPOSLENI_KLJUC, "
    s = s & "PP.SIFRA_PROJEKTA, PP.NAZIV_PROJEKTA, AP.RB_AKTIVNOSTI, AP.NAZIV_AKTIVNOSTI, AN.ULOGA_NA_SNIMANJU, AN.DATUM_OD, AN.DATUM_DO, AN.BROJ_ANGAZOVANIH_SATI FROM "
    s = s & "(((ANGAZOVANJE_NA_AKTIVNOSTI AS AN INNER JOIN ZAPOSLENI AS Z ON AN.SIFRA_ZAPOSLENOG = Z.SIFRA_ZAPOSLENOG) INNER JOIN ORGANIZACIONA_JEDINICA AS OJ ON Z.SIFRA_JEDINICE = "
    s = s & "OJ.SIFRA_JEDINICE) INNER JOIN AKTIVNOST_PRODUKCIJE AS AP ON (AN.SIFRA_PROJEKTA = AP.SIFRA_PROJEKTA) AND (AN.RB_AKTIVNOSTI = AP.RB_AKTIVNOSTI)) INNER JOIN "
    s = s & "PROJEKAT_PRODUKCIJE AS PP ON AP.SIFRA_PROJEKTA = PP.SIFRA_PROJEKTA ORDER BY Z.PREZIME, Z.IME, AN.DATUM_OD; "
    Upit "qIzv5_Angazovanje", s
    ' qIzv5_Oprema
    s = "SELECT O.INVENTARSKI_BROJ, O.NAZIV_OPREME, O.MODEL_OPREME, O.STATUS_OPREME, PP.NAZIV_PROJEKTA, AP.RB_AKTIVNOSTI, AP.NAZIV_AKTIVNOSTI, RO.DATUM_REZERVACIJE, "
    s = s & "RO.TRAJANJE_ZADUZENJA FROM ((REZERVACIJA_OPREME AS RO INNER JOIN OPREMA AS O ON RO.INVENTARSKI_BROJ = O.INVENTARSKI_BROJ) INNER JOIN AKTIVNOST_PRODUKCIJE AS AP ON "
    s = s & "(RO.SIFRA_PROJEKTA = AP.SIFRA_PROJEKTA) AND (RO.RB_AKTIVNOSTI = AP.RB_AKTIVNOSTI)) INNER JOIN PROJEKAT_PRODUKCIJE AS PP ON AP.SIFRA_PROJEKTA = PP.SIFRA_PROJEKTA ORDER BY "
    s = s & "O.INVENTARSKI_BROJ, RO.DATUM_REZERVACIJE; "
    Upit "qIzv5_Oprema", s
End Sub

' ---------------------------------------------- upiti (3)
Private Sub Upiti3()
    Dim s As String
    ' qIzv6_Fakture
    s = "SELECT F.BROJ_UGOVORA, Sum(F.IZNOS_ZA_PLACANJE) AS FAKTURISANO, Count(F.BROJ_FAKTURE) AS BROJ_FAKTURA, Min(F.STATUS_PLACANJA) AS STATUS_FAKTURE FROM FAKTURA AS F WHERE "
    s = s & "F.BROJ_UGOVORA Is Not Null GROUP BY F.BROJ_UGOVORA; "
    Upit "qIzv6_Fakture", s
    ' qIzv6_Kartica
    s = "PARAMETERS [~Sifra ili naziv ogla~siva~ca:] Text ( 255 ); SELECT K.SIFRA_KLIJENTA, K.NAZIV_KLIJENTA, K.PIB, K.KONTAKT_OSOBA, K.GRAD, OG.BRANSA, OG.GODISNJI_BUDZET, "
    s = s & "U.BROJ_UGOVORA, U.DATUM_SKLAPANJA, U.VAZI_OD, U.VAZI_DO, U.STATUS_UGOVORA, U.UKUPNA_VREDNOST, UO.UGOVORENI_TERMINI, SU.RB_STAVKE, SU.OPIS_STAVKE, SU.KOLICINA_SEKUNDE, "
    s = s & "SU.JEDINICNA_CENA, SU.POPUST, SU.VREDNOST_STAVKE, (U.BROJ_UGOVORA & ""-"" & Format(SU.RB_STAVKE,""000"")) AS STAVKA_KLJUC, ER.DATUM_EMITOVANJA, ER.VREME_EMITOVANJA, "
    s = s & "ER.SIFRA_BLOKA, RB.SIFRA_TERMINA, CN.ZONA, ER.TRAJANJE_SPOTA, ER.NAPLACENI_IZNOS, ER.STATUS_NAPLATE, (SELECT Sum(S2.KOLICINA_SEKUNDE) FROM STAVKA_UGOVORA AS S2 WHERE "
    s = s & "S2.BROJ_UGOVORA = U.BROJ_UGOVORA) AS UGOVORENO_SEKUNDI, (SELECT Sum(S2.VREDNOST_STAVKE) FROM STAVKA_UGOVORA AS S2 WHERE S2.BROJ_UGOVORA = U.BROJ_UGOVORA) AS "
    s = s & "UGOVORENA_VREDNOST, FK.FAKTURISANO, FK.STATUS_FAKTURE FROM (((((((KLIJENT AS K INNER JOIN OGLASIVAC AS OG ON K.SIFRA_KLIJENTA = OG.SIFRA_KLIJENTA) INNER JOIN UGOVOR AS U "
    s = s & "ON K.SIFRA_KLIJENTA = U.SIFRA_KLIJENTA) INNER JOIN UGOVOR_O_OGLASAVANJU AS UO ON U.BROJ_UGOVORA = UO.BROJ_UGOVORA) INNER JOIN STAVKA_UGOVORA AS SU ON U.BROJ_UGOVORA = "
    s = s & "SU.BROJ_UGOVORA) LEFT JOIN EMITOVANJE_REKLAME AS ER ON (SU.BROJ_UGOVORA = ER.BROJ_UGOVORA) AND (SU.RB_STAVKE = ER.RB_STAVKE_UGOVORA)) LEFT JOIN REKLAMNI_BLOK AS RB ON "
    s = s & "ER.SIFRA_BLOKA = RB.SIFRA_BLOKA) LEFT JOIN CENOVNIK_REKL_TERMINA AS CN ON RB.SIFRA_CENOVNIKA = CN.SIFRA_CENOVNIKA) LEFT JOIN [qIzv6_Fakture] AS FK ON U.BROJ_UGOVORA = "
    s = s & "FK.BROJ_UGOVORA WHERE K.SIFRA_KLIJENTA = [~Sifra ili naziv ogla~siva~ca:] OR K.NAZIV_KLIJENTA LIKE ""*"" & [~Sifra ili naziv ogla~siva~ca:] & ""*"" ORDER BY U.BROJ_UGOVORA, "
    s = s & "SU.RB_STAVKE, ER.DATUM_EMITOVANJA; "
    Upit "qIzv6_Kartica", s
    ' qIzv7_Zahtev
    s = "SELECT Z.SIFRA_PLANA, Z.BROJ_ZAHTEVA, Z.DATUM_ZAHTEVA, Z.VRSTA_NABAVKE, Z.STATUS_ZAHTEVA, Z.PRIORITET, Z.PROCENJENA_VREDNOST FROM ZAHTEV_ZA_NABAVKU AS Z WHERE "
    s = s & "Z.SIFRA_PLANA Is Not Null AND Z.BROJ_ZAHTEVA = (SELECT Min(Z2.BROJ_ZAHTEVA) FROM ZAHTEV_ZA_NABAVKU AS Z2 WHERE Z2.SIFRA_PLANA = Z.SIFRA_PLANA); "
    Upit "qIzv7_Zahtev", s
    ' qIzv7_Narudzbe
    s = "SELECT N.SIFRA_DOBAVLJACA, Min(N.BROJ_NARUDZBENICE) AS BROJ_NARUDZBENICE, Sum(N.UKUPAN_IZNOS) AS IZNOS_NARUDZBENICA, Count(N.BROJ_NARUDZBENICE) AS BROJ_NARUDZBENICA FROM "
    s = s & "NARUDZBENICA AS N GROUP BY N.SIFRA_DOBAVLJACA; "
    Upit "qIzv7_Narudzbe", s
End Sub

' ---------------------------------------------- upiti (4)
Private Sub Upiti4()
    Dim s As String
    ' qIzv7_Izabrana
    s = "SELECT PS.SIFRA_PLANA, PS.RB_STAVKE, Min(PD.BROJ_PONUDE) AS BROJ_PONUDE, Min(PD.SIFRA_DOBAVLJACA) AS SIFRA_DOBAVLJACA, Min(PS.PONUDJENA_CENA) AS PONUDJENA_CENA FROM "
    s = s & "PONUDJENA_STAVKA AS PS INNER JOIN PONUDA_DOBAVLJACA AS PD ON PS.BROJ_PONUDE = PD.BROJ_PONUDE WHERE PD.STATUS_PONUDE = ""Izabrana"" GROUP BY PS.SIFRA_PLANA, PS.RB_STAVKE; "
    Upit "qIzv7_Izabrana", s
    ' qIzv7_Stavke
    s = "SELECT PN.SIFRA_PLANA, PN.GODINA_PLANA, PN.DATUM_DONOSENJA, PN.STATUS_PLANA, PN.DONOSILAC_PLANA, PN.UKUPNA_VREDNOST, SP.RB_STAVKE, SP.OPIS_ARTIKLA, SP.KOLICINA, "
    s = s & "SP.JEDINICA_MERE, SP.PROCENJENA_CENA, SP.PLANIRANI_KVARTAL, ZH.BROJ_ZAHTEVA, ZH.STATUS_ZAHTEVA, ZH.PRIORITET, IZ.BROJ_PONUDE AS IZABRANA_PONUDA, IZ.PONUDJENA_CENA, "
    s = s & "D.NAZIV_DOBAVLJACA, NB.BROJ_NARUDZBENICE, NB.IZNOS_NARUDZBENICA, (Nz(NB.IZNOS_NARUDZBENICA,0) - Nz(SP.PROCENJENA_CENA,0)) AS ODSTUPANJE FROM ((((PLAN_NABAVKE AS PN INNER "
    s = s & "JOIN STAVKA_PLANA_NABAVKE AS SP ON PN.SIFRA_PLANA = SP.SIFRA_PLANA) LEFT JOIN [qIzv7_Zahtev] AS ZH ON PN.SIFRA_PLANA = ZH.SIFRA_PLANA) LEFT JOIN [qIzv7_Izabrana] AS IZ ON "
    s = s & "(SP.SIFRA_PLANA = IZ.SIFRA_PLANA) AND (SP.RB_STAVKE = IZ.RB_STAVKE)) LEFT JOIN DOBAVLJAC AS D ON IZ.SIFRA_DOBAVLJACA = D.SIFRA_DOBAVLJACA) LEFT JOIN [qIzv7_Narudzbe] AS "
    s = s & "NB ON IZ.SIFRA_DOBAVLJACA = NB.SIFRA_DOBAVLJACA ORDER BY PN.SIFRA_PLANA, SP.RB_STAVKE; "
    Upit "qIzv7_Stavke", s
    ' qIzv7_Ponude
    s = "SELECT PS.SIFRA_PLANA, PS.RB_STAVKE, PD.BROJ_PONUDE, D.NAZIV_DOBAVLJACA, PD.DATUM_PRIJEMA, PD.UKUPNA_CENA, PS.PONUDJENA_CENA, PD.ROK_ISPORUKE, PD.USLOVI_PLACANJA, "
    s = s & "PD.UKUPNO_BODOVA, PD.STATUS_PONUDE, (PS.SIFRA_PLANA & ""-"" & Format(PS.RB_STAVKE,""000"") & ""-"" & PD.BROJ_PONUDE) AS PONUDA_KLJUC, KV.NAZIV_KRITERIJUMA, KV.NACIN_BODOVANJA, "
    s = s & "OP.BROJ_BODOVA, OP.KOMENTAR_OCENE FROM (((PONUDJENA_STAVKA AS PS INNER JOIN PONUDA_DOBAVLJACA AS PD ON PS.BROJ_PONUDE = PD.BROJ_PONUDE) INNER JOIN DOBAVLJAC AS D ON "
    s = s & "PD.SIFRA_DOBAVLJACA = D.SIFRA_DOBAVLJACA) LEFT JOIN OCENA_PONUDE AS OP ON PD.BROJ_PONUDE = OP.BROJ_PONUDE) LEFT JOIN KRITERIJUM_VREDNOVANJA AS KV ON OP.SIFRA_KRITERIJUMA "
    s = s & "= KV.SIFRA_KRITERIJUMA ORDER BY PS.SIFRA_PLANA, PS.RB_STAVKE, PD.BROJ_PONUDE, KV.NAZIV_KRITERIJUMA; "
    Upit "qIzv7_Ponude", s
    ' qIzv8_Prava
    s = "SELECT PK.BROJ_LICENCE, PK.VRSTA_PRAVA, PK.NOSILAC_PRAVA, PK.TERITORIJA, PK.DATUM_OD, PK.DATUM_DO, DateDiff(""d"", Date(), PK.DATUM_DO) AS DANA_DO_ISTEKA, "
    s = s & "PK.DOZVOLJENO_EMITOVANJA, PK.ISKORISCENO_EMITOVANJA, (Nz(PK.DOZVOLJENO_EMITOVANJA,0) - Nz(PK.ISKORISCENO_EMITOVANJA,0)) AS PREOSTALO_EMITOVANJA, IIf(PK.DATUM_DO < Date(), "
    s = s & """Isteklo"", IIf(Nz(PK.ISKORISCENO_EMITOVANJA,0) >= Nz(PK.DOZVOLJENO_EMITOVANJA,0), ""Iskori~s~ceno"", IIf(DateDiff(""d"", Date(), PK.DATUM_DO) <= 30, ""Uskoro isti~ce"", "
    s = s & """Va~ze~ce""))) AS STATUS_PRAVA, IIf(PK.DATUM_DO < Date() OR Nz(PK.ISKORISCENO_EMITOVANJA,0) >= Nz(PK.DOZVOLJENO_EMITOVANJA,0) OR DateDiff(""d"", Date(), PK.DATUM_DO) <= 30, "
    s = s & "0, 1) AS PRIORITET_STATUSA, IIf(PK.DATUM_DO < Date() OR Nz(PK.ISKORISCENO_EMITOVANJA,0) >= Nz(PK.DOZVOLJENO_EMITOVANJA,0) OR DateDiff(""d"", Date(), PK.DATUM_DO) <= 30, ""1. "
    s = s & "Prava kojima je rok istekao, uskoro isti~ce ili je iskori~s~cen"" & "" dozvoljen broj emitovanja"", ""2. Va~ze~ca prava"") AS GRUPA_STATUSA, (Format(PK.DATUM_DO,""yyyymmdd"") & "
    s = s & """-"" & PK.BROJ_LICENCE) AS LICENCA_KLJUC, MS.SIFRA_SADRZAJA, MS.NAZIV_SADRZAJA, MS.FORMAT_ZAPISA, PP.OBLAST_POKRIVENOSTI, NS.ZEMLJA_POREKLA, UN.BROJ_UGOVORA AS "
    s = s & "UGOVOR_NABAVKE, (SELECT Count(*) FROM ZAPIS_O_EMITOVANJU AS ZE WHERE ZE.SIFRA_SADRZAJA = MS.SIFRA_SADRZAJA) AS BROJ_EMITOVANJA FROM (((PRAVO_KORISCENJA AS PK LEFT JOIN "
    s = s & "POKRIVENOST_PRAVOM AS PP ON PK.BROJ_LICENCE = PP.BROJ_LICENCE) LEFT JOIN MEDIJSKI_SADRZAJ AS MS ON PP.SIFRA_SADRZAJA = MS.SIFRA_SADRZAJA) LEFT JOIN NABAVLJENI_SADRZAJ AS "
    s = s & "NS ON MS.SIFRA_SADRZAJA = NS.SIFRA_SADRZAJA) LEFT JOIN UGOVOR_O_NABAVCI AS UN ON NS.BROJ_UGOVORA = UN.BROJ_UGOVORA ORDER BY IIf(PK.DATUM_DO < Date() OR "
    s = s & "Nz(PK.ISKORISCENO_EMITOVANJA,0) >= Nz(PK.DOZVOLJENO_EMITOVANJA,0) OR DateDiff(""d"", Date(), PK.DATUM_DO) <= 30, 0, 1), PK.DATUM_DO, PK.BROJ_LICENCE, MS.NAZIV_SADRZAJA; "
    Upit "qIzv8_Prava", s
End Sub

' ---------------------------------------------- izvestaj 1
Private Sub Izvestaj1()
    Dim r As String
    ObrisiIzvestaj "rptIzv1"
    r = Poc("qIzv1_Sema")
    Gr r, "SIFRA_SEME", True, True
    Gr r, "CELINA_KLJUC", True, True
    Gr r, "VREME_POCETKA", False, False
    Sek r, acHeader, 820
    Lab r, acHeader, 0, 60, 14600, 400, "Izve~staj 1 - Programska ~sema sa terminima emitovanja", 15, True
    Lab r, acHeader, 0, 480, 14600, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lin r, acHeader, 0, 780, 14600
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 0, 90, 1020, 250, "Vreme", 9, True, 2
    Lab r, acPageHeader, 1100, 90, 1320, 250, "Datum", 9, True, 2
    Lab r, acPageHeader, 2500, 90, 1120, 250, "~Sifra termina", 9, True
    Lab r, acPageHeader, 3700, 90, 3220, 250, "Emisija", 9, True
    Lab r, acPageHeader, 7000, 90, 1620, 250, "~Zanr", 9, True
    Lab r, acPageHeader, 8700, 90, 1020, 250, "Trajanje (min)", 9, True, 3
    Lab r, acPageHeader, 9800, 90, 1320, 250, "Tip termina", 9, True
    Lab r, acPageHeader, 11200, 90, 820, 250, "Zona", 9, True, 2
    Lab r, acPageHeader, 12100, 90, 920, 250, "Repriza", 9, True, 3
    Lab r, acPageHeader, 13100, 90, 1420, 250, "Status", 9, True
    Lin r, acPageHeader, 0, 380, 14600
    Sek r, acGroupLevel1Header, 780
    Lab r, acGroupLevel1Header, 0, 90, 1500, 220, "Programska ~sema:"
    Txt r, acGroupLevel1Header, 1500, 60, 3000, 260, "NAZIV_SEME", 9, True
    Lab r, acGroupLevel1Header, 4660, 90, 900, 220, "Sezona:"
    Txt r, acGroupLevel1Header, 5560, 60, 1500, 260, "SEZONA", 9, True
    Lab r, acGroupLevel1Header, 7220, 90, 900, 220, "Verzija:"
    Txt r, acGroupLevel1Header, 8120, 60, 1100, 260, "VERZIJA_SEME", 9, True
    Lab r, acGroupLevel1Header, 9380, 90, 800, 220, "Status:"
    Txt r, acGroupLevel1Header, 10180, 60, 1600, 260, "STATUS_SEME", 9, True
    Lab r, acGroupLevel1Header, 0, 410, 1000, 220, "Va~zi od:"
    Txt r, acGroupLevel1Header, 1000, 380, 1300, 260, "SEMA_OD", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 2460, 410, 500, 220, "do:"
    Txt r, acGroupLevel1Header, 2960, 380, 1300, 260, "SEMA_DO", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 4420, 410, 1100, 220, "Usvojena:"
    Txt r, acGroupLevel1Header, 5520, 380, 1300, 260, "DATUM_USVAJANJA", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 6980, 410, 900, 220, "Urednik:"
    Txt r, acGroupLevel1Header, 7880, 380, 2400, 260, "UREDNIK_NAZIV", 9, True
    Lab r, acGroupLevel1Header, 10440, 410, 1100, 220, "Redakcija:"
    Txt r, acGroupLevel1Header, 11540, 380, 2600, 260, "REDAKCIJA", 9, True
    Lin r, acGroupLevel1Header, 0, 720, 14600
    Sek r, acGroupLevel2Header, 500
    Lab r, acGroupLevel2Header, 0, 110, 1700, 220, "Programska celina:"
    Txt r, acGroupLevel2Header, 1700, 80, 3000, 260, "NAZIV_CELINE", 9, True
    Lab r, acGroupLevel2Header, 4860, 110, 600, 220, "Tip:"
    Txt r, acGroupLevel2Header, 5460, 80, 1500, 260, "TIP_CELINE", 9, True
    Lab r, acGroupLevel2Header, 7120, 110, 800, 220, "Datum:"
    Txt r, acGroupLevel2Header, 7920, 80, 1300, 260, "DATUM_CELINE", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel2Header, 9380, 110, 1000, 220, "Vreme od:"
    Txt r, acGroupLevel2Header, 10380, 80, 900, 260, "VREME_OD", 9, True, 1, "hh:nn"
    Lab r, acGroupLevel2Header, 11440, 110, 500, 220, "do:"
    Txt r, acGroupLevel2Header, 11940, 80, 900, 260, "VREME_DO", 9, True, 1, "hh:nn"
    Lin r, acGroupLevel2Header, 0, 420, 14600
    Sek r, acDetail, 300
    Txt r, acDetail, 0, 30, 1020, 240, "VREME_POCETKA", 9, False, 2, "hh:nn"
    Txt r, acDetail, 1100, 30, 1320, 240, "DATUM_TERMINA", 9, False, 2, "dd.mm.yyyy"
    Txt r, acDetail, 2500, 30, 1120, 240, "SIFRA_TERMINA"
    Txt r, acDetail, 3700, 30, 3220, 240, "NAZIV_EMISIJE"
    Txt r, acDetail, 7000, 30, 1620, 240, "ZANR"
    Txt r, acDetail, 8700, 30, 1020, 240, "TRAJANJE_TERMINA", 9, False, 3, "0"
    Txt r, acDetail, 9800, 30, 1320, 240, "TIP_TERMINA"
    Txt r, acDetail, 11200, 30, 820, 240, "ZONA_GLEDANOSTI", 9, False, 2
    Txt r, acDetail, 12100, 30, 920, 240, "REDNI_BROJ_REPRIZE", 9, False, 3, "0"
    Txt r, acDetail, 13100, 30, 1420, 240, "STATUS_TERMINA"
    Sek r, acGroupLevel2Footer, 400
    Lin r, acGroupLevel2Footer, 0, 20, 14600
    Lab r, acGroupLevel2Footer, 0, 80, 2800, 250, "Ukupno u celini:", 9, True
    Txt r, acGroupLevel2Footer, 2850, 80, 2200, 250, "=Count([SIFRA_TERMINA]) & "" termina""", 9, True
    Txt r, acGroupLevel2Footer, 8700, 80, 1020, 260, "=Sum([TRAJANJE_TERMINA])", 9, True, 3, "0"
    Sek r, acGroupLevel1Footer, 480
    Lin r, acGroupLevel1Footer, 0, 20, 14600
    Lab r, acGroupLevel1Footer, 0, 90, 2800, 260, "UKUPNO PO ~SEMI:", 10, True
    Txt r, acGroupLevel1Footer, 2850, 90, 2200, 260, "=Count([SIFRA_TERMINA]) & "" termina""", 10, True
    Txt r, acGroupLevel1Footer, 8700, 90, 1020, 260, "=Sum([TRAJANJE_TERMINA])", 9, True, 3, "0"
    Sek r, acFooter, 500
    Lin r, acFooter, 0, 40, 14600
    Lab r, acFooter, 0, 120, 2800, 280, "UKUPNO (sve ~seme):", 11, True
    Txt r, acFooter, 2850, 120, 2200, 280, "=Count([SIFRA_TERMINA]) & "" termina""", 11, True
    Txt r, acFooter, 8700, 120, 1020, 260, "=Sum([TRAJANJE_TERMINA])", 9, True, 3, "0"
    Podnozje r, 14600
    Kraj r, "rptIzv1", "Izve~staj 1 - Programska ~sema sa terminima emitovanja", 14600, True
End Sub

' ---------------------------------------------- izvestaj 2
Private Sub Izvestaj2()
    Dim r As String
    ObrisiIzvestaj "rptIzv2"
    r = Poc("qIzv2_Playout")
    Gr r, "DATUM", True, True
    Gr r, "STVARNO_VREME_POCETKA", False, False
    Sek r, acHeader, 1120
    Lab r, acHeader, 0, 60, 15400, 400, "Izve~staj 2 - Evidencija emitovanog sadr~zaja (playout log)", 15, True
    Lab r, acHeader, 0, 480, 15400, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lin r, acHeader, 0, 1080, 15400
    Lab r, acHeader, 0, 790, 1000, 220, "Period od:"
    Txt r, acHeader, 1000, 760, 1400, 260, "PAR_OD", 9, True, 1, "dd.mm.yyyy"
    Lab r, acHeader, 2560, 790, 500, 220, "do:"
    Txt r, acHeader, 3060, 760, 1400, 260, "PAR_DO", 9, True, 1, "dd.mm.yyyy"
    Lab r, acHeader, 4620, 790, 1300, 220, "Stanje na dan:"
    Txt r, acHeader, 5920, 760, 1400, 260, "=Date()", 9, True, 1, "dd.mm.yyyy"
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 0, 90, 1020, 250, "Stvarno vreme", 9, True, 2
    Lab r, acPageHeader, 1100, 90, 2220, 250, "Emisija", 9, True
    Lab r, acPageHeader, 3400, 90, 2220, 250, "Medijski sadr~zaj", 9, True
    Lab r, acPageHeader, 5700, 90, 920, 250, "Plan (min)", 9, True, 3
    Lab r, acPageHeader, 6700, 90, 920, 250, "Stvarno (min)", 9, True, 3
    Lab r, acPageHeader, 7700, 90, 920, 250, "Odstupanje", 9, True, 3
    Lab r, acPageHeader, 8700, 90, 1220, 250, "Status realizacije", 9, True
    Lab r, acPageHeader, 10000, 90, 1120, 250, "Broj licence", 9, True
    Lab r, acPageHeader, 11200, 90, 1420, 250, "Vrsta prava", 9, True
    Lab r, acPageHeader, 12700, 90, 1120, 250, "Operater", 9, True
    Lab r, acPageHeader, 13900, 90, 1420, 250, "Napomena o smetnjama", 9, True
    Lin r, acPageHeader, 0, 380, 15400
    Sek r, acGroupLevel1Header, 460
    Lab r, acGroupLevel1Header, 0, 90, 1600, 220, "Datum emitovanja:"
    Txt r, acGroupLevel1Header, 1600, 60, 1600, 260, "DATUM", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 3360, 90, 500, 220, "dan:"
    Txt r, acGroupLevel1Header, 3860, 60, 1800, 260, "DATUM", 9, True, 1, "dddd"
    Lin r, acGroupLevel1Header, 0, 390, 15400
    Sek r, acDetail, 290
    Txt r, acDetail, 0, 30, 1020, 240, "STVARNO_VREME_POCETKA", 9, False, 2, "hh:nn"
    Txt r, acDetail, 1100, 30, 2220, 240, "NAZIV_EMISIJE"
    Txt r, acDetail, 3400, 30, 2220, 240, "NAZIV_SADRZAJA"
    Txt r, acDetail, 5700, 30, 920, 240, "TRAJANJE_TERMINA", 9, False, 3, "0"
    Txt r, acDetail, 6700, 30, 920, 240, "STVARNO_TRAJANJE", 9, False, 3, "0"
    Txt r, acDetail, 7700, 30, 920, 240, "ODSTUPANJE", 9, False, 3, "0"
    Txt r, acDetail, 8700, 30, 1220, 240, "STATUS_REALIZACIJE"
    Txt r, acDetail, 10000, 30, 1120, 240, "BROJ_LICENCE"
    Txt r, acDetail, 11200, 30, 1420, 240, "VRSTA_PRAVA"
    Txt r, acDetail, 12700, 30, 1120, 240, "OPERATER_EMITOVANJA"
    Txt r, acDetail, 13900, 30, 1420, 240, "NAPOMENA_O_SMETNJAMA"
    Sek r, acGroupLevel1Footer, 420
    Lin r, acGroupLevel1Footer, 0, 20, 15400
    Lab r, acGroupLevel1Footer, 0, 80, 2200, 250, "Ukupno za dan:", 9, True
    Txt r, acGroupLevel1Footer, 2250, 80, 2000, 250, "=Count([NAZIV_EMISIJE]) & "" emitovanja""", 9, True
    Txt r, acGroupLevel1Footer, 6700, 80, 920, 260, "=Sum([STVARNO_TRAJANJE])", 9, True, 3, "0"
    Txt r, acGroupLevel1Footer, 8700, 80, 3400, 250, "=Sum([IMA_SMETNJU]) & "" sa zabele~zenim smetnjama""", 9, True
    Sek r, acFooter, 500
    Lin r, acFooter, 0, 40, 15400
    Lab r, acFooter, 0, 120, 2200, 280, "UKUPNO ZA PERIOD:", 11, True
    Txt r, acFooter, 2250, 120, 2000, 280, "=Count([NAZIV_EMISIJE]) & "" emitovanja""", 11, True
    Txt r, acFooter, 6700, 120, 920, 260, "=Sum([STVARNO_TRAJANJE])", 9, True, 3, "0"
    Txt r, acFooter, 8700, 120, 3400, 280, "=Sum([IMA_SMETNJU]) & "" sa zabele~zenim smetnjama""", 10, True
    Podnozje r, 15400
    Kraj r, "rptIzv2", "Izve~staj 2 - Evidencija emitovanog sadr~zaja (playout log)", 15400, True
End Sub

' ---------------------------------------------- izvestaj 3
Private Sub Izvestaj3()
    Dim r As String
    ObrisiIzvestaj "rptIzv3"
    r = Poc("qIzv3_Emisije")
    Sek r, acHeader, 8000
    Lab r, acHeader, 0, 60, 10700, 400, "Izve~staj 3 - Gledanost emisija po ~zanru", 15, True
    Lab r, acHeader, 0, 480, 10700, 240, "Informacioni sistem TV stanice - TV Panorama"
    Txt r, acHeader, 0, 760, 10700, 260, "=Zaglavlje3()", 9, True
    Lin r, acHeader, 0, 7960, 10700
    Lab r, acHeader, 0, 1120, 10700, 280, "Prose~can ostvareni rejting po ~zanru emisije", 10, True
    Grafikon r, acHeader, 0, 1420, 10700, 2900, "qIzv3_RejtingPoZanru"
    Lab r, acHeader, 0, 4420, 10700, 280, "Kretanje prose~cnog rejtinga po datumu merenja", 10, True
    Grafikon r, acHeader, 0, 4720, 10700, 2900, "qIzv3_RejtingPoDatumu"
    Lab r, acHeader, 0, 7680, 10700, 260, "Prate~ki tabelarni prikaz - sortirano opadaju~ke po ostvarenom rejtingu", 9, True
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 0, 90, 2520, 250, "Emisija", 9, True
    Lab r, acPageHeader, 2600, 90, 1520, 250, "~Zanr", 9, True
    Lab r, acPageHeader, 4200, 90, 820, 250, "Merenja", 9, True, 3
    Lab r, acPageHeader, 5100, 90, 1120, 250, "Prose~can rejting", 9, True, 3
    Lab r, acPageHeader, 6300, 90, 1120, 250, "Prose~can udeo (%)", 9, True, 3
    Lab r, acPageHeader, 7500, 90, 1620, 250, "Prose~cno gledalaca", 9, True, 3
    Lab r, acPageHeader, 9200, 90, 1420, 250, "Prose~cno gledanje (min)", 9, True, 3
    Lin r, acPageHeader, 0, 380, 10700
    Sek r, acDetail, 300
    Txt r, acDetail, 0, 30, 2520, 240, "NAZIV_EMISIJE"
    Txt r, acDetail, 2600, 30, 1520, 240, "ZANR"
    Txt r, acDetail, 4200, 30, 820, 240, "BROJ_MERENJA", 9, False, 3, "0"
    Txt r, acDetail, 5100, 30, 1120, 240, "PROSECAN_REJTING", 9, False, 3, "0.00"
    Txt r, acDetail, 6300, 30, 1120, 240, "PROSECAN_UDEO", 9, False, 3, "0.00"
    Txt r, acDetail, 7500, 30, 1620, 240, "PROSECAN_BROJ_GLEDALACA", 9, False, 3, "#,##0"
    Txt r, acDetail, 9200, 30, 1420, 240, "PROSECNO_GLEDANJE", 9, False, 3, "0.0"
    Sek r, acFooter, 520
    Lin r, acFooter, 0, 40, 10700
    Lab r, acFooter, 0, 120, 1400, 280, "UKUPNO:", 11, True
    Txt r, acFooter, 1450, 120, 2700, 280, "=Count([NAZIV_EMISIJE]) & "" emisija""", 11, True
    Txt r, acFooter, 4200, 120, 820, 260, "=Sum([BROJ_MERENJA])", 9, True, 3, "0"
    Txt r, acFooter, 5100, 120, 1120, 260, "=Avg([PROSECAN_REJTING])", 9, True, 3, "0.00"
    Txt r, acFooter, 6300, 120, 1120, 260, "=Avg([PROSECAN_UDEO])", 9, True, 3, "0.00"
    Txt r, acFooter, 7500, 120, 1620, 260, "=Avg([PROSECAN_BROJ_GLEDALACA])", 9, True, 3, "#,##0"
    Podnozje r, 10700
    Kraj r, "rptIzv3", "Izve~staj 3 - Gledanost emisija po ~zanru", 10700, False
End Sub

' ---------------------------------------------- izvestaj 4
Private Sub Izvestaj4()
    Dim r As String
    ObrisiIzvestaj "rptIzv4"
    r = Poc("qIzv4_Troskovi")
    Gr r, "SIFRA_PROJEKTA", True, True
    Gr r, "AKT_KLJUC", True, True
    Gr r, "RB_TROSKA", False, False
    Sek r, acHeader, 820
    Lab r, acHeader, 0, 60, 13200, 400, "Izve~staj 4 - Realizacija i tro~skovi projekta produkcije", 15, True
    Lab r, acHeader, 0, 480, 13200, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lin r, acHeader, 0, 780, 13200
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 800, 90, 620, 250, "RB", 9, True, 3
    Lab r, acPageHeader, 1500, 90, 1920, 250, "Vrsta tro~ska", 9, True
    Lab r, acPageHeader, 3500, 90, 3320, 250, "Opis tro~ska", 9, True
    Lab r, acPageHeader, 6900, 90, 1320, 250, "Datum nastanka", 9, True, 2
    Lab r, acPageHeader, 8300, 90, 1720, 250, "Iznos", 9, True, 3
    Lab r, acPageHeader, 10100, 90, 1320, 250, "Broj fakture", 9, True
    Lab r, acPageHeader, 11500, 90, 1620, 250, "Status pla~kanja", 9, True
    Lin r, acPageHeader, 0, 380, 13200
    Sek r, acGroupLevel1Header, 760
    Lab r, acGroupLevel1Header, 0, 90, 900, 220, "Projekat:"
    Txt r, acGroupLevel1Header, 900, 60, 1400, 260, "SIFRA_PROJEKTA", 9, True
    Lab r, acGroupLevel1Header, 2460, 90, 700, 220, "Naziv:"
    Txt r, acGroupLevel1Header, 3160, 60, 3000, 260, "NAZIV_PROJEKTA", 9, True
    Lab r, acGroupLevel1Header, 6320, 90, 1500, 220, "Vrsta produkcije:"
    Txt r, acGroupLevel1Header, 7820, 60, 1800, 260, "VRSTA_PRODUKCIJE", 9, True
    Lab r, acGroupLevel1Header, 9780, 90, 800, 220, "Status:"
    Txt r, acGroupLevel1Header, 10580, 60, 1600, 260, "STATUS_PROJEKTA", 9, True
    Lab r, acGroupLevel1Header, 0, 410, 900, 220, "Urednik:"
    Txt r, acGroupLevel1Header, 900, 380, 2000, 260, "UREDNIK_NAZIV", 9, True
    Lab r, acGroupLevel1Header, 3060, 410, 800, 220, "Emisija:"
    Txt r, acGroupLevel1Header, 3860, 380, 2000, 260, "NAZIV_EMISIJE", 9, True
    Lab r, acGroupLevel1Header, 6020, 410, 700, 220, "Period:"
    Txt r, acGroupLevel1Header, 6720, 380, 1300, 260, "DATUM_POCETKA", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 8180, 410, 200, 220, "-"
    Txt r, acGroupLevel1Header, 8380, 380, 1300, 260, "DATUM_ZAVRSETKA", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 9840, 410, 1500, 220, "Odobren bud~zet:"
    Txt r, acGroupLevel1Header, 11340, 380, 1800, 260, "ODOBREN_BUDZET", 9, True, 1, "#,##0.00"
    Lin r, acGroupLevel1Header, 0, 700, 13200
    Sek r, acGroupLevel2Header, 680
    Lab r, acGroupLevel2Header, 400, 90, 900, 220, "Aktivnost:"
    Txt r, acGroupLevel2Header, 1300, 60, 500, 260, "RB_AKTIVNOSTI", 9, True
    Lab r, acGroupLevel2Header, 1960, 90, 700, 220, "Naziv:"
    Txt r, acGroupLevel2Header, 2660, 60, 3000, 260, "NAZIV_AKTIVNOSTI", 9, True
    Lab r, acGroupLevel2Header, 5820, 90, 600, 220, "Vrsta:"
    Txt r, acGroupLevel2Header, 6420, 60, 1800, 260, "VRSTA_AKTIVNOSTI", 9, True
    Lab r, acGroupLevel2Header, 8380, 90, 700, 220, "Status:"
    Txt r, acGroupLevel2Header, 9080, 60, 1500, 260, "STATUS_AKTIVNOSTI", 9, True
    Lab r, acGroupLevel2Header, 400, 360, 900, 220, "Lokacija:"
    Txt r, acGroupLevel2Header, 1300, 330, 2400, 260, "LOKACIJA_SNIMANJA", 9, True
    Lab r, acGroupLevel2Header, 3860, 360, 700, 220, "Period:"
    Txt r, acGroupLevel2Header, 4560, 330, 1200, 260, "DATUM_OD", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel2Header, 5920, 360, 200, 220, "-"
    Txt r, acGroupLevel2Header, 6120, 330, 1200, 260, "DATUM_DO", 9, True, 1, "dd.mm.yyyy"
    Lin r, acGroupLevel2Header, 400, 640, 12800
    Sek r, acDetail, 300
    Txt r, acDetail, 800, 30, 620, 240, "RB_TROSKA", 9, False, 3, "0"
    Txt r, acDetail, 1500, 30, 1920, 240, "VRSTA_TROSKA"
    Txt r, acDetail, 3500, 30, 3320, 240, "OPIS_TROSKA"
    Txt r, acDetail, 6900, 30, 1320, 240, "DATUM_NASTANKA", 9, False, 2, "dd.mm.yyyy"
    Txt r, acDetail, 8300, 30, 1720, 240, "IZNOS", 9, False, 3, "#,##0.00"
    Txt r, acDetail, 10100, 30, 1320, 240, "BROJ_FAKTURE"
    Txt r, acDetail, 11500, 30, 1620, 240, "STATUS_PLACANJA"
    Sek r, acGroupLevel2Footer, 360
    Lin r, acGroupLevel2Footer, 400, 20, 12800
    Lab r, acGroupLevel2Footer, 400, 60, 3000, 250, "Ukupno za aktivnost:", 9, True
    Txt r, acGroupLevel2Footer, 8300, 60, 1720, 260, "=Sum([IZNOS])", 9, True, 3, "#,##0.00"
    Sek r, acGroupLevel1Footer, 700
    Lin r, acGroupLevel1Footer, 0, 20, 13200
    Lab r, acGroupLevel1Footer, 0, 80, 2600, 260, "UKUPNO ZA PROJEKAT:", 10, True
    Txt r, acGroupLevel1Footer, 8300, 80, 1720, 260, "=Sum([IZNOS])", 9, True, 3, "#,##0.00"
    Lab r, acGroupLevel1Footer, 0, 360, 2600, 250, "Odobren bud~zet:"
    Txt r, acGroupLevel1Footer, 2650, 360, 1800, 250, "=Max([ODOBREN_BUDZET])", 9, True, 3, "#,##0.00"
    Lab r, acGroupLevel1Footer, 4600, 360, 2000, 250, "Iskori~s~keno bud~zeta:"
    Txt r, acGroupLevel1Footer, 6650, 360, 1200, 250, "=IIf(Max([ODOBREN_BUDZET])>0,Sum([IZNOS])/Max([ODOBREN_BUDZET]),0)", 9, True, 1, "0.0%"
    Sek r, acFooter, 520
    Lin r, acFooter, 0, 40, 13200
    Lab r, acFooter, 0, 120, 3400, 280, "UKUPNO (svi projekti):", 11, True
    Txt r, acFooter, 8300, 120, 1720, 260, "=Sum([IZNOS])", 9, True, 3, "#,##0.00"
    Podnozje r, 13200
    Kraj r, "rptIzv4", "Izve~staj 4 - Realizacija i tro~skovi projekta produkcije", 13200, True
End Sub

' ------------------------------- podizvestaj: zaduzenje opreme (izvestaj 5)
Private Sub Izvestaj5Oprema()
    Dim r As String
    ObrisiIzvestaj "rptIzv5_Oprema"
    r = Poc("qIzv5_Oprema")
    Gr r, "INVENTARSKI_BROJ", True, True
    Gr r, "DATUM_REZERVACIJE", False, False
    Sek r, acHeader, 340
    Lab r, acHeader, 600, 40, 2920, 240, "Projekat", 9, True
    Lab r, acHeader, 3600, 40, 620, 240, "RB", 9, True, 3
    Lab r, acHeader, 4300, 40, 2920, 240, "Aktivnost", 9, True
    Lab r, acHeader, 7300, 40, 1520, 240, "Datum rezervacije", 9, True, 2
    Lab r, acHeader, 8900, 40, 1720, 240, "Trajanje (dana)", 9, True, 3
    Lin r, acHeader, 0, 300, 10700
    Sek r, acGroupLevel1Header, 460
    Lab r, acGroupLevel1Header, 0, 70, 900, 220, "Oprema:"
    Txt r, acGroupLevel1Header, 900, 40, 1400, 260, "INVENTARSKI_BROJ", 9, True
    Lab r, acGroupLevel1Header, 2460, 70, 700, 220, "Naziv:"
    Txt r, acGroupLevel1Header, 3160, 40, 2400, 260, "NAZIV_OPREME", 9, True
    Lab r, acGroupLevel1Header, 5720, 70, 700, 220, "Model:"
    Txt r, acGroupLevel1Header, 6420, 40, 2000, 260, "MODEL_OPREME", 9, True
    Lab r, acGroupLevel1Header, 8580, 70, 700, 220, "Status:"
    Txt r, acGroupLevel1Header, 9280, 40, 1400, 260, "STATUS_OPREME", 9, True
    Lin r, acGroupLevel1Header, 0, 400, 10700
    Sek r, acDetail, 290
    Txt r, acDetail, 600, 30, 2920, 240, "NAZIV_PROJEKTA"
    Txt r, acDetail, 3600, 30, 620, 240, "RB_AKTIVNOSTI", 9, False, 3, "0"
    Txt r, acDetail, 4300, 30, 2920, 240, "NAZIV_AKTIVNOSTI"
    Txt r, acDetail, 7300, 30, 1520, 240, "DATUM_REZERVACIJE", 9, False, 2, "dd.mm.yyyy"
    Txt r, acDetail, 8900, 30, 1720, 240, "TRAJANJE_ZADUZENJA", 9, False, 3, "0"
    Sek r, acGroupLevel1Footer, 340
    Lin r, acGroupLevel1Footer, 600, 20, 10100
    Lab r, acGroupLevel1Footer, 600, 50, 3000, 250, "Ukupno dana zadu~zenja:", 9, True
    Txt r, acGroupLevel1Footer, 8900, 50, 1720, 260, "=Sum([TRAJANJE_ZADUZENJA])", 9, True, 3, "0"
    Sek r, acFooter, 420
    Lin r, acFooter, 0, 40, 10700
    Lab r, acFooter, 0, 100, 3400, 260, "UKUPNO dana zadu~zenja:", 10, True
    Txt r, acFooter, 8900, 100, 1720, 260, "=Sum([TRAJANJE_ZADUZENJA])", 9, True, 3, "0"
    Kraj r, "rptIzv5_Oprema", "Zadu~zenje opreme na aktivnostima produkcije", 10700, True
End Sub

' ---------------------------------------------- izvestaj 5
Private Sub Izvestaj5()
    Dim r As String
    ObrisiIzvestaj "rptIzv5"
    r = Poc("qIzv5_Angazovanje")
    Gr r, "ZAPOSLENI_KLJUC", True, True
    Gr r, "DATUM_OD", False, False
    Sek r, acHeader, 1080
    Lab r, acHeader, 0, 60, 14000, 400, "Izve~staj 5 - Anga~zovanje zaposlenih i zadu~zenje opreme na produkciji", 15, True
    Lab r, acHeader, 0, 480, 14000, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lab r, acHeader, 0, 760, 14000, 260, "Prvi deo - anga~zovanje zaposlenih na aktivnostima produkcije"
    Lin r, acHeader, 0, 1040, 14000
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 600, 90, 2920, 250, "Projekat", 9, True
    Lab r, acPageHeader, 3600, 90, 620, 250, "RB", 9, True, 3
    Lab r, acPageHeader, 4300, 90, 2920, 250, "Aktivnost", 9, True
    Lab r, acPageHeader, 7300, 90, 2320, 250, "Uloga na snimanju", 9, True
    Lab r, acPageHeader, 9700, 90, 1320, 250, "Datum od", 9, True, 2
    Lab r, acPageHeader, 11100, 90, 1320, 250, "Datum do", 9, True, 2
    Lab r, acPageHeader, 12500, 90, 1420, 250, "Sati", 9, True, 3
    Lin r, acPageHeader, 0, 380, 14000
    Sek r, acGroupLevel1Header, 500
    Lab r, acGroupLevel1Header, 0, 90, 1100, 220, "Zaposleni:"
    Txt r, acGroupLevel1Header, 1100, 60, 3200, 260, "ZAPOSLENI_KLJUC", 9, True
    Lab r, acGroupLevel1Header, 4460, 90, 1300, 220, "Radno mesto:"
    Txt r, acGroupLevel1Header, 5760, 60, 2400, 260, "RADNO_MESTO", 9, True
    Lab r, acGroupLevel1Header, 8320, 90, 2000, 220, "Organizaciona jedinica:"
    Txt r, acGroupLevel1Header, 10320, 60, 2600, 260, "NAZIV_JEDINICE", 9, True
    Lin r, acGroupLevel1Header, 0, 440, 14000
    Sek r, acDetail, 290
    Txt r, acDetail, 600, 30, 2920, 240, "NAZIV_PROJEKTA"
    Txt r, acDetail, 3600, 30, 620, 240, "RB_AKTIVNOSTI", 9, False, 3, "0"
    Txt r, acDetail, 4300, 30, 2920, 240, "NAZIV_AKTIVNOSTI"
    Txt r, acDetail, 7300, 30, 2320, 240, "ULOGA_NA_SNIMANJU"
    Txt r, acDetail, 9700, 30, 1320, 240, "DATUM_OD", 9, False, 2, "dd.mm.yyyy"
    Txt r, acDetail, 11100, 30, 1320, 240, "DATUM_DO", 9, False, 2, "dd.mm.yyyy"
    Txt r, acDetail, 12500, 30, 1420, 240, "BROJ_ANGAZOVANIH_SATI", 9, False, 3, "0"
    Sek r, acGroupLevel1Footer, 380
    Lin r, acGroupLevel1Footer, 600, 20, 13400
    Lab r, acGroupLevel1Footer, 600, 60, 3000, 250, "Ukupno za zaposlenog:", 9, True
    Txt r, acGroupLevel1Footer, 3650, 60, 2400, 250, "=Count([NAZIV_AKTIVNOSTI]) & "" anga~zovanja""", 9, True
    Txt r, acGroupLevel1Footer, 12500, 60, 1420, 260, "=Sum([BROJ_ANGAZOVANIH_SATI])", 9, True, 3, "0"
    Sek r, acFooter, 4600, True
    Lin r, acFooter, 0, 40, 14000
    Lab r, acFooter, 0, 110, 3400, 280, "UKUPNO SATI (svi zaposleni):", 11, True
    Txt r, acFooter, 12500, 110, 1420, 260, "=Sum([BROJ_ANGAZOVANIH_SATI])", 9, True, 3, "0"
    Lab r, acFooter, 0, 520, 14000, 320, "Drugi deo - zadu~zenje opreme na aktivnostima produkcije", 12, True
    Pod r, acFooter, 0, 880, 13800, 3500, "rptIzv5_Oprema"
    Podnozje r, 14000
    Kraj r, "rptIzv5", "Izve~staj 5 - Anga~zovanje zaposlenih i zadu~zenje opreme", 14000, True
End Sub

' ---------------------------------------------- izvestaj 6
Private Sub Izvestaj6()
    Dim r As String
    ObrisiIzvestaj "rptIzv6"
    r = Poc("qIzv6_Kartica")
    Gr r, "BROJ_UGOVORA", True, True
    Gr r, "STAVKA_KLJUC", True, True
    Gr r, "DATUM_EMITOVANJA", False, False
    Sek r, acHeader, 1440
    Lab r, acHeader, 0, 60, 14000, 400, "Izve~staj 6 - Realizacija ugovora o ogla~savanju i naplata po ogla~siva~cu", 15, True
    Lab r, acHeader, 0, 480, 14000, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lin r, acHeader, 0, 1400, 14000
    Lab r, acHeader, 0, 790, 1200, 220, "Ogla~siva~c:"
    Txt r, acHeader, 1200, 760, 3000, 260, "NAZIV_KLIJENTA", 9, True
    Lab r, acHeader, 4360, 790, 700, 220, "~Sifra:"
    Txt r, acHeader, 5060, 760, 1300, 260, "SIFRA_KLIJENTA", 9, True
    Lab r, acHeader, 6520, 790, 500, 220, "PIB:"
    Txt r, acHeader, 7020, 760, 1200, 260, "PIB", 9, True
    Lab r, acHeader, 8380, 790, 1500, 220, "Kontakt osoba:"
    Txt r, acHeader, 9880, 760, 2200, 260, "KONTAKT_OSOBA", 9, True
    Lab r, acHeader, 0, 1070, 800, 220, "Bran~sa:"
    Txt r, acHeader, 800, 1040, 2200, 260, "BRANSA", 9, True
    Lab r, acHeader, 3160, 1070, 600, 220, "Grad:"
    Txt r, acHeader, 3760, 1040, 1800, 260, "GRAD", 9, True
    Lab r, acHeader, 5720, 1070, 1500, 220, "Godi~snji bud~zet:"
    Txt r, acHeader, 7220, 1040, 2000, 260, "GODISNJI_BUDZET", 9, True, 1, "#,##0.00"
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 800, 90, 1320, 250, "Datum emitovanja", 9, True, 2
    Lab r, acPageHeader, 2200, 90, 1020, 250, "Vreme", 9, True, 2
    Lab r, acPageHeader, 3300, 90, 1320, 250, "Reklamni blok", 9, True
    Lab r, acPageHeader, 4700, 90, 1320, 250, "Termin", 9, True
    Lab r, acPageHeader, 6100, 90, 820, 250, "Zona", 9, True, 2
    Lab r, acPageHeader, 7000, 90, 1120, 250, "Trajanje (s)", 9, True, 3
    Lab r, acPageHeader, 8200, 90, 1820, 250, "Napla~keni iznos", 9, True, 3
    Lab r, acPageHeader, 10100, 90, 1720, 250, "Status naplate", 9, True
    Lin r, acPageHeader, 0, 380, 14000
    Sek r, acGroupLevel1Header, 700
    Lab r, acGroupLevel1Header, 0, 90, 800, 220, "Ugovor:"
    Txt r, acGroupLevel1Header, 800, 60, 1400, 260, "BROJ_UGOVORA", 9, True
    Lab r, acGroupLevel1Header, 2360, 90, 1000, 220, "Sklopljen:"
    Txt r, acGroupLevel1Header, 3360, 60, 1300, 260, "DATUM_SKLAPANJA", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 4820, 90, 900, 220, "Va~zi od:"
    Txt r, acGroupLevel1Header, 5720, 60, 1300, 260, "VAZI_OD", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 7180, 90, 500, 220, "do:"
    Txt r, acGroupLevel1Header, 7680, 60, 1300, 260, "VAZI_DO", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 9140, 90, 700, 220, "Status:"
    Txt r, acGroupLevel1Header, 9840, 60, 1500, 260, "STATUS_UGOVORA", 9, True
    Lab r, acGroupLevel1Header, 0, 370, 1700, 220, "Vrednost ugovora:"
    Txt r, acGroupLevel1Header, 1700, 340, 1900, 260, "UKUPNA_VREDNOST", 9, True, 1, "#,##0.00"
    Lab r, acGroupLevel1Header, 3760, 370, 1700, 220, "Ugovoreni termini:"
    Txt r, acGroupLevel1Header, 5460, 340, 3000, 260, "UGOVORENI_TERMINI", 9, True
    Lin r, acGroupLevel1Header, 0, 660, 14000
    Sek r, acGroupLevel2Header, 680
    Lab r, acGroupLevel2Header, 400, 90, 700, 220, "Stavka:"
    Txt r, acGroupLevel2Header, 1100, 60, 400, 260, "RB_STAVKE", 9, True
    Lab r, acGroupLevel2Header, 1660, 90, 600, 220, "Opis:"
    Txt r, acGroupLevel2Header, 2260, 60, 3200, 260, "OPIS_STAVKE", 9, True
    Lab r, acGroupLevel2Header, 5620, 90, 1300, 220, "Ugovoreno (s):"
    Txt r, acGroupLevel2Header, 6920, 60, 900, 260, "KOLICINA_SEKUNDE", 9, True, 1, "0"
    Lab r, acGroupLevel2Header, 7980, 90, 1000, 220, "Jed. cena:"
    Txt r, acGroupLevel2Header, 8980, 60, 1500, 260, "JEDINICNA_CENA", 9, True, 1, "#,##0.00"
    Lab r, acGroupLevel2Header, 10640, 90, 1100, 220, "Popust (%):"
    Txt r, acGroupLevel2Header, 11740, 60, 700, 260, "POPUST", 9, True, 1, "0.0"
    Lab r, acGroupLevel2Header, 400, 360, 1600, 220, "Vrednost stavke:"
    Txt r, acGroupLevel2Header, 2000, 330, 1800, 260, "VREDNOST_STAVKE", 9, True, 1, "#,##0.00"
    Lin r, acGroupLevel2Header, 400, 640, 13600
    Sek r, acDetail, 290
    Txt r, acDetail, 800, 30, 1320, 240, "DATUM_EMITOVANJA", 9, False, 2, "dd.mm.yyyy"
    Txt r, acDetail, 2200, 30, 1020, 240, "VREME_EMITOVANJA", 9, False, 2, "hh:nn"
    Txt r, acDetail, 3300, 30, 1320, 240, "SIFRA_BLOKA"
    Txt r, acDetail, 4700, 30, 1320, 240, "SIFRA_TERMINA"
    Txt r, acDetail, 6100, 30, 820, 240, "ZONA", 9, False, 2
    Txt r, acDetail, 7000, 30, 1120, 240, "TRAJANJE_SPOTA", 9, False, 3, "0"
    Txt r, acDetail, 8200, 30, 1820, 240, "NAPLACENI_IZNOS", 9, False, 3, "#,##0.00"
    Txt r, acDetail, 10100, 30, 1720, 240, "STATUS_NAPLATE"
    Sek r, acGroupLevel2Footer, 360
    Lin r, acGroupLevel2Footer, 800, 20, 13200
    Lab r, acGroupLevel2Footer, 800, 50, 2600, 250, "Realizovano po stavci:", 9, True
    Txt r, acGroupLevel2Footer, 7000, 50, 1120, 260, "=Sum([TRAJANJE_SPOTA])", 9, True, 3, "0"
    Txt r, acGroupLevel2Footer, 8200, 50, 1820, 260, "=Sum([NAPLACENI_IZNOS])", 9, True, 3, "#,##0.00"
    Sek r, acGroupLevel1Footer, 960
    Lin r, acGroupLevel1Footer, 0, 20, 14000
    Lab r, acGroupLevel1Footer, 0, 70, 3000, 260, "REALIZACIJA UGOVORA", 10, True
    Lab r, acGroupLevel1Footer, 0, 350, 1900, 250, "Ugovoreno:"
    Txt r, acGroupLevel1Footer, 1950, 350, 1200, 250, "=Max([UGOVORENO_SEKUNDI])", 9, True, 3, "0"
    Lab r, acGroupLevel1Footer, 3200, 350, 300, 250, "s"
    Txt r, acGroupLevel1Footer, 3550, 350, 1900, 250, "=Max([UGOVORENA_VREDNOST])", 9, True, 3, "#,##0.00"
    Lab r, acGroupLevel1Footer, 0, 620, 1900, 250, "Realizovano:"
    Txt r, acGroupLevel1Footer, 1950, 620, 1200, 250, "=Sum([TRAJANJE_SPOTA])", 9, True, 3, "0"
    Lab r, acGroupLevel1Footer, 3200, 620, 300, 250, "s"
    Txt r, acGroupLevel1Footer, 3550, 620, 1900, 250, "=Sum([NAPLACENI_IZNOS])", 9, True, 3, "#,##0.00"
    Lab r, acGroupLevel1Footer, 5700, 350, 1700, 250, "Razlika (sekundi):"
    Txt r, acGroupLevel1Footer, 7450, 350, 1200, 250, "=Nz(Max([UGOVORENO_SEKUNDI]),0)-Nz(Sum([TRAJANJE_SPOTA]),0)", 9, True, 3, "0"
    Lab r, acGroupLevel1Footer, 5700, 620, 1700, 250, "Fakturisano:"
    Txt r, acGroupLevel1Footer, 7450, 620, 1900, 250, "=Max([FAKTURISANO])", 9, True, 3, "#,##0.00"
    Lab r, acGroupLevel1Footer, 9600, 620, 1700, 250, "Status fakture:"
    Txt r, acGroupLevel1Footer, 11350, 620, 2200, 250, "=Max([STATUS_FAKTURE])", 9, True
    Sek r, acFooter, 520
    Lin r, acFooter, 0, 40, 14000
    Lab r, acFooter, 0, 120, 3400, 280, "UKUPNO PO OGLA~SIVA~CU:", 11, True
    Txt r, acFooter, 7000, 120, 1120, 260, "=Sum([TRAJANJE_SPOTA])", 9, True, 3, "0"
    Txt r, acFooter, 8200, 120, 1820, 260, "=Sum([NAPLACENI_IZNOS])", 9, True, 3, "#,##0.00"
    Podnozje r, 14000
    Kraj r, "rptIzv6", "Izve~staj 6 - Realizacija ugovora o ogla~savanju po ogla~siva~cu", 14000, True
End Sub

' ------------------------------- podizvestaj: ponude (izvestaj 7)
Private Sub Izvestaj7Ponude()
    Dim r As String
    ObrisiIzvestaj "rptIzv7_Ponude"
    r = Poc("qIzv7_Ponude")
    Gr r, "PONUDA_KLJUC", True, True
    Gr r, "NAZIV_KRITERIJUMA", False, False
    Sek r, acHeader, 330
    Lab r, acHeader, 500, 40, 3320, 240, "Kriterijum vrednovanja", 9, True
    Lab r, acHeader, 3900, 40, 1720, 240, "Na~cin bodovanja", 9, True
    Lab r, acHeader, 5700, 40, 1020, 240, "Bodovi", 9, True, 3
    Lab r, acHeader, 6800, 40, 3320, 240, "Komentar ocene", 9, True
    Lin r, acHeader, 0, 300, 13800
    Sek r, acGroupLevel1Header, 660
    Lab r, acGroupLevel1Header, 0, 70, 800, 220, "Ponuda:"
    Txt r, acGroupLevel1Header, 800, 40, 1300, 260, "BROJ_PONUDE", 9, True
    Lab r, acGroupLevel1Header, 2260, 70, 1000, 220, "Dobavlja~c:"
    Txt r, acGroupLevel1Header, 3260, 40, 2000, 260, "NAZIV_DOBAVLJACA", 9, True
    Lab r, acGroupLevel1Header, 5420, 70, 1300, 220, "Ukupna cena:"
    Txt r, acGroupLevel1Header, 6720, 40, 1600, 260, "UKUPNA_CENA", 9, True, 1, "#,##0.00"
    Lab r, acGroupLevel1Header, 8480, 70, 1400, 220, "Cena za stavku:"
    Txt r, acGroupLevel1Header, 9880, 40, 1500, 260, "PONUDJENA_CENA", 9, True, 1, "#,##0.00"
    Lab r, acGroupLevel1Header, 11540, 70, 700, 220, "Status:"
    Txt r, acGroupLevel1Header, 12240, 40, 1500, 260, "STATUS_PONUDE", 9, True
    Lab r, acGroupLevel1Header, 0, 350, 1300, 220, "Rok isporuke:"
    Txt r, acGroupLevel1Header, 1300, 320, 1300, 260, "ROK_ISPORUKE", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 2760, 350, 1500, 220, "Uslovi pla~kanja:"
    Txt r, acGroupLevel1Header, 4260, 320, 2600, 260, "USLOVI_PLACANJA", 9, True
    Lab r, acGroupLevel1Header, 7020, 350, 1400, 220, "Ukupno bodova:"
    Txt r, acGroupLevel1Header, 8420, 320, 900, 260, "UKUPNO_BODOVA", 9, True, 1, "0.00"
    Lin r, acGroupLevel1Header, 0, 620, 13800
    Sek r, acDetail, 280
    Txt r, acDetail, 500, 20, 3320, 240, "NAZIV_KRITERIJUMA"
    Txt r, acDetail, 3900, 20, 1720, 240, "NACIN_BODOVANJA"
    Txt r, acDetail, 5700, 20, 1020, 240, "BROJ_BODOVA", 9, False, 3, "0.00"
    Txt r, acDetail, 6800, 20, 3320, 240, "KOMENTAR_OCENE"
    Sek r, acGroupLevel1Footer, 160
    Lin r, acGroupLevel1Footer, 500, 40, 13300
    Kraj r, "rptIzv7_Ponude", "Vrednovanje prikupljenih ponuda", 13800, True
End Sub

' ---------------------------------------------- izvestaj 7
Private Sub Izvestaj7()
    Dim r As String
    ObrisiIzvestaj "rptIzv7"
    r = Poc("qIzv7_Stavke")
    Gr r, "SIFRA_PLANA", True, True
    Gr r, "RB_STAVKE", False, False
    Sek r, acHeader, 820
    Lab r, acHeader, 0, 60, 14700, 400, "Izve~staj 7 - Realizacija plana nabavke sa vrednovanjem ponuda", 15, True
    Lab r, acHeader, 0, 480, 14700, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lin r, acHeader, 0, 780, 14700
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 0, 90, 520, 250, "RB", 9, True, 3
    Lab r, acPageHeader, 600, 90, 2320, 250, "Opis artikla", 9, True
    Lab r, acPageHeader, 3000, 90, 620, 250, "Kol.", 9, True, 3
    Lab r, acPageHeader, 3700, 90, 720, 250, "JM", 9, True
    Lab r, acPageHeader, 4500, 90, 1420, 250, "Procenjena cena", 9, True, 3
    Lab r, acPageHeader, 6000, 90, 820, 250, "Kvartal", 9, True, 2
    Lab r, acPageHeader, 6900, 90, 1120, 250, "Zahtev", 9, True
    Lab r, acPageHeader, 8100, 90, 1120, 250, "Status zahteva", 9, True
    Lab r, acPageHeader, 9300, 90, 1120, 250, "Izabrana ponuda", 9, True
    Lab r, acPageHeader, 10500, 90, 1220, 250, "Narud~zbenica", 9, True
    Lab r, acPageHeader, 11800, 90, 1420, 250, "Iznos narud~zbenice", 9, True, 3
    Lab r, acPageHeader, 13300, 90, 1320, 250, "Odstupanje", 9, True, 3
    Lin r, acPageHeader, 0, 380, 14700
    Sek r, acGroupLevel1Header, 760
    Lab r, acGroupLevel1Header, 0, 90, 1300, 220, "Plan nabavke:"
    Txt r, acGroupLevel1Header, 1300, 60, 1400, 260, "SIFRA_PLANA", 9, True
    Lab r, acGroupLevel1Header, 2860, 90, 800, 220, "Godina:"
    Txt r, acGroupLevel1Header, 3660, 60, 800, 260, "GODINA_PLANA", 9, True, 1, "0"
    Lab r, acGroupLevel1Header, 4620, 90, 700, 220, "Donet:"
    Txt r, acGroupLevel1Header, 5320, 60, 1300, 260, "DATUM_DONOSENJA", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel1Header, 6780, 90, 700, 220, "Status:"
    Txt r, acGroupLevel1Header, 7480, 60, 1500, 260, "STATUS_PLANA", 9, True
    Lab r, acGroupLevel1Header, 9140, 90, 1600, 220, "Ukupna vrednost:"
    Txt r, acGroupLevel1Header, 10740, 60, 1900, 260, "UKUPNA_VREDNOST", 9, True, 1, "#,##0.00"
    Lab r, acGroupLevel1Header, 0, 410, 1000, 220, "Donosilac:"
    Txt r, acGroupLevel1Header, 1000, 380, 2400, 260, "DONOSILAC_PLANA", 9, True
    Lab r, acGroupLevel1Header, 3560, 410, 1700, 220, "Zahtev za nabavku:"
    Txt r, acGroupLevel1Header, 5260, 380, 1400, 260, "BROJ_ZAHTEVA", 9, True
    Lab r, acGroupLevel1Header, 6820, 410, 1400, 220, "Status zahteva:"
    Txt r, acGroupLevel1Header, 8220, 380, 1400, 260, "STATUS_ZAHTEVA", 9, True
    Lab r, acGroupLevel1Header, 9780, 410, 900, 220, "Prioritet:"
    Txt r, acGroupLevel1Header, 10680, 380, 1200, 260, "PRIORITET", 9, True
    Lin r, acGroupLevel1Header, 0, 720, 14700
    Sek r, acDetail, 3300, True
    Txt r, acDetail, 0, 30, 520, 240, "RB_STAVKE", 9, False, 3, "0"
    Txt r, acDetail, 600, 30, 2320, 240, "OPIS_ARTIKLA"
    Txt r, acDetail, 3000, 30, 620, 240, "KOLICINA", 9, False, 3, "0"
    Txt r, acDetail, 3700, 30, 720, 240, "JEDINICA_MERE"
    Txt r, acDetail, 4500, 30, 1420, 240, "PROCENJENA_CENA", 9, False, 3, "#,##0.00"
    Txt r, acDetail, 6000, 30, 820, 240, "PLANIRANI_KVARTAL", 9, False, 2
    Txt r, acDetail, 6900, 30, 1120, 240, "BROJ_ZAHTEVA"
    Txt r, acDetail, 8100, 30, 1120, 240, "STATUS_ZAHTEVA"
    Txt r, acDetail, 9300, 30, 1120, 240, "IZABRANA_PONUDA"
    Txt r, acDetail, 10500, 30, 1220, 240, "BROJ_NARUDZBENICE"
    Txt r, acDetail, 11800, 30, 1420, 240, "IZNOS_NARUDZBENICA", 9, False, 3, "#,##0.00"
    Txt r, acDetail, 13300, 30, 1320, 240, "ODSTUPANJE", 9, False, 3, "#,##0.00"
    Lab r, acDetail, 400, 340, 5000, 250, "Prikupljene ponude i vrednovanje:", 9, True
    Pod r, acDetail, 400, 620, 13900, 2500, "rptIzv7_Ponude", "SIFRA_PLANA;RB_STAVKE", "SIFRA_PLANA;RB_STAVKE"
    Sek r, acGroupLevel1Footer, 700
    Lin r, acGroupLevel1Footer, 0, 20, 14700
    Lab r, acGroupLevel1Footer, 0, 70, 2800, 260, "UKUPNO ZA PLAN:", 10, True
    Txt r, acGroupLevel1Footer, 4500, 70, 1420, 260, "=Sum([PROCENJENA_CENA])", 9, True, 3, "#,##0.00"
    Txt r, acGroupLevel1Footer, 11800, 70, 1420, 260, "=Sum([IZNOS_NARUDZBENICA])", 9, True, 3, "#,##0.00"
    Lab r, acGroupLevel1Footer, 0, 360, 2800, 250, "Izvr~senje plana:"
    Txt r, acGroupLevel1Footer, 2850, 360, 1400, 250, "=IIf(Sum([PROCENJENA_CENA])>0,Sum([IZNOS_NARUDZBENICA])/Sum([PROCENJENA_CENA]),0)", 9, True, 1, "0.0%"
    Sek r, acFooter, 700
    Lin r, acFooter, 0, 40, 14700
    Lab r, acFooter, 0, 110, 3400, 280, "UKUPNO (svi planovi):", 11, True
    Txt r, acFooter, 4500, 110, 1420, 260, "=Sum([PROCENJENA_CENA])", 9, True, 3, "#,##0.00"
    Txt r, acFooter, 11800, 110, 1420, 260, "=Sum([IZNOS_NARUDZBENICA])", 9, True, 3, "#,##0.00"
    Lab r, acFooter, 0, 400, 3400, 250, "Izvr~senje plana - ukupno:"
    Txt r, acFooter, 3450, 400, 1400, 250, "=IIf(Sum([PROCENJENA_CENA])>0,Sum([IZNOS_NARUDZBENICA])/Sum([PROCENJENA_CENA]),0)", 10, True, 1, "0.0%"
    Podnozje r, 14700
    Kraj r, "rptIzv7", "Izve~staj 7 - Realizacija plana nabavke sa vrednovanjem ponuda", 14700, True
End Sub

' ---------------------------------------------- izvestaj 8
Private Sub Izvestaj8()
    Dim r As String
    ObrisiIzvestaj "rptIzv8"
    r = Poc("qIzv8_Prava")
    Gr r, "PRIORITET_STATUSA", True, True
    Gr r, "LICENCA_KLJUC", True, True
    Gr r, "NAZIV_SADRZAJA", False, False
    Sek r, acHeader, 1080
    Lab r, acHeader, 0, 60, 14600, 400, "Izve~staj 8 - Prava kori~s~kenja medijskog sadr~zaja i rokovi va~zenja", 15, True
    Lab r, acHeader, 0, 480, 14600, 240, "Informacioni sistem TV stanice - TV Panorama"
    Lin r, acHeader, 0, 1040, 14600
    Lab r, acHeader, 0, 790, 1900, 220, "Stanje prava na dan:"
    Txt r, acHeader, 1900, 760, 1400, 260, "=Date()", 9, True, 1, "dd.mm.yyyy"
    Sek r, acPageHeader, 420
    Lab r, acPageHeader, 800, 90, 1320, 250, "~Sifra sadr~zaja", 9, True
    Lab r, acPageHeader, 2200, 90, 3520, 250, "Medijski sadr~zaj", 9, True
    Lab r, acPageHeader, 5800, 90, 1420, 250, "Format zapisa", 9, True
    Lab r, acPageHeader, 7300, 90, 2520, 250, "Oblast pokrivenosti", 9, True
    Lab r, acPageHeader, 9900, 90, 1520, 250, "Zemlja porekla", 9, True
    Lab r, acPageHeader, 11500, 90, 1420, 250, "Ugovor o nabavci", 9, True
    Lab r, acPageHeader, 13000, 90, 1520, 250, "Emitovanja", 9, True, 3
    Lin r, acPageHeader, 0, 380, 14600
    Sek r, acGroupLevel1Header, 520
    Txt r, acGroupLevel1Header, 0, 80, 11000, 320, "GRUPA_STATUSA", 12, True
    Lin r, acGroupLevel1Header, 0, 460, 14600
    Sek r, acGroupLevel2Header, 920
    Lab r, acGroupLevel2Header, 400, 90, 800, 220, "Licenca:"
    Txt r, acGroupLevel2Header, 1200, 60, 1400, 260, "BROJ_LICENCE", 9, True
    Lab r, acGroupLevel2Header, 2760, 90, 1200, 220, "Vrsta prava:"
    Txt r, acGroupLevel2Header, 3960, 60, 2200, 260, "VRSTA_PRAVA", 9, True
    Lab r, acGroupLevel2Header, 6320, 90, 1400, 220, "Nosilac prava:"
    Txt r, acGroupLevel2Header, 7720, 60, 2400, 260, "NOSILAC_PRAVA", 9, True
    Lab r, acGroupLevel2Header, 10280, 90, 1000, 220, "Teritorija:"
    Txt r, acGroupLevel2Header, 11280, 60, 2000, 260, "TERITORIJA", 9, True
    Lab r, acGroupLevel2Header, 400, 370, 900, 220, "Va~zi od:"
    Txt r, acGroupLevel2Header, 1300, 340, 1300, 260, "DATUM_OD", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel2Header, 2760, 370, 400, 220, "do:"
    Txt r, acGroupLevel2Header, 3160, 340, 1300, 260, "DATUM_DO", 9, True, 1, "dd.mm.yyyy"
    Lab r, acGroupLevel2Header, 4620, 370, 1400, 220, "Dana do isteka:"
    Txt r, acGroupLevel2Header, 6020, 340, 900, 260, "DANA_DO_ISTEKA", 9, True, 1, "0"
    Lab r, acGroupLevel2Header, 7080, 370, 1200, 220, "Status prava:"
    Txt r, acGroupLevel2Header, 8280, 340, 1900, 260, "STATUS_PRAVA", 9, True
    Lab r, acGroupLevel2Header, 400, 650, 2200, 220, "Dozvoljeno emitovanja:"
    Txt r, acGroupLevel2Header, 2600, 620, 700, 260, "DOZVOLJENO_EMITOVANJA", 9, True, 1, "0"
    Lab r, acGroupLevel2Header, 3460, 650, 1200, 220, "Iskori~s~keno:"
    Txt r, acGroupLevel2Header, 4660, 620, 700, 260, "ISKORISCENO_EMITOVANJA", 9, True, 1, "0"
    Lab r, acGroupLevel2Header, 5520, 650, 1100, 220, "Preostalo:"
    Txt r, acGroupLevel2Header, 6620, 620, 700, 260, "PREOSTALO_EMITOVANJA", 9, True, 1, "0"
    Lin r, acGroupLevel2Header, 400, 880, 14200
    Sek r, acDetail, 290
    Txt r, acDetail, 800, 30, 1320, 240, "SIFRA_SADRZAJA"
    Txt r, acDetail, 2200, 30, 3520, 240, "NAZIV_SADRZAJA"
    Txt r, acDetail, 5800, 30, 1420, 240, "FORMAT_ZAPISA"
    Txt r, acDetail, 7300, 30, 2520, 240, "OBLAST_POKRIVENOSTI"
    Txt r, acDetail, 9900, 30, 1520, 240, "ZEMLJA_POREKLA"
    Txt r, acDetail, 11500, 30, 1420, 240, "UGOVOR_NABAVKE"
    Txt r, acDetail, 13000, 30, 1520, 240, "BROJ_EMITOVANJA", 9, False, 3, "0"
    Sek r, acGroupLevel2Footer, 340
    Lin r, acGroupLevel2Footer, 800, 20, 13800
    Lab r, acGroupLevel2Footer, 800, 50, 3000, 250, "Broj pokrivenih sadr~zaja:", 9, True
    Txt r, acGroupLevel2Footer, 3850, 50, 900, 250, "=Count([SIFRA_SADRZAJA])", 9, True, 1, "0"
    Txt r, acGroupLevel2Footer, 13000, 50, 1520, 260, "=Sum([BROJ_EMITOVANJA])", 9, True, 3, "0"
    Sek r, acGroupLevel1Footer, 420
    Lin r, acGroupLevel1Footer, 0, 20, 14600
    Lab r, acGroupLevel1Footer, 0, 80, 3400, 260, "Ukupno u grupi:", 10, True
    Txt r, acGroupLevel1Footer, 3450, 80, 3000, 260, "=Count([BROJ_LICENCE]) & "" redova (pravo x sadr~zaj)""", 10, True
    Txt r, acGroupLevel1Footer, 13000, 80, 1520, 260, "=Sum([BROJ_EMITOVANJA])", 9, True, 3, "0"
    Sek r, acFooter, 520
    Lin r, acFooter, 0, 40, 14600
    Lab r, acFooter, 0, 120, 3400, 280, "UKUPNO:", 11, True
    Txt r, acFooter, 3450, 120, 3000, 280, "=Count([BROJ_LICENCE]) & "" redova (pravo x sadr~zaj)""", 11, True
    Txt r, acFooter, 13000, 120, 1520, 260, "=Sum([BROJ_EMITOVANJA])", 9, True, 3, "0"
    Podnozje r, 14600
    Kraj r, "rptIzv8", "Izve~staj 8 - Prava kori~s~kenja medijskog sadr~zaja i rokovi va~zenja", 14600, True
End Sub

' ---------------------------------------------- meni izvestaja
Private Sub MeniForma()
    Dim frm As Form, ctl As Control, lbl As Control, priv As String
    On Error GoTo Greska
    ObrisiFormu "frmIzvestaji"
    Set frm = CreateForm()
    priv = frm.Name
    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 260, 9400, 440)
    lbl.Caption = "Izve~staji informacionog sistema TV stanice"
    lbl.FontSize = 17
    lbl.FontBold = True
    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 740, 9400, 280)
    lbl.Caption = "Osam izve~staja iz Specifikacije izve~staja"
    lbl.FontSize = 10
    lbl.ForeColor = RGB(90, 100, 120)
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 1180, 9400, 420)
    ctl.Caption = "Izve~staj 1 - Programska ~sema sa terminima emitovanja"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv1"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 1650, 9400, 420)
    ctl.Caption = "Izve~staj 2 - Evidencija emitovanog sadr~zaja (playout log) - parametarski"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv2"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 2120, 9400, 420)
    ctl.Caption = "Izve~staj 3 - Gledanost emisija po ~zanru - sa grafi~ckim prikazom"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv3"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 2590, 9400, 420)
    ctl.Caption = "Izve~staj 4 - Realizacija i tro~skovi projekta produkcije"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv4"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 3060, 9400, 420)
    ctl.Caption = "Izve~staj 5 - Anga~zovanje zaposlenih i zadu~zenje opreme na produkciji"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv5"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 3530, 9400, 420)
    ctl.Caption = "Izve~staj 6 - Realizacija ugovora o ogla~savanju po ogla~siva~cu - parametarski"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv6"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 4000, 9400, 420)
    ctl.Caption = "Izve~staj 7 - Realizacija plana nabavke sa vrednovanjem ponuda"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv7"")"
    ctl.FontSize = 9
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, 4470, 9400, 420)
    ctl.Caption = "Izve~staj 8 - Prava kori~s~kenja medijskog sadr~zaja i rokovi va~zenja"
    ctl.OnClick = "=OtvoriIzvestaj(""rptIzv8"")"
    ctl.FontSize = 9
    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 5100, 9400, 560)
    lbl.Caption = "Parametarski izve~staji (2 i 6) pri pokretanju tra~ze vrednosti: izve~staj 2 period od-do, izve~staj 6 ~sifru ili naziv ogla~siva~ca."
    lbl.FontSize = 9
    lbl.ForeColor = RGB(90, 100, 120)
    frm.Section(acDetail).Height = 5840
    frm.Width = 9800
    frm.Caption = "Izve~staji - TV Panorama"
    frm.NavigationButtons = False
    frm.RecordSelectors = False
    frm.DividingLines = False
    DoCmd.Close acForm, priv, acSaveYes
    DoCmd.Rename "frmIzvestaji", acForm, priv
    gForm = gForm + 1
    Beleska "  forma frmIzvestaji napravljena"
    Exit Sub
Greska:
    gGreske = gGreske + 1
    Beleska "  forma frmIzvestaji nije napravljena: " & Err.Description
    Err.Clear
    On Error Resume Next
    DoCmd.Close acForm, priv, acSaveNo
    Err.Clear
End Sub

' ================================================================
'  GLAVNA PROCEDURA - klikni u nju i pritisni F5
' ================================================================
Public Sub KreirajIzvestaje()
    Dim t0 As Single
    On Error GoTo Greska
    t0 = Timer
    gUpit = 0: gIzv = 0: gForm = 0: gGreske = 0
    gPoruke = ""
    DoCmd.SetWarnings False
    Beleska "--- TV Panorama: dodavanje izve~staja ---"
    Beleska "> upiti (qIzv...)"
    Upiti1
    Upiti2
    Upiti3
    Upiti4
    Beleska "> podizvestaji"
    Izvestaj5Oprema
    Izvestaj7Ponude
    Beleska "> izvestaji 1-8"
    Izvestaj1
    Izvestaj2
    Izvestaj3
    Izvestaj4
    Izvestaj5
    Izvestaj6
    Izvestaj7
    Izvestaj8
    Beleska "> meni"
    MeniForma
    Application.RefreshDatabaseWindow
    Beleska "> provera (otvara se svaki upit i izve~staj)"
    Beleska ProveriSve()
    DoCmd.SetWarnings True
    Beleska "--- gotovo ---"
    MsgBox "Izve~staji su dodati u bazu." & vbCrLf & vbCrLf & _
           "upita (qIzv...): " & gUpit & vbCrLf & _
           "izve~staja (rptIzv...): " & gIzv & vbCrLf & _
           "formi (frmIzvestaji): " & gForm & vbCrLf & _
           "upozorenja pri kreiranju: " & gGreske & vbCrLf & vbCrLf & _
           "PROVERA" & vbCrLf & _
           "u redu: " & gOk & vbCrLf & _
           "prazno (radi, ali bez podataka): " & gPrazno & vbCrLf & _
           "gre~ska: " & gLose & vbCrLf & vbCrLf & _
           "Detaljan spisak: Ctrl+G (Immediate prozor) ili procedura Dnevnik." & vbCrLf & _
           "Trajanje: " & Format(Timer - t0, "0.0") & " s" & vbCrLf & _
           "Tabele, forme i postoje~ki upiti nisu menjani.", _
           vbInformation, APP_NAZIV
    Exit Sub
Greska:
    DoCmd.SetWarnings True
    MsgBox "Prekid pri kreiranju izve~staja:" & vbCrLf & _
           Err.Number & " - " & Err.Description, vbCritical, APP_NAZIV
End Sub

' Dnevnik poslednjeg pokretanja (Ctrl+G).
Public Sub Dnevnik()
    Debug.Print gPoruke
End Sub
