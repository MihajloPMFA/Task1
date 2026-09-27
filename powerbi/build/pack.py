# -*- coding: utf-8 -*-
import json, zipfile, os, sys
schema=json.load(open('DataModelSchema.json'))
L=json.load(open('Layout.json'))

cols={t['name']:{c['name'] for c in t['columns']} for t in schema['model']['tables']}
meas={m['name'] for t in schema['model']['tables'] for m in t.get('measures',[])}
err=[]
for s in L['sections']:
    for vc in s['visualContainers']:
        cfg=json.loads(vc['config']); sv=cfg['singleVisual']
        pq=sv.get('prototypeQuery')
        if not pq: continue
        alias={f['Name']:f['Entity'] for f in pq['From']}
        for e in alias.values():
            if e not in cols: err.append(f"{s['displayName']}: nepoznata tabela {e}")
        names=set()
        for sel in pq['Select']:
            key='Measure' if 'Measure' in sel else 'Column'
            src=sel[key]['Expression']['SourceRef']['Source']; prop=sel[key]['Property']
            ent=alias.get(src); names.add(sel['Name'])
            if key=='Measure':
                if prop not in meas: err.append(f"{s['displayName']}: nema mere '{prop}'")
            else:
                if ent in cols and prop not in cols[ent]:
                    err.append(f"{s['displayName']}: {ent} nema kolonu {prop}")
        for role,items in sv['projections'].items():
            for it in items:
                if it['queryRef'] not in names:
                    err.append(f"{s['displayName']}: projekcija {role} -> {it['queryRef']} nije u Select")
if err:
    print("GRESKE:"); [print("  -",e) for e in err]; sys.exit(1)
print("Validacija rasporeda: OK (sve reference postoje u modelu)")

# ---------------- pakovanje .pbit ----------------
def u16(s): return s.encode('utf-16-le')
def u16bom(s): return b'\xff\xfe' + s.encode('utf-16-le')

CT = ('<?xml version="1.0" encoding="utf-8"?>'
 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 '<Default Extension="json" ContentType="" />'
 '<Override PartName="/Version" ContentType="" />'
 '<Override PartName="/Report/Layout" ContentType="" />'
 '<Override PartName="/Settings" ContentType="" />'
 '<Override PartName="/Metadata" ContentType="" />'
 '<Override PartName="/DataModelSchema" ContentType="" />'
 '<Override PartName="/DiagramLayout" ContentType="" />'
 '</Types>')

DIAGRAM = {"version":"1.1.0","diagrams":[{"ordinal":0,"scrollPosition":{"x":0,"y":0},
  "nodes":[{"location":{"x":i%6*220,"y":i//6*180},"nodeIndex":t['name'],"nodeLineageTag":t.get('lineageTag',''),
            "size":{"height":150,"width":200},"zIndex":i}
           for i,t in enumerate(schema['model']['tables'])],
  "name":"All tables","zoomValue":100,"pinKeyFieldsToTop":False,"showExtraHeaderInfo":False,
  "hideKeyFieldsWhenCollapsed":False,"tablesLocked":False}],"selectedDiagram":"All tables",
  "defaultDiagram":"All tables"}

def write_pbit(path, schema_obj, note):
    j=lambda o: json.dumps(o, ensure_ascii=False)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr('[Content_Types].xml', b'\xef\xbb\xbf'+CT.encode('utf-8'))
        z.writestr('Version', u16('1.28'))
        z.writestr('DataModelSchema', u16bom(j(schema_obj)))
        z.writestr('DiagramLayout', u16bom(j(DIAGRAM)))
        z.writestr('Report/Layout', u16bom(j(L)))
        z.writestr('Settings', u16(j({"Version":4,"ReportSettings":{},
                    "QueriesSettings":{"TypeDetectionEnabled":False,"RelationshipImportEnabled":False,"Version":"2.130.0.0"}})))
        z.writestr('Metadata', u16(j({"Version":3,"AutoCreatedRelationships":[],
                    "FileDescription":note})))
    return os.path.getsize(path)

OUT='/home/user/Task1/powerbi'
n=write_pbit(os.path.join(OUT,'TV_stanica_Izvestaji.pbit'), schema,
             "TV stanica - 5 izvestaja (podaci ugradjeni u fajl)")
print(f"Napisano TV_stanica_Izvestaji.pbit  ({n/1024:.0f} KB)")
