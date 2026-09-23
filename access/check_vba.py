# -*- coding: utf-8 -*-
"""Gruba provera Option Explicit: svaki identifikator u proceduri mora biti
deklarisan (Dim/Const/parametar), globalna promenljiva, druga procedura ovog
modula ili poznata VBA/Access ugradjena rec."""
import io, re, sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
txt = io.open(os.path.join(BASE, 'TV_Stanica_Access.bas'), encoding='latin-1').read()
txt = txt.replace('\r\n', '\n')

# spoj nastavke linija
txt = re.sub(r' _\n\s*', ' ', txt)
lines = txt.split('\n')

UGRADJENO = set("""
Abs And As Array Asc AscW Attribute Boolean ByRef ByVal Byte Call Case ChrW Chr CInt CLng CDbl CStr CVar
Const Currency Date DateAdd DateDiff DateSerial Day Debug Dim Do Double Each Else ElseIf Empty End
Eqv Erase Err Error Exit False For Format Function Get Global GoTo If Imp In InStr InStrRev Int
Integer Is IsNull IsNumeric IsDate IIf Len Let Like Loop LBound LCase Left Long Loop Me Mid Mod
Month MsgBox New Next Not Nothing Now Null Object On Option Optional Or Preserve Print Private
Property Public ReDim Rem Replace Resume Return Right RGB Round Select Set Single Space Split Static
Step Stop String Sub Then Time Timer To Trim True Type UBound UCase Until Val Variant Wend While
With Xor Year Str CBool CDate CCur Choose Switch Environ Nz DLookup DCount DSum DMax DMin Rnd
Application CurrentDb CurrentProject DoCmd Forms Reports Screen CreateObject GetObject
CreateForm CreateReport CreateControl CreateReportControl CreateGroupLevel DeleteControl
vbCrLf vbCr vbLf vbTab vbNullString vbInformation vbCritical vbExclamation vbQuestion vbOKOnly
vbYesNo vbYes vbNo vbBinaryCompare vbTextCompare vbDatabaseCompare
acForm acReport acTable acQuery acDetail acHeader acFooter acPageHeader acPageFooter
acGroupLevel1Header acGroupLevel1Footer acGroupLevel2Header acGroupLevel2Footer
acLabel acTextBox acCommandButton acLine acObjectFrame acSubform acRectangle
acSaveYes acSaveNo acViewDesign acViewPreview acViewNormal acNormal acHidden
dbText dbLong dbInteger dbDouble dbCurrency dbDate dbMemo dbBoolean dbByte dbSingle
dbFailOnError dbRelationUpdateCascade dbRelationDeleteCascade dbRelationDontEnforce
dbRelationUnique dbRelationLeft dbRelationRight dbAppendOnly dbOpenDynaset dbOpenSnapshot
DAO Database TableDef QueryDef Field Index Relation Recordset Form Report Control Printer
Orientation
""".split())

proc_re = re.compile(r'^\s*(?:Public |Private )?(Sub|Function) (\w+)\s*\((.*?)\)', re.I)
# imena procedura u modulu
proc_imena = set(re.findall(r'(?m)^\s*(?:Public |Private )?(?:Sub|Function) (\w+)', txt))
# globalne
glob = set()
for m in re.finditer(r'(?m)^Private (?:Const )?(.+)$', txt):
    telo = m.group(1)
    if telo.startswith(('Sub ', 'Function ', 'Property ')):
        continue
    for v in re.findall(r'\b(\w+)\s+As\s+\w+', telo):
        glob.add(v)
    for v in re.findall(r'(?:^|,)\s*(\w+)\s*(?:As|=)', telo):
        glob.add(v)

greske = []
i = 0
while i < len(lines):
    m = proc_re.match(lines[i])
    if not m:
        i += 1
        continue
    kraj = 'End ' + m.group(1)
    j = i + 1
    while j < len(lines) and lines[j].strip().lower() != kraj.lower():
        j += 1
    telo = lines[i:j + 1]
    lokalne = set(re.findall(r'\b(\w+)\s+As\s+\w+', m.group(3)))
    lokalne.add(m.group(2))
    for l in telo:
        for v in re.findall(r'(?m)^\s*(?:Dim|Static|Const|ReDim)\s+(.+)$', l):
            for x in re.findall(r'\b(\w+)\s*(?:\(\s*\))?\s*(?:As|=|,|$)', v):
                lokalne.add(x)
        for v in re.findall(r'(?m)^(\w+):\s*$', l):   # labele
            lokalne.add(v)
    for n, l in enumerate(telo):
        kod = re.sub(r'"[^"]*"', '""', l)
        kod = re.sub(r"'.*$", '', kod)
        if re.match(r'\s*(Dim|Const|Static|ReDim|Attribute|Option)\b', kod):
            continue
        for w in re.findall(r'(?<![\.\w$#\[])\b([A-Za-z_]\w*)\b', kod):
            if w in lokalne or w in glob or w in proc_imena or w in UGRADJENO:
                continue
            greske.append('%s:%d  %s   << %s' % (m.group(2), n, l.strip()[:90], w))
    i = j + 1

if greske:
    print('SUMNJIVI IDENTIFIKATORI (%d):' % len(greske))
    for g in greske[:60]:
        print('  ' + g)
    sys.exit(1)
print('Option Explicit: svi identifikatori prepoznati')
