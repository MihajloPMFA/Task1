# Generator izveštaja

Skripte kojima su `.pbit` fajlovi napravljeni iz `Access_v3.accdb`.
Redosled pokretanja (potreban Python 3.11+ i `pip install access-parser`):

| Korak | Skripta | Šta radi |
|---|---|---|
| 1 | `extract.py` | Čita `.accdb`, konvertuje tipove (Currency ÷ 10.000, datumi u ISO) → `/tmp/model.json` |
| 2 | `prep.py` | Dodaje izvedene kolone (Godina/Kvartal/Mesec), denormalizuje nazive, gradi `Kalendar` |
| 3 | `rels.py` | Validira ključeve i gradi veze; union-find sprečava dvosmislene putanje |
| 4 | `pbit.py` | Gradi `DataModelSchema` sa podacima ugrađenim kao deflate+base64 u M upite |
| 5 | `layout.py` | Gradi `Report/Layout` — 5 stranica × 9 vizuala |
| 6 | `pack.py` | Validira sve reference i pakuje `.pbit` (UTF-16LE delovi u ZIP-u) |
| 7 | `live.py` | Ista šema, ali M upiti čitaju iz Accessa preko parametra putanje |

U `extract.py` i `prep.py` je putanja do `.accdb` upisana direktno — promeni je ako pokrećeš ponovo.
