# -*- coding: utf-8 -*-
"""Staticki delovi VBA modula modIzvestaji.  Cist ASCII."""

ZAGLAVLJE = r'''Attribute VB_Name = "modIzvestaji"
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
'''
