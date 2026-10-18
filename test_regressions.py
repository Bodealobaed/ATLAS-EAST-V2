from pathlib import Path
import ast,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from i18n import tr, MESSAGES
from science import table_insights, unique_column_names, simulate_linear
for name in ('app.py','analyzer.py','book.py','i18n.py','medical.py','report.py','science.py'):
    ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
app=(ROOT/'app.py').read_text(encoding='utf-8')
assert 'T[k]' not in app
assert 'V2.2' not in app
assert 'tab_names=[T(k)' in app
for language in ('العربية','Deutsch','English'):
    for key in ('summary','methods','results','tables','figures','medical','simulation','refs','export','upload','book_studio'):
        assert isinstance(tr(key,language),str) and tr(key,language).strip(),(language,key)
assert len(unique_column_names(['x','x','','x']))==4
insights,df=table_insights([['Value','Value',''],['1','2','3'],['4','5','6']])
assert df.columns.is_unique and len(insights)==3
assert list(simulate_linear(1,.5,2,1)['hypothetical_output'])==[1.,1.5,2.]
print('PASS: syntax, translations, tabs, table headings, descriptive statistics, linear scenario')
