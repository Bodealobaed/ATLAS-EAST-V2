"""Reproducible, explicitly bounded research calculations; no autonomous clinical inference."""
import io, re
import numpy as np
import pandas as pd
from PIL import Image

def parse_numeric(value):
    s=str(value).strip().replace('−','-').replace(' ','')
    s=re.sub(r'(?i)(µm|μm|mm|cm|nm|pf/n|pf|nf|hz|khz|ms|mv|v|%|kg|mg|g|°c)$','',s).strip()
    if re.fullmatch(r'[-+]?\d{1,3}(?:\.\d{3})+,\d+',s): s=s.replace('.','').replace(',','.')
    elif re.fullmatch(r'[-+]?\d+,\d+',s): s=s.replace(',','.')
    try: return float(s) if re.fullmatch(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',s) else np.nan
    except (ValueError,TypeError): return np.nan

def unique_column_names(headers):
    """Keep every extracted column, including blank and repeated PDF headers."""
    seen=set(); result=[]
    for i, raw in enumerate(headers):
        base=str(raw).strip() if raw is not None else ''
        base=base or f'Column {i+1}'
        candidate=base; n=2
        while candidate in seen:
            candidate=f'{base} ({n})'; n+=1
        seen.add(candidate); result.append(candidate)
    return result

def table_insights(rows):
    """Only arithmetic summaries, not claims of significance or causal relationships."""
    if not rows: return [],pd.DataFrame()
    # PDF tables often contain duplicate/empty headings and ragged rows.
    width=max((len(row) if isinstance(row,(list,tuple)) else 1 for row in rows),default=0)
    header=list(rows[0]) if isinstance(rows[0],(list,tuple)) else [rows[0]]
    header=header+[f'Column {i+1}' for i in range(len(header),width)]
    names=unique_column_names(header)
    body=rows[1:] if len(rows)>1 else []
    normalized=[(list(row) if isinstance(row,(list,tuple)) else [row])[:width] for row in body]
    normalized=[row+[None]*(width-len(row)) for row in normalized]
    frame=pd.DataFrame(normalized,columns=names)
    out=[]
    for col in frame.columns:
        series=frame[col].map(parse_numeric).dropna()
        if len(series)<2: continue
        vals=series.to_numpy(dtype=float)
        out.append({'column':str(col),'n':len(vals),'min':float(np.min(vals)),'max':float(np.max(vals)),'mean':float(np.mean(vals)),'median':float(np.median(vals)),'std_sample':float(np.std(vals,ddof=1)),'unit':'as in source (verify)','status':'Descriptive arithmetic only; verify extracted cells, units, and independence.'})
    return out,frame

def simulate_linear(x0, rate, steps, step_size):
    """User-defined hypothetical sensitivity scenario, never fitted from PDF or clinical data."""
    xs=np.arange(int(steps)+1,dtype=float)*float(step_size)
    return pd.DataFrame({'input_delta':xs,'hypothetical_output':float(x0)+float(rate)*xs})

def image_measurements(blob):
    """Pixel-only diagnostics; not chart digitization or disease segmentation."""
    im=Image.open(io.BytesIO(blob)).convert('L')
    a=np.asarray(im,dtype=np.float32)
    return {'width_px':int(a.shape[1]),'height_px':int(a.shape[0]),'mean_gray_0_255':round(float(a.mean()),2),'std_gray':round(float(a.std()),2),'min_gray':int(a.min()),'max_gray':int(a.max())}

def threshold_mask(blob, threshold=128, invert=False):
    """Exploratory threshold-based pixel selection; never anatomical segmentation."""
    im=Image.open(io.BytesIO(blob)).convert('L')
    a=np.asarray(im,dtype=np.uint8)
    mask=a<int(threshold) if invert else a>=int(threshold)
    output=Image.fromarray((mask*255).astype('uint8'))
    b=io.BytesIO();output.save(b,format='PNG')
    return b.getvalue(),{'selected_pixels':int(mask.sum()),'fraction_selected':round(float(mask.mean()),5)}


def scenario_summary(curve,language='English'):
    """Deterministic interpretation of a user-defined scenario, not evidence from a thesis."""
    start=float(curve['hypothetical_output'].iloc[0]); end=float(curve['hypothetical_output'].iloc[-1]); delta=end-start
    span=float(curve['input_delta'].iloc[-1]-curve['input_delta'].iloc[0])
    if language=='Deutsch':
        return f'Im hypothetischen linearen Modell ändert sich die Ausgabe von {start:.5g} auf {end:.5g} (Differenz {delta:+.5g}) über eine Eingabespanne von {span:.5g}. Diese Änderung folgt ausschließlich aus den gewählten Parametern; sie ist weder ein experimentelles Ergebnis noch ein validierter physikalischer Befund. Für wissenschaftliche Schlussfolgerungen sind Einheiten, Messdaten, Modellannahmen und Unsicherheiten erforderlich.'
    if language=='العربية':
        return f'في النموذج الخطي الافتراضي يتغير الناتج من {start:.5g} إلى {end:.5g} (الفرق {delta:+.5g}) عبر مجال إدخال مقداره {span:.5g}. هذه النتيجة حسابية ناتجة فقط عن المعلمات المختارة، وليست نتيجة تجريبية أو إثباتًا فيزيائيًا. لاستخلاص نتيجة علمية يلزم تحديد الوحدات، والبيانات المقاسة، وافتراضات النموذج، وعدم اليقين.'
    return f'In this hypothetical linear scenario, output changes from {start:.5g} to {end:.5g} (difference {delta:+.5g}) over an input span of {span:.5g}. This follows solely from the selected parameters; it is not an experimental finding or a validated physical conclusion. Scientific inference requires units, measured data, model assumptions and uncertainty estimates.'
