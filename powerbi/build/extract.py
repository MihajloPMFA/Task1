import contextlib, io, json, datetime, re
from access_parser import AccessParser

SRC="/root/.claude/uploads/9a351302-edaf-538b-9743-c5208465cbfb/a3d4b9e9-Access_v3.accdb"
db = AccessParser(SRC)

JET = {1:"bool",2:"byte",3:"int",4:"long",5:"currency",6:"single",7:"double",8:"datetime",
       9:"binary",10:"text",11:"ole",12:"memo",15:"guid",16:"bigint",20:"decimal"}

def quiet(fn,*a,**k):
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        return fn(*a,**k)

tables=[t for t in sorted(db.catalog) if not t.startswith('MSys') and not t.startswith('f_')]
model={}
for t in tables:
    try:
        tb = quiet(db.get_table, t)
        data = quiet(db.parse_table, t)
    except Exception as e:
        print("SKIP",t,e); continue
    meta=[]
    for idx in sorted(tb.columns):
        c=tb.columns[idx]
        nm=str(c.col_name_str)
        cap=(c.extra_props or {}).get('Caption') or ''
        meta.append({"name":nm,"jet":int(c.type),"kind":JET.get(int(c.type),str(c.type)),"caption":cap})
    order=[m["name"] for m in meta if m["name"] in data]
    n=len(data[order[0]]) if order else 0
    rows=[]
    for i in range(n):
        row=[]
        for m in meta:
            if m["name"] not in data: continue
            v=data[m["name"]][i]
            k=m["kind"]
            if v is None or v=="": row.append(None); continue
            try:
                if k=="currency":
                    row.append(round(int(str(v))/10000.0,4))
                elif k in ("int","long","byte","bigint"):
                    row.append(int(v))
                elif k in ("single","double","decimal"):
                    row.append(float(v))
                elif k=="bool":
                    row.append(bool(v))
                elif k=="datetime":
                    s=str(v)
                    dt=datetime.datetime.strptime(s[:19],"%Y-%m-%d %H:%M:%S")
                    if dt.year==1899:
                        row.append(dt.strftime("%H:%M:%S")); m["istime"]=True
                    else:
                        row.append(dt.strftime("%Y-%m-%d"))
                else:
                    row.append(str(v))
            except Exception:
                row.append(str(v))
        rows.append(row)
    model[t]={"columns":[m for m in meta if m["name"] in data],"rows":rows}
    print(f"{t}: {len(rows)} rows, {len(model[t]['columns'])} cols")

json.dump(model, open('/tmp/model.json','w'), ensure_ascii=False)
print("\nWROTE /tmp/model.json")
# currency + datetime overview
print("\nCURRENCY COLUMNS:")
for t,v in model.items():
    cur=[c['name'] for c in v['columns'] if c['kind']=='currency']
    if cur: print(" ",t,cur)
