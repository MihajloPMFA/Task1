# -*- coding: utf-8 -*-
"""Staticki delovi VBA modula (pomocne procedure).  Cist ASCII."""

ZAGLAVLJE = r'''Option Compare Database
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
'''

FORME_IZVESTAJI = r'''
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
'''
