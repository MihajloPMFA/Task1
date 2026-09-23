Attribute VB_Name = "modKreirajBazu"
Option Compare Database
Option Explicit

' =====================================================================
'  TV PANORAMA - informacioni sistem TV stanice
'  Automatsko kreiranje baze u Microsoft Access-u:
'  tabele, veze, upiti, forme za svaku tabelu, osam izvestaja i demo podaci.
'
'  Generisano iz ER seme projekta (er/ER_TV_stanica.sql).
'
'  KAKO SE KORISTI
'    1. Napravi prazan Access fajl (.accdb).
'    2. Alt+F11  ->  File  ->  Import File...  ->  izaberi ovaj .bas
'    3. Tools -> References...  ->  ukljuci "Microsoft Office x.0 Access
'       database engine Object Library" (DAO), ako vec nije ukljucena.
'    4. Klikni bilo gde u proceduru KreirajSve i pritisni F5.
'
'  NAPOMENA O SRPSKIM SLOVIMA
'    Fajl je namerno ciste ASCII sadrzine da bi se uvozio bez obzira na
'    kodnu stranu Windows-a.  Slova c, c, s, z, d se sastavljaju u funkciji
'    T() preko ChrW, pa su natpisi u bazi ispravni.
' =====================================================================

Private Const APP_NAZIV As String = "TV Panorama"

Private gRec As Object          ' recnik izuzetaka za natpise
Private gTab As Long, gUpit As Long, gForm As Long, gIzv As Long
Private gVeza As Long, gRed As Long, gGreske As Long
Private gPoruke As String

' ---------------------------------------------------------------- srpska slova
Private Function Z(ByVal s As String, ByVal marker As String, ByVal kod As Long) As String
    ' vbBinaryCompare je obavezan: uz Option Compare Database Replace ne razlikuje
    ' velika i mala slova, pa bi "~c" i "~C" davali isti znak.
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

' ---------------------------------------------------------------- natpisi
Private Sub R(ByVal k As String, ByVal v As String)
    gRec(k) = v
End Sub

Private Function Natpis(ByVal ime As String) As String
    Dim d() As String, i As Long, w As String, r As String, s As String
    If gRec Is Nothing Then PuniRecnik
    d = Split(ime, "_")
    For i = 0 To UBound(d)
        w = d(i)
        If gRec.Exists(w) Then
            r = T(gRec(w))
        ElseIf w = "PIB" Or w = "JMBG" Or w = "PDV" Or w = "TV" Then
            r = w
        ElseIf w = "RB" Then
            If i = 0 Then r = "redni broj" Else r = "rb"
        Else
            r = LCase(w)
        End If
        If i = 0 And Len(r) > 0 And w <> "PIB" And w <> "JMBG" And w <> "PDV" And w <> "TV" Then
            r = UCase(Left(r, 1)) & Mid(r, 2)
        End If
        If i = 0 Then s = r Else s = s & " " & r
    Next i
    Natpis = s
End Function

' ---------------------------------------------------------------- brisanje
Private Sub Obrisi(ByVal vrsta As String, ByVal ime As String)
    On Error Resume Next
    Select Case vrsta
        Case "T": CurrentDb.TableDefs.Delete ime
        Case "Q": CurrentDb.QueryDefs.Delete ime
        Case "F": DoCmd.DeleteObject acForm, ime
        Case "R": DoCmd.DeleteObject acReport, ime
    End Select
    Err.Clear
    On Error GoTo 0
End Sub

Private Sub ObrisiSve()
    Dim db As DAO.Database, i As Long, spisak As String
    Set db = CurrentDb
    On Error Resume Next
    For i = db.Relations.Count - 1 To 0 Step -1
        db.Relations.Delete db.Relations(i).Name
    Next i
    Err.Clear
    On Error GoTo 0

    spisak = ""
    For i = 0 To db.QueryDefs.Count - 1
        If Left(db.QueryDefs(i).Name, 1) <> "~" Then spisak = spisak & db.QueryDefs(i).Name & vbCrLf
    Next i
    Pobrisi "Q", spisak

    spisak = ""
    For i = 0 To db.TableDefs.Count - 1
        If Left(db.TableDefs(i).Name, 4) <> "MSys" Then spisak = spisak & db.TableDefs(i).Name & vbCrLf
    Next i
    Pobrisi "T", spisak

    spisak = ""
    For i = 0 To CurrentProject.AllForms.Count - 1
        spisak = spisak & CurrentProject.AllForms(i).Name & vbCrLf
    Next i
    Pobrisi "F", spisak

    spisak = ""
    For i = 0 To CurrentProject.AllReports.Count - 1
        spisak = spisak & CurrentProject.AllReports(i).Name & vbCrLf
    Next i
    Pobrisi "R", spisak

    CurrentDb.TableDefs.Refresh
End Sub

Private Sub Pobrisi(ByVal vrsta As String, ByVal spisak As String)
    Dim d() As String, i As Long
    If Len(spisak) = 0 Then Exit Sub
    d = Split(Left(spisak, Len(spisak) - 2), vbCrLf)
    For i = 0 To UBound(d)
        Obrisi vrsta, d(i)
    Next i
End Sub

' ---------------------------------------------------------------- tabele
Private Sub NapraviTabelu(ByVal ime As String, ByVal polja As String)
    Dim db As DAO.Database, td As DAO.TableDef, f As DAO.Field
    Dim d() As String, p() As String, i As Long
    Obrisi "T", ime
    Set db = CurrentDb
    Set td = db.CreateTableDef(ime)
    d = Split(polja, "|")
    For i = 0 To UBound(d)
        p = Split(d(i), ":")
        Select Case p(1)
            Case "T":  Set f = td.CreateField(p(0), dbText, CLng(p(2)))
                       f.AllowZeroLength = False
            Case "L":  Set f = td.CreateField(p(0), dbLong)
            Case "C":  Set f = td.CreateField(p(0), dbCurrency)
            Case "D":  Set f = td.CreateField(p(0), dbDouble)
            Case Else: Set f = td.CreateField(p(0), dbDate)
        End Select
        If p(3) = "1" Then f.Required = True
        td.Fields.Append f
    Next i
    db.TableDefs.Append td
    db.TableDefs.Refresh
    PodesiPolja ime, polja
    gTab = gTab + 1
End Sub

Private Sub PodesiPolja(ByVal ime As String, ByVal polja As String)
    ' natpis (Caption) i format za svako polje - odatle ih forme i izvestaji preuzimaju
    Dim db As DAO.Database, td As DAO.TableDef, f As DAO.Field
    Dim d() As String, p() As String, i As Long
    Set db = CurrentDb
    Set td = db.TableDefs(ime)
    d = Split(polja, "|")
    For i = 0 To UBound(d)
        p = Split(d(i), ":")
        Set f = td.Fields(p(0))
        Osobina f, "Caption", dbText, Natpis(p(0))
        Select Case p(1)
            Case "C":  Osobina f, "Format", dbText, "#,##0.00"
            Case "D":  Osobina f, "Format", dbText, "0.00"
            Case "Dt": Osobina f, "Format", dbText, "Short Date"
            Case "Tm": Osobina f, "Format", dbText, "Short Time"
        End Select
    Next i
End Sub

Private Sub Osobina(ByVal o As Object, ByVal ime As String, ByVal tip As Integer, ByVal v As Variant)
    On Error Resume Next
    o.Properties(ime) = v
    If Err.Number <> 0 Then
        Err.Clear
        o.Properties.Append o.CreateProperty(ime, tip, v)
    End If
    Err.Clear
    On Error GoTo 0
End Sub

' ---------------------------------------------------------------- kljucevi i veze
Private Sub PK(ByVal tabela As String, ByVal polja As String)
    Dim db As DAO.Database, td As DAO.TableDef, ix As DAO.Index
    Dim d() As String, i As Long
    Set db = CurrentDb
    Set td = db.TableDefs(tabela)
    Set ix = td.CreateIndex("PrimaryKey")
    d = Split(polja, ",")
    For i = 0 To UBound(d)
        ix.Fields.Append ix.CreateField(Trim(d(i)))
    Next i
    ix.Primary = True
    ix.Unique = True
    td.Indexes.Append ix
    td.Indexes.Refresh
End Sub

Private Sub FK(ByVal ime As String, ByVal dete As String, ByVal poljaDeteta As String, _
               ByVal roditelj As String, ByVal poljaRoditelja As String)
    Dim db As DAO.Database, rel As DAO.Relation
    Dim a() As String, b() As String, i As Long
    Set db = CurrentDb
    On Error Resume Next
    db.Relations.Delete ime
    Err.Clear
    On Error GoTo Greska
    Set rel = db.CreateRelation(ime, roditelj, dete, dbRelationUpdateCascade)
    a = Split(poljaRoditelja, ","): b = Split(poljaDeteta, ",")
    For i = 0 To UBound(a)
        rel.Fields.Append rel.CreateField(Trim(a(i)))
        rel.Fields(Trim(a(i))).ForeignName = Trim(b(i))
    Next i
    db.Relations.Append rel
    gVeza = gVeza + 1
    Exit Sub
Greska:
    Beleska "  veza " & ime & " nije napravljena: " & Err.Description
    Err.Clear
End Sub

' ---------------------------------------------------------------- upiti
Private Sub NapraviUpit(ByVal ime As String, ByVal sql As String)
    Dim db As DAO.Database, qd As DAO.QueryDef
    Obrisi "Q", ime
    Set db = CurrentDb
    On Error GoTo Greska
    Set qd = db.CreateQueryDef(ime, T(sql))
    db.QueryDefs.Refresh
    gUpit = gUpit + 1
    Exit Sub
Greska:
    Beleska "  upit " & ime & " nije napravljen: " & Err.Description
    Err.Clear
End Sub

' ---------------------------------------------------------------- demo podaci
Private Sub Ubaci(ByVal sql As String)
    On Error GoTo Greska
    CurrentDb.Execute T(sql), dbFailOnError
    gRed = gRed + 1
    Exit Sub
Greska:
    gGreske = gGreske + 1
    If gGreske <= 15 Then Beleska "  red nije upisan: " & Err.Description & " | " & Left(sql, 80)
    Err.Clear
End Sub

' ---------------------------------------------------------------- forme
Private Sub NapraviFormu(ByVal tabela As String)
    Dim frm As Form, ctl As Control, lbl As Control, td As DAO.TableDef
    Dim i As Long, n As Long, kol As Long, red As Long, x As Long, y As Long
    Dim priv As String, brKol As Long
    Const WL As Long = 2400, WT As Long = 3300, HH As Long = 300
    Const KORAK As Long = 380, POKOL As Long = 12
    On Error GoTo Greska
    Obrisi "F", "frm_" & tabela
    Set frm = CreateForm()
    priv = frm.Name
    frm.RecordSource = tabela
    Set td = CurrentDb.TableDefs(tabela)
    n = td.Fields.Count
    brKol = ((n - 1) \ POKOL) + 1

    Set lbl = CreateControl(priv, acLabel, acDetail, , , 200, 150, WL + WT, 380)
    lbl.Caption = Natpis(tabela)
    lbl.FontSize = 14
    lbl.FontBold = True

    For i = 0 To n - 1
        kol = i \ POKOL
        red = i Mod POKOL
        x = 200 + kol * (WL + WT + 500)
        y = 750 + red * KORAK
        Set ctl = CreateControl(priv, acTextBox, acDetail, , td.Fields(i).Name, _
                                x + WL + 100, y, WT, HH)
        ctl.Name = "t_" & td.Fields(i).Name
        Set lbl = CreateControl(priv, acLabel, acDetail, ctl.Name, , x, y + 40, WL, HH - 60)
        lbl.Caption = Natpis(td.Fields(i).Name) & ":"
        lbl.FontSize = 9
    Next i

    If n > POKOL Then
        frm.Section(acDetail).Height = 750 + POKOL * KORAK + 400
    Else
        frm.Section(acDetail).Height = 750 + n * KORAK + 400
    End If
    frm.Width = 200 + brKol * (WL + WT + 500)
    frm.Caption = Natpis(tabela)
    frm.NavigationButtons = True
    frm.RecordSelectors = False
    DoCmd.Close acForm, priv, acSaveYes
    DoCmd.Rename "frm_" & tabela, acForm, priv
    gForm = gForm + 1
    Exit Sub
Greska:
    Beleska "  forma frm_" & tabela & " nije napravljena: " & Err.Description
    Err.Clear
    On Error Resume Next
    DoCmd.Close acForm, priv, acSaveNo
End Sub

' ---------------------------------------------------------------- izvestaji
Private Function KolX(ByVal kolone As String, ByVal polje As String, ByRef w As Long) As Long
    Dim k() As String, p() As String, i As Long, x As Long
    k = Split(kolone, "|")
    x = 100
    For i = 0 To UBound(k)
        p = Split(k(i), ":")
        If p(0) = polje Then
            w = CLng(p(1)) - 60
            KolX = x
            Exit Function
        End If
        x = x + CLng(p(1))
    Next i
    w = 1500
    KolX = 100
End Function

Private Function NapraviIzvestaj(ByVal ime As String, ByVal izvor As String, ByVal naslov As String, _
                          ByVal kolone As String, ByVal grupa As String, ByVal sume As String, _
                          ByVal pejzaz As Boolean) As String
    Dim rpt As Report, ctl As Control, lbl As Control
    Dim k() As String, p() As String, s() As String
    Dim i As Long, x As Long, w As Long, uk As Long, priv As String
    Const VIS As Long = 260
    On Error GoTo Greska
    naslov = T(naslov)
    Obrisi "R", ime
    Set rpt = CreateReport()
    priv = rpt.Name
    rpt.RecordSource = izvor

    k = Split(kolone, "|")
    uk = 0
    For i = 0 To UBound(k)
        p = Split(k(i), ":")
        uk = uk + CLng(p(1))
    Next i

    If Len(grupa) > 0 Then CreateGroupLevel priv, grupa, True, True

    On Error Resume Next
    rpt.Section(acHeader).Height = 1000
    rpt.Section(acPageHeader).Height = 420
    rpt.Section(acDetail).Height = VIS + 60
    rpt.Section(acPageFooter).Height = 360
    On Error GoTo Greska

    Set lbl = CreateReportControl(priv, acLabel, acHeader, , , 100, 120, uk, 420)
    lbl.Caption = naslov
    lbl.FontSize = 16
    lbl.FontBold = True
    Set lbl = CreateReportControl(priv, acLabel, acHeader, , , 100, 580, uk, 280)
    lbl.Caption = T("Informacioni sistem TV stanice - TV Panorama")
    lbl.FontSize = 9
    lbl.ForeColor = RGB(90, 100, 120)

    x = 100
    For i = 0 To UBound(k)
        p = Split(k(i), ":")
        w = CLng(p(1))
        Set lbl = CreateReportControl(priv, acLabel, acPageHeader, , , x, 90, w - 60, 260)
        lbl.Caption = Natpis(p(0))
        lbl.FontBold = True
        lbl.FontSize = 9
        x = x + w
    Next i
    Set ctl = CreateReportControl(priv, acLine, acPageHeader, , , 100, 390, uk, 0)

    If Len(grupa) > 0 Then
        On Error Resume Next
        rpt.Section(acGroupLevel1Header).Height = 460
        rpt.Section(acGroupLevel1Footer).Height = IIf(Len(sume) > 0, 420, 160)
        On Error GoTo Greska
        Set ctl = CreateReportControl(priv, acTextBox, acGroupLevel1Header, , grupa, 100, 120, 7000, 280)
        ctl.Name = "g_zaglavlje"
        ctl.FontBold = True
        ctl.FontSize = 11
        ctl.BorderStyle = 0
        Set ctl = CreateReportControl(priv, acLine, acGroupLevel1Header, , , 100, 430, uk, 0)
    End If

    x = 100
    For i = 0 To UBound(k)
        p = Split(k(i), ":")
        w = CLng(p(1))
        Set ctl = CreateReportControl(priv, acTextBox, acDetail, , p(0), x, 40, w - 60, VIS)
        ctl.Name = "d_" & p(0)
        ctl.FontSize = 9
        ctl.BorderStyle = 0
        x = x + w
    Next i

    If Len(sume) > 0 Then
        s = Split(sume, "|")
        If Len(grupa) > 0 Then
            Set lbl = CreateReportControl(priv, acLabel, acGroupLevel1Footer, , , 100, 70, 2400, 260)
            lbl.Caption = T("Ukupno za grupu:")
            lbl.FontBold = True
            lbl.FontSize = 9
            For i = 0 To UBound(s)
                x = KolX(kolone, s(i), w)
                Set ctl = CreateReportControl(priv, acTextBox, acGroupLevel1Footer, , , x, 70, w, 260)
                ctl.ControlSource = "=Sum([" & s(i) & "])"
                ctl.Name = "gs_" & s(i)
                ctl.FontBold = True
                ctl.FontSize = 9
                ctl.BorderStyle = 0
            Next i
            Set ctl = CreateReportControl(priv, acLine, acGroupLevel1Footer, , , 100, 40, uk, 0)
        End If
        On Error Resume Next
        rpt.Section(acFooter).Height = 460
        On Error GoTo Greska
        Set lbl = CreateReportControl(priv, acLabel, acFooter, , , 100, 120, 2400, 280)
        lbl.Caption = T("UKUPNO:")
        lbl.FontBold = True
        For i = 0 To UBound(s)
            x = KolX(kolone, s(i), w)
            Set ctl = CreateReportControl(priv, acTextBox, acFooter, , , x, 120, w, 280)
            ctl.ControlSource = "=Sum([" & s(i) & "])"
            ctl.Name = "us_" & s(i)
            ctl.FontBold = True
            ctl.BorderStyle = 0
        Next i
        Set ctl = CreateReportControl(priv, acLine, acFooter, , , 100, 80, uk, 0)
    End If

    Set ctl = CreateReportControl(priv, acTextBox, acPageFooter, , , 100, 80, 4200, 260)
    ctl.ControlSource = "=Now()"
    ctl.Format = "dd.mm.yyyy. hh:nn"
    ctl.FontSize = 8
    ctl.BorderStyle = 0
    Set ctl = CreateReportControl(priv, acTextBox, acPageFooter, , , uk - 3200, 80, 3100, 260)
    ctl.ControlSource = "=""Strana "" & [Page] & "" od "" & [Pages]"
    ctl.FontSize = 8
    ctl.TextAlign = 3
    ctl.BorderStyle = 0

    rpt.Width = uk + 200
    rpt.Caption = naslov
    If pejzaz Then
        On Error Resume Next
        rpt.Printer.Orientation = 2
        On Error GoTo Greska
    End If
    DoCmd.Close acReport, priv, acSaveYes
    DoCmd.Rename ime, acReport, priv
    gIzv = gIzv + 1
    NapraviIzvestaj = ime
    Exit Function
Greska:
    Beleska "  izvestaj " & ime & " nije napravljen: " & Err.Description
    Err.Clear
    On Error Resume Next
    DoCmd.Close acReport, priv, acSaveNo
    NapraviIzvestaj = ""
End Function

Private Sub DodajGrafikon(ByVal izvestaj As String, ByVal upit As String, ByVal naslov As String)
    ' Grafikon se dodaje kao MSGraph objekat u zaglavlje izvestaja.
    ' Ako MSGraph nije registrovan, izvestaj ostaje ispravan - samo bez slike.
    Dim rpt As Report, ctl As Control, lbl As Control
    On Error GoTo Greska
    naslov = T(naslov)
    DoCmd.OpenReport izvestaj, acViewDesign
    Set rpt = Reports(izvestaj)
    rpt.Section(acHeader).Height = 6200
    Set lbl = CreateReportControl(izvestaj, acLabel, acHeader, , , 100, 1000, 9000, 280)
    lbl.Caption = naslov
    lbl.FontBold = True
    lbl.FontSize = 10
    Set ctl = CreateReportControl(izvestaj, acObjectFrame, acHeader, , , 100, 1320, 9200, 4600)
    ctl.Name = "grafikon"
    ctl.Class = "MSGraph.Chart.8"
    ctl.RowSourceType = "Table/Query"
    ctl.RowSource = upit
    DoCmd.Close acReport, izvestaj, acSaveYes
    Beleska "  grafikon dodat u " & izvestaj
    Exit Sub
Greska:
    Beleska "  grafikon nije dodat (" & Err.Description & ") - izvestaj radi bez njega;" & _
            " grafikon se moze dodati carobnjakom nad upitom " & upit
    Err.Clear
    On Error Resume Next
    DoCmd.Close acReport, izvestaj, acSaveYes
End Sub

Private Sub DodajPodizvestaj(ByVal glavni As String, ByVal podizvestaj As String, _
                             ByVal naslov As String, ByVal visina As Long)
    Dim rpt As Report, ctl As Control, lbl As Control
    On Error GoTo Greska
    naslov = T(naslov)
    DoCmd.OpenReport glavni, acViewDesign
    Set rpt = Reports(glavni)
    rpt.Section(acFooter).Height = rpt.Section(acFooter).Height + visina + 700
    Set lbl = CreateReportControl(glavni, acLabel, acFooter, , , 100, _
                                  rpt.Section(acFooter).Height - visina - 500, 8000, 300)
    lbl.Caption = naslov
    lbl.FontBold = True
    lbl.FontSize = 11
    Set ctl = CreateReportControl(glavni, acSubform, acFooter, , , 100, _
                                  rpt.Section(acFooter).Height - visina - 120, rpt.Width - 300, visina)
    ctl.Name = "pod_" & podizvestaj
    ctl.SourceObject = "Report." & podizvestaj
    DoCmd.Close acReport, glavni, acSaveYes
    Beleska "  podizvestaj " & podizvestaj & " ugradjen u " & glavni
    Exit Sub
Greska:
    Beleska "  podizvestaj " & podizvestaj & " nije ugradjen: " & Err.Description
    Err.Clear
    On Error Resume Next
    DoCmd.Close acReport, glavni, acSaveYes
End Sub

' ---------------------------------------------------------------- recnik
Private Sub PuniRecnik()
    Set gRec = CreateObject("Scripting.Dictionary")
    R "ANGAZOVANIH", T("anga~zovanih")
    R "ANGAZOVANJE", T("anga~zovanje")
    R "BRANSA", T("bran~sa")
    R "BUDZET", T("bud~zet")
    R "CELINA", "celina"
    R "CELINE", "celine"
    R "DOBAVLJAC", T("dobavlja~c")
    R "DOBAVLJACA", T("dobavlja~ca")
    R "DONOSENJA", T("dono~senja")
    R "GODISNJI", T("godi~snji")
    R "GRAFICKI", T("grafi~cki")
    R "INFO", "informacija"
    R "ISKORISCENO", T("iskori~s~keno")
    R "ISKORISCENOST", T("iskori~s~kenost")
    R "IZVESTAVANJA", T("izve~stavanja")
    R "JEDINICNA", T("jedini~cna")
    R "KOLICINA", T("koli~cina")
    R "KORISCENJA", T("kori~s~kenja")
    R "LEGITIM", "legitimacije"
    R "MATICNI", T("mati~cni")
    R "MEDIJSKI", "medijski"
    R "MONTAZA", T("monta~za")
    R "MUZICKI", T("muzi~cki")
    R "NADREDJENE", T("nadre~dene")
    R "NARUDZBENICA", T("narud~zbenica")
    R "NARUDZBENICE", T("narud~zbenice")
    R "NARUDZBINE", T("narud~zbine")
    R "OBRAZLOZENJE", T("obrazlo~zenje")
    R "OGLASAVANJU", T("ogla~savanju")
    R "OGLASIVAC", T("ogla~siva~c")
    R "OGLASIVACA", T("ogla~siva~ca")
    R "OVLASCENI", T("ovla~s~keni")
    R "OVLASCENJA", T("ovla~s~kenja")
    R "PLACANJA", T("pla~kanja")
    R "PLACANJE", T("pla~kanje")
    R "POSTANSKI", T("po~stanski")
    R "PREDVIDJENO", T("predvi~deno")
    R "PROIZVODJAC", T("proizvo~da~c")
    R "PROSECNO", T("prose~cno")
    R "RATING", "rejting"
    R "RAZDUZENJA", T("razdu~zenja")
    R "REKL", "reklamnih"
    R "RESAVANJA", T("re~savanja")
    R "RESENJA", T("re~senja")
    R "SADRZAJ", T("sadr~zaj")
    R "SADRZAJA", T("sadr~zaja")
    R "SEMA", T("~sema")
    R "SEME", T("~seme")
    R "SIFRA", T("~sifra")
    R "SKLADISTA", T("skladi~sta")
    R "TEHNICKO", T("tehni~cko")
    R "TROSAK", T("tro~sak")
    R "TROSKA", T("tro~ska")
    R "UTVRDJENO", T("utvr~deno")
    R "VLASNISTVA", T("vlasni~stva")
    R "VRACANJU", T("vra~kanju")
    R "ZADUZENJA", T("zadu~zenja")
    R "ZADUZENJE", T("zadu~zenje")
    R "ZAHTEV", "zahtev"
    R "ZAKUPLJENO", "zakupljeno"
    R "ZANR", T("~zanr")
    R "ZAPIS", "zapis"
    R "ZAVRSETKA", T("zavr~setka")
End Sub

Private Sub Tabele1()
    NapraviTabelu "ORGANIZACIONA_JEDINICA", "SIFRA_JEDINICE:T:18:1|SIFRA_NADREDJENE_JEDINICE:T:18:0|NAZIV_JEDINICE:T:60:1|TIP_JEDINICE:T:30:0|OPIS_DELATNOSTI:T:255:0|DATUM_OSNIVANJA:Dt:0:0|BROJ_ZAPOSLENIH:L:0:0"
    NapraviTabelu "ZAPOSLENI", "SIFRA_ZAPOSLENOG:T:18:1|SIFRA_JEDINICE:T:18:1|JMBG:T:13:1|IME:T:30:1|PREZIME:T:30:1|RADNO_MESTO:T:60:0|DATUM_ZAPOSLENJA:Dt:0:0|OSNOVNA_ZARADA:C:0:0|STATUS_ZAPOSLENJA:T:20:0"
    NapraviTabelu "UREDNIK", "SIFRA_ZAPOSLENOG:T:18:1|NIVO_OVLASCENJA:T:30:0|REDAKCIJA:T:60:0"
    NapraviTabelu "NOVINAR_REPORTER", "SIFRA_ZAPOSLENOG:T:18:1|OBLAST_IZVESTAVANJA:T:60:0|BROJ_NOVINARSKE_LEGITIM:T:20:0"
    NapraviTabelu "TEHNICKO_OSOBLJE", "SIFRA_ZAPOSLENOG:T:18:1|SPECIJALIZACIJA:T:60:0|TIP_EKIPE:T:30:0"
    NapraviTabelu "REFERENT", "SIFRA_ZAPOSLENOG:T:18:1|TIP_REFERENTA:T:30:0|NIVO_OVLASCENJA:T:30:0"
    NapraviTabelu "SERVISERI", "SIFRA_ZAPOSLENOG:T:18:1|LICENCA:T:60:0"
    NapraviTabelu "OPREMA", "INVENTARSKI_BROJ:T:18:1|NAZIV_OPREME:T:60:1|MODEL_OPREME:T:60:0|PROIZVODJAC:T:60:0|STATUS_OPREME:T:20:0|DATUM_NABAVKE:Dt:0:0|GARANCIJA_DO:Dt:0:0|NABAVNA_VREDNOST:C:0:0"
    NapraviTabelu "SNIMATELJSKA_OPREMA", "INVENTARSKI_BROJ:T:18:1|TIP_MEMORIJSKOG_SKLADISTA:T:30:0|REZOLUCIJA:T:20:0|TIP_KAMERE:T:30:0"
    NapraviTabelu "STUDIJSKA_I_EMISIONA_OPREMA", "INVENTARSKI_BROJ:T:18:1|LOKACIJA_U_STUDIJU:T:60:0"
    NapraviTabelu "AUDIO_OPREMA", "INVENTARSKI_BROJ:T:18:1|TIP:T:30:0|FREKVENCIJA:T:20:0"
    NapraviTabelu "SVETLOSNA_OPREMA", "INVENTARSKI_BROJ:T:18:1|SNAGA:T:20:0|TIP_SVETLOSTI:T:30:0"
    NapraviTabelu "ZADUZENJE_OPREME", "SIFRA_ZAPOSLENOG:T:18:1|INVENTARSKI_BROJ:T:18:1|DATUM_ZADUZENJA:Dt:0:1|DATUM_RAZDUZENJA:Dt:0:0|STANJE_PRI_VRACANJU:T:255:0"
    NapraviTabelu "SERVISIRANJE_OPREME", "SIFRA_ZAPOSLENOG:T:18:1|INVENTARSKI_BROJ:T:18:1|DATUM_SERVISA:Dt:0:1|OPIS_RADOVA:T:255:0|TROSAK:C:0:0"
    NapraviTabelu "PROJEKAT_PRODUKCIJE", "SIFRA_PROJEKTA:T:18:1|SIFRA_UREDNIKA:T:18:1|SIFRA_EMISIJE:T:18:0|NAZIV_PROJEKTA:T:60:1|DATUM_POCETKA:Dt:0:0|DATUM_ZAVRSETKA:Dt:0:0|ODOBREN_BUDZET:C:0:0|STATUS_PROJEKTA:T:20:0|VRSTA_PRODUKCIJE:T:30:0|OPIS_PROJEKTA:T:255:0"
    NapraviTabelu "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA:T:18:1|RB_AKTIVNOSTI:L:0:1|NAZIV_AKTIVNOSTI:T:60:1|DATUM_OD:Dt:0:0|DATUM_DO:Dt:0:0|VRSTA_AKTIVNOSTI:T:30:0|LOKACIJA_SNIMANJA:T:60:0|STATUS_AKTIVNOSTI:T:20:0"
    NapraviTabelu "TROSAK_PRODUKCIJE", "SIFRA_PROJEKTA:T:18:1|RB_AKTIVNOSTI:L:0:1|RB_TROSKA:L:0:1|BROJ_FAKTURE:T:18:0|VRSTA_TROSKA:T:30:0|IZNOS:C:0:1|DATUM_NASTANKA:Dt:0:0|OPIS_TROSKA:T:255:0"
    NapraviTabelu "ANGAZOVANJE_NA_AKTIVNOSTI", "SIFRA_PROJEKTA:T:18:1|RB_AKTIVNOSTI:L:0:1|SIFRA_ZAPOSLENOG:T:18:1|ULOGA_NA_SNIMANJU:T:60:0|DATUM_OD:Dt:0:0|DATUM_DO:Dt:0:0|BROJ_ANGAZOVANIH_SATI:L:0:0"
    NapraviTabelu "REZERVACIJA_OPREME", "SIFRA_PROJEKTA:T:18:1|RB_AKTIVNOSTI:L:0:1|INVENTARSKI_BROJ:T:18:1|DATUM_REZERVACIJE:Dt:0:0|TRAJANJE_ZADUZENJA:L:0:0"
    NapraviTabelu "SIROVI_SNIMAK", "SIFRA_SNIMKA:T:18:1|SIFRA_PROJEKTA:T:18:1|RB_AKTIVNOSTI:L:0:1|DATUM_SNIMANJA:Dt:0:0|TRAJANJE:L:0:0|FORMAT_SNIMKA:T:30:0|LOKACIJA_SNIMKA:T:60:0|OCENA_KVALITETA:T:20:0"
    NapraviTabelu "GRAFICKI_I_MUZICKI_ELEMENT", "SIFRA_ELEMENTA:T:18:1|NAZIV_ELEMENTA:T:60:1|TIP_ELEMENTA:T:30:0|AUTOR:T:60:0|FORMAT_ELEMENTA:T:30:0|USLOV_KORISCENJA:T:255:0"
    NapraviTabelu "PROGRAMSKA_SEMA", "SIFRA_SEME:T:18:1|SIFRA_UREDNIKA:T:18:1|NAZIV_SEME:T:60:1|SEZONA:T:20:0|VERZIJA_SEME:T:20:0|DATUM_OD:Dt:0:0|DATUM_DO:Dt:0:0|STATUS_SEME:T:20:0|DATUM_USVAJANJA:Dt:0:0"
    NapraviTabelu "PROGRAMSKA_CELINA", "SIFRA_SEME:T:18:1|RB_CELINE:L:0:1|NAZIV_CELINE:T:60:1|TIP_CELINE:T:30:0|DATUM:Dt:0:0|VREME_OD:Tm:0:0|VREME_DO:Tm:0:0"
    NapraviTabelu "EMISIJA", "SIFRA_EMISIJE:T:18:1|NAZIV_EMISIJE:T:60:1|ZANR:T:30:0|FORMAT_EMISIJE:T:30:0|PREDVIDJENO_TRAJANJE:L:0:0|CILJNA_PUBLIKA:T:60:0|STATUS_EMISIJE:T:20:0|PROGRAMSKI_ELABORAT:T:255:0"
End Sub

Private Sub Tabele2()
    NapraviTabelu "TERMIN_EMITOVANJA", "SIFRA_TERMINA:T:18:1|SIFRA_SEME:T:18:1|RB_CELINE:L:0:1|SIFRA_EMISIJE:T:18:1|DATUM:Dt:0:1|VREME_POCETKA:Tm:0:1|TRAJANJE_TERMINA:L:0:0|TIP_TERMINA:T:30:0|ZONA_GLEDANOSTI:T:20:0|STATUS_TERMINA:T:20:0|REDNI_BROJ_REPRIZE:L:0:0"
    NapraviTabelu "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA:T:18:1|NAZIV_SADRZAJA:T:60:1|TRAJANJE:L:0:0|FORMAT_ZAPISA:T:30:0|DATUM_ARHIVIRANJA:Dt:0:0|LOKACIJA_U_ARHIVI:T:60:0"
    NapraviTabelu "PRODUCIRANI_SADRZAJ", "SIFRA_SADRZAJA:T:18:1|DATUM_PRODUKCIJE:Dt:0:0|VERZIJA_MASTERA:T:20:0"
    NapraviTabelu "NABAVLJENI_SADRZAJ", "SIFRA_SADRZAJA:T:18:1|BROJ_UGOVORA:T:18:1|ZEMLJA_POREKLA:T:60:0|CENA_NABAVKE:C:0:0|DATUM_PREUZIMANJA:Dt:0:0|UGOVORENA_NAKNADA:C:0:0"
    NapraviTabelu "REKLAMNI_SADRZAJ", "SIFRA_SADRZAJA:T:18:1|SIFRA_OGLASIVACA:T:18:1|DATUM_PRIJEMA:Dt:0:0|STATUS:T:20:0"
    NapraviTabelu "ZAPIS_O_EMITOVANJU", "SIFRA_TERMINA:T:18:1|RB_EMITOVANJA:L:0:1|SIFRA_SADRZAJA:T:18:1|STATUS_REALIZACIJE:T:20:0|STVARNO_VREME_POCETKA:Tm:0:0|STVARNO_TRAJANJE:L:0:0|NAPOMENA_O_SMETNJAMA:T:255:0|OPERATER_EMITOVANJA:T:60:0"
    NapraviTabelu "MONTAZA_SNIMKA", "SIFRA_SADRZAJA:T:18:1|SIFRA_SNIMKA:T:18:1"
    NapraviTabelu "UGRADNJA_ELEMENTA", "SIFRA_SADRZAJA:T:18:1|SIFRA_ELEMENTA:T:18:1|VREME_POJAVLJIVANJA:Tm:0:0|NACIN_KORISCENJA:T:60:0"
    NapraviTabelu "SADRZAJ_EMISIJE", "SIFRA_EMISIJE:T:18:1|SIFRA_SADRZAJA:T:18:1|REDNI_BROJ_U_EMISIJI:L:0:0"
    NapraviTabelu "PRAVO_KORISCENJA", "BROJ_LICENCE:T:18:1|VRSTA_PRAVA:T:30:0|DATUM_OD:Dt:0:0|DATUM_DO:Dt:0:0|DOZVOLJENO_EMITOVANJA:L:0:0|ISKORISCENO_EMITOVANJA:L:0:0|TERITORIJA:T:60:0|NOSILAC_PRAVA:T:60:0"
    NapraviTabelu "POKRIVENOST_PRAVOM", "BROJ_LICENCE:T:18:1|SIFRA_SADRZAJA:T:18:1|OBLAST_POKRIVENOSTI:T:60:0"
    NapraviTabelu "POVRATNA_INFO_GLEDALACA", "BROJ_PRIJAVE:T:18:1|SIFRA_EMISIJE:T:18:0|DATUM_PRIJEMA:Dt:0:0|VRSTA_PRIJAVE:T:30:0|KANAL_PRIJEMA:T:30:0|SADRZAJ_PRIJAVE:T:255:0|STATUS_OBRADE:T:20:0|DATUM_ODGOVORA:Dt:0:0|PROFIL_GLEDAOCA:T:60:0"
    NapraviTabelu "MERENJE_GLEDANOSTI", "SIFRA_MERENJA:T:18:1|DATUM_MERENJA:Dt:0:0|IZVOR_MERENJA:T:60:0|CILJNA_GRUPA:T:60:0|RATING:D:0:0|SHARE_UDEO:D:0:0|BROJ_GLEDALACA:L:0:0|PROSECNO_GLEDANJE:L:0:0"
    NapraviTabelu "MERENJE_EMISIJE", "SIFRA_MERENJA:T:18:1|SIFRA_EMISIJE:T:18:1|OSTVARENI_RATING:D:0:0|UDEO_U_TERMINU:D:0:0"
    NapraviTabelu "CENOVNIK_REKL_TERMINA", "SIFRA_CENOVNIKA:T:18:1|VAZI_OD:Dt:0:0|VAZI_DO:Dt:0:0|ZONA:T:30:0|CENA_PO_SEKUNDI:C:0:0|TIP_CENOVNOG_PAKETA:T:30:0|OPIS_CENOVNOG_PAKETA:T:255:0"
    NapraviTabelu "REKLAMNI_BLOK", "SIFRA_BLOKA:T:18:1|SIFRA_TERMINA:T:18:1|SIFRA_CENOVNIKA:T:18:1|DATUM:Dt:0:0|VREME_POCETKA:Tm:0:0|TRAJANJE_BLOKA:L:0:0|ZAKUPLJENO_SEKUNDI:L:0:0|SLOBODNO_SEKUNDI:L:0:0|ISKORISCENOST:D:0:0|STATUS_BLOKA:T:20:0"
    NapraviTabelu "EMITOVANJE_REKLAME", "SIFRA_BLOKA:T:18:1|RB_U_BLOKU:L:0:1|SIFRA_SADRZAJA:T:18:1|BROJ_UGOVORA:T:18:1|RB_STAVKE_UGOVORA:L:0:1|DATUM_EMITOVANJA:Dt:0:0|VREME_EMITOVANJA:Tm:0:0|TRAJANJE_SPOTA:L:0:0|NAPLACENI_IZNOS:C:0:0|STATUS_NAPLATE:T:20:0"
    NapraviTabelu "KLIJENT", "SIFRA_KLIJENTA:T:18:1|NAZIV_KLIJENTA:T:60:1|PIB:T:9:0|MATICNI_BROJ:T:8:0|ULICA_I_BROJ:T:60:0|GRAD:T:30:0|POSTANSKI_BROJ:T:5:0|KONTAKT_OSOBA:T:60:0"
    NapraviTabelu "OGLASIVAC", "SIFRA_KLIJENTA:T:18:1|BRANSA:T:60:0|GODISNJI_BUDZET:C:0:0"
    NapraviTabelu "KUPAC_SADRZAJA", "SIFRA_KLIJENTA:T:18:1|TIP_MEDIJA:T:30:0|TERITORIJA_EMITOVANJA:T:60:0"
    NapraviTabelu "UGOVOR", "BROJ_UGOVORA:T:18:1|SIFRA_KLIJENTA:T:18:0|DATUM_SKLAPANJA:Dt:0:0|VAZI_OD:Dt:0:0|VAZI_DO:Dt:0:0|UKUPNA_VREDNOST:C:0:0|STATUS_UGOVORA:T:20:0"
    NapraviTabelu "STAVKA_UGOVORA", "BROJ_UGOVORA:T:18:1|RB_STAVKE:L:0:1|OPIS_STAVKE:T:255:0|KOLICINA_SEKUNDE:L:0:0|JEDINICNA_CENA:C:0:0|POPUST:D:0:0|VREDNOST_STAVKE:C:0:0"
    NapraviTabelu "UGOVOR_O_OGLASAVANJU", "BROJ_UGOVORA:T:18:1|UGOVORENI_TERMINI:T:255:0"
    NapraviTabelu "UGOVOR_O_PRODAJI_TV_SADRZAJA", "BROJ_UGOVORA:T:18:1|PRENOS_VLASNISTVA:T:20:0|OBIM_USTUPLJENIH_PRAVA:T:255:0"
End Sub

Private Sub Tabele3()
    NapraviTabelu "UGOVOR_O_NABAVCI", "BROJ_UGOVORA:T:18:1|SIFRA_DOBAVLJACA:T:18:1|VRSTA_REKLAMIRANJA:T:30:0|ROK_ISPORUKE:Dt:0:0|USLOVI_PLACANJA:T:255:0"
    NapraviTabelu "USTUPANJE_SADRZAJA", "BROJ_UGOVORA:T:18:1|SIFRA_SADRZAJA:T:18:1|UGOVORENA_CENA:C:0:0|OBIM_USTUPANJA:T:255:0"
    NapraviTabelu "PLAN_NABAVKE", "SIFRA_PLANA:T:18:1|GODINA_PLANA:L:0:0|DATUM_DONOSENJA:Dt:0:0|STATUS_PLANA:T:20:0|UKUPNA_VREDNOST:C:0:0|DONOSILAC_PLANA:T:60:0"
    NapraviTabelu "ZAHTEV_ZA_NABAVKU", "BROJ_ZAHTEVA:T:18:1|SIFRA_JEDINICE:T:18:1|SIFRA_PLANA:T:18:0|DATUM_ZAHTEVA:Dt:0:0|VRSTA_NABAVKE:T:30:0|PREDMET_ZAHTEVA:T:255:0|OBRAZLOZENJE:T:255:0|STATUS_ZAHTEVA:T:20:0|PRIORITET:T:20:0|PROCENJENA_VREDNOST:C:0:0"
    NapraviTabelu "STAVKA_PLANA_NABAVKE", "SIFRA_PLANA:T:18:1|RB_STAVKE:L:0:1|OPIS_ARTIKLA:T:255:0|KOLICINA:L:0:0|JEDINICA_MERE:T:20:0|PROCENJENA_CENA:C:0:0|PLANIRANI_KVARTAL:T:20:0"
    NapraviTabelu "DOBAVLJAC", "SIFRA_DOBAVLJACA:T:18:1|NAZIV_DOBAVLJACA:T:60:1|PIB:T:9:0|MATICNI_BROJ:T:8:0|ADRESA:T:60:0|OCENA_DOBAVLJACA:D:0:0"
    NapraviTabelu "DOBAVLJAC_TV_SADRZAJA", "SIFRA_DOBAVLJACA:T:18:1|VRSTA_SADRZAJA:T:30:0|KATALOG_PONUDE:T:255:0"
    NapraviTabelu "DOBAVLJAC_OPREME_I_MATERIJALA", "SIFRA_DOBAVLJACA:T:18:1|ASORTIMAN:T:255:0|OVLASCENI_SERVIS:T:20:0"
    NapraviTabelu "PONUDA_DOBAVLJACA", "BROJ_PONUDE:T:18:1|SIFRA_DOBAVLJACA:T:18:1|DATUM_PRIJEMA:Dt:0:0|VAZI_DO:Dt:0:0|UKUPNA_CENA:C:0:0|ROK_ISPORUKE:Dt:0:0|USLOVI_PLACANJA:T:255:0|STATUS_PONUDE:T:20:0|UKUPNO_BODOVA:D:0:0"
    NapraviTabelu "PONUDJENA_STAVKA", "SIFRA_PLANA:T:18:1|RB_STAVKE:L:0:1|BROJ_PONUDE:T:18:1|PONUDJENA_CENA:C:0:0|ROK_ZA_STAVKU:Dt:0:0"
    NapraviTabelu "KRITERIJUM_VREDNOVANJA", "SIFRA_KRITERIJUMA:T:18:1|NAZIV_KRITERIJUMA:T:60:1|NACIN_BODOVANJA:T:60:0|OPIS_KRITERIJUMA:T:255:0"
    NapraviTabelu "OCENA_PONUDE", "BROJ_PONUDE:T:18:1|SIFRA_KRITERIJUMA:T:18:1|BROJ_BODOVA:D:0:0|KOMENTAR_OCENE:T:255:0"
    NapraviTabelu "NARUDZBENICA", "BROJ_NARUDZBENICE:T:18:1|SIFRA_DOBAVLJACA:T:18:1|DATUM_IZDAVANJA:Dt:0:0|ROK_ISPORUKE:Dt:0:0|MESTO_ISPORUKE:T:60:0|UKUPAN_IZNOS:C:0:0|STATUS_NARUDZBINE:T:20:0"
    NapraviTabelu "STAVKA_NARUDZBENICE", "BROJ_NARUDZBENICE:T:18:1|RB_STAVKE:L:0:1|NAZIV_ARTIKLA:T:60:0|KOLICINA:L:0:0|JEDINICNA_CENA:C:0:0|STATUS_STAVKE:T:20:0|VREDNOST_STAVKE:C:0:0"
    NapraviTabelu "PRIJEMNICA", "BROJ_PRIJEMNICE:T:18:1|BROJ_NARUDZBENICE:T:18:1|BROJ_FAKTURE:T:18:0|DATUM_PRIJEMA:Dt:0:0|BROJ_OTPREMNICE:T:30:0|PRIMIO_MAGACIONER:T:60:0|ISPRAVNOST_ISPORUKE:T:20:0|NAPOMENA:T:255:0"
    NapraviTabelu "PRIJEM_STAVKE", "BROJ_PRIJEMNICE:T:18:1|BROJ_NARUDZBENICE:T:18:1|RB_STAVKE:L:0:1|PRIMLJENA_KOLICINA:L:0:0|UTVRDJENO_ODSTUPANJE:T:255:0"
    NapraviTabelu "REKLAMACIJA", "BROJ_REKLAMACIJE:T:18:1|BROJ_PRIJEMNICE:T:18:1|DATUM_REKLAMACIJE:Dt:0:0|RAZLOG_REKLAMACIJE:T:60:0|OPIS_NEDOSTATKA:T:255:0|STATUS_REKLAMACIJE:T:20:0|DATUM_RESENJA:Dt:0:0|REKLAMIRANI_IZNOS:C:0:0|NACIN_RESAVANJA:T:60:0"
    NapraviTabelu "REKLAMIRANA_STAVKA", "BROJ_REKLAMACIJE:T:18:1|BROJ_NARUDZBENICE:T:18:1|RB_STAVKE:L:0:1"
    NapraviTabelu "FAKTURA", "BROJ_FAKTURE:T:18:1|BROJ_UGOVORA:T:18:0|DATUM_IZDAVANJA:Dt:0:0|ROK_PLACANJA:Dt:0:0|SMER:T:20:0|OSNOVICA:C:0:0|IZNOS_PDV:C:0:0|STATUS_PLACANJA:T:20:0|IZNOS_ZA_PLACANJE:C:0:0"
    NapraviTabelu "STAVKA_FAKTURE", "BROJ_FAKTURE:T:18:1|RB_STAVKE:L:0:1|OPIS_STAVKE:T:255:0|KOLICINA:L:0:0|JEDINICNA_CENA:C:0:0|STOPA_PDV:D:0:0|VREDNOST_STAVKE:C:0:0"
    NapraviTabelu "NALOG_ZA_PLACANJE", "BROJ_NALOGA:T:18:1|BROJ_FAKTURE:T:18:1|DATUM_NALOGA:Dt:0:0|IZNOS_NALOGA:C:0:0|SVRHA_PLACANJA:T:255:0|DATUM_REALIZACIJE:Dt:0:0|STATUS_NALOGA:T:20:0|RACUN_PRIMAOCA:T:30:0|ODOBRIO:T:60:0"
End Sub

Private Sub Kljucevi1()
    PK "ORGANIZACIONA_JEDINICA", "SIFRA_JEDINICE"
    PK "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    PK "UREDNIK", "SIFRA_ZAPOSLENOG"
    PK "NOVINAR_REPORTER", "SIFRA_ZAPOSLENOG"
    PK "TEHNICKO_OSOBLJE", "SIFRA_ZAPOSLENOG"
    PK "REFERENT", "SIFRA_ZAPOSLENOG"
    PK "SERVISERI", "SIFRA_ZAPOSLENOG"
    PK "OPREMA", "INVENTARSKI_BROJ"
    PK "SNIMATELJSKA_OPREMA", "INVENTARSKI_BROJ"
    PK "STUDIJSKA_I_EMISIONA_OPREMA", "INVENTARSKI_BROJ"
    PK "AUDIO_OPREMA", "INVENTARSKI_BROJ"
    PK "SVETLOSNA_OPREMA", "INVENTARSKI_BROJ"
    PK "ZADUZENJE_OPREME", "SIFRA_ZAPOSLENOG,INVENTARSKI_BROJ,DATUM_ZADUZENJA"
    PK "SERVISIRANJE_OPREME", "SIFRA_ZAPOSLENOG,INVENTARSKI_BROJ,DATUM_SERVISA"
    PK "PROJEKAT_PRODUKCIJE", "SIFRA_PROJEKTA"
    PK "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI"
    PK "TROSAK_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI,RB_TROSKA"
    PK "ANGAZOVANJE_NA_AKTIVNOSTI", "SIFRA_PROJEKTA,RB_AKTIVNOSTI,SIFRA_ZAPOSLENOG"
    PK "REZERVACIJA_OPREME", "SIFRA_PROJEKTA,RB_AKTIVNOSTI,INVENTARSKI_BROJ"
    PK "SIROVI_SNIMAK", "SIFRA_SNIMKA"
    PK "GRAFICKI_I_MUZICKI_ELEMENT", "SIFRA_ELEMENTA"
    PK "PROGRAMSKA_SEMA", "SIFRA_SEME"
    PK "PROGRAMSKA_CELINA", "SIFRA_SEME,RB_CELINE"
    PK "EMISIJA", "SIFRA_EMISIJE"
    PK "TERMIN_EMITOVANJA", "SIFRA_TERMINA"
    PK "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    PK "PRODUCIRANI_SADRZAJ", "SIFRA_SADRZAJA"
    PK "NABAVLJENI_SADRZAJ", "SIFRA_SADRZAJA"
    PK "REKLAMNI_SADRZAJ", "SIFRA_SADRZAJA"
    PK "ZAPIS_O_EMITOVANJU", "SIFRA_TERMINA,RB_EMITOVANJA"
    PK "MONTAZA_SNIMKA", "SIFRA_SADRZAJA,SIFRA_SNIMKA"
    PK "UGRADNJA_ELEMENTA", "SIFRA_SADRZAJA,SIFRA_ELEMENTA"
    PK "SADRZAJ_EMISIJE", "SIFRA_EMISIJE,SIFRA_SADRZAJA"
    PK "PRAVO_KORISCENJA", "BROJ_LICENCE"
    PK "POKRIVENOST_PRAVOM", "BROJ_LICENCE,SIFRA_SADRZAJA"
    PK "POVRATNA_INFO_GLEDALACA", "BROJ_PRIJAVE"
    PK "MERENJE_GLEDANOSTI", "SIFRA_MERENJA"
    PK "MERENJE_EMISIJE", "SIFRA_MERENJA,SIFRA_EMISIJE"
    PK "CENOVNIK_REKL_TERMINA", "SIFRA_CENOVNIKA"
    PK "REKLAMNI_BLOK", "SIFRA_BLOKA"
End Sub

Private Sub Kljucevi2()
    PK "EMITOVANJE_REKLAME", "SIFRA_BLOKA,RB_U_BLOKU"
    PK "KLIJENT", "SIFRA_KLIJENTA"
    PK "OGLASIVAC", "SIFRA_KLIJENTA"
    PK "KUPAC_SADRZAJA", "SIFRA_KLIJENTA"
    PK "UGOVOR", "BROJ_UGOVORA"
    PK "STAVKA_UGOVORA", "BROJ_UGOVORA,RB_STAVKE"
    PK "UGOVOR_O_OGLASAVANJU", "BROJ_UGOVORA"
    PK "UGOVOR_O_PRODAJI_TV_SADRZAJA", "BROJ_UGOVORA"
    PK "UGOVOR_O_NABAVCI", "BROJ_UGOVORA"
    PK "USTUPANJE_SADRZAJA", "BROJ_UGOVORA,SIFRA_SADRZAJA"
    PK "PLAN_NABAVKE", "SIFRA_PLANA"
    PK "ZAHTEV_ZA_NABAVKU", "BROJ_ZAHTEVA"
    PK "STAVKA_PLANA_NABAVKE", "SIFRA_PLANA,RB_STAVKE"
    PK "DOBAVLJAC", "SIFRA_DOBAVLJACA"
    PK "DOBAVLJAC_TV_SADRZAJA", "SIFRA_DOBAVLJACA"
    PK "DOBAVLJAC_OPREME_I_MATERIJALA", "SIFRA_DOBAVLJACA"
    PK "PONUDA_DOBAVLJACA", "BROJ_PONUDE"
    PK "PONUDJENA_STAVKA", "SIFRA_PLANA,RB_STAVKE,BROJ_PONUDE"
    PK "KRITERIJUM_VREDNOVANJA", "SIFRA_KRITERIJUMA"
    PK "OCENA_PONUDE", "BROJ_PONUDE,SIFRA_KRITERIJUMA"
    PK "NARUDZBENICA", "BROJ_NARUDZBENICE"
    PK "STAVKA_NARUDZBENICE", "BROJ_NARUDZBENICE,RB_STAVKE"
    PK "PRIJEMNICA", "BROJ_PRIJEMNICE"
    PK "PRIJEM_STAVKE", "BROJ_PRIJEMNICE,BROJ_NARUDZBENICE,RB_STAVKE"
    PK "REKLAMACIJA", "BROJ_REKLAMACIJE"
    PK "REKLAMIRANA_STAVKA", "BROJ_REKLAMACIJE,BROJ_NARUDZBENICE,RB_STAVKE"
    PK "FAKTURA", "BROJ_FAKTURE"
    PK "STAVKA_FAKTURE", "BROJ_FAKTURE,RB_STAVKE"
    PK "NALOG_ZA_PLACANJE", "BROJ_NALOGA"
End Sub

Private Sub Veze1()
    FK "FK_ORGJED_PODREDJENA", "ORGANIZACIONA_JEDINICA", "SIFRA_NADREDJENE_JEDINICE", "ORGANIZACIONA_JEDINICA", "SIFRA_JEDINICE"
    FK "FK_ZAPOSLENI_RADI_U", "ZAPOSLENI", "SIFRA_JEDINICE", "ORGANIZACIONA_JEDINICA", "SIFRA_JEDINICE"
    FK "FK_UREDNIK_ZAPOSLENI", "UREDNIK", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_NOVINAR_ZAPOSLENI", "NOVINAR_REPORTER", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_TEHOSOB_ZAPOSLENI", "TEHNICKO_OSOBLJE", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_REFERENT_ZAPOSLENI", "REFERENT", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_SERVISERI_ZAPOSLENI", "SERVISERI", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_SNIMOPR_OPREMA", "SNIMATELJSKA_OPREMA", "INVENTARSKI_BROJ", "OPREMA", "INVENTARSKI_BROJ"
    FK "FK_STUDOPR_OPREMA", "STUDIJSKA_I_EMISIONA_OPREMA", "INVENTARSKI_BROJ", "OPREMA", "INVENTARSKI_BROJ"
    FK "FK_AUDIOOPR_STUDOPR", "AUDIO_OPREMA", "INVENTARSKI_BROJ", "STUDIJSKA_I_EMISIONA_OPREMA", "INVENTARSKI_BROJ"
    FK "FK_SVETLOPR_STUDOPR", "SVETLOSNA_OPREMA", "INVENTARSKI_BROJ", "STUDIJSKA_I_EMISIONA_OPREMA", "INVENTARSKI_BROJ"
    FK "FK_ZADUZ_ZAPOSLENI", "ZADUZENJE_OPREME", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_ZADUZ_OPREMA", "ZADUZENJE_OPREME", "INVENTARSKI_BROJ", "OPREMA", "INVENTARSKI_BROJ"
    FK "FK_SERVIS_SERVISERI", "SERVISIRANJE_OPREME", "SIFRA_ZAPOSLENOG", "SERVISERI", "SIFRA_ZAPOSLENOG"
    FK "FK_SERVIS_OPREMA", "SERVISIRANJE_OPREME", "INVENTARSKI_BROJ", "OPREMA", "INVENTARSKI_BROJ"
    FK "FK_PROJEKAT_UREDJUJE", "PROJEKAT_PRODUKCIJE", "SIFRA_UREDNIKA", "UREDNIK", "SIFRA_ZAPOSLENOG"
    FK "FK_PROJEKAT_PROIZVODI", "PROJEKAT_PRODUKCIJE", "SIFRA_EMISIJE", "EMISIJA", "SIFRA_EMISIJE"
    FK "FK_AKTIVNOST_PROJEKAT", "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA", "PROJEKAT_PRODUKCIJE", "SIFRA_PROJEKTA"
    FK "FK_TROSAK_IZAZIVA", "TROSAK_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI", "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI"
    FK "FK_TROSAK_DOKUMENTOVAN", "TROSAK_PRODUKCIJE", "BROJ_FAKTURE", "FAKTURA", "BROJ_FAKTURE"
    FK "FK_ANGAZ_AKTIVNOST", "ANGAZOVANJE_NA_AKTIVNOSTI", "SIFRA_PROJEKTA,RB_AKTIVNOSTI", "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI"
    FK "FK_ANGAZ_ZAPOSLENI", "ANGAZOVANJE_NA_AKTIVNOSTI", "SIFRA_ZAPOSLENOG", "ZAPOSLENI", "SIFRA_ZAPOSLENOG"
    FK "FK_REZERV_AKTIVNOST", "REZERVACIJA_OPREME", "SIFRA_PROJEKTA,RB_AKTIVNOSTI", "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI"
    FK "FK_REZERV_OPREMA", "REZERVACIJA_OPREME", "INVENTARSKI_BROJ", "OPREMA", "INVENTARSKI_BROJ"
    FK "FK_SNIMAK_SNIMLJEN_NA", "SIROVI_SNIMAK", "SIFRA_PROJEKTA,RB_AKTIVNOSTI", "AKTIVNOST_PRODUKCIJE", "SIFRA_PROJEKTA,RB_AKTIVNOSTI"
    FK "FK_PSEMA_ODOBRAVA", "PROGRAMSKA_SEMA", "SIFRA_UREDNIKA", "UREDNIK", "SIFRA_ZAPOSLENOG"
    FK "FK_PCELINA_PSEMA", "PROGRAMSKA_CELINA", "SIFRA_SEME", "PROGRAMSKA_SEMA", "SIFRA_SEME"
    FK "FK_TERMIN_OBUHVATA", "TERMIN_EMITOVANJA", "SIFRA_SEME,RB_CELINE", "PROGRAMSKA_CELINA", "SIFRA_SEME,RB_CELINE"
    FK "FK_TERMIN_PLANIRANA", "TERMIN_EMITOVANJA", "SIFRA_EMISIJE", "EMISIJA", "SIFRA_EMISIJE"
    FK "FK_MSPROD_MSADRZAJ", "PRODUCIRANI_SADRZAJ", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
End Sub

Private Sub Veze2()
    FK "FK_MSNAB_MSADRZAJ", "NABAVLJENI_SADRZAJ", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_MSNAB_NABAVLJEN_PO", "NABAVLJENI_SADRZAJ", "BROJ_UGOVORA", "UGOVOR_O_NABAVCI", "BROJ_UGOVORA"
    FK "FK_MSREK_MSADRZAJ", "REKLAMNI_SADRZAJ", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_MSREK_DOSTAVLJA", "REKLAMNI_SADRZAJ", "SIFRA_OGLASIVACA", "OGLASIVAC", "SIFRA_KLIJENTA"
    FK "FK_ZAPISEM_REALIZOVAN", "ZAPIS_O_EMITOVANJU", "SIFRA_TERMINA", "TERMIN_EMITOVANJA", "SIFRA_TERMINA"
    FK "FK_ZAPISEM_EVIDENTIRA", "ZAPIS_O_EMITOVANJU", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_MONTAZA_MSADRZAJ", "MONTAZA_SNIMKA", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_MONTAZA_SNIMAK", "MONTAZA_SNIMKA", "SIFRA_SNIMKA", "SIROVI_SNIMAK", "SIFRA_SNIMKA"
    FK "FK_UGRADNJA_MSADRZAJ", "UGRADNJA_ELEMENTA", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_UGRADNJA_ELEMENT", "UGRADNJA_ELEMENTA", "SIFRA_ELEMENTA", "GRAFICKI_I_MUZICKI_ELEMENT", "SIFRA_ELEMENTA"
    FK "FK_SADREM_EMISIJA", "SADRZAJ_EMISIJE", "SIFRA_EMISIJE", "EMISIJA", "SIFRA_EMISIJE"
    FK "FK_SADREM_MSADRZAJ", "SADRZAJ_EMISIJE", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_POKRIV_PRAVO", "POKRIVENOST_PRAVOM", "BROJ_LICENCE", "PRAVO_KORISCENJA", "BROJ_LICENCE"
    FK "FK_POKRIV_MSADRZAJ", "POKRIVENOST_PRAVOM", "SIFRA_SADRZAJA", "MEDIJSKI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_POVRINF_EMISIJA", "POVRATNA_INFO_GLEDALACA", "SIFRA_EMISIJE", "EMISIJA", "SIFRA_EMISIJE"
    FK "FK_MERENJEEM_MERENJE", "MERENJE_EMISIJE", "SIFRA_MERENJA", "MERENJE_GLEDANOSTI", "SIFRA_MERENJA"
    FK "FK_MERENJEEM_EMISIJA", "MERENJE_EMISIJE", "SIFRA_EMISIJE", "EMISIJA", "SIFRA_EMISIJE"
    FK "FK_RBLOK_ZAKUPLJEN_U", "REKLAMNI_BLOK", "SIFRA_TERMINA", "TERMIN_EMITOVANJA", "SIFRA_TERMINA"
    FK "FK_RBLOK_TARIFIRAN", "REKLAMNI_BLOK", "SIFRA_CENOVNIKA", "CENOVNIK_REKL_TERMINA", "SIFRA_CENOVNIKA"
    FK "FK_EMREK_SADRZI_SPOT", "EMITOVANJE_REKLAME", "SIFRA_BLOKA", "REKLAMNI_BLOK", "SIFRA_BLOKA"
    FK "FK_EMREK_PRIKAZUJE", "EMITOVANJE_REKLAME", "SIFRA_SADRZAJA", "REKLAMNI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_EMREK_UGOVOREN", "EMITOVANJE_REKLAME", "BROJ_UGOVORA,RB_STAVKE_UGOVORA", "STAVKA_UGOVORA", "BROJ_UGOVORA,RB_STAVKE"
    FK "FK_OGLASIVAC_KLIJENT", "OGLASIVAC", "SIFRA_KLIJENTA", "KLIJENT", "SIFRA_KLIJENTA"
    FK "FK_KUPACSAD_KLIJENT", "KUPAC_SADRZAJA", "SIFRA_KLIJENTA", "KLIJENT", "SIFRA_KLIJENTA"
    FK "FK_UGOVOR_SKLAPA", "UGOVOR", "SIFRA_KLIJENTA", "KLIJENT", "SIFRA_KLIJENTA"
    FK "FK_STUGOV_PRECIZIRA", "STAVKA_UGOVORA", "BROJ_UGOVORA", "UGOVOR", "BROJ_UGOVORA"
    FK "FK_UGOGL_UGOVOR", "UGOVOR_O_OGLASAVANJU", "BROJ_UGOVORA", "UGOVOR", "BROJ_UGOVORA"
    FK "FK_UGPROD_UGOVOR", "UGOVOR_O_PRODAJI_TV_SADRZAJA", "BROJ_UGOVORA", "UGOVOR", "BROJ_UGOVORA"
    FK "FK_UGNAB_UGOVOR", "UGOVOR_O_NABAVCI", "BROJ_UGOVORA", "UGOVOR", "BROJ_UGOVORA"
    FK "FK_UGNAB_UGOVARA", "UGOVOR_O_NABAVCI", "SIFRA_DOBAVLJACA", "DOBAVLJAC", "SIFRA_DOBAVLJACA"
End Sub

Private Sub Veze3()
    FK "FK_USTUP_UGPROD", "USTUPANJE_SADRZAJA", "BROJ_UGOVORA", "UGOVOR_O_PRODAJI_TV_SADRZAJA", "BROJ_UGOVORA"
    FK "FK_USTUP_MSPROD", "USTUPANJE_SADRZAJA", "SIFRA_SADRZAJA", "PRODUCIRANI_SADRZAJ", "SIFRA_SADRZAJA"
    FK "FK_ZAHNAB_PODNOSI", "ZAHTEV_ZA_NABAVKU", "SIFRA_JEDINICE", "ORGANIZACIONA_JEDINICA", "SIFRA_JEDINICE"
    FK "FK_ZAHNAB_UVRSTEN_U", "ZAHTEV_ZA_NABAVKU", "SIFRA_PLANA", "PLAN_NABAVKE", "SIFRA_PLANA"
    FK "FK_STPLAN_PLAN", "STAVKA_PLANA_NABAVKE", "SIFRA_PLANA", "PLAN_NABAVKE", "SIFRA_PLANA"
    FK "FK_DOBTVSAD_DOBAVLJAC", "DOBAVLJAC_TV_SADRZAJA", "SIFRA_DOBAVLJACA", "DOBAVLJAC", "SIFRA_DOBAVLJACA"
    FK "FK_DOBOPR_DOBAVLJAC", "DOBAVLJAC_OPREME_I_MATERIJALA", "SIFRA_DOBAVLJACA", "DOBAVLJAC", "SIFRA_DOBAVLJACA"
    FK "FK_PONUDA_DOSTAVIO", "PONUDA_DOBAVLJACA", "SIFRA_DOBAVLJACA", "DOBAVLJAC", "SIFRA_DOBAVLJACA"
    FK "FK_PONSTAV_STPLAN", "PONUDJENA_STAVKA", "SIFRA_PLANA,RB_STAVKE", "STAVKA_PLANA_NABAVKE", "SIFRA_PLANA,RB_STAVKE"
    FK "FK_PONSTAV_PONUDA", "PONUDJENA_STAVKA", "BROJ_PONUDE", "PONUDA_DOBAVLJACA", "BROJ_PONUDE"
    FK "FK_OCENA_PONUDA", "OCENA_PONUDE", "BROJ_PONUDE", "PONUDA_DOBAVLJACA", "BROJ_PONUDE"
    FK "FK_OCENA_KRITERIJUM", "OCENA_PONUDE", "SIFRA_KRITERIJUMA", "KRITERIJUM_VREDNOVANJA", "SIFRA_KRITERIJUMA"
    FK "FK_NARUDZB_NARUCENO_OD", "NARUDZBENICA", "SIFRA_DOBAVLJACA", "DOBAVLJAC", "SIFRA_DOBAVLJACA"
    FK "FK_STNARUD_NARUDZBENICA", "STAVKA_NARUDZBENICE", "BROJ_NARUDZBENICE", "NARUDZBENICA", "BROJ_NARUDZBENICE"
    FK "FK_PRIJEMN_PRACENA", "PRIJEMNICA", "BROJ_NARUDZBENICE", "NARUDZBENICA", "BROJ_NARUDZBENICE"
    FK "FK_PRIJEMN_FAKTURISANA", "PRIJEMNICA", "BROJ_FAKTURE", "FAKTURA", "BROJ_FAKTURE"
    FK "FK_PRIJSTAV_PRIJEMNICA", "PRIJEM_STAVKE", "BROJ_PRIJEMNICE", "PRIJEMNICA", "BROJ_PRIJEMNICE"
    FK "FK_PRIJSTAV_STNARUD", "PRIJEM_STAVKE", "BROJ_NARUDZBENICE,RB_STAVKE", "STAVKA_NARUDZBENICE", "BROJ_NARUDZBENICE,RB_STAVKE"
    FK "FK_REKLAMAC_PRIJEMNICA", "REKLAMACIJA", "BROJ_PRIJEMNICE", "PRIJEMNICA", "BROJ_PRIJEMNICE"
    FK "FK_REKSTAV_REKLAMACIJA", "REKLAMIRANA_STAVKA", "BROJ_REKLAMACIJE", "REKLAMACIJA", "BROJ_REKLAMACIJE"
    FK "FK_REKSTAV_STNARUD", "REKLAMIRANA_STAVKA", "BROJ_NARUDZBENICE,RB_STAVKE", "STAVKA_NARUDZBENICE", "BROJ_NARUDZBENICE,RB_STAVKE"
    FK "FK_FAKTURA_IZDATA_PO", "FAKTURA", "BROJ_UGOVORA", "UGOVOR", "BROJ_UGOVORA"
    FK "FK_STFAKT_FAKTURA", "STAVKA_FAKTURE", "BROJ_FAKTURE", "FAKTURA", "BROJ_FAKTURE"
    FK "FK_NALOG_PLACENA", "NALOG_ZA_PLACANJE", "BROJ_FAKTURE", "FAKTURA", "BROJ_FAKTURE"
End Sub

Private Sub Upiti1()
    Dim s As String
    ' qryProgramskaSema
    s = "SELECT PS.NAZIV_SEME, PS.SEZONA, PC.RB_CELINE, PC.NAZIV_CELINE, PC.TIP_CELINE, PC.DATUM AS DATUM_CELINE, TE.VREME_POCETKA, E.NAZIV_EMISIJE, E.ZANR, TE.TRAJANJE_TERMINA, "
    s = s & "TE.TIP_TERMINA, TE.ZONA_GLEDANOSTI, TE.REDNI_BROJ_REPRIZE, TE.STATUS_TERMINA FROM ((PROGRAMSKA_SEMA AS PS INNER JOIN PROGRAMSKA_CELINA AS PC ON PS.SIFRA_SEME = PC.SIFRA_SEME) INNER "
    s = s & "JOIN TERMIN_EMITOVANJA AS TE ON (PC.SIFRA_SEME = TE.SIFRA_SEME) AND (PC.RB_CELINE = TE.RB_CELINE)) INNER JOIN EMISIJA AS E ON TE.SIFRA_EMISIJE = E.SIFRA_EMISIJE ORDER BY "
    s = s & "PC.RB_CELINE, TE.DATUM, TE.VREME_POCETKA; "
    NapraviUpit "qryProgramskaSema", s
    ' qryPlayoutLog
    s = "PARAMETERS [Unesite datum od:] DateTime, [Unesite datum do:] DateTime; SELECT TE.DATUM, ZE.STVARNO_VREME_POCETKA, E.NAZIV_EMISIJE, MS.NAZIV_SADRZAJA, TE.TRAJANJE_TERMINA, "
    s = s & "ZE.STVARNO_TRAJANJE, (ZE.STVARNO_TRAJANJE - TE.TRAJANJE_TERMINA) AS ODSTUPANJE, ZE.STATUS_REALIZACIJE, PK.BROJ_LICENCE, PK.VRSTA_PRAVA, ZE.OPERATER_EMITOVANJA, "
    s = s & "ZE.NAPOMENA_O_SMETNJAMA FROM ((((ZAPIS_O_EMITOVANJU AS ZE INNER JOIN TERMIN_EMITOVANJA AS TE ON ZE.SIFRA_TERMINA = TE.SIFRA_TERMINA) INNER JOIN EMISIJA AS E ON TE.SIFRA_EMISIJE = "
    s = s & "E.SIFRA_EMISIJE) INNER JOIN MEDIJSKI_SADRZAJ AS MS ON ZE.SIFRA_SADRZAJA = MS.SIFRA_SADRZAJA) LEFT JOIN POKRIVENOST_PRAVOM AS PP ON MS.SIFRA_SADRZAJA = PP.SIFRA_SADRZAJA) LEFT JOIN "
    s = s & "PRAVO_KORISCENJA AS PK ON PP.BROJ_LICENCE = PK.BROJ_LICENCE WHERE TE.DATUM BETWEEN [Unesite datum od:] AND [Unesite datum do:] ORDER BY TE.DATUM, ZE.STVARNO_VREME_POCETKA; "
    NapraviUpit "qryPlayoutLog", s
    ' qryGledanostPoZanru
    s = "SELECT E.ZANR, Round(Avg(ME.OSTVARENI_RATING),2) AS PROSECAN_REJTING FROM EMISIJA AS E INNER JOIN MERENJE_EMISIJE AS ME ON E.SIFRA_EMISIJE = ME.SIFRA_EMISIJE GROUP BY E.ZANR ORDER "
    s = s & "BY Avg(ME.OSTVARENI_RATING) DESC; "
    NapraviUpit "qryGledanostPoZanru", s
    ' qryGledanostEmisija
    s = "SELECT E.NAZIV_EMISIJE, E.ZANR, Count(ME.SIFRA_MERENJA) AS BROJ_MERENJA, Round(Avg(ME.OSTVARENI_RATING),2) AS PROSECAN_REJTING, Round(Avg(ME.UDEO_U_TERMINU),2) AS PROSECAN_UDEO, "
    s = s & "Round(Avg(MG.BROJ_GLEDALACA),0) AS PROSECAN_BROJ_GLEDALACA, Round(Avg(MG.PROSECNO_GLEDANJE),0) AS PROSECNO_GLEDANJE FROM (EMISIJA AS E INNER JOIN MERENJE_EMISIJE AS ME ON "
    s = s & "E.SIFRA_EMISIJE = ME.SIFRA_EMISIJE) INNER JOIN MERENJE_GLEDANOSTI AS MG ON ME.SIFRA_MERENJA = MG.SIFRA_MERENJA GROUP BY E.NAZIV_EMISIJE, E.ZANR ORDER BY Avg(ME.OSTVARENI_RATING) "
    s = s & "DESC; "
    NapraviUpit "qryGledanostEmisija", s
    ' qryTroskoviProjekta
    s = "SELECT PP.SIFRA_PROJEKTA, PP.NAZIV_PROJEKTA, PP.VRSTA_PRODUKCIJE, PP.ODOBREN_BUDZET, PP.STATUS_PROJEKTA, AP.RB_AKTIVNOSTI, AP.NAZIV_AKTIVNOSTI, AP.VRSTA_AKTIVNOSTI, "
    s = s & "AP.LOKACIJA_SNIMANJA, AP.STATUS_AKTIVNOSTI, TP.RB_TROSKA, TP.VRSTA_TROSKA, TP.OPIS_TROSKA, TP.DATUM_NASTANKA, TP.IZNOS, TP.BROJ_FAKTURE FROM (PROJEKAT_PRODUKCIJE AS PP INNER JOIN "
    s = s & "AKTIVNOST_PRODUKCIJE AS AP ON PP.SIFRA_PROJEKTA = AP.SIFRA_PROJEKTA) LEFT JOIN TROSAK_PRODUKCIJE AS TP ON (AP.SIFRA_PROJEKTA = TP.SIFRA_PROJEKTA) AND (AP.RB_AKTIVNOSTI = "
    s = s & "TP.RB_AKTIVNOSTI) ORDER BY PP.SIFRA_PROJEKTA, AP.RB_AKTIVNOSTI, TP.RB_TROSKA; "
    NapraviUpit "qryTroskoviProjekta", s
End Sub

Private Sub Upiti2()
    Dim s As String
    ' qryAngazovanje
    s = "SELECT Z.PREZIME & "" "" & Z.IME AS ZAPOSLENI_NAZIV, Z.RADNO_MESTO, PP.NAZIV_PROJEKTA, AP.NAZIV_AKTIVNOSTI, AN.ULOGA_NA_SNIMANJU, AN.DATUM_OD, AN.DATUM_DO, AN.BROJ_ANGAZOVANIH_SATI "
    s = s & "FROM ((ANGAZOVANJE_NA_AKTIVNOSTI AS AN INNER JOIN ZAPOSLENI AS Z ON AN.SIFRA_ZAPOSLENOG = Z.SIFRA_ZAPOSLENOG) INNER JOIN AKTIVNOST_PRODUKCIJE AS AP ON (AN.SIFRA_PROJEKTA = "
    s = s & "AP.SIFRA_PROJEKTA) AND (AN.RB_AKTIVNOSTI = AP.RB_AKTIVNOSTI)) INNER JOIN PROJEKAT_PRODUKCIJE AS PP ON AP.SIFRA_PROJEKTA = PP.SIFRA_PROJEKTA ORDER BY Z.PREZIME, Z.IME, AN.DATUM_OD; "
    NapraviUpit "qryAngazovanje", s
    ' qryZaduzenjeOpreme
    s = "SELECT O.INVENTARSKI_BROJ, O.NAZIV_OPREME, O.MODEL_OPREME, PP.NAZIV_PROJEKTA, AP.NAZIV_AKTIVNOSTI, RO.DATUM_REZERVACIJE, RO.TRAJANJE_ZADUZENJA FROM ((REZERVACIJA_OPREME AS RO INNER "
    s = s & "JOIN OPREMA AS O ON RO.INVENTARSKI_BROJ = O.INVENTARSKI_BROJ) INNER JOIN AKTIVNOST_PRODUKCIJE AS AP ON (RO.SIFRA_PROJEKTA = AP.SIFRA_PROJEKTA) AND (RO.RB_AKTIVNOSTI = "
    s = s & "AP.RB_AKTIVNOSTI)) INNER JOIN PROJEKAT_PRODUKCIJE AS PP ON AP.SIFRA_PROJEKTA = PP.SIFRA_PROJEKTA ORDER BY O.INVENTARSKI_BROJ, RO.DATUM_REZERVACIJE; "
    NapraviUpit "qryZaduzenjeOpreme", s
    ' qryKarticaOglasivaca
    s = "PARAMETERS [Unesite ~sifru ogla~siva~ca:] Text ( 255 ); SELECT K.SIFRA_KLIJENTA, K.NAZIV_KLIJENTA, K.PIB, K.KONTAKT_OSOBA, OG.BRANSA, U.BROJ_UGOVORA, U.DATUM_SKLAPANJA, U.VAZI_OD, "
    s = s & "U.VAZI_DO, U.STATUS_UGOVORA, SU.RB_STAVKE, SU.OPIS_STAVKE, SU.KOLICINA_SEKUNDE, SU.JEDINICNA_CENA, SU.POPUST, SU.VREDNOST_STAVKE, ER.DATUM_EMITOVANJA, ER.VREME_EMITOVANJA, "
    s = s & "ER.SIFRA_BLOKA, ER.TRAJANJE_SPOTA, ER.NAPLACENI_IZNOS, ER.STATUS_NAPLATE FROM ((((KLIJENT AS K INNER JOIN OGLASIVAC AS OG ON K.SIFRA_KLIJENTA = OG.SIFRA_KLIJENTA) INNER JOIN UGOVOR "
    s = s & "AS U ON K.SIFRA_KLIJENTA = U.SIFRA_KLIJENTA) INNER JOIN UGOVOR_O_OGLASAVANJU AS UO ON U.BROJ_UGOVORA = UO.BROJ_UGOVORA) INNER JOIN STAVKA_UGOVORA AS SU ON U.BROJ_UGOVORA = "
    s = s & "SU.BROJ_UGOVORA) LEFT JOIN EMITOVANJE_REKLAME AS ER ON (SU.BROJ_UGOVORA = ER.BROJ_UGOVORA) AND (SU.RB_STAVKE = ER.RB_STAVKE_UGOVORA) WHERE K.SIFRA_KLIJENTA = [Unesite ~sifru "
    s = s & "ogla~siva~ca:] ORDER BY U.BROJ_UGOVORA, SU.RB_STAVKE, ER.DATUM_EMITOVANJA; "
    NapraviUpit "qryKarticaOglasivaca", s
    ' qryPlanNabavke
    s = "SELECT PN.SIFRA_PLANA, PN.GODINA_PLANA, SP.RB_STAVKE, SP.OPIS_ARTIKLA, SP.KOLICINA, SP.JEDINICA_MERE, SP.PROCENJENA_CENA, SP.PLANIRANI_KVARTAL, ZN.BROJ_ZAHTEVA, ZN.STATUS_ZAHTEVA, "
    s = s & "NR.BROJ_NARUDZBENICE, NR.UKUPAN_IZNOS, (Nz(NR.UKUPAN_IZNOS,0) - SP.PROCENJENA_CENA) AS ODSTUPANJE FROM (((PLAN_NABAVKE AS PN INNER JOIN STAVKA_PLANA_NABAVKE AS SP ON PN.SIFRA_PLANA "
    s = s & "= SP.SIFRA_PLANA) LEFT JOIN ZAHTEV_ZA_NABAVKU AS ZN ON PN.SIFRA_PLANA = ZN.SIFRA_PLANA) LEFT JOIN PONUDJENA_STAVKA AS PS ON (SP.SIFRA_PLANA = PS.SIFRA_PLANA) AND (SP.RB_STAVKE = "
    s = s & "PS.RB_STAVKE)) LEFT JOIN (PONUDA_DOBAVLJACA AS PD INNER JOIN NARUDZBENICA AS NR ON PD.SIFRA_DOBAVLJACA = NR.SIFRA_DOBAVLJACA) ON PS.BROJ_PONUDE = PD.BROJ_PONUDE AND "
    s = s & "PD.STATUS_PONUDE = ""Izabrana"" ORDER BY SP.RB_STAVKE; "
    NapraviUpit "qryPlanNabavke", s
    ' qryVrednovanjePonuda
    s = "SELECT PD.BROJ_PONUDE, D.NAZIV_DOBAVLJACA, PD.UKUPNA_CENA, PD.ROK_ISPORUKE, PD.USLOVI_PLACANJA, KV.NAZIV_KRITERIJUMA, OP.BROJ_BODOVA, OP.KOMENTAR_OCENE, PD.UKUPNO_BODOVA, "
    s = s & "PD.STATUS_PONUDE FROM ((PONUDA_DOBAVLJACA AS PD INNER JOIN DOBAVLJAC AS D ON PD.SIFRA_DOBAVLJACA = D.SIFRA_DOBAVLJACA) INNER JOIN OCENA_PONUDE AS OP ON PD.BROJ_PONUDE = "
    s = s & "OP.BROJ_PONUDE) INNER JOIN KRITERIJUM_VREDNOVANJA AS KV ON OP.SIFRA_KRITERIJUMA = KV.SIFRA_KRITERIJUMA ORDER BY PD.BROJ_PONUDE, KV.SIFRA_KRITERIJUMA; "
    NapraviUpit "qryVrednovanjePonuda", s
End Sub

Private Sub Upiti3()
    Dim s As String
    ' qryPravaKoriscenja
    s = "SELECT PK.BROJ_LICENCE, PK.VRSTA_PRAVA, PK.NOSILAC_PRAVA, PK.TERITORIJA, PK.DATUM_OD, PK.DATUM_DO, DateDiff(""d"", Date(), PK.DATUM_DO) AS DANA_DO_ISTEKA, PK.DOZVOLJENO_EMITOVANJA, "
    s = s & "PK.ISKORISCENO_EMITOVANJA, (PK.DOZVOLJENO_EMITOVANJA - PK.ISKORISCENO_EMITOVANJA) AS PREOSTALO_EMITOVANJA, MS.NAZIV_SADRZAJA, PP.OBLAST_POKRIVENOSTI, IIf(PK.DATUM_DO < Date(), "
    s = s & """Isteklo"", IIf(PK.ISKORISCENO_EMITOVANJA >= PK.DOZVOLJENO_EMITOVANJA, ""Iskori~sceno"", IIf(DateDiff(""d"", Date(), PK.DATUM_DO) <= 30, ""Uskoro isti~ce"", ""Va~ze~ce""))) AS STATUS_PRAVA "
    s = s & "FROM (PRAVO_KORISCENJA AS PK LEFT JOIN POKRIVENOST_PRAVOM AS PP ON PK.BROJ_LICENCE = PP.BROJ_LICENCE) LEFT JOIN MEDIJSKI_SADRZAJ AS MS ON PP.SIFRA_SADRZAJA = MS.SIFRA_SADRZAJA "
    s = s & "ORDER BY PK.DATUM_DO; "
    NapraviUpit "qryPravaKoriscenja", s
    ' qryEmisijePregled
    s = "SELECT E.SIFRA_EMISIJE, E.NAZIV_EMISIJE, E.ZANR, E.PREDVIDJENO_TRAJANJE, E.STATUS_EMISIJE FROM EMISIJA AS E ORDER BY E.NAZIV_EMISIJE; "
    NapraviUpit "qryEmisijePregled", s
    ' qryOglasivaciPregled
    s = "SELECT K.SIFRA_KLIJENTA, K.NAZIV_KLIJENTA, K.PIB, OG.BRANSA, OG.GODISNJI_BUDZET FROM KLIJENT AS K INNER JOIN OGLASIVAC AS OG ON K.SIFRA_KLIJENTA = OG.SIFRA_KLIJENTA ORDER BY "
    s = s & "K.NAZIV_KLIJENTA; "
    NapraviUpit "qryOglasivaciPregled", s
End Sub

Private Sub DemoPodaci1()
    Ubaci "INSERT INTO [ORGANIZACIONA_JEDINICA] ([SIFRA_JEDINICE],[SIFRA_NADREDJENE_JEDINICE],[NAZIV_JEDINICE],[TIP_JEDINICE],[DATUM_OSNIVANJA]) VALUES ('OJ-01',Null,'Uprava stanice','Uprava',#3/1/2004#);"
    Ubaci "INSERT INTO [ORGANIZACIONA_JEDINICA] ([SIFRA_JEDINICE],[SIFRA_NADREDJENE_JEDINICE],[NAZIV_JEDINICE],[TIP_JEDINICE],[DATUM_OSNIVANJA]) VALUES ('OJ-02','OJ-01','Redakcija programa','Redakcija',#3/1/2004#);"
    Ubaci T("INSERT INTO [ORGANIZACIONA_JEDINICA] ([SIFRA_JEDINICE],[SIFRA_NADREDJENE_JEDINICE],[NAZIV_JEDINICE],[TIP_JEDINICE],[DATUM_OSNIVANJA]) VALUES ('OJ-03','OJ-01','Tehni~cka slu~zba','Tehnika',#3/1/2004#);")
    Ubaci "INSERT INTO [ORGANIZACIONA_JEDINICA] ([SIFRA_JEDINICE],[SIFRA_NADREDJENE_JEDINICE],[NAZIV_JEDINICE],[TIP_JEDINICE],[DATUM_OSNIVANJA]) VALUES ('OJ-04','OJ-01','Marketing i prodaja','Komercijala',#5/1/2006#);"
    Ubaci T("INSERT INTO [ORGANIZACIONA_JEDINICA] ([SIFRA_JEDINICE],[SIFRA_NADREDJENE_JEDINICE],[NAZIV_JEDINICE],[TIP_JEDINICE],[DATUM_OSNIVANJA]) VALUES ('OJ-05','OJ-01','Slu~zba nabavke','Nabavka',#5/1/2006#);")
    Ubaci T("INSERT INTO [ORGANIZACIONA_JEDINICA] ([SIFRA_JEDINICE],[SIFRA_NADREDJENE_JEDINICE],[NAZIV_JEDINICE],[TIP_JEDINICE],[DATUM_OSNIVANJA]) VALUES ('OJ-06','OJ-01','Finansijska slu~zba','Finansije',#5/1/2006#);")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-001','OJ-02','0101985800012','Milica','Jovanovi~k','Urednik programa',#2/1/2012#,142000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-002','OJ-02','1203979800031','Dragan','Stankovi~k','Glavni urednik',#9/15/2008#,168000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-003','OJ-02','2207990805044','Ana','Ili~k','Novinar',#4/1/2018#,96000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-004','OJ-02','0512988800017','Marko','Petrovi~k','Reporter',#10/1/2016#,92000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-005','OJ-03','1809983800022','Nenad','Kova~c','Snimatelj',#6/1/2014#,88000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-006','OJ-03','3001992805019','Jelena','Mari~k','Ton majstor',#3/1/2019#,84000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-007','OJ-03','1104980800026','Vladimir','~Duri~k','Operater emitovanja',#1/15/2011#,90000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-008','OJ-05','2506987800033','Nikola','Anti~k','Referent nabavke',#8/1/2015#,95000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-009','OJ-04','0703991800011','Stefan','Peri~k','Referent marketinga',#2/1/2017#,98000,'Aktivan');")
    Ubaci T("INSERT INTO [ZAPOSLENI] ([SIFRA_ZAPOSLENOG],[SIFRA_JEDINICE],[JMBG],[IME],[PREZIME],[RADNO_MESTO],[DATUM_ZAPOSLENJA],[OSNOVNA_ZARADA],[STATUS_ZAPOSLENJA]) VALUES ('ZAP-010','OJ-03','1502975800044','Goran','Luki~k','Serviser opreme',#5/1/2010#,86000,'Aktivan');")
    Ubaci "INSERT INTO [UREDNIK] ([SIFRA_ZAPOSLENOG],[NIVO_OVLASCENJA],[REDAKCIJA]) VALUES ('ZAP-001','Urednik emisije','Dokumentarni program');"
    Ubaci "INSERT INTO [UREDNIK] ([SIFRA_ZAPOSLENOG],[NIVO_OVLASCENJA],[REDAKCIJA]) VALUES ('ZAP-002','Glavni urednik','Informativni program');"
    Ubaci T("INSERT INTO [NOVINAR_REPORTER] ([SIFRA_ZAPOSLENOG],[OBLAST_IZVESTAVANJA],[BROJ_NOVINARSKE_LEGITIM]) VALUES ('ZAP-003','Unutra~snja politika','NL-2018-114');")
    Ubaci "INSERT INTO [NOVINAR_REPORTER] ([SIFRA_ZAPOSLENOG],[OBLAST_IZVESTAVANJA],[BROJ_NOVINARSKE_LEGITIM]) VALUES ('ZAP-004','Ekologija i regioni','NL-2016-087');"
    Ubaci "INSERT INTO [TEHNICKO_OSOBLJE] ([SIFRA_ZAPOSLENOG],[SPECIJALIZACIJA],[TIP_EKIPE]) VALUES ('ZAP-005','Kamera','Terenska');"
    Ubaci "INSERT INTO [TEHNICKO_OSOBLJE] ([SIFRA_ZAPOSLENOG],[SPECIJALIZACIJA],[TIP_EKIPE]) VALUES ('ZAP-006','Ton','Terenska');"
    Ubaci "INSERT INTO [TEHNICKO_OSOBLJE] ([SIFRA_ZAPOSLENOG],[SPECIJALIZACIJA],[TIP_EKIPE]) VALUES ('ZAP-007','Emitovanje','Studijska');"
    Ubaci "INSERT INTO [REFERENT] ([SIFRA_ZAPOSLENOG],[TIP_REFERENTA],[NIVO_OVLASCENJA]) VALUES ('ZAP-008','Nabavka','Do 5.000.000 RSD');"
    Ubaci "INSERT INTO [REFERENT] ([SIFRA_ZAPOSLENOG],[TIP_REFERENTA],[NIVO_OVLASCENJA]) VALUES ('ZAP-009','Marketing','Do 3.000.000 RSD');"
    Ubaci T("INSERT INTO [SERVISERI] ([SIFRA_ZAPOSLENOG],[LICENCA]) VALUES ('ZAP-010','Ovla~s~keni serviser Sony/Canon');")
    Ubaci "INSERT INTO [OPREMA] ([INVENTARSKI_BROJ],[NAZIV_OPREME],[MODEL_OPREME],[PROIZVODJAC],[STATUS_OPREME],[DATUM_NABAVKE],[GARANCIJA_DO],[NABAVNA_VREDNOST]) VALUES ('INV-0101','Studijska kamera','PXW-Z750','Sony','U upotrebi',#4/12/2023#,#4/12/2026#,1850000);"
    Ubaci "INSERT INTO [OPREMA] ([INVENTARSKI_BROJ],[NAZIV_OPREME],[MODEL_OPREME],[PROIZVODJAC],[STATUS_OPREME],[DATUM_NABAVKE],[GARANCIJA_DO],[NABAVNA_VREDNOST]) VALUES ('INV-0102','Studijska kamera','PXW-Z750','Sony','U upotrebi',#4/12/2023#,#4/12/2026#,1850000);"
    Ubaci T("INSERT INTO [OPREMA] ([INVENTARSKI_BROJ],[NAZIV_OPREME],[MODEL_OPREME],[PROIZVODJAC],[STATUS_OPREME],[DATUM_NABAVKE],[GARANCIJA_DO],[NABAVNA_VREDNOST]) VALUES ('INV-0103','Reporta~zna kamera','XF605','Canon','U upotrebi',#9/3/2024#,#9/3/2027#,640000);")
    Ubaci T("INSERT INTO [OPREMA] ([INVENTARSKI_BROJ],[NAZIV_OPREME],[MODEL_OPREME],[PROIZVODJAC],[STATUS_OPREME],[DATUM_NABAVKE],[GARANCIJA_DO],[NABAVNA_VREDNOST]) VALUES ('INV-0104','Be~zi~cni mikrofonski set','UWP-D21','Sony','U upotrebi',#2/20/2024#,#2/20/2026#,145000);")
    Ubaci "INSERT INTO [OPREMA] ([INVENTARSKI_BROJ],[NAZIV_OPREME],[MODEL_OPREME],[PROIZVODJAC],[STATUS_OPREME],[DATUM_NABAVKE],[GARANCIJA_DO],[NABAVNA_VREDNOST]) VALUES ('INV-0105','LED panel rasvete','Forza 500B','Nanlite','U upotrebi',#6/10/2024#,#6/10/2026#,210000);"
    Ubaci "INSERT INTO [OPREMA] ([INVENTARSKI_BROJ],[NAZIV_OPREME],[MODEL_OPREME],[PROIZVODJAC],[STATUS_OPREME],[DATUM_NABAVKE],[GARANCIJA_DO],[NABAVNA_VREDNOST]) VALUES ('INV-0106','Miks pult','Wing','Behringer','Na servisu',#11/5/2022#,#11/5/2024#,380000);"
    Ubaci T("INSERT INTO [SNIMATELJSKA_OPREMA] ([INVENTARSKI_BROJ],[TIP_MEMORIJSKOG_SKLADISTA],[REZOLUCIJA],[TIP_KAMERE]) VALUES ('INV-0103','CFexpress','4K UHD','Reporta~zna');")
    Ubaci "INSERT INTO [STUDIJSKA_I_EMISIONA_OPREMA] ([INVENTARSKI_BROJ],[LOKACIJA_U_STUDIJU]) VALUES ('INV-0101','Studio 1');"
    Ubaci "INSERT INTO [STUDIJSKA_I_EMISIONA_OPREMA] ([INVENTARSKI_BROJ],[LOKACIJA_U_STUDIJU]) VALUES ('INV-0102','Studio 2');"
    Ubaci "INSERT INTO [STUDIJSKA_I_EMISIONA_OPREMA] ([INVENTARSKI_BROJ],[LOKACIJA_U_STUDIJU]) VALUES ('INV-0104','Studio 2');"
    Ubaci "INSERT INTO [STUDIJSKA_I_EMISIONA_OPREMA] ([INVENTARSKI_BROJ],[LOKACIJA_U_STUDIJU]) VALUES ('INV-0105','Studio 2');"
    Ubaci T("INSERT INTO [STUDIJSKA_I_EMISIONA_OPREMA] ([INVENTARSKI_BROJ],[LOKACIJA_U_STUDIJU]) VALUES ('INV-0106','Re~zija 1');")
    Ubaci T("INSERT INTO [AUDIO_OPREMA] ([INVENTARSKI_BROJ],[TIP],[FREKVENCIJA]) VALUES ('INV-0104','Be~zi~cni mikrofon','566-608 MHz');")
    Ubaci "INSERT INTO [AUDIO_OPREMA] ([INVENTARSKI_BROJ],[TIP],[FREKVENCIJA]) VALUES ('INV-0106','Miks pult','20 Hz - 20 kHz');"
    Ubaci "INSERT INTO [SVETLOSNA_OPREMA] ([INVENTARSKI_BROJ],[SNAGA],[TIP_SVETLOSTI]) VALUES ('INV-0105','500 W','LED bi-color');"
    Ubaci T("INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-001','Dnevnik u 19','Informativni','Studijska',42,'Op~sta populacija','Aktivna');")
    Ubaci T("INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-002','Jutarnji program','Jutarnji','Studijska',180,'Op~sta populacija','Aktivna');")
    Ubaci "INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-003','Panorama magazin','Magazin','Kombinovana',60,'25-54','Aktivna');"
    Ubaci T("INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-004','Sportski ~zurnal','Sportski','Studijska',25,'18-49','Aktivna');")
End Sub

Private Sub DemoPodaci2()
    Ubaci "INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-005','Reke Vojvodine','Dokumentarni','Terenska',25,'35+','U produkciji');"
    Ubaci "INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-006','Kulturni pregled','Kulturni','Kombinovana',45,'35+','Aktivna');"
    Ubaci T("INSERT INTO [EMISIJA] ([SIFRA_EMISIJE],[NAZIV_EMISIJE],[ZANR],[FORMAT_EMISIJE],[PREDVIDJENO_TRAJANJE],[CILJNA_PUBLIKA],[STATUS_EMISIJE]) VALUES ('EM-007','De~cije carstvo','De~ciji','Studijska',30,'4-12','Aktivna');")
    Ubaci T("INSERT INTO [PROGRAMSKA_SEMA] ([SIFRA_SEME],[SIFRA_UREDNIKA],[NAZIV_SEME],[SEZONA],[VERZIJA_SEME],[DATUM_OD],[DATUM_DO],[STATUS_SEME],[DATUM_USVAJANJA]) VALUES ('PS-2026-J','ZAP-002','Jesenja ~sema 2026','Jesen 2026','v1.2',#9/1/2026#,#12/15/2026#,'Usvojena',#8/20/2026#);")
    Ubaci "INSERT INTO [PROGRAMSKA_CELINA] ([SIFRA_SEME],[RB_CELINE],[NAZIV_CELINE],[TIP_CELINE],[DATUM],[VREME_OD],[VREME_DO]) VALUES ('PS-2026-J',1,'Jutarnji blok','Jutarnji',#9/14/2026#,#07:00:00#,#10:00:00#);"
    Ubaci "INSERT INTO [PROGRAMSKA_CELINA] ([SIFRA_SEME],[RB_CELINE],[NAZIV_CELINE],[TIP_CELINE],[DATUM],[VREME_OD],[VREME_DO]) VALUES ('PS-2026-J',2,'Popodnevni blok','Popodnevni',#9/14/2026#,#16:00:00#,#19:00:00#);"
    Ubaci "INSERT INTO [PROGRAMSKA_CELINA] ([SIFRA_SEME],[RB_CELINE],[NAZIV_CELINE],[TIP_CELINE],[DATUM],[VREME_OD],[VREME_DO]) VALUES ('PS-2026-J',3,'Udarni termin','Prime time',#9/14/2026#,#19:00:00#,#23:00:00#);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0001','PS-2026-J',1,'EM-002',#9/14/2026#,#07:00:00#,180,'Premijera','C','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0002','PS-2026-J',2,'EM-007',#9/14/2026#,#16:00:00#,30,'Premijera','B','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0003','PS-2026-J',2,'EM-006',#9/14/2026#,#16:30:00#,45,'Premijera','B','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0004','PS-2026-J',3,'EM-001',#9/14/2026#,#19:00:00#,42,'Premijera','A','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0005','PS-2026-J',3,'EM-003',#9/14/2026#,#20:00:00#,60,'Premijera','A','Otkazan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0006','PS-2026-J',3,'EM-004',#9/14/2026#,#22:15:00#,25,'Premijera','B','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0007','PS-2026-J',3,'EM-001',#9/15/2026#,#19:00:00#,42,'Premijera','A','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0008','PS-2026-J',3,'EM-005',#9/15/2026#,#20:00:00#,25,'Premijera','A','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0009','PS-2026-J',1,'EM-002',#9/15/2026#,#07:00:00#,180,'Premijera','C','Realizovan',0);"
    Ubaci "INSERT INTO [TERMIN_EMITOVANJA] ([SIFRA_TERMINA],[SIFRA_SEME],[RB_CELINE],[SIFRA_EMISIJE],[DATUM],[VREME_POCETKA],[TRAJANJE_TERMINA],[TIP_TERMINA],[ZONA_GLEDANOSTI],[STATUS_TERMINA],[REDNI_BROJ_REPRIZE]) VALUES ('TR-0010','PS-2026-J',2,'EM-006',#9/15/2026#,#16:30:00#,45,'Repriza','B','Realizovan',1);"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0001','Dnevnik 14.09.2026',42,'MXF 1080i',#9/14/2026#,'ARH/2026/09/A-114');"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0002','Jutarnji program 14.09.2026',180,'MXF 1080i',#9/14/2026#,'ARH/2026/09/A-115');"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0003','Kulturni pregled - epizoda 12',45,'MXF 1080i',#9/14/2026#,'ARH/2026/09/A-116');"
    Ubaci T("INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0004','De~cije carstvo - epizoda 30',30,'MXF 1080i',#9/14/2026#,'ARH/2026/09/A-117');")
    Ubaci T("INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0005','Sportski ~zurnal 14.09.2026',25,'MXF 1080i',#9/14/2026#,'ARH/2026/09/A-118');")
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0006','Reke Vojvodine - epizoda 1',25,'MXF 2160p',#9/10/2026#,'ARH/2026/09/D-021');"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0007','Dnevnik 15.09.2026',42,'MXF 1080i',#9/15/2026#,'ARH/2026/09/A-119');"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0008','Spot Delta Market - Jesenja akcija',30,'MP4 1080p',#9/1/2026#,'ARH/REK/2026/S-4417');"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0009','Spot NIS Petrol - Zimska priprema',30,'MP4 1080p',#9/1/2026#,'ARH/REK/2026/S-4290');"
    Ubaci "INSERT INTO [MEDIJSKI_SADRZAJ] ([SIFRA_SADRZAJA],[NAZIV_SADRZAJA],[TRAJANJE],[FORMAT_ZAPISA],[DATUM_ARHIVIRANJA],[LOKACIJA_U_ARHIVI]) VALUES ('MS-0010','Strani dokumentarac - Divlja Evropa',50,'MXF 1080p',#7/15/2026#,'ARH/NAB/2026/N-008');"
    Ubaci "INSERT INTO [PRODUCIRANI_SADRZAJ] ([SIFRA_SADRZAJA],[DATUM_PRODUKCIJE],[VERZIJA_MASTERA]) VALUES ('MS-0001',#9/14/2026#,'v1');"
    Ubaci "INSERT INTO [PRODUCIRANI_SADRZAJ] ([SIFRA_SADRZAJA],[DATUM_PRODUKCIJE],[VERZIJA_MASTERA]) VALUES ('MS-0003',#9/12/2026#,'v2');"
    Ubaci "INSERT INTO [PRODUCIRANI_SADRZAJ] ([SIFRA_SADRZAJA],[DATUM_PRODUKCIJE],[VERZIJA_MASTERA]) VALUES ('MS-0006',#9/9/2026#,'v3');"
    Ubaci "INSERT INTO [PRODUCIRANI_SADRZAJ] ([SIFRA_SADRZAJA],[DATUM_PRODUKCIJE],[VERZIJA_MASTERA]) VALUES ('MS-0007',#9/15/2026#,'v1');"
    Ubaci T("INSERT INTO [KLIJENT] ([SIFRA_KLIJENTA],[NAZIV_KLIJENTA],[PIB],[MATICNI_BROJ],[ULICA_I_BROJ],[GRAD],[POSTANSKI_BROJ],[KONTAKT_OSOBA]) VALUES ('KL-001','Delta Market d.o.o.','100234567','07123456','Bulevar oslobo~denja 12','Novi Sad','21000','Ivana Simi~k');")
    Ubaci T("INSERT INTO [KLIJENT] ([SIFRA_KLIJENTA],[NAZIV_KLIJENTA],[PIB],[MATICNI_BROJ],[ULICA_I_BROJ],[GRAD],[POSTANSKI_BROJ],[KONTAKT_OSOBA]) VALUES ('KL-002','NIS Petrol a.d.','100112233','20011223','Narodnog fronta 12','Novi Sad','21000','Petar Vukovi~k');")
    Ubaci T("INSERT INTO [KLIJENT] ([SIFRA_KLIJENTA],[NAZIV_KLIJENTA],[PIB],[MATICNI_BROJ],[ULICA_I_BROJ],[GRAD],[POSTANSKI_BROJ],[KONTAKT_OSOBA]) VALUES ('KL-003','Telekom Srbija a.d.','100445566','17162543','Takovska 2','Beograd','11000','Maja Nikoli~k');")
    Ubaci "INSERT INTO [KLIJENT] ([SIFRA_KLIJENTA],[NAZIV_KLIJENTA],[PIB],[MATICNI_BROJ],[ULICA_I_BROJ],[GRAD],[POSTANSKI_BROJ],[KONTAKT_OSOBA]) VALUES ('KL-004','RTV Kanal Plus','101778899','08877665','Trg slobode 3','Subotica','24000','Zoran Balint');"
    Ubaci "INSERT INTO [OGLASIVAC] ([SIFRA_KLIJENTA],[BRANSA],[GODISNJI_BUDZET]) VALUES ('KL-001','Maloprodaja',24000000);"
    Ubaci "INSERT INTO [OGLASIVAC] ([SIFRA_KLIJENTA],[BRANSA],[GODISNJI_BUDZET]) VALUES ('KL-002','Naftna industrija',18000000);"
    Ubaci "INSERT INTO [OGLASIVAC] ([SIFRA_KLIJENTA],[BRANSA],[GODISNJI_BUDZET]) VALUES ('KL-003','Telekomunikacije',31000000);"
    Ubaci T("INSERT INTO [KUPAC_SADRZAJA] ([SIFRA_KLIJENTA],[TIP_MEDIJA],[TERITORIJA_EMITOVANJA]) VALUES ('KL-004','Regionalna TV','Severna Ba~cka');")
    Ubaci T("INSERT INTO [DOBAVLJAC] ([SIFRA_DOBAVLJACA],[NAZIV_DOBAVLJACA],[PIB],[MATICNI_BROJ],[ADRESA],[OCENA_DOBAVLJACA]) VALUES ('DOB-01','AV Studio d.o.o.','102334455','20334455','Cara Du~sana 45, Novi Sad',9.1);")
    Ubaci "INSERT INTO [DOBAVLJAC] ([SIFRA_DOBAVLJACA],[NAZIV_DOBAVLJACA],[PIB],[MATICNI_BROJ],[ADRESA],[OCENA_DOBAVLJACA]) VALUES ('DOB-02','TechnoMedia d.o.o.','103445566','21445566','Vojvode Stepe 88, Beograd',7.8);"
    Ubaci "INSERT INTO [DOBAVLJAC] ([SIFRA_DOBAVLJACA],[NAZIV_DOBAVLJACA],[PIB],[MATICNI_BROJ],[ADRESA],[OCENA_DOBAVLJACA]) VALUES ('DOB-03','Panorama Oprema d.o.o.','104556677','22556677','Industrijska 7, Zrenjanin',7.2);"
    Ubaci T("INSERT INTO [DOBAVLJAC] ([SIFRA_DOBAVLJACA],[NAZIV_DOBAVLJACA],[PIB],[MATICNI_BROJ],[ADRESA],[OCENA_DOBAVLJACA]) VALUES ('DOB-04','Global Media Rights Ltd','105667788','23667788','Praha 3, ~Ce~ska',8.4);")
    Ubaci "INSERT INTO [DOBAVLJAC_OPREME_I_MATERIJALA] ([SIFRA_DOBAVLJACA],[ASORTIMAN],[OVLASCENI_SERVIS]) VALUES ('DOB-01','Kamere, stativi, optika','Da');"
    Ubaci "INSERT INTO [DOBAVLJAC_OPREME_I_MATERIJALA] ([SIFRA_DOBAVLJACA],[ASORTIMAN],[OVLASCENI_SERVIS]) VALUES ('DOB-02','Emisiona i studijska oprema','Da');"
End Sub

Private Sub DemoPodaci3()
    Ubaci T("INSERT INTO [DOBAVLJAC_OPREME_I_MATERIJALA] ([SIFRA_DOBAVLJACA],[ASORTIMAN],[OVLASCENI_SERVIS]) VALUES ('DOB-03','Rasveta i potro~sni materijal','Ne');")
    Ubaci "INSERT INTO [DOBAVLJAC_TV_SADRZAJA] ([SIFRA_DOBAVLJACA],[VRSTA_SADRZAJA],[KATALOG_PONUDE]) VALUES ('DOB-04','Dokumentarni program','Katalog 2026 - Divlja Evropa');"
    Ubaci "INSERT INTO [UGOVOR] ([BROJ_UGOVORA],[SIFRA_KLIJENTA],[DATUM_SKLAPANJA],[VAZI_OD],[VAZI_DO],[UKUPNA_VREDNOST],[STATUS_UGOVORA]) VALUES ('UG-2026-0087','KL-001',#8/20/2026#,#9/1/2026#,#12/31/2026#,18720000,'Aktivan');"
    Ubaci "INSERT INTO [UGOVOR] ([BROJ_UGOVORA],[SIFRA_KLIJENTA],[DATUM_SKLAPANJA],[VAZI_OD],[VAZI_DO],[UKUPNA_VREDNOST],[STATUS_UGOVORA]) VALUES ('UG-2026-0044','KL-002',#7/10/2026#,#8/1/2026#,#12/31/2026#,10980000,'Aktivan');"
    Ubaci "INSERT INTO [UGOVOR] ([BROJ_UGOVORA],[SIFRA_KLIJENTA],[DATUM_SKLAPANJA],[VAZI_OD],[VAZI_DO],[UKUPNA_VREDNOST],[STATUS_UGOVORA]) VALUES ('UG-2026-0031','KL-003',#6/1/2026#,#7/1/2026#,#12/31/2026#,14850000,'Aktivan');"
    Ubaci "INSERT INTO [UGOVOR] ([BROJ_UGOVORA],[SIFRA_KLIJENTA],[DATUM_SKLAPANJA],[VAZI_OD],[VAZI_DO],[UKUPNA_VREDNOST],[STATUS_UGOVORA]) VALUES ('UG-2026-0110','KL-004',#9/1/2026#,#9/15/2026#,#3/15/2027#,2400000,'Aktivan');"
    Ubaci "INSERT INTO [UGOVOR] ([BROJ_UGOVORA],[SIFRA_KLIJENTA],[DATUM_SKLAPANJA],[VAZI_OD],[VAZI_DO],[UKUPNA_VREDNOST],[STATUS_UGOVORA]) VALUES ('UG-2026-0120',Null,#7/1/2026#,#7/1/2026#,#6/30/2027#,3600000,'Aktivan');"
    Ubaci "INSERT INTO [UGOVOR_O_OGLASAVANJU] ([BROJ_UGOVORA],[UGOVORENI_TERMINI]) VALUES ('UG-2026-0087','Zona A, radnim danima 19-23h');"
    Ubaci "INSERT INTO [UGOVOR_O_OGLASAVANJU] ([BROJ_UGOVORA],[UGOVORENI_TERMINI]) VALUES ('UG-2026-0044','Zona A i B, vikendom');"
    Ubaci "INSERT INTO [UGOVOR_O_OGLASAVANJU] ([BROJ_UGOVORA],[UGOVORENI_TERMINI]) VALUES ('UG-2026-0031','Zona A, svakodnevno');"
    Ubaci T("INSERT INTO [UGOVOR_O_PRODAJI_TV_SADRZAJA] ([BROJ_UGOVORA],[PRENOS_VLASNISTVA],[OBIM_USTUPLJENIH_PRAVA]) VALUES ('UG-2026-0110','Ne','Emitovanje, 6 meseci, Severna Ba~cka');")
    Ubaci T("INSERT INTO [UGOVOR_O_NABAVCI] ([BROJ_UGOVORA],[SIFRA_DOBAVLJACA],[VRSTA_REKLAMIRANJA],[ROK_ISPORUKE],[USLOVI_PLACANJA]) VALUES ('UG-2026-0120','DOB-04','Pisana reklamacija u roku od 8 dana',#7/15/2026#,'60 dana odlo~zeno');")
    Ubaci T("INSERT INTO [NABAVLJENI_SADRZAJ] ([SIFRA_SADRZAJA],[BROJ_UGOVORA],[ZEMLJA_POREKLA],[CENA_NABAVKE],[DATUM_PREUZIMANJA],[UGOVORENA_NAKNADA]) VALUES ('MS-0010','UG-2026-0120','~Ce~ska',1200000,#7/15/2026#,1200000);")
    Ubaci "INSERT INTO [REKLAMNI_SADRZAJ] ([SIFRA_SADRZAJA],[SIFRA_OGLASIVACA],[DATUM_PRIJEMA],[STATUS]) VALUES ('MS-0008','KL-001',#9/1/2026#,'Proveren');"
    Ubaci "INSERT INTO [REKLAMNI_SADRZAJ] ([SIFRA_SADRZAJA],[SIFRA_OGLASIVACA],[DATUM_PRIJEMA],[STATUS]) VALUES ('MS-0009','KL-002',#9/1/2026#,'Proveren');"
    Ubaci "INSERT INTO [CENOVNIK_REKL_TERMINA] ([SIFRA_CENOVNIKA],[VAZI_OD],[VAZI_DO],[ZONA],[CENA_PO_SEKUNDI],[TIP_CENOVNOG_PAKETA]) VALUES ('CN-2026-03',#9/1/2026#,#12/31/2026#,'A',4500,'Udarni termin');"
    Ubaci "INSERT INTO [CENOVNIK_REKL_TERMINA] ([SIFRA_CENOVNIKA],[VAZI_OD],[VAZI_DO],[ZONA],[CENA_PO_SEKUNDI],[TIP_CENOVNOG_PAKETA]) VALUES ('CN-2026-04',#9/1/2026#,#12/31/2026#,'B',2200,'Dnevni termin');"
    Ubaci T("INSERT INTO [CENOVNIK_REKL_TERMINA] ([SIFRA_CENOVNIKA],[VAZI_OD],[VAZI_DO],[ZONA],[CENA_PO_SEKUNDI],[TIP_CENOVNOG_PAKETA]) VALUES ('CN-2026-05',#9/1/2026#,#12/31/2026#,'C',1100,'No~kni termin');")
    Ubaci "INSERT INTO [REKLAMNI_BLOK] ([SIFRA_BLOKA],[SIFRA_TERMINA],[SIFRA_CENOVNIKA],[DATUM],[VREME_POCETKA],[TRAJANJE_BLOKA],[ZAKUPLJENO_SEKUNDI],[SLOBODNO_SEKUNDI],[ISKORISCENOST],[STATUS_BLOKA]) VALUES ('RB-1187','TR-0004','CN-2026-03',#9/14/2026#,#19:42:00#,180,150,30,83.33,'Popunjen');"
    Ubaci T("INSERT INTO [REKLAMNI_BLOK] ([SIFRA_BLOKA],[SIFRA_TERMINA],[SIFRA_CENOVNIKA],[DATUM],[VREME_POCETKA],[TRAJANJE_BLOKA],[ZAKUPLJENO_SEKUNDI],[SLOBODNO_SEKUNDI],[ISKORISCENOST],[STATUS_BLOKA]) VALUES ('RB-1188','TR-0006','CN-2026-04',#9/14/2026#,#22:40:00#,120,60,60,50.00,'Delimi~cno');")
    Ubaci T("INSERT INTO [REKLAMNI_BLOK] ([SIFRA_BLOKA],[SIFRA_TERMINA],[SIFRA_CENOVNIKA],[DATUM],[VREME_POCETKA],[TRAJANJE_BLOKA],[ZAKUPLJENO_SEKUNDI],[SLOBODNO_SEKUNDI],[ISKORISCENOST],[STATUS_BLOKA]) VALUES ('RB-1189','TR-0007','CN-2026-03',#9/15/2026#,#19:42:00#,180,120,60,66.67,'Delimi~cno');")
    Ubaci "INSERT INTO [STAVKA_UGOVORA] ([BROJ_UGOVORA],[RB_STAVKE],[OPIS_STAVKE],[KOLICINA_SEKUNDE],[JEDINICNA_CENA],[POPUST],[VREDNOST_STAVKE]) VALUES ('UG-2026-0087',1,'TV spot 30 sekundi, jesenja kampanja',1800,4500,10.00,7290000);"
    Ubaci T("INSERT INTO [STAVKA_UGOVORA] ([BROJ_UGOVORA],[RB_STAVKE],[OPIS_STAVKE],[KOLICINA_SEKUNDE],[JEDINICNA_CENA],[POPUST],[VREDNOST_STAVKE]) VALUES ('UG-2026-0087',2,'TV spot 15 sekundi, podr~ska kampanji',900,4500,10.00,3645000);")
    Ubaci "INSERT INTO [STAVKA_UGOVORA] ([BROJ_UGOVORA],[RB_STAVKE],[OPIS_STAVKE],[KOLICINA_SEKUNDE],[JEDINICNA_CENA],[POPUST],[VREDNOST_STAVKE]) VALUES ('UG-2026-0044',1,'TV spot 30 sekundi, zimska priprema',1200,4500,5.00,5130000);"
    Ubaci T("INSERT INTO [STAVKA_UGOVORA] ([BROJ_UGOVORA],[RB_STAVKE],[OPIS_STAVKE],[KOLICINA_SEKUNDE],[JEDINICNA_CENA],[POPUST],[VREDNOST_STAVKE]) VALUES ('UG-2026-0031',1,'TV spot 30 sekundi, godi~snji zakup',2400,4500,15.00,9180000);")
    Ubaci "INSERT INTO [EMITOVANJE_REKLAME] ([SIFRA_BLOKA],[RB_U_BLOKU],[SIFRA_SADRZAJA],[BROJ_UGOVORA],[RB_STAVKE_UGOVORA],[DATUM_EMITOVANJA],[VREME_EMITOVANJA],[TRAJANJE_SPOTA],[NAPLACENI_IZNOS],[STATUS_NAPLATE]) VALUES ('RB-1187',1,'MS-0008','UG-2026-0087',1,#9/14/2026#,#19:42:10#,30,121500,'Fakturisano');"
    Ubaci T("INSERT INTO [EMITOVANJE_REKLAME] ([SIFRA_BLOKA],[RB_U_BLOKU],[SIFRA_SADRZAJA],[BROJ_UGOVORA],[RB_STAVKE_UGOVORA],[DATUM_EMITOVANJA],[VREME_EMITOVANJA],[TRAJANJE_SPOTA],[NAPLACENI_IZNOS],[STATUS_NAPLATE]) VALUES ('RB-1187',2,'MS-0009','UG-2026-0044',1,#9/14/2026#,#19:42:45#,30,128250,'Napla~keno');")
    Ubaci "INSERT INTO [EMITOVANJE_REKLAME] ([SIFRA_BLOKA],[RB_U_BLOKU],[SIFRA_SADRZAJA],[BROJ_UGOVORA],[RB_STAVKE_UGOVORA],[DATUM_EMITOVANJA],[VREME_EMITOVANJA],[TRAJANJE_SPOTA],[NAPLACENI_IZNOS],[STATUS_NAPLATE]) VALUES ('RB-1187',3,'MS-0008','UG-2026-0087',2,#9/14/2026#,#19:43:20#,15,60750,'Fakturisano');"
    Ubaci T("INSERT INTO [EMITOVANJE_REKLAME] ([SIFRA_BLOKA],[RB_U_BLOKU],[SIFRA_SADRZAJA],[BROJ_UGOVORA],[RB_STAVKE_UGOVORA],[DATUM_EMITOVANJA],[VREME_EMITOVANJA],[TRAJANJE_SPOTA],[NAPLACENI_IZNOS],[STATUS_NAPLATE]) VALUES ('RB-1188',1,'MS-0009','UG-2026-0044',1,#9/14/2026#,#22:40:15#,30,62700,'Napla~keno');")
    Ubaci T("INSERT INTO [EMITOVANJE_REKLAME] ([SIFRA_BLOKA],[RB_U_BLOKU],[SIFRA_SADRZAJA],[BROJ_UGOVORA],[RB_STAVKE_UGOVORA],[DATUM_EMITOVANJA],[VREME_EMITOVANJA],[TRAJANJE_SPOTA],[NAPLACENI_IZNOS],[STATUS_NAPLATE]) VALUES ('RB-1189',1,'MS-0008','UG-2026-0087',1,#9/15/2026#,#19:42:10#,30,121500,'Nenapla~keno');")
    Ubaci T("INSERT INTO [EMITOVANJE_REKLAME] ([SIFRA_BLOKA],[RB_U_BLOKU],[SIFRA_SADRZAJA],[BROJ_UGOVORA],[RB_STAVKE_UGOVORA],[DATUM_EMITOVANJA],[VREME_EMITOVANJA],[TRAJANJE_SPOTA],[NAPLACENI_IZNOS],[STATUS_NAPLATE]) VALUES ('RB-1189',2,'MS-0008','UG-2026-0087',2,#9/15/2026#,#19:42:45#,15,60750,'Nenapla~keno');")
    Ubaci T("INSERT INTO [FAKTURA] ([BROJ_FAKTURE],[BROJ_UGOVORA],[DATUM_IZDAVANJA],[ROK_PLACANJA],[SMER],[OSNOVICA],[IZNOS_PDV],[STATUS_PLACANJA],[IZNOS_ZA_PLACANJE]) VALUES ('FA-2026-0301','UG-2026-0087',#9/30/2026#,#10/30/2026#,'Izlazna',182250,36450,'Nepla~kena',218700);")
    Ubaci T("INSERT INTO [FAKTURA] ([BROJ_FAKTURE],[BROJ_UGOVORA],[DATUM_IZDAVANJA],[ROK_PLACANJA],[SMER],[OSNOVICA],[IZNOS_PDV],[STATUS_PLACANJA],[IZNOS_ZA_PLACANJE]) VALUES ('FA-2026-0302','UG-2026-0044',#9/30/2026#,#10/15/2026#,'Izlazna',190950,38190,'Pla~kena',229140);")
    Ubaci T("INSERT INTO [FAKTURA] ([BROJ_FAKTURE],[BROJ_UGOVORA],[DATUM_IZDAVANJA],[ROK_PLACANJA],[SMER],[OSNOVICA],[IZNOS_PDV],[STATUS_PLACANJA],[IZNOS_ZA_PLACANJE]) VALUES ('FA-2026-0410',Null,#5/20/2026#,#6/20/2026#,'Ulazna',186000,37200,'Pla~kena',223200);")
    Ubaci T("INSERT INTO [FAKTURA] ([BROJ_FAKTURE],[BROJ_UGOVORA],[DATUM_IZDAVANJA],[ROK_PLACANJA],[SMER],[OSNOVICA],[IZNOS_PDV],[STATUS_PLACANJA],[IZNOS_ZA_PLACANJE]) VALUES ('FA-2026-0411',Null,#6/8/2026#,#7/8/2026#,'Ulazna',92000,18400,'Pla~kena',110400);")
    Ubaci T("INSERT INTO [PROJEKAT_PRODUKCIJE] ([SIFRA_PROJEKTA],[SIFRA_UREDNIKA],[SIFRA_EMISIJE],[NAZIV_PROJEKTA],[DATUM_POCETKA],[DATUM_ZAVRSETKA],[ODOBREN_BUDZET],[STATUS_PROJEKTA],[VRSTA_PRODUKCIJE],[OPIS_PROJEKTA]) VALUES ('PRJ-2026-014','ZAP-001','EM-005','Dokumentarni serijal Reke Vojvodine',#3/1/2026#,#6/30/2026#,1800000,'U realizaciji','Sopstvena produkcija','~Sestodelni serijal, snimanje u tri etape.');")
    Ubaci "INSERT INTO [PROJEKAT_PRODUKCIJE] ([SIFRA_PROJEKTA],[SIFRA_UREDNIKA],[SIFRA_EMISIJE],[NAZIV_PROJEKTA],[DATUM_POCETKA],[DATUM_ZAVRSETKA],[ODOBREN_BUDZET],[STATUS_PROJEKTA],[VRSTA_PRODUKCIJE],[OPIS_PROJEKTA]) VALUES ('PRJ-2026-021','ZAP-002','EM-003','Panorama magazin - jesenja sezona',#8/1/2026#,#12/15/2026#,1200000,'U realizaciji','Sopstvena produkcija','Nedeljni magazin, 16 epizoda.');"
    Ubaci T("INSERT INTO [AKTIVNOST_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[NAZIV_AKTIVNOSTI],[DATUM_OD],[DATUM_DO],[VRSTA_AKTIVNOSTI],[LOKACIJA_SNIMANJA],[STATUS_AKTIVNOSTI]) VALUES ('PRJ-2026-014',1,'Istra~zivanje i scenario',#3/1/2026#,#3/20/2026#,'Priprema','Redakcija, Novi Sad','Zavr~sena');")
    Ubaci T("INSERT INTO [AKTIVNOST_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[NAZIV_AKTIVNOSTI],[DATUM_OD],[DATUM_DO],[VRSTA_AKTIVNOSTI],[LOKACIJA_SNIMANJA],[STATUS_AKTIVNOSTI]) VALUES ('PRJ-2026-014',2,'Snimanje - gornji tok Tise',#4/6/2026#,#4/12/2026#,'Terensko snimanje','Kanji~za / Senta','Zavr~sena');")
    Ubaci "INSERT INTO [AKTIVNOST_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[NAZIV_AKTIVNOSTI],[DATUM_OD],[DATUM_DO],[VRSTA_AKTIVNOSTI],[LOKACIJA_SNIMANJA],[STATUS_AKTIVNOSTI]) VALUES ('PRJ-2026-014',3,'Snimanje - Dunav kod Apatina',#5/4/2026#,#5/11/2026#,'Terensko snimanje','Apatin','U toku');"
    Ubaci T("INSERT INTO [AKTIVNOST_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[NAZIV_AKTIVNOSTI],[DATUM_OD],[DATUM_DO],[VRSTA_AKTIVNOSTI],[LOKACIJA_SNIMANJA],[STATUS_AKTIVNOSTI]) VALUES ('PRJ-2026-014',4,'Monta~za i postprodukcija',#5/25/2026#,#6/19/2026#,'Postprodukcija','Monta~za 1','Planirana');")
    Ubaci T("INSERT INTO [AKTIVNOST_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[NAZIV_AKTIVNOSTI],[DATUM_OD],[DATUM_DO],[VRSTA_AKTIVNOSTI],[LOKACIJA_SNIMANJA],[STATUS_AKTIVNOSTI]) VALUES ('PRJ-2026-021',1,'Priprema sezone',#8/1/2026#,#8/20/2026#,'Priprema','Redakcija, Novi Sad','Zavr~sena');")
    Ubaci "INSERT INTO [AKTIVNOST_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[NAZIV_AKTIVNOSTI],[DATUM_OD],[DATUM_DO],[VRSTA_AKTIVNOSTI],[LOKACIJA_SNIMANJA],[STATUS_AKTIVNOSTI]) VALUES ('PRJ-2026-021',2,'Studijsko snimanje epizoda 1-8',#9/1/2026#,#10/20/2026#,'Studijsko snimanje','Studio 2','U toku');"
    Ubaci "INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-014',1,1,Null,'Honorari',180000,#3/25/2026#,'Autorski honorar za scenario');"
    Ubaci T("INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-014',2,1,'FA-2026-0410','Putni tro~skovi',223200,#4/15/2026#,'Sme~staj i prevoz ekipe');")
End Sub

Private Sub DemoPodaci4()
    Ubaci T("INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-014',2,2,Null,'Honorari',240000,#4/20/2026#,'Anga~zovanje terenske ekipe');")
    Ubaci T("INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-014',3,1,'FA-2026-0411','Putni tro~skovi',110400,#5/12/2026#,'Sme~staj i prevoz ekipe');")
    Ubaci "INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-014',3,2,Null,'Zakup opreme',150000,#5/10/2026#,'Zakup dodatne optike');"
    Ubaci T("INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-014',4,1,Null,'Postprodukcija',340000,#6/10/2026#,'Monta~za, grafika i ton');")
    Ubaci "INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-021',1,1,Null,'Honorari',120000,#8/18/2026#,'Priprema formata i najave');"
    Ubaci "INSERT INTO [TROSAK_PRODUKCIJE] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[RB_TROSKA],[BROJ_FAKTURE],[VRSTA_TROSKA],[IZNOS],[DATUM_NASTANKA],[OPIS_TROSKA]) VALUES ('PRJ-2026-021',2,1,Null,'Scenografija',260000,#9/5/2026#,'Izrada scenografije u Studiju 2');"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-014',1,'ZAP-003','Autor i novinar',#3/1/2026#,#3/20/2026#,96);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-014',2,'ZAP-003','Novinar na terenu',#4/6/2026#,#4/12/2026#,56);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-014',2,'ZAP-005','Snimatelj',#4/6/2026#,#4/12/2026#,56);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-014',2,'ZAP-006','Ton majstor',#4/6/2026#,#4/12/2026#,48);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-014',3,'ZAP-004','Reporter',#5/4/2026#,#5/11/2026#,64);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-014',3,'ZAP-005','Snimatelj',#5/4/2026#,#5/11/2026#,64);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-021',2,'ZAP-005','Snimatelj',#9/1/2026#,#10/20/2026#,120);"
    Ubaci "INSERT INTO [ANGAZOVANJE_NA_AKTIVNOSTI] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[SIFRA_ZAPOSLENOG],[ULOGA_NA_SNIMANJU],[DATUM_OD],[DATUM_DO],[BROJ_ANGAZOVANIH_SATI]) VALUES ('PRJ-2026-021',2,'ZAP-006','Ton majstor',#9/1/2026#,#10/20/2026#,110);"
    Ubaci "INSERT INTO [REZERVACIJA_OPREME] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[INVENTARSKI_BROJ],[DATUM_REZERVACIJE],[TRAJANJE_ZADUZENJA]) VALUES ('PRJ-2026-014',2,'INV-0103',#4/5/2026#,8);"
    Ubaci "INSERT INTO [REZERVACIJA_OPREME] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[INVENTARSKI_BROJ],[DATUM_REZERVACIJE],[TRAJANJE_ZADUZENJA]) VALUES ('PRJ-2026-014',2,'INV-0104',#4/5/2026#,8);"
    Ubaci "INSERT INTO [REZERVACIJA_OPREME] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[INVENTARSKI_BROJ],[DATUM_REZERVACIJE],[TRAJANJE_ZADUZENJA]) VALUES ('PRJ-2026-014',3,'INV-0103',#5/3/2026#,9);"
    Ubaci "INSERT INTO [REZERVACIJA_OPREME] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[INVENTARSKI_BROJ],[DATUM_REZERVACIJE],[TRAJANJE_ZADUZENJA]) VALUES ('PRJ-2026-021',2,'INV-0101',#9/1/2026#,50);"
    Ubaci "INSERT INTO [REZERVACIJA_OPREME] ([SIFRA_PROJEKTA],[RB_AKTIVNOSTI],[INVENTARSKI_BROJ],[DATUM_REZERVACIJE],[TRAJANJE_ZADUZENJA]) VALUES ('PRJ-2026-021',2,'INV-0105',#9/1/2026#,50);"
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0001',1,'MS-0002','Realizovano',#07:00:05#,180,Null,'Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0002',1,'MS-0004','Realizovano',#16:00:00#,30,Null,'Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0003',1,'MS-0003','Realizovano',#16:30:10#,47,'Produ~zen intervju sa gostom','Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0004',1,'MS-0001','Realizovano',#19:00:02#,44,'Produ~zen zbog vanredne vesti','Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0005',1,'MS-0010','Otkazano',#20:00:00#,0,'Kvar emisione opreme - miks pult','Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0006',1,'MS-0005','Realizovano',#22:15:00#,22,'Skra~ken zbog prenosa utakmice','Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0007',1,'MS-0007','Realizovano',#19:00:01#,42,Null,'Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0008',1,'MS-0006','Realizovano',#20:00:00#,25,Null,'Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0009',1,'MS-0002','Realizovano',#07:00:00#,176,'Prekid signala u trajanju 3 min','Vladimir ~Duri~k');")
    Ubaci T("INSERT INTO [ZAPIS_O_EMITOVANJU] ([SIFRA_TERMINA],[RB_EMITOVANJA],[SIFRA_SADRZAJA],[STATUS_REALIZACIJE],[STVARNO_VREME_POCETKA],[STVARNO_TRAJANJE],[NAPOMENA_O_SMETNJAMA],[OPERATER_EMITOVANJA]) VALUES ('TR-0010',1,'MS-0003','Realizovano',#16:30:00#,45,Null,'Vladimir ~Duri~k');")
    Ubaci "INSERT INTO [PRAVO_KORISCENJA] ([BROJ_LICENCE],[VRSTA_PRAVA],[DATUM_OD],[DATUM_DO],[DOZVOLJENO_EMITOVANJA],[ISKORISCENO_EMITOVANJA],[TERITORIJA],[NOSILAC_PRAVA]) VALUES ('LIC-2026-001','Emitovanje - sopstvena produkcija',#1/1/2026#,#12/31/2030#,999,12,'Srbija','TV Panorama');"
    Ubaci "INSERT INTO [PRAVO_KORISCENJA] ([BROJ_LICENCE],[VRSTA_PRAVA],[DATUM_OD],[DATUM_DO],[DOZVOLJENO_EMITOVANJA],[ISKORISCENO_EMITOVANJA],[TERITORIJA],[NOSILAC_PRAVA]) VALUES ('LIC-2026-014','Emitovanje - kupljeni format',#7/15/2026#,#10/15/2026#,6,5,'Srbija','Global Media Rights Ltd');"
    Ubaci T("INSERT INTO [PRAVO_KORISCENJA] ([BROJ_LICENCE],[VRSTA_PRAVA],[DATUM_OD],[DATUM_DO],[DOZVOLJENO_EMITOVANJA],[ISKORISCENO_EMITOVANJA],[TERITORIJA],[NOSILAC_PRAVA]) VALUES ('LIC-2026-022','Muzi~cka prava',#1/1/2026#,#12/31/2026#,999,48,'Srbija','SOKOJ');")
    Ubaci "INSERT INTO [PRAVO_KORISCENJA] ([BROJ_LICENCE],[VRSTA_PRAVA],[DATUM_OD],[DATUM_DO],[DOZVOLJENO_EMITOVANJA],[ISKORISCENO_EMITOVANJA],[TERITORIJA],[NOSILAC_PRAVA]) VALUES ('LIC-2025-088','Emitovanje - arhivski materijal',#6/1/2025#,#9/30/2026#,20,20,'Srbija','Filmski centar');"
    Ubaci "INSERT INTO [POKRIVENOST_PRAVOM] ([BROJ_LICENCE],[SIFRA_SADRZAJA],[OBLAST_POKRIVENOSTI]) VALUES ('LIC-2026-001','MS-0001','Linearno emitovanje');"
    Ubaci "INSERT INTO [POKRIVENOST_PRAVOM] ([BROJ_LICENCE],[SIFRA_SADRZAJA],[OBLAST_POKRIVENOSTI]) VALUES ('LIC-2026-001','MS-0003','Linearno emitovanje');"
    Ubaci "INSERT INTO [POKRIVENOST_PRAVOM] ([BROJ_LICENCE],[SIFRA_SADRZAJA],[OBLAST_POKRIVENOSTI]) VALUES ('LIC-2026-001','MS-0006','Linearno emitovanje i internet');"
    Ubaci "INSERT INTO [POKRIVENOST_PRAVOM] ([BROJ_LICENCE],[SIFRA_SADRZAJA],[OBLAST_POKRIVENOSTI]) VALUES ('LIC-2026-001','MS-0007','Linearno emitovanje');"
    Ubaci "INSERT INTO [POKRIVENOST_PRAVOM] ([BROJ_LICENCE],[SIFRA_SADRZAJA],[OBLAST_POKRIVENOSTI]) VALUES ('LIC-2026-014','MS-0010','Linearno emitovanje');"
    Ubaci "INSERT INTO [POKRIVENOST_PRAVOM] ([BROJ_LICENCE],[SIFRA_SADRZAJA],[OBLAST_POKRIVENOSTI]) VALUES ('LIC-2026-022','MS-0002','Muzika u jutarnjem programu');"
    Ubaci "INSERT INTO [MERENJE_GLEDANOSTI] ([SIFRA_MERENJA],[DATUM_MERENJA],[IZVOR_MERENJA],[CILJNA_GRUPA],[RATING],[SHARE_UDEO],[BROJ_GLEDALACA],[PROSECNO_GLEDANJE]) VALUES ('MG-0914',#9/14/2026#,'Nielsen','4+',6.80,22.40,470000,28);"
    Ubaci "INSERT INTO [MERENJE_GLEDANOSTI] ([SIFRA_MERENJA],[DATUM_MERENJA],[IZVOR_MERENJA],[CILJNA_GRUPA],[RATING],[SHARE_UDEO],[BROJ_GLEDALACA],[PROSECNO_GLEDANJE]) VALUES ('MG-0915',#9/15/2026#,'Nielsen','4+',6.40,21.10,442000,26);"
    Ubaci "INSERT INTO [MERENJE_GLEDANOSTI] ([SIFRA_MERENJA],[DATUM_MERENJA],[IZVOR_MERENJA],[CILJNA_GRUPA],[RATING],[SHARE_UDEO],[BROJ_GLEDALACA],[PROSECNO_GLEDANJE]) VALUES ('MG-0916',#9/16/2026#,'Nielsen','4+',7.10,23.80,491000,31);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0914','EM-001',9.40,31.20);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0914','EM-002',4.10,18.60);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0914','EM-003',7.80,25.40);"
End Sub

Private Sub DemoPodaci5()
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0914','EM-004',7.10,24.10);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0914','EM-006',6.20,19.80);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0914','EM-007',5.10,17.20);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0915','EM-001',9.10,30.40);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0915','EM-002',3.90,17.90);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0915','EM-005',6.90,22.60);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0915','EM-006',6.00,19.10);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0916','EM-001',9.70,32.10);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0916','EM-003',8.00,26.20);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0916','EM-004',7.30,24.80);"
    Ubaci "INSERT INTO [MERENJE_EMISIJE] ([SIFRA_MERENJA],[SIFRA_EMISIJE],[OSTVARENI_RATING],[UDEO_U_TERMINU]) VALUES ('MG-0916','EM-005',7.20,23.40);"
    Ubaci "INSERT INTO [PLAN_NABAVKE] ([SIFRA_PLANA],[GODINA_PLANA],[DATUM_DONOSENJA],[STATUS_PLANA],[UKUPNA_VREDNOST],[DONOSILAC_PLANA]) VALUES ('PN-2026',2026,#12/20/2025#,'Usvojen',14450000,'Uprava stanice');"
    Ubaci "INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',1,'Studijske kamere i stativi',2,'kom',4200000,'Q2');"
    Ubaci "INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',2,'Rasveta studija 2',6,'kom',1850000,'Q2');"
    Ubaci "INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',3,'Audio miks pult',1,'kom',2400000,'Q3');"
    Ubaci "INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',4,'Servis emisione opreme',1,'usluga',1200000,'Q1-Q4');"
    Ubaci "INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',5,'Prava emitovanja - strani format',1,'licenca',3600000,'Q3');"
    Ubaci T("INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',6,'Potro~sni materijal',1,'paket',780000,'Q1-Q4');")
    Ubaci "INSERT INTO [STAVKA_PLANA_NABAVKE] ([SIFRA_PLANA],[RB_STAVKE],[OPIS_ARTIKLA],[KOLICINA],[JEDINICA_MERE],[PROCENJENA_CENA],[PLANIRANI_KVARTAL]) VALUES ('PN-2026',7,'Kancelarijski materijal',1,'paket',420000,'Q1-Q4');"
    Ubaci "INSERT INTO [ZAHTEV_ZA_NABAVKU] ([BROJ_ZAHTEVA],[SIFRA_JEDINICE],[SIFRA_PLANA],[DATUM_ZAHTEVA],[VRSTA_NABAVKE],[PREDMET_ZAHTEVA],[STATUS_ZAHTEVA],[PRIORITET],[PROCENJENA_VREDNOST]) VALUES ('ZN-2026-0042','OJ-03','PN-2026',#3/10/2026#,'Oprema','Zamena dve studijske kamere i stativa - Studio 2','Realizovan','Visok',4200000);"
    Ubaci "INSERT INTO [ZAHTEV_ZA_NABAVKU] ([BROJ_ZAHTEVA],[SIFRA_JEDINICE],[SIFRA_PLANA],[DATUM_ZAHTEVA],[VRSTA_NABAVKE],[PREDMET_ZAHTEVA],[STATUS_ZAHTEVA],[PRIORITET],[PROCENJENA_VREDNOST]) VALUES ('ZN-2026-0051','OJ-03','PN-2026',#4/2/2026#,'Oprema','Rasveta studija 2 - LED paneli','Realizovan','Srednji',1850000);"
    Ubaci T("INSERT INTO [ZAHTEV_ZA_NABAVKU] ([BROJ_ZAHTEVA],[SIFRA_JEDINICE],[SIFRA_PLANA],[DATUM_ZAHTEVA],[VRSTA_NABAVKE],[PREDMET_ZAHTEVA],[STATUS_ZAHTEVA],[PRIORITET],[PROCENJENA_VREDNOST]) VALUES ('ZN-2026-0067','OJ-03','PN-2026',#6/18/2026#,'Oprema','Audio miks pult za re~ziju 1','U postupku','Visok',2400000);")
    Ubaci "INSERT INTO [PONUDA_DOBAVLJACA] ([BROJ_PONUDE],[SIFRA_DOBAVLJACA],[DATUM_PRIJEMA],[VAZI_DO],[UKUPNA_CENA],[ROK_ISPORUKE],[USLOVI_PLACANJA],[STATUS_PONUDE],[UKUPNO_BODOVA]) VALUES ('PD-2026-0113','DOB-01',#3/25/2026#,#4/30/2026#,4480000,#4/20/2026#,'Avans 50%','Nije izabrana',7.60);"
    Ubaci T("INSERT INTO [PONUDA_DOBAVLJACA] ([BROJ_PONUDE],[SIFRA_DOBAVLJACA],[DATUM_PRIJEMA],[VAZI_DO],[UKUPNA_CENA],[ROK_ISPORUKE],[USLOVI_PLACANJA],[STATUS_PONUDE],[UKUPNO_BODOVA]) VALUES ('PD-2026-0114','DOB-02',#3/26/2026#,#4/30/2026#,3950000,#5/5/2026#,'60 dana odlo~zeno','Izabrana',9.15);")
    Ubaci T("INSERT INTO [PONUDA_DOBAVLJACA] ([BROJ_PONUDE],[SIFRA_DOBAVLJACA],[DATUM_PRIJEMA],[VAZI_DO],[UKUPNA_CENA],[ROK_ISPORUKE],[USLOVI_PLACANJA],[STATUS_PONUDE],[UKUPNO_BODOVA]) VALUES ('PD-2026-0115','DOB-03',#3/27/2026#,#4/30/2026#,4180000,#5/15/2026#,'45 dana odlo~zeno','Nije izabrana',7.15);")
    Ubaci T("INSERT INTO [KRITERIJUM_VREDNOVANJA] ([SIFRA_KRITERIJUMA],[NAZIV_KRITERIJUMA],[NACIN_BODOVANJA],[OPIS_KRITERIJUMA]) VALUES ('KR-01','Ponu~dena cena','Najni~za cena = 10 bodova','Ponder 40%');")
    Ubaci T("INSERT INTO [KRITERIJUM_VREDNOVANJA] ([SIFRA_KRITERIJUMA],[NAZIV_KRITERIJUMA],[NACIN_BODOVANJA],[OPIS_KRITERIJUMA]) VALUES ('KR-02','Rok isporuke','Kra~ki rok = vi~se bodova','Ponder 20%');")
    Ubaci T("INSERT INTO [KRITERIJUM_VREDNOVANJA] ([SIFRA_KRITERIJUMA],[NAZIV_KRITERIJUMA],[NACIN_BODOVANJA],[OPIS_KRITERIJUMA]) VALUES ('KR-03','Uslovi pla~kanja','Du~ze odlo~zeno = vi~se bodova','Ponder 15%');")
    Ubaci T("INSERT INTO [KRITERIJUM_VREDNOVANJA] ([SIFRA_KRITERIJUMA],[NAZIV_KRITERIJUMA],[NACIN_BODOVANJA],[OPIS_KRITERIJUMA]) VALUES ('KR-04','Garantni rok i servis','Du~za garancija = vi~se bodova','Ponder 15%');")
    Ubaci T("INSERT INTO [KRITERIJUM_VREDNOVANJA] ([SIFRA_KRITERIJUMA],[NAZIV_KRITERIJUMA],[NACIN_BODOVANJA],[OPIS_KRITERIJUMA]) VALUES ('KR-05','Dosada~snja ocena dobavlja~ca','Iz evidencije reklamacija','Ponder 10%');")
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0113','KR-01',7.00,Null);"
    Ubaci T("INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0113','KR-02',9.00,'Najkra~ki rok');")
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0113','KR-03',6.00,Null);"
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0113','KR-04',8.00,Null);"
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0113','KR-05',9.00,'14 isporuka bez reklamacije');"
    Ubaci T("INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0114','KR-01',10.00,'Najni~za cena');")
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0114','KR-02',7.00,Null);"
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0114','KR-03',9.00,Null);"
    Ubaci T("INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0114','KR-04',9.00,'36 meseci, ovla~s~keni servis');")
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0114','KR-05',8.00,Null);"
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0115','KR-01',8.00,Null);"
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0115','KR-02',6.00,Null);"
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0115','KR-03',8.00,Null);"
    Ubaci T("INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0115','KR-04',5.00,'Bez ovla~s~kenog servisa');")
    Ubaci "INSERT INTO [OCENA_PONUDE] ([BROJ_PONUDE],[SIFRA_KRITERIJUMA],[BROJ_BODOVA],[KOMENTAR_OCENE]) VALUES ('PD-2026-0115','KR-05',7.00,Null);"
End Sub

Private Sub DemoPodaci6()
    Ubaci "INSERT INTO [PONUDJENA_STAVKA] ([SIFRA_PLANA],[RB_STAVKE],[BROJ_PONUDE],[PONUDJENA_CENA],[ROK_ZA_STAVKU]) VALUES ('PN-2026',1,'PD-2026-0113',4480000,#4/20/2026#);"
    Ubaci "INSERT INTO [PONUDJENA_STAVKA] ([SIFRA_PLANA],[RB_STAVKE],[BROJ_PONUDE],[PONUDJENA_CENA],[ROK_ZA_STAVKU]) VALUES ('PN-2026',1,'PD-2026-0114',3950000,#5/5/2026#);"
    Ubaci "INSERT INTO [PONUDJENA_STAVKA] ([SIFRA_PLANA],[RB_STAVKE],[BROJ_PONUDE],[PONUDJENA_CENA],[ROK_ZA_STAVKU]) VALUES ('PN-2026',1,'PD-2026-0115',4180000,#5/15/2026#);"
    Ubaci T("INSERT INTO [NARUDZBENICA] ([BROJ_NARUDZBENICE],[SIFRA_DOBAVLJACA],[DATUM_IZDAVANJA],[ROK_ISPORUKE],[MESTO_ISPORUKE],[UKUPAN_IZNOS],[STATUS_NARUDZBINE]) VALUES ('NR-2026-0211','DOB-02',#4/5/2026#,#5/5/2026#,'TV Panorama, Novi Sad',3950000,'Isporu~cena');")
    Ubaci T("INSERT INTO [NARUDZBENICA] ([BROJ_NARUDZBENICE],[SIFRA_DOBAVLJACA],[DATUM_IZDAVANJA],[ROK_ISPORUKE],[MESTO_ISPORUKE],[UKUPAN_IZNOS],[STATUS_NARUDZBINE]) VALUES ('NR-2026-0238','DOB-03',#4/20/2026#,#5/20/2026#,'TV Panorama, Novi Sad',2080000,'Isporu~cena');")
End Sub

Private Sub Forme1()
    NapraviFormu "ORGANIZACIONA_JEDINICA"
    NapraviFormu "ZAPOSLENI"
    NapraviFormu "UREDNIK"
    NapraviFormu "NOVINAR_REPORTER"
    NapraviFormu "TEHNICKO_OSOBLJE"
    NapraviFormu "REFERENT"
    NapraviFormu "SERVISERI"
    NapraviFormu "OPREMA"
    NapraviFormu "SNIMATELJSKA_OPREMA"
    NapraviFormu "STUDIJSKA_I_EMISIONA_OPREMA"
    NapraviFormu "AUDIO_OPREMA"
    NapraviFormu "SVETLOSNA_OPREMA"
    NapraviFormu "ZADUZENJE_OPREME"
    NapraviFormu "SERVISIRANJE_OPREME"
    NapraviFormu "PROJEKAT_PRODUKCIJE"
    NapraviFormu "AKTIVNOST_PRODUKCIJE"
    NapraviFormu "TROSAK_PRODUKCIJE"
    NapraviFormu "ANGAZOVANJE_NA_AKTIVNOSTI"
    NapraviFormu "REZERVACIJA_OPREME"
    NapraviFormu "SIROVI_SNIMAK"
    NapraviFormu "GRAFICKI_I_MUZICKI_ELEMENT"
    NapraviFormu "PROGRAMSKA_SEMA"
    NapraviFormu "PROGRAMSKA_CELINA"
    NapraviFormu "EMISIJA"
End Sub

Private Sub Forme2()
    NapraviFormu "TERMIN_EMITOVANJA"
    NapraviFormu "MEDIJSKI_SADRZAJ"
    NapraviFormu "PRODUCIRANI_SADRZAJ"
    NapraviFormu "NABAVLJENI_SADRZAJ"
    NapraviFormu "REKLAMNI_SADRZAJ"
    NapraviFormu "ZAPIS_O_EMITOVANJU"
    NapraviFormu "MONTAZA_SNIMKA"
    NapraviFormu "UGRADNJA_ELEMENTA"
    NapraviFormu "SADRZAJ_EMISIJE"
    NapraviFormu "PRAVO_KORISCENJA"
    NapraviFormu "POKRIVENOST_PRAVOM"
    NapraviFormu "POVRATNA_INFO_GLEDALACA"
    NapraviFormu "MERENJE_GLEDANOSTI"
    NapraviFormu "MERENJE_EMISIJE"
    NapraviFormu "CENOVNIK_REKL_TERMINA"
    NapraviFormu "REKLAMNI_BLOK"
    NapraviFormu "EMITOVANJE_REKLAME"
    NapraviFormu "KLIJENT"
    NapraviFormu "OGLASIVAC"
    NapraviFormu "KUPAC_SADRZAJA"
    NapraviFormu "UGOVOR"
    NapraviFormu "STAVKA_UGOVORA"
    NapraviFormu "UGOVOR_O_OGLASAVANJU"
    NapraviFormu "UGOVOR_O_PRODAJI_TV_SADRZAJA"
End Sub

Private Sub Forme3()
    NapraviFormu "UGOVOR_O_NABAVCI"
    NapraviFormu "USTUPANJE_SADRZAJA"
    NapraviFormu "PLAN_NABAVKE"
    NapraviFormu "ZAHTEV_ZA_NABAVKU"
    NapraviFormu "STAVKA_PLANA_NABAVKE"
    NapraviFormu "DOBAVLJAC"
    NapraviFormu "DOBAVLJAC_TV_SADRZAJA"
    NapraviFormu "DOBAVLJAC_OPREME_I_MATERIJALA"
    NapraviFormu "PONUDA_DOBAVLJACA"
    NapraviFormu "PONUDJENA_STAVKA"
    NapraviFormu "KRITERIJUM_VREDNOVANJA"
    NapraviFormu "OCENA_PONUDE"
    NapraviFormu "NARUDZBENICA"
    NapraviFormu "STAVKA_NARUDZBENICE"
    NapraviFormu "PRIJEMNICA"
    NapraviFormu "PRIJEM_STAVKE"
    NapraviFormu "REKLAMACIJA"
    NapraviFormu "REKLAMIRANA_STAVKA"
    NapraviFormu "FAKTURA"
    NapraviFormu "STAVKA_FAKTURE"
    NapraviFormu "NALOG_ZA_PLACANJE"
End Sub

' ---------------------------------------------------------------- izvestaji
Private Sub Izvestaji()
    Dim r As String
    r = NapraviIzvestaj("rptProgramskaSema", "qryProgramskaSema", T("Izve~staj 1 - Programska ~sema sa terminima emitovanja"), _
        "VREME_POCETKA:1100|NAZIV_EMISIJE:2600|ZANR:1400|TRAJANJE_TERMINA:1100|TIP_TERMINA:1300|ZONA_GLEDANOSTI:1100|REDNI_BROJ_REPRIZE:1100|STATUS_TERMINA:1400", "NAZIV_CELINE", "TRAJANJE_TERMINA", True)
    r = NapraviIzvestaj("rptPlayoutLog", "qryPlayoutLog", T("Izve~staj 2 - Evidencija emitovanog sadr~zaja (playout log)"), _
        "DATUM:1100|STVARNO_VREME_POCETKA:1100|NAZIV_EMISIJE:2200|NAZIV_SADRZAJA:2400|TRAJANJE_TERMINA:1000|STVARNO_TRAJANJE:1000|ODSTUPANJE:1000|STATUS_REALIZACIJE:1300|BROJ_LICENCE:1400|NAPOMENA_O_SMETNJAMA:2400", "DATUM", "STVARNO_TRAJANJE", True)
    r = NapraviIzvestaj("rptGledanost", "qryGledanostEmisija", T("Izve~staj 3 - Gledanost emisija po ~zanru"), _
        "NAZIV_EMISIJE:2800|ZANR:1600|BROJ_MERENJA:1200|PROSECAN_REJTING:1500|PROSECAN_UDEO:1500|PROSECAN_BROJ_GLEDALACA:2000|PROSECNO_GLEDANJE:1800", "", "", True)
    r = NapraviIzvestaj("rptTroskoviProjekta", "qryTroskoviProjekta", T("Izve~staj 4 - Realizacija i tro~skovi projekta produkcije"), _
        "RB_AKTIVNOSTI:700|NAZIV_AKTIVNOSTI:2600|VRSTA_AKTIVNOSTI:1600|RB_TROSKA:700|VRSTA_TROSKA:1600|OPIS_TROSKA:2400|DATUM_NASTANKA:1200|IZNOS:1500|BROJ_FAKTURE:1400", "NAZIV_PROJEKTA", "IZNOS", True)
    r = NapraviIzvestaj("rptZaduzenjeOpreme", "qryZaduzenjeOpreme", T("Zadu~zenje opreme po aktivnostima produkcije"), _
        "INVENTARSKI_BROJ:1500|NAZIV_OPREME:2400|NAZIV_AKTIVNOSTI:3000|DATUM_REZERVACIJE:1500|TRAJANJE_ZADUZENJA:1600", "", "TRAJANJE_ZADUZENJA", False)
    r = NapraviIzvestaj("rptAngazovanjeIOprema", "qryAngazovanje", T("Izve~staj 5 - Anga~zovanje zaposlenih i zadu~zenje opreme"), _
        "NAZIV_PROJEKTA:3000|NAZIV_AKTIVNOSTI:3000|ULOGA_NA_SNIMANJU:2400|DATUM_OD:1300|DATUM_DO:1300|BROJ_ANGAZOVANIH_SATI:1600", "ZAPOSLENI_NAZIV", "BROJ_ANGAZOVANIH_SATI", True)
    r = NapraviIzvestaj("rptKarticaOglasivaca", "qryKarticaOglasivaca", T("Izve~staj 6 - Realizacija ugovora o ogla~savanju po ogla~siva~cu"), _
        "RB_STAVKE:800|OPIS_STAVKE:2800|KOLICINA_SEKUNDE:1300|JEDINICNA_CENA:1400|VREDNOST_STAVKE:1600|DATUM_EMITOVANJA:1400|VREME_EMITOVANJA:1200|TRAJANJE_SPOTA:1200|NAPLACENI_IZNOS:1600|STATUS_NAPLATE:1600", "BROJ_UGOVORA", "NAPLACENI_IZNOS", True)
    r = NapraviIzvestaj("rptVrednovanjePonuda", "qryVrednovanjePonuda", T("Vrednovanje ponuda dobavlja~ca"), _
        "NAZIV_DOBAVLJACA:2600|NAZIV_KRITERIJUMA:2800|BROJ_BODOVA:1200|UKUPNO_BODOVA:1400|STATUS_PONUDE:1600", "BROJ_PONUDE", "", False)
    r = NapraviIzvestaj("rptPlanNabavke", "qryPlanNabavke", T("Izve~staj 7 - Realizacija plana nabavke sa vrednovanjem ponuda"), _
        "RB_STAVKE:800|OPIS_ARTIKLA:3000|KOLICINA:1000|PLANIRANI_KVARTAL:1400|PROCENJENA_CENA:1600|BROJ_ZAHTEVA:1600|STATUS_ZAHTEVA:1400|BROJ_NARUDZBENICE:1500|UKUPAN_IZNOS:1600", "", "PROCENJENA_CENA|UKUPAN_IZNOS", True)
    r = NapraviIzvestaj("rptPravaKoriscenja", "qryPravaKoriscenja", T("Izve~staj 8 - Prava kori~s~kenja medijskog sadr~zaja i rokovi va~zenja"), _
        "BROJ_LICENCE:1600|VRSTA_PRAVA:2400|DATUM_DO:1200|DANA_DO_ISTEKA:1300|DOZVOLJENO_EMITOVANJA:1400|ISKORISCENO_EMITOVANJA:1400|PREOSTALO_EMITOVANJA:1400|NAZIV_SADRZAJA:2400|STATUS_PRAVA:1500", "", "", True)

    DodajGrafikon "rptGledanost", "qryGledanostPoZanru", T("Prose~can ostvareni rejting po ~zanru emisije")
    DodajPodizvestaj "rptAngazovanjeIOprema", "rptZaduzenjeOpreme", T("Zadu~zenje opreme u istom periodu"), 3000
    DodajPodizvestaj "rptPlanNabavke", "rptVrednovanjePonuda", "Vrednovanje prikupljenih ponuda", 3400
End Sub

' ---------------------------------------------------------------- glavni meni
Public Function OtvoriIzvestaj(ByVal ime As String)
    On Error Resume Next
    DoCmd.OpenReport ime, acViewPreview
End Function

Public Function OtvoriFormu(ByVal ime As String)
    On Error Resume Next
    DoCmd.OpenForm ime
End Function

Private Sub GlavniMeni()
    Dim frm As Form, ctl As Control, lbl As Control, priv As String, y As Long
    On Error GoTo Greska
    Obrisi "F", "frm_GLAVNI_MENI"
    Set frm = CreateForm()
    priv = frm.Name
    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 260, 9000, 460)
    lbl.Caption = "TV Panorama - informacioni sistem TV stanice"
    lbl.FontSize = 18
    lbl.FontBold = True
    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, 760, 9000, 300)
    lbl.Caption = T("Izve~staji")
    lbl.FontSize = 11
    lbl.FontBold = True
    y = 1120
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 1 - Programska ~sema sa terminima emitovanja")
    ctl.OnClick = "=OtvoriIzvestaj(""rptProgramskaSema"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 2 - Evidencija emitovanog sadr~zaja (playout log)")
    ctl.OnClick = "=OtvoriIzvestaj(""rptPlayoutLog"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 3 - Gledanost emisija po ~zanru")
    ctl.OnClick = "=OtvoriIzvestaj(""rptGledanost"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 4 - Realizacija i tro~skovi projekta produkcije")
    ctl.OnClick = "=OtvoriIzvestaj(""rptTroskoviProjekta"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 5 - Anga~zovanje zaposlenih i zadu~zenje opreme")
    ctl.OnClick = "=OtvoriIzvestaj(""rptAngazovanjeIOprema"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 6 - Realizacija ugovora o ogla~savanju po ogla~siva~cu")
    ctl.OnClick = "=OtvoriIzvestaj(""rptKarticaOglasivaca"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 7 - Realizacija plana nabavke sa vrednovanjem ponuda")
    ctl.OnClick = "=OtvoriIzvestaj(""rptPlanNabavke"")"
    y = y + 460
    Set ctl = CreateControl(priv, acCommandButton, acDetail, , , 300, y, 8600, 400)
    ctl.Caption = T("Izve~staj 8 - Prava kori~s~kenja medijskog sadr~zaja i rokovi va~zenja")
    ctl.OnClick = "=OtvoriIzvestaj(""rptPravaKoriscenja"")"
    y = y + 460
    Set lbl = CreateControl(priv, acLabel, acDetail, , , 300, y + 200, 9000, 300)
    lbl.Caption = "Forme za unos nalaze se u oknu objekata, sa prefiksom frm_"
    lbl.FontSize = 9
    lbl.ForeColor = RGB(90, 100, 120)
    frm.Section(acDetail).Height = y + 800
    frm.Width = 9300
    frm.Caption = "TV Panorama"
    frm.NavigationButtons = False
    frm.RecordSelectors = False
    DoCmd.Close acForm, priv, acSaveYes
    DoCmd.Rename "frm_GLAVNI_MENI", acForm, priv
    gForm = gForm + 1
    Exit Sub
Greska:
    Beleska "  glavni meni nije napravljen: " & Err.Description
    Err.Clear
End Sub

' ================================================================
'  GLAVNA PROCEDURA - pokrenuti je (kursor u njoj, pa F5)
' ================================================================
Public Sub KreirajSve()
    Dim t0 As Single
    On Error GoTo Greska
    t0 = Timer
    gTab = 0: gUpit = 0: gForm = 0: gIzv = 0
    gVeza = 0: gRed = 0: gGreske = 0
    gPoruke = ""
    DoCmd.SetWarnings False
    Beleska "--- TV Panorama: kreiranje baze ---"
    Beleska "> brisanje postojecih objekata"
    ObrisiSve
    Beleska "> recnik natpisa"
    PuniRecnik
    Beleska "> tabele"
    Tabele1
    Tabele2
    Tabele3
    CurrentDb.TableDefs.Refresh
    Beleska "> primarni kljucevi"
    Kljucevi1
    Kljucevi2
    Beleska "> veze"
    Veze1
    Veze2
    Veze3
    Beleska "> upiti"
    Upiti1
    Upiti2
    Upiti3
    Beleska "> demo podaci"
    DemoPodaci1
    DemoPodaci2
    DemoPodaci3
    DemoPodaci4
    DemoPodaci5
    DemoPodaci6
    Beleska "> forme"
    Forme1
    Forme2
    Forme3
    Beleska "> izvestaji"
    Izvestaji
    Beleska "> glavni meni"
    GlavniMeni
    Application.RefreshDatabaseWindow
    DoCmd.SetWarnings True
    Beleska "--- gotovo ---"
    MsgBox "Baza je kreirana." & vbCrLf & vbCrLf & _
           "tabela: " & gTab & vbCrLf & _
           "veza: " & gVeza & vbCrLf & _
           "upita: " & gUpit & vbCrLf & _
           "formi: " & gForm & vbCrLf & _
           T("izve~staja: ") & gIzv & vbCrLf & _
           "demo redova: " & gRed & vbCrLf & _
           "upozorenja: " & gGreske & vbCrLf & vbCrLf & _
           "Trajanje: " & Format(Timer - t0, "0.0") & " s", _
           vbInformation, APP_NAZIV
    Exit Sub
Greska:
    DoCmd.SetWarnings True
    MsgBox "Prekid u koraku kreiranja:" & vbCrLf & _
           Err.Number & " - " & Err.Description, vbCritical, APP_NAZIV
End Sub

' Ispis dnevnika poslednjeg pokretanja u Immediate prozor (Ctrl+G).
Public Sub Dnevnik()
    Debug.Print gPoruke
End Sub
