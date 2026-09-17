# -*- coding: utf-8 -*-
"""Generator .vsdx (Visio 2013+) paketa za PMOV dijagram.
Oblici su definisani inline (bez zavisnosti od stencil-a), pa se fajl otvara
u Microsoft Visio-u bez dodatnih biblioteka oblika.
"""
import zipfile, datetime, math, html
import layout
from layout import PAGE_W, PAGE_H
from geom import *

ORANGE, SUBFILL, WHITE = '#f59d56', '#fbd9b6', '#ffffff'
FONT = 'Arial'
NS = ("xmlns='http://schemas.microsoft.com/office/visio/2012/main' "
      "xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' "
      "xml:space='preserve'")
HDR = "<?xml version='1.0' encoding='utf-8' ?>\n"
esc = lambda s: html.escape(s, quote=True)
f = lambda v: ('%.6f' % v).rstrip('0').rstrip('.') if isinstance(v, float) else str(v)

def C(n, v, u=None):
    return "<Cell N='%s' V='%s'%s/>" % (n, v, (" U='%s'" % u) if u else '')

def char_sec(size_pt, style=0, color='#000000', font=FONT):
    return ("<Section N='Character'><Row IX='0'>"
            + C('Font', font) + C('Color', color) + C('Style', style)
            + C('Size', f(size_pt/72.0)) + "</Row></Section>")

def para_sec(align=1):
    return "<Section N='Paragraph'><Row IX='0'>" + C('HorzAlign', align) + "</Row></Section>"

def text_el(s):
    return "<Text><cp IX='0'/>%s</Text>" % esc(s).replace('\n', '<![CDATA[\n]]>') if False else \
           "<Text><cp IX='0'/>%s</Text>" % esc(s)

def geom_rect(w, h):
    r = ["<Section N='Geometry' IX='0'>", C('NoFill', 0), C('NoLine', 0)]
    pts = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
    r.append("<Row T='MoveTo' IX='1'>%s%s</Row>" % (C('X', f(pts[0][0])), C('Y', f(pts[0][1]))))
    for i, (x, y) in enumerate(pts[1:], start=2):
        r.append("<Row T='LineTo' IX='%d'>%s%s</Row>" % (i, C('X', f(x)), C('Y', f(y))))
    r.append("</Section>")
    return ''.join(r)

def geom_diamond(w, h):
    pts = [(w/2, 0), (w, h/2), (w/2, h), (0, h/2), (w/2, 0)]
    r = ["<Section N='Geometry' IX='0'>", C('NoFill', 0), C('NoLine', 0),
         "<Row T='MoveTo' IX='1'>%s%s</Row>" % (C('X', f(pts[0][0])), C('Y', f(pts[0][1])))]
    for i, (x, y) in enumerate(pts[1:], start=2):
        r.append("<Row T='LineTo' IX='%d'>%s%s</Row>" % (i, C('X', f(x)), C('Y', f(y))))
    r.append("</Section>")
    return ''.join(r)

def geom_ellipse(w, h):
    """Elipsa kao MoveTo + dva EllipticalArcTo (identicna sintaksa kao Visio stencil)."""
    ratio = f(w/h) if h else '1'
    return ("<Section N='Geometry' IX='0'>" + C('NoFill', 0) + C('NoLine', 0)
            + "<Row T='MoveTo' IX='1'>" + C('X', 0) + C('Y', f(h/2)) + "</Row>"
            + "<Row T='EllipticalArcTo' IX='2'>" + C('X', f(w)) + C('Y', f(h/2))
            + C('A', f(w/2), 'DL') + C('B', f(h), 'DL') + C('C', 0) + C('D', ratio)
            + "</Row>"
            + "<Row T='EllipticalArcTo' IX='3'>" + C('X', 0) + C('Y', f(h/2))
            + C('A', f(w/2), 'DL') + C('B', 0, 'DL') + C('C', 0) + C('D', ratio)
            + "</Row></Section>")

def geom_poly(pts):
    r = ["<Section N='Geometry' IX='0'>", C('NoFill', 1), C('NoLine', 0),
         "<Row T='MoveTo' IX='1'>%s%s</Row>" % (C('X', f(pts[0][0])), C('Y', f(pts[0][1])))]
    for i, (x, y) in enumerate(pts[1:], start=2):
        r.append("<Row T='LineTo' IX='%d'>%s%s</Row>" % (i, C('X', f(x)), C('Y', f(y))))
    r.append("</Section>")
    return ''.join(r)

class Page:
    def __init__(self):
        self.shapes = []
        self.next_id = 1

    def _sid(self):
        i = self.next_id; self.next_id += 1; return i

    def box(self, x, y, w, h, kind='rect', text='', fill=WHITE, size=9.5, style=0,
            line_w=0.01041666666666667, line_pat=1, name='Shape', tscale=None):
        i = self._sid()
        cells = [C('PinX', f(x)), C('PinY', f(y)), C('Width', f(w)), C('Height', f(h)),
                 C('LocPinX', f(w/2)), C('LocPinY', f(h/2)), C('Angle', 0),
                 C('FlipX', 0), C('FlipY', 0), C('ResizeMode', 0),
                 C('LineWeight', f(line_w), 'PT'), C('LineColor', '#000000'),
                 C('LinePattern', line_pat), C('FillForegnd', fill),
                 C('FillBkgnd', '#ffffff'), C('FillPattern', 1),
                 C('LeftMargin', 0, 'PT'), C('RightMargin', 0, 'PT'),
                 C('TopMargin', 0, 'PT'), C('BottomMargin', 0, 'PT'),
                 C('VerticalAlign', 1), C('ObjType', 1)]
        if tscale:
            tw, th = w*tscale[0], h*tscale[1]
            cells += [C('TxtWidth', f(tw)), C('TxtHeight', f(th)),
                      C('TxtPinX', f(w/2)), C('TxtPinY', f(h/2)),
                      C('TxtLocPinX', f(tw/2)), C('TxtLocPinY', f(th/2)), C('TxtAngle', 0)]
        geom = {'rect': geom_rect, 'diamond': geom_diamond, 'ellipse': geom_ellipse}[kind](w, h)
        conn = ("<Section N='Connection'>"
                + "<Row T='Connection' IX='0'>%s%s</Row>" % (C('X', f(w/2)), C('Y', f(h)))
                + "<Row T='Connection' IX='1'>%s%s</Row>" % (C('X', f(w)), C('Y', f(h/2)))
                + "<Row T='Connection' IX='2'>%s%s</Row>" % (C('X', f(w/2)), C('Y', 0))
                + "<Row T='Connection' IX='3'>%s%s</Row>" % (C('X', 0), C('Y', f(h/2)))
                + "</Section>")
        s = ("<Shape ID='%d' NameU='%s.%d' Name='%s.%d' Type='Shape' LineStyle='0' "
             "FillStyle='0' TextStyle='0'>" % (i, name, i, name, i)
             + ''.join(cells) + conn + char_sec(size, style) + para_sec() + geom
             + (text_el(text) if text else '') + "</Shape>")
        self.shapes.append(s); return i

    def label(self, x, y, w, h, text, size=7.0, style=0, align=1, color='#000000'):
        i = self._sid()
        cells = [C('PinX', f(x)), C('PinY', f(y)), C('Width', f(w)), C('Height', f(h)),
                 C('LocPinX', f(w/2)), C('LocPinY', f(h/2)), C('Angle', 0),
                 C('FlipX', 0), C('FlipY', 0), C('LineWeight', 0, 'PT'),
                 C('LinePattern', 0), C('FillPattern', 0),
                 C('LeftMargin', 0, 'PT'), C('RightMargin', 0, 'PT'),
                 C('TopMargin', 0, 'PT'), C('BottomMargin', 0, 'PT'),
                 C('VerticalAlign', 1), C('ObjType', 1)]
        s = ("<Shape ID='%d' NameU='Text.%d' Name='Text.%d' Type='Shape' LineStyle='0' "
             "FillStyle='0' TextStyle='0'>" % (i, i, i)
             + ''.join(cells) + char_sec(size, style, color) + para_sec(align)
             + geom_rect(w, h).replace("<Cell N='NoLine' V='0'/>", "<Cell N='NoLine' V='1'/>")
                              .replace("<Cell N='NoFill' V='0'/>", "<Cell N='NoFill' V='1'/>")
             + text_el(text) + "</Shape>")
        self.shapes.append(s); return i

    def polyline(self, pts, weight=0.01041666666666667):
        """1-D linijski oblik po Visio konvenciji: lokalno poreklo = pocetna tacka,
        Pin = sredina Begin-End, Width/Height = End-Begin, Angle = 0."""
        i = self._sid()
        bx, by = pts[0]; ex, ey = pts[-1]
        w, h = ex - bx, ey - by
        loc = [(px - bx, py - by) for px, py in pts]
        cells = [C('PinX', f((bx+ex)/2.0)), C('PinY', f((by+ey)/2.0)),
                 C('Width', f(w)), C('Height', f(h)),
                 C('LocPinX', f(w/2.0)), C('LocPinY', f(h/2.0)),
                 C('Angle', 0), C('FlipX', 0), C('FlipY', 0), C('ResizeMode', 0),
                 C('BeginX', f(bx)), C('BeginY', f(by)),
                 C('EndX', f(ex)), C('EndY', f(ey)),
                 C('LineWeight', f(weight), 'PT'), C('LineColor', '#000000'),
                 C('LinePattern', 1), C('LineCap', 0),
                 C('BeginArrow', 0), C('EndArrow', 0),
                 C('FillPattern', 0), C('ObjType', 2), C('NoLiveDynamics', 1),
                 C('DynFeedback', 0), C('GlueType', 0), C('LockHeight', 0),
                 C('NoAlignBox', 1)]
        rows = ["<Row T='MoveTo' IX='1'>%s%s</Row>" % (C('X', f(loc[0][0])), C('Y', f(loc[0][1])))]
        for k, (lx, ly) in enumerate(loc[1:], start=2):
            rows.append("<Row T='LineTo' IX='%d'>%s%s</Row>" % (k, C('X', f(lx)), C('Y', f(ly))))
        geom = ("<Section N='Geometry' IX='0'>" + C('NoFill', 1) + C('NoLine', 0)
                + ''.join(rows) + "</Section>")
        s_ = ("<Shape ID='%d' NameU='Veza.%d' Name='Veza.%d' Type='Shape' LineStyle='0' "
              "FillStyle='0' TextStyle='0'>" % (i, i, i) + ''.join(cells) + geom + "</Shape>")
        self.shapes.append(s_); return i

    def xml(self):
        return (HDR + "<PageContents %s><Shapes>" % NS + ''.join(self.shapes)
                + "</Shapes></PageContents>")

# ---------------------------------------------------------------- emit + pakovanje
def emit_page():
    S, L = layout.build_all()
    p = Page()
    for li in L:                                    # linije ispod oblika
        p.polyline(li['pts'])
    for d in S:
        x, y, w, h, t, tx = d['x'], d['y'], d['w'], d['h'], d['t'], d['text']
        if t == 'rect':
            fill = ORANGE
            if d.get('inner'): fill = WHITE
            elif d.get('sub'): fill = SUBFILL
            p.box(x, y, w, h, 'rect', tx, fill=fill, size=9.5, style=1,
                  name='Entitet', tscale=(0.95, 0.9))
        elif t == 'ellipse':
            p.box(x, y, w, h, 'ellipse', tx, fill=WHITE, size=7.0,
                  style=(4 if d.get('pk') else 0),
                  line_pat=(2 if d.get('der') else 1),
                  name='Atribut', tscale=(0.84, 0.86))
        elif t == 'diamond':
            p.box(x, y, w, h, 'diamond', tx, fill=WHITE, size=7.6, style=0,
                  name='Veza', tscale=(0.66, 0.62))
        elif t == 'sdiamond':
            p.box(x, y, w, h, 'diamond', tx, fill=WHITE, size=8.5, style=1,
                  name='Specijalizacija', tscale=(0.8, 0.8))
        elif t == 'circle':
            p.box(x, y, w, h, 'ellipse', '', fill=WHITE, name='Krug')
        elif t == 'card':
            p.label(x, y, w, h, tx, size=6.8)
        elif t == 'title':
            p.label(x, y, w, h, tx, size=30, style=1)
        elif t == 'subtitle':
            p.label(x, y, w, h, tx, size=13)
        elif t == 'frame':
            p.box(x, y, w, h, 'rect', '', fill='#fdf3e8', name='Legenda')
        elif t == 'legend':
            p.label(x, y, w, h, tx, size=12.5, style=1)
        elif t == 'leglbl':
            p.label(x, y, w, h, tx, size=9.8, align=0)
        elif t == 'cardbig':
            p.label(x, y, w, h, tx, size=9.8)
        elif t == 'bandlbl':
            p.box(x, y, w, h, 'rect', tx, fill='#fdf3e8', size=15, style=1,
                  name='Celina', tscale=(0.92, 0.9))
    return p

STYLE0 = ("<StyleSheet ID='0' NameU='PMOV' Name='PMOV'>"
          + C('EnableLineProps', 1) + C('EnableFillProps', 1) + C('EnableTextProps', 1)
          + C('HideForApply', 0)
          + C('LineWeight', 0.01041666666666667) + C('LineColor', '#000000')
          + C('LinePattern', 1) + C('Rounding', 0) + C('EndArrowSize', 2)
          + C('BeginArrow', 0) + C('EndArrow', 0) + C('LineCap', 0)
          + C('BeginArrowSize', 2) + C('LineColorTrans', 0) + C('CompoundType', 0)
          + C('FillForegnd', '#ffffff') + C('FillBkgnd', '#ffffff') + C('FillPattern', 1)
          + C('ShdwForegnd', '#000000') + C('ShdwPattern', 0)
          + C('FillForegndTrans', 0) + C('FillBkgndTrans', 0) + C('ShdwForegndTrans', 0)
          + C('ShapeShdwType', 0) + C('ShapeShdwOffsetX', 0) + C('ShapeShdwOffsetY', 0)
          + C('ShapeShdwObliqueAngle', 0) + C('ShapeShdwScaleFactor', 1)
          + C('ShapeShdwBlur', 0) + C('ShapeShdwShow', 0)
          + C('LeftMargin', 0) + C('RightMargin', 0) + C('TopMargin', 0)
          + C('BottomMargin', 0) + C('VerticalAlign', 1) + C('TextBkgnd', 0)
          + C('DefaultTabStop', 0.5) + C('TextDirection', 0) + C('TextBkgndTrans', 0)
          + C('LockWidth', 0) + C('LockHeight', 0) + C('LockMoveX', 0) + C('LockMoveY', 0)
          + C('LockAspect', 0) + C('LockDelete', 0) + C('LockBegin', 0) + C('LockEnd', 0)
          + C('LockRotate', 0) + C('LockCrop', 0) + C('LockVtxEdit', 0)
          + C('LockTextEdit', 0) + C('LockFormat', 0) + C('LockGroup', 0)
          + C('LockCalcWH', 0) + C('LockSelect', 0) + C('LockCustProp', 0)
          + C('LockFromGroupFormat', 0) + C('LockThemeColors', 0)
          + C('LockThemeEffects', 0) + C('LockReplace', 0)
          + "<Section N='Character'><Row IX='0'>"
          + C('Font', FONT) + C('Color', '#000000') + C('Style', 0)
          + C('Case', 0) + C('Pos', 0) + C('FontScale', 1)
          + C('Size', 0.1111111111111111) + C('DblUnderline', 0)
          + C('Overline', 0) + C('Strikethru', 0)
          + C('DoubleStrikethrough', 0)
          + C('Letterspace', 0) + C('ColorTrans', 0) + C('AsianFont', 0)
          + C('ComplexScriptFont', 0) + C('LangID', 1033)
          + C('ComplexScriptSize', -1)
          + "</Row></Section>"
          + "<Section N='Paragraph'><Row IX='0'>"
          + C('IndFirst', 0) + C('IndLeft', 0) + C('IndRight', 0) + C('SpLine', -1.2)
          + C('SpBefore', 0) + C('SpAfter', 0) + C('HorzAlign', 1) + C('Bullet', 0)
          + C('BulletStr', '') + C('BulletFont', 0) + C('BulletFontSize', -1)
          + C('TextPosAfterBullet', 0) + C('Flags', 0)
          + "</Row></Section>"
          + "<Section N='Tabs'><Row IX='0'/></Section>"
          + "</StyleSheet>")

def doc_xml():
    return (HDR + "<VisioDocument %s>" % NS
            + "<DocumentSettings TopPage='0' DefaultTextStyle='0' DefaultLineStyle='0' "
              "DefaultFillStyle='0' DefaultGuideStyle='0'>"
              "<GlueSettings>9</GlueSettings><SnapSettings>65847</SnapSettings>"
              "<SnapExtensions>34</SnapExtensions><SnapAngles/>"
              "<DynamicGridEnabled>1</DynamicGridEnabled><ProtectStyles>0</ProtectStyles>"
              "<ProtectShapes>0</ProtectShapes><ProtectMasters>0</ProtectMasters>"
              "<ProtectBkgnds>0</ProtectBkgnds></DocumentSettings>"
            + "<Colors><ColorEntry IX='24' RGB='#F59D56'/><ColorEntry IX='25' RGB='#FBD9B6'/>"
              "<ColorEntry IX='26' RGB='#FFFFFF'/><ColorEntry IX='27' RGB='#000000'/></Colors>"
            + "<FaceNames><FaceName NameU='Arial' UnicodeRanges='-536858881 -1073711013 9 0' "
              "CharSets='1073742335 -65536' Panose='2 11 6 4 2 2 2 2 2 4' Flags='325'/>"
              "</FaceNames>"
            + "<StyleSheets>" + STYLE0 + "</StyleSheets>"
            + "<DocumentSheet NameU='TheDoc' LineStyle='0' FillStyle='0' TextStyle='0'>"
            + C('OutputFormat', 0) + C('LockPreview', 0) + C('AddMarkup', 0)
            + C('ViewMarkup', 0) + C('PreviewQuality', 0) + C('PreviewScope', 0)
            + C('DocLangID', 1033) + "</DocumentSheet>"
            + "</VisioDocument>")

def pages_xml():
    return (HDR + "<Pages %s>" % NS
            + "<Page ID='0' NameU='PMOV' Name='PMOV' ViewScale='-1' "
              "ViewCenterX='%s' ViewCenterY='%s'>" % (f(PAGE_W/2), f(PAGE_H/2))
            + "<PageSheet LineStyle='0' FillStyle='0' TextStyle='0'>"
            + C('PageWidth', f(PAGE_W)) + C('PageHeight', f(PAGE_H))
            + C('ShdwOffsetX', 0.125) + C('ShdwOffsetY', -0.125)
            + C('PageScale', 1, 'IN_F') + C('DrawingScale', 1, 'IN_F')
            + C('DrawingSizeType', 0) + C('DrawingScaleType', 0)
            + C('InhibitSnap', 0) + C('UIVisibility', 0) + C('ShdwType', 0)
            + C('ShdwObliqueAngle', 0) + C('ShdwScaleFactor', 1)
            + C('DrawingResizeType', 1) + C('RouteStyle', 1)
            + C('LineRouteExt', 1) + C('PageShapeSplit', 1)
            + C('PrintPageOrientation', 2)
            + "</PageSheet><Rel r:id='rId1'/></Page></Pages>")

def windows_xml():
    return (HDR + "<Windows ClientWidth='1600' ClientHeight='900' %s>" % NS
            + "<Window ID='0' WindowType='Drawing' WindowState='1073741824' "
              "WindowLeft='-4' WindowTop='-23' WindowWidth='1616' WindowHeight='990' "
              "ContainerType='Page' Page='0' ViewScale='-1' ViewCenterX='%s' "
              "ViewCenterY='%s'>" % (f(PAGE_W/2), f(PAGE_H/2))
            + "<ShowRulers>1</ShowRulers><ShowGrid>1</ShowGrid>"
              "<ShowPageBreaks>0</ShowPageBreaks><ShowGuides>1</ShowGuides>"
              "<ShowConnectionPoints>0</ShowConnectionPoints>"
              "<GlueSettings>9</GlueSettings><SnapSettings>65847</SnapSettings>"
              "<SnapExtensions>34</SnapExtensions><SnapAngles/>"
              "<DynamicGridEnabled>1</DynamicGridEnabled>"
              "<TabSplitterPos>0.5</TabSplitterPos></Window></Windows>")

CT = (HDR.replace("'", '"').replace('utf-8 ?', 'UTF-8" standalone="yes?')
      if False else
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/visio/document.xml" ContentType="application/vnd.ms-visio.drawing.main+xml"/>'
      '<Override PartName="/visio/pages/pages.xml" ContentType="application/vnd.ms-visio.pages+xml"/>'
      '<Override PartName="/visio/pages/page1.xml" ContentType="application/vnd.ms-visio.page+xml"/>'
      '<Override PartName="/visio/windows.xml" ContentType="application/vnd.ms-visio.windows+xml"/>'
      '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
      '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
      '</Types>')

RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/document" Target="visio/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>')

DOC_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/pages" Target="pages/pages.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.microsoft.com/visio/2010/relationships/windows" Target="windows.xml"/>'
            '</Relationships>')

PAGES_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
              '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/page" Target="page1.xml"/>'
              '</Relationships>')

def core_xml():
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:title>PMOV - Informacioni sistem televizijske stanice</dc:title>'
            '<dc:subject>Prosireni model objekti-veze izveden iz DFD i IDEF0 modela</dc:subject>'
            '<dc:description>Generisano iz DFD_16_09_2026__v12 i IDEF0_16_09_2026__v11</dc:description>'
            '<cp:keywords>PMOV;ER;TV stanica;emitovanje;produkcija;marketing;nabavka</cp:keywords>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
            '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
            '</cp:coreProperties>' % (now, now))

APP_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
           'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
           '<Application>Microsoft Visio</Application><AppVersion>15.0000</AppVersion>'
           '<Template></Template><Manager></Manager><Company></Company>'
           '<HyperlinkBase></HyperlinkBase></Properties>')

def write(path):
    page = emit_page()
    parts = {
        '[Content_Types].xml': CT,
        '_rels/.rels': RELS,
        'docProps/core.xml': core_xml(),
        'docProps/app.xml': APP_XML,
        'visio/document.xml': doc_xml(),
        'visio/_rels/document.xml.rels': DOC_RELS,
        'visio/pages/pages.xml': pages_xml(),
        'visio/pages/_rels/pages.xml.rels': PAGES_RELS,
        'visio/pages/page1.xml': page.xml(),
        'visio/windows.xml': windows_xml(),
    }
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, c in parts.items():
            z.writestr(n, c.encode('utf-8'))
    return path, len(page.shapes)

if __name__ == '__main__':
    import sys
    print(write(sys.argv[1]))
