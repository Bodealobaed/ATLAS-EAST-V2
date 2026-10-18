"""ATLAS EAST Research Intelligence — multilingual research workstation."""
import os, io, hashlib, base64
from i18n import tr
import streamlit as st
import pandas as pd
from analyzer import extract_document, extract_links, verify_links, analyze_with_ai, basic_analysis
from report import build_pdf
from science import table_insights, simulate_linear, image_measurements, threshold_mask, scenario_summary
from medical import read_medical_image
from book import create_book_content, build_book_pdf

st.set_page_config(page_title='ATLAS EAST | Research Intelligence',page_icon='🔬',layout='wide',initial_sidebar_state='expanded')
with st.sidebar:
    lang=st.selectbox('🌐 Language / Sprache / اللغة', ['العربية','Deutsch','English'],index=0,format_func=lambda x: {'العربية':'العربية','Deutsch':'Deutsch','English':'English'}[x],label_visibility='collapsed',key='interface_language')
def T(key): return tr(key,lang)
st.markdown("""<style>
/* ATLAS EAST: readable, calm, high-contrast multicolor identity */
html, body, [class*="css"], .stApp {font-size:17px}
.stApp{background:radial-gradient(ellipse at 90% 4%,#d8eeec 0%,transparent 42%),linear-gradient(135deg,#f1f5f9 0%,#e5edf4 53%,#f1f0f8 100%);color:#193448}
.block-container{max-width:1500px;padding-top:2.3rem;padding-left:2.2rem;padding-right:2.2rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:linear-gradient(155deg,#102a41 0%,#164b5d 52%,#283c61 100%);border-right:2px solid #3f9c9d}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2{color:#e7f4f8!important}
[data-testid="stSidebar"] .stAlert p{color:#18384a!important}
[data-testid="stSidebar"] [data-baseweb="select"] *,[data-testid="stSidebar"] input{color:#17384f!important}
[data-testid="stHeader"]{background:rgba(241,245,249,.87)}
[data-testid="stMetric"]{background:#fff;padding:18px;border-radius:16px;border:1px solid #c8dce3;box-shadow:0 3px 12px #1b405410}
.stTabs [data-baseweb="tab-list"]{gap:6px;overflow-x:auto}
.stTabs [data-baseweb="tab"]{font-size:1rem;font-weight:650;border-radius:9px 9px 0 0;padding:13px 16px}
h1,h2,h3{color:#14394d!important;letter-spacing:.1px}
h1{font-size:2.15rem!important}h2{font-size:1.55rem!important}h3{font-size:1.25rem!important}
.hero{background:linear-gradient(115deg,#16334f 0%,#205b70 54%,#326b72 100%);border:1px solid #589da0;border-radius:24px;padding:34px 36px;color:#fff;margin:0 0 26px;box-shadow:0 12px 28px #193f5529}
.hero h1,.hero p{color:#fff!important}.hero p{opacity:.94;font-size:1.08rem;margin:12px 0 0}
.stButton>button[kind="primary"],.stDownloadButton>button{background:#167f8b;color:#fff;border-radius:12px;border:0;min-height:44px;font-weight:650}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#53b5b2;color:#fff}
[data-testid="stFileUploader"]{border-radius:14px}
@media(max-width:800px){.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:22px}.atlas-brand img{max-width:64px}}
</style>""",unsafe_allow_html=True)
if lang=='العربية':
    st.markdown('<style>[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label{direction:rtl;text-align:right}</style>',unsafe_allow_html=True)
# ATLAS brand: original microscope motif, enlarged and colored, not a generic atom/diamond.
MICROSCOPE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="ATLAS EAST microscope"><defs><linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#6CE2D1"/><stop offset="1" stop-color="#37A8CA"/></linearGradient></defs><path d="M36 8l14 14-7 7-14-14z" fill="url(#glass)" stroke="#D6F2F5" stroke-width="1.5"/><path d="M28 19l12 12" stroke="#D5EFF5" stroke-width="5" stroke-linecap="round"/><path d="M28 30l-9 9" stroke="#62C6E7" stroke-width="5" stroke-linecap="round"/><path d="M43 33c6 13-3 19-15 19-10 0-16-6-15-15" fill="none" stroke="#63BDE0" stroke-width="5" stroke-linecap="round"/><path d="M11 56h43" stroke="#6DE3D1" stroke-width="5" stroke-linecap="round"/><circle cx="19" cy="39" r="4" fill="#F2C778"/></svg>"""
LOGO_DATA = base64.b64encode(MICROSCOPE_SVG.encode('utf-8')).decode('ascii')
def brand_html(sidebar=False):
    size=76 if sidebar else 96
    title_size=28 if sidebar else 49
    return (f'<div class="atlas-brand" style="display:flex;align-items:center;gap:19px">'
            f'<img alt="ATLAS EAST microscope" src="data:image/svg+xml;base64,{LOGO_DATA}" width="{size}" height="{size}"/>'
            f'<div><div style="font-size:{title_size}px;font-weight:850;letter-spacing:0.8px;white-space:nowrap;color:#f3fbfd">ATLAS EAST</div>'
            f'<div style="font-size:12px;letter-spacing:1.1px;color:#b4e5e9">RESEARCH INTELLIGENCE</div></div></div>')
with st.sidebar:
    st.markdown(brand_html(sidebar=True),unsafe_allow_html=True)
    st.divider()
    target=st.selectbox(T('output'),['English','German','Arabic'],index={'English':0,'Deutsch':1,'العربية':2}[lang],format_func=lambda v: {'English':{'English':'English','Deutsch':'Englisch','العربية':'الإنجليزية'},'German':{'English':'German','Deutsch':'Deutsch','العربية':'الألمانية'},'Arabic':{'English':'Arabic','Deutsch':'Arabisch','العربية':'العربية'}}[v][lang])
    model=st.selectbox(T('model'),['gpt-4.1-mini','gpt-4o-mini','gpt-4.1'])
    try: api_key=st.secrets.get('OPENAI_API_KEY','')
    except Exception: api_key=''
    api_key=api_key or os.environ.get('OPENAI_API_KEY','')
    st.caption('🔐 '+T('api_caption'))
    check=st.checkbox(T('check_links'),False)
    st.warning(T('privacy'))
# Navigation is intentionally independent of document/session state: opening the app
# never extracts or uploads a document, and switching pages preserves existing work.
WELCOME_TEXT = {
    'العربية': {
        'home': 'الرئيسية', 'workspace': 'مساحة العمل', 'navigation': 'التنقل',
        'intro_title': 'من مشروع بحثي إلى معرفة علمية منظمة',
        'intro': 'ATLAS EAST منصة مساعدة للباحثين لقراءة المشاريع والرسائل العلمية، وفحص الأدلة والجداول والصور، وإعداد تقارير بحثية ومسودات أوراق علمية وكتب قابلة للطباعة.',
        'languages': 'اللغات المدعومة', 'language_detail': 'العربية · الألمانية · الإنجليزية — يمكنك اختيار لغة الواجهة ولغة المخرجات بشكل مستقل.',
        'tools': 'ما الذي يمكنك إنجازه؟',
        'features': [('تدقيق البحث', 'ملخصات ومنهجية وأدلة مرتبطة بالمصدر.'), ('البيانات والمحاكاة', 'جداول وحسابات وصفية وسيناريوهات بحثية مع بيان حدودها.'), ('الصور الطبية', 'عرض وقياسات استكشافية للصور، وليست تشخيصًا طبيًا.'), ('النشر العلمي', 'مسودات أوراق بحثية وكتب علمية مع فهرس وأغلفة للطباعة.')],
        'enter': 'الانتقال إلى مساحة العمل', 'note': 'أداة مساعدة للبحث؛ جميع النتائج العلمية والمخرجات المعدة للنشر تحتاج إلى مراجعة الباحث والتحقق من الحقوق.',
        'workspace_note': 'ارفع مشروعك هنا، ثم اختر أداة التحليل أو التقرير أو الكتاب من الأقسام أدناه.'
    },
    'Deutsch': {
        'home': 'Startseite', 'workspace': 'Arbeitsbereich', 'navigation': 'Navigation',
        'intro_title': 'Vom Forschungsprojekt zu strukturierter wissenschaftlicher Erkenntnis',
        'intro': 'ATLAS EAST unterstützt Forschende beim Auswerten von Abschlussarbeiten und Forschungsdokumenten, beim Prüfen von Belegen, Tabellen und Bildern sowie beim Erstellen von Berichten, Manuskriptentwürfen und druckbaren Büchern.',
        'languages': 'Unterstützte Sprachen', 'language_detail': 'Deutsch · Englisch · Arabisch — Oberfläche und Ausgabesprache können unabhängig gewählt werden.',
        'tools': 'Was bietet ATLAS EAST?',
        'features': [('Forschungsprüfung', 'Zusammenfassungen, Methoden und quellengestützte Belege.'), ('Daten und Simulation', 'Tabellen, deskriptive Berechnungen und gekennzeichnete Forschungsszenarien.'), ('Medizinische Bildgebung', 'Explorative Bildanzeige und Messungen, keine medizinische Diagnose.'), ('Wissenschaftliche Publikationen', 'Entwürfe für Forschungsartikel und druckbare Fachbücher mit Inhaltsverzeichnis und Umschlag.')],
        'enter': 'Zum Arbeitsbereich', 'note': 'Forschungsassistenz: Wissenschaftliche Aussagen und Publikationen erfordern fachliche Prüfung und geklärte Nutzungsrechte.',
        'workspace_note': 'Laden Sie Ihr Projekt hoch und wählen Sie unten Analyse, Bericht oder Bucherstellung.'
    },
    'English': {
        'home': 'Home', 'workspace': 'Workspace', 'navigation': 'Navigation',
        'intro_title': 'From research projects to structured scientific insight',
        'intro': 'ATLAS EAST helps researchers review theses and scientific documents, examine evidence, tables and images, and prepare research reports, manuscript drafts and print-ready book layouts.',
        'languages': 'Supported languages', 'language_detail': 'English · German · Arabic — choose interface and output languages independently.',
        'tools': 'Explore the platform',
        'features': [('Research audit', 'Summaries, methodology and source-linked evidence.'), ('Data and simulation', 'Tables, descriptive calculations and clearly labeled research scenarios.'), ('Medical imaging', 'Exploratory image viewing and measurements, not clinical diagnosis.'), ('Scientific publishing', 'Research manuscript drafts and printable scientific books with contents and covers.')],
        'enter': 'Open research workspace', 'note': 'Research assistance only. Scientific findings and publishable outputs require expert review and appropriate usage rights.',
        'workspace_note': 'Upload your project, then use the analysis, report or book tools below.'
    }
}
ui = WELCOME_TEXT[lang]
with st.sidebar:
    selected_page = st.radio(ui['navigation'], ['home', 'workspace'],
        format_func=lambda page: ui[page], key='atlas_page', horizontal=True)

st.markdown(f'<div class="hero">{brand_html()}<p style="color:#d5f5f3;font-size:1.16rem;margin-top:14px">{T("hero_sub")}</p><p style="color:#a7e6df;font-size:0.96rem;letter-spacing:0.4px">Discover · Analyze · Model · Publish</p></div>',unsafe_allow_html=True)
if selected_page == 'home':
    st.title(ui['intro_title'])
    st.write(ui['intro'])
    st.subheader(ui['tools'])
    feature_columns = st.columns(2)
    for index, (heading, description) in enumerate(ui['features']):
        with feature_columns[index % 2]:
            with st.container(border=True):
                st.markdown('#### ' + heading)
                st.write(description)
    with st.container(border=True):
        st.markdown('#### 🌐 ' + ui['languages'])
        st.write(ui['language_detail'])
    st.caption(ui['note'])
    # Streamlit callbacks run before widget creation on the next rerun.
    # Do not mutate atlas_page after the radio widget is instantiated.
    def open_research_workspace():
        st.session_state['atlas_page'] = 'workspace'

    st.button('→ ' + ui['enter'], type='primary', use_container_width=True,
              key='atlas_enter_workspace', on_click=open_research_workspace)
    st.stop()

st.caption(ui['workspace_note'])

upload=st.file_uploader(T('upload'),type=['pdf','docx'])
if upload:
    signature=hashlib.sha256(upload.getvalue()).hexdigest()
    if st.session_state.get('document_signature')!=signature:
        st.session_state['document_signature']=signature
        for k in ['analysis','doc','checks','book_content','book_signature']: st.session_state.pop(k,None)
        try: st.session_state['doc']=extract_document(upload)
        except Exception as exc: st.error(str(exc));st.stop()
    doc=st.session_state['doc'];links=extract_links(doc['text'])
    metrics=st.columns(4)
    for col,title,value in zip(metrics,[T('pages'),T('tables'),T('figures_count'),T('links_count')],[len(doc['pages']),len(doc['tables']),len(doc['images']),len(links)]): col.metric(title,value)
    st.caption(f"{doc['name']} · {len(doc['text']):,} {T('characters')}")
    c1,c2=st.columns(2)
    with c1:
        if st.button(T('run'),type='primary',use_container_width=True,disabled=not bool(api_key)):
            try:
                with st.spinner(T('working')):
                    st.session_state['analysis']=analyze_with_ai(doc,api_key,model,target)
                    st.session_state['analysis_language']=target
            except Exception as exc: st.error(f'{T("analysis_error")}: {type(exc).__name__}: {exc}')
    with c2:
        if st.button(T('inspect'),use_container_width=True): st.session_state['analysis']=basic_analysis(doc);st.session_state['analysis_language']='source'
    if not api_key: st.info(T('api_missing'))
    analysis=st.session_state.get('analysis')
    if analysis and st.session_state.get('analysis_language') not in (target,):
        st.info({'العربية':'تم تغيير لغة التقرير أو استُخدم الفحص دون ذكاء اصطناعي؛ أعد التدقيق بالذكاء الاصطناعي للحصول على نص كامل باللغة المختارة.','Deutsch':'Die Berichtssprache wurde geändert oder eine Prüfung ohne KI verwendet; starten Sie die KI-Analyse erneut, um alle Texte in der gewählten Sprache zu erhalten.','English':'The report language changed or inspection without AI was used; rerun the AI audit to generate all content in the chosen language.'}[lang])
else:
    doc=None;analysis=None;links=[]
    st.info(T('upload_hint'))

tab_names=[T(k) for k in ['summary','methods','results','tables','figures','medical','simulation','refs','export']]
tabs=st.tabs(tab_names)
with tabs[0]:
    if analysis:
        st.subheader(analysis.get('proposed_title') or T('summary'))
        st.write(analysis.get('executive_summary',''))
        for key in ['research_question','discipline','study_design','translation_notes']:
            with st.expander(T('field_'+key)):st.write(analysis.get(key,''))
    else: st.info(T('missing'))
with tabs[1]:
    if analysis:
        for key in ['methods','sample_and_materials','statistics','limitations','risk_of_bias','reproducibility']:
            st.markdown('#### '+T('field_'+key));st.write(analysis.get(key,''))
    else:st.info(T('missing'))
with tabs[2]:
    if analysis:
        for key in ['scientific_contribution','key_findings','clinical_findings','engineering_findings','pharmaceutical_findings','new_hypotheses','discussion','conclusion']:
            st.markdown('#### '+T('field_'+key));st.write(analysis.get(key,''))
        st.caption(T('quote_note'))
    else:st.info(T('missing'))
with tabs[3]:
    if doc and doc['tables']:
        for i,table in enumerate(doc['tables']):
            with st.expander(table['title'],expanded=i==0):
                try:
                    insights,frame=table_insights(table['rows'])
                    st.dataframe(frame.fillna('').astype(str),use_container_width=True)
                except (ValueError,TypeError,IndexError) as exc:
                    st.warning(T('bad_table'))
                    continue
                if insights:
                    st.write(T('descriptive'))
                    st.dataframe(pd.DataFrame([{**item,'unit':T('unit_source'),'status':T('stat_note')} for item in insights]).rename(columns={'column':T('stat_column'),'mean':T('stat_mean'),'median':T('stat_median'),'std_sample':T('stat_std'),'unit':T('stat_unit'),'status':T('stat_status')}),use_container_width=True)
                    st.download_button(T('csv_table'),frame.to_csv(index=False).encode('utf-8-sig'),file_name=f'atlas_table_{i+1}.csv',key=f'table_{i}')
                else:st.caption(T('no_numbers'))
    else:st.info(T('no_tables'))
with tabs[4]:
    if doc and doc['images']:
        for i,img in enumerate(doc['images']):
            with st.expander(img['label'],expanded=i==0):
                st.image(img['bytes'],caption=img['label'],width=650)
                st.json({T('pixel_'+k):v for k,v in image_measurements(img['bytes']).items()})
                st.caption(T('pixel_note'))
    else:st.info(T('no_images'))
with tabs[5]:
    st.markdown('### '+T('med_title'))
    st.caption(T('med_caption'))
    medical_file=st.file_uploader(T('med_upload'),type=['dcm','dicom','nii','gz','png','jpg','jpeg','tif','tiff'],key='medical_upload')
    if medical_file:
        try:
            preview,metadata=read_medical_image(medical_file.name,medical_file.getvalue())
            st.image(preview,caption=T('med_preview'),width=500)
            st.json(metadata)
            st.caption({'العربية':'المعاينة والعتبة توضحان توزيع الشدة فقط، ولا تكشفان المرض أو تحددان الأعضاء آليًا.','Deutsch':'Vorschau und Schwellenwert zeigen nur die Intensitätsverteilung, nicht Krankheiten oder anatomische Strukturen.','English':'Preview and threshold show intensity distribution only, not disease or validated anatomy.'}[lang])
            cutoff=st.slider(T('med_threshold'),0,255,128,key='medical_threshold')
            mask,stats=threshold_mask(preview,cutoff)
            st.image(mask,caption=T('med_mask'),width=500)
            st.json({T('mask_'+k):v for k,v in stats.items()})
            st.download_button(T('med_mask_download'),mask,'atlas_exploratory_mask.png','image/png')
        except Exception as exc:st.error(f'{T("med_error")}: {exc}')
    st.warning(T('med_warning'))
with tabs[6]:
    st.markdown('### '+T('sim_title'))
    st.caption(T('sim_caption'))
    p1,p2,p3,p4=st.columns(4)
    base=p1.number_input(T('sim_initial'),value=1.0)
    slope=p2.number_input(T('sim_slope'),value=0.15)
    n=p3.number_input(T('sim_steps'),min_value=2,max_value=1000,value=20)
    step=p4.number_input(T('sim_step'),min_value=0.00001,value=1.0)
    curve=simulate_linear(base,slope,n,step)
    st.line_chart(curve.set_index('input_delta'))
    st.info(scenario_summary(curve,lang))
    st.download_button(T('sim_download'),curve.to_csv(index=False).encode('utf-8-sig'),'atlas_hypothetical_simulation.csv')
with tabs[7]:
    if links:
        st.dataframe(pd.DataFrame({T('ref_heading'):links}),use_container_width=True)
        if check and st.button(T('ref_check'),key='check_urls'):
            with st.spinner(T('ref_working')):st.session_state['checks']=verify_links(links)
        if st.session_state.get('checks'):st.dataframe(pd.DataFrame(st.session_state['checks']))
    else:st.info(T('ref_empty'))
    st.caption(T('ref_caution'))
with tabs[8]:
    if analysis and doc:
        proposed=analysis.get('proposed_title') or os.path.splitext(doc['name'])[0]
        project_title=st.text_input(T('project'),value=proposed)
        report_type=st.radio(T('format'),[T('audit'),T('manuscript')],horizontal=True)
        manuscript=report_type==T('manuscript')
        st.info(T('manuscript_warning'))
        st.markdown('#### '+T('evidence'))
        for i,item in enumerate(analysis.get('evidence',[])):
            if not isinstance(item,dict):continue
            mark='✓' if item.get('verified_quote') else '⚠'
            with st.expander(f'{mark} {T("page")} {item.get("page","?")} — {str(item.get("claim",""))[:90]}'):
                st.write(item.get('claim',''))
                st.code(item.get('excerpt',''))
                st.caption(T('verified') if item.get('verified_quote') else T('unverified'))
        for warning in analysis.get('warnings',[]):st.warning(str(warning))
        st.caption(analysis.get('_coverage',''))
        try:
            pdf=build_pdf(doc,analysis,links,title=project_title,manuscript=manuscript,language=target)
            st.download_button(T('download'),pdf,file_name='ATLAS_EAST_Research_Manuscript_DRAFT.pdf' if manuscript else 'ATLAS_EAST_Scientific_Audit.pdf',mime='application/pdf',type='primary',use_container_width=True)
        except Exception as exc:st.error(f'{T("pdf_error")}: {exc}')
    else:st.info(T('missing'))

# Independent book-production workflow: no dependency on the audit/manuscript export.
st.divider()
st.header('📚 '+T('book_studio'))
st.caption(T('book_intro'))
if doc:
    bc1,bc2=st.columns(2)
    with bc1:
        book_lang=st.selectbox(T('book_language'),['Arabic','German','English'],index={'العربية':0,'Deutsch':1,'English':2}[lang],key='book_language',format_func=lambda v: {'Arabic':{'English':'Arabic','Deutsch':'Arabisch','العربية':'العربية'},'German':{'English':'German','Deutsch':'Deutsch','العربية':'الألمانية'},'English':{'English':'English','Deutsch':'Englisch','العربية':'الإنجليزية'}}[v][lang])
        trim=st.selectbox(T('book_size'),['A5','A4'],key='book_trim')
    with bc2:
        book_author=st.text_input(T('book_author'),value=T('book_author_default'),key='book_author')
        st.caption(T('book_rights'))
    st.caption({'العربية':'المشاريع الطويلة قد تتطلب عشرات طلبات API وتكلفة ملحوظة. يمكن استئناف الأجزاء المكتملة بعد انقطاع العملية.','Deutsch':'Lange Dokumente können viele API-Aufrufe und Kosten verursachen. Abgeschlossene Abschnitte können nach Unterbrechungen fortgesetzt werden.','English':'Long documents may require many API calls and incur significant cost. Completed sections can be resumed after interruptions.'}[lang])
    if st.button(T('book_generate'),type='primary',disabled=not bool(api_key),key='book_generate'):
        try:
            with st.spinner(T('book_working')):
                resume_key=f'book_progress_{signature}_{book_lang}_{model}'
                prior=st.session_state.get(resume_key,[])
                progress_bar=st.progress(0,text=T('book_working'))
                def save_progress(done,total,chapters):
                    st.session_state[resume_key]=list(chapters)
                    progress_bar.progress(done/total,text=f'{done}/{total}')
                st.session_state['book_content']=create_book_content(doc,api_key,model,book_lang,analysis,progress=save_progress,resume=prior)
                st.session_state.pop(resume_key,None)
                st.session_state['book_signature']=(signature,book_lang)
        except Exception as exc:
            st.error(f'{T("book_error")}: {type(exc).__name__}: {exc}')
    book=st.session_state.get('book_content')
    if book and st.session_state.get('book_signature')==(signature,book_lang):
        st.success(T('book_prepared')+' · '+book['coverage'])
        title=st.text_input(T('book_title'),value=book['title'],key='book_title')
        book['title']=title
        st.write(T('chapters')+':',len(book['chapters']))
        for i,ch in enumerate(book['chapters']):
            with st.expander(f"{i+1}. {ch['heading']} · {T('page')} {ch['page']}"):
                for paragraph in ch['paragraphs']:st.write(paragraph)
        show_tables=st.checkbox(T('include_tables'),value=True,key='book_tables')
        show_figures=st.checkbox(T('include_figures'),value=True,key='book_figures')
        try:
            book_pdf=build_book_pdf(doc,book,links,book_author,show_figures,show_tables,trim)
            st.download_button(T('book_download'),book_pdf,'ATLAS_EAST_Scientific_Book_'+book_lang+'.pdf','application/pdf',type='primary',key='download_book')
            st.caption(T('book_print_note'))
        except Exception as exc:st.error(f'{T("book_pdf_error")}: {exc}')
    elif book:
        st.info(T('book_regenerate'))
else:
    st.info(T('book_need_upload'))
