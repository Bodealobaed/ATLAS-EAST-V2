"""Paginated research audit and clearly marked manuscript DRAFT PDFs."""
import io,os,re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_RIGHT,TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from analyzer import SECTIONS

FONT_PATHS=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf']
font='Helvetica'
for path in FONT_PATHS:
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont('AtlasBodyFont',path));font='AtlasBodyFont';break

def shape(text):
    s=str(text or '')
    if re.search('[\u0600-\u06ff]',s):
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return '\n'.join(get_display(arabic_reshaper.reshape(line)) for line in s.split('\n'))
        except ImportError:pass
    return s

def build_pdf(doc,analysis,links,title=None,manuscript=False,language='English'):
    out=io.BytesIO()
    project_title=title or analysis.get('proposed_title') or os.path.splitext(doc['name'])[0]
    pdf=SimpleDocTemplate(out,pagesize=(210*mm,297*mm),leftMargin=19*mm,rightMargin=19*mm,topMargin=23*mm,bottomMargin=21*mm,title=project_title)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='AtlasCover',fontName=font,fontSize=21,leading=30,textColor=colors.HexColor('#143a4b'),spaceAfter=14,alignment=TA_CENTER,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='AtlasSection',fontName=font,fontSize=12,leading=18,textColor=colors.HexColor('#0e7e88'),spaceBefore=12,spaceAfter=6,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='AtlasText',fontName=font,fontSize=9,leading=15,textColor=colors.HexColor('#273a4a'),spaceAfter=8,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='AtlasNote',fontName=font,fontSize=8,leading=12,textColor=colors.HexColor('#52677a'),spaceAfter=8,wordWrap='CJK'))
    def para(s,style='AtlasText'):
        return Paragraph(escape(shape(str(s))[:30000]).replace('\n','<br/>'),styles[style])
    story=[Spacer(1,25*mm),para('◈ ATLAS  |  RESEARCH INTELLIGENCE','AtlasCover'),para(project_title,'AtlasCover'),Spacer(1,8*mm),para('SCIENTIFIC MANUSCRIPT — UNREVIEWED DRAFT' if manuscript else 'EVIDENCE-BASED RESEARCH AUDIT','AtlasSection'),para('Document: '+doc['name'],'AtlasNote'),para('Language: '+language+'  |  AI-assisted; author verification required','AtlasNote'),para('This is not a peer-reviewed publication or a clinical certification. Authorship, ethics, permissions, numerical results and references must be checked before submission.','AtlasNote'),PageBreak()]
    if manuscript:
        sections=[('Abstract','abstract'),('1. Introduction / Research question','research_question'),('2. Materials and methods','methods'),('2.1 Samples and materials','sample_and_materials'),('2.2 Statistical methods','statistics'),('3. Results','key_findings'),('3.1 Scientific contribution','scientific_contribution'),('4. Discussion','discussion'),('4.1 Limitations','limitations'),('5. Conclusion','conclusion')]
    else: sections=[(key.replace('_',' ').title(),key) for key in SECTIONS]
    for heading,key in sections:
        story.extend([para(heading,'AtlasSection'),para(analysis.get(key,'Not reported'))])
    story.append(para('Page-anchored evidence','AtlasSection'))
    for item in analysis.get('evidence',[])[:45]:
        if isinstance(item,dict):
            story.append(para(f"Page {item.get('page','?')} · {'Exact quote located' if item.get('verified_quote') else 'UNVERIFIED QUOTE'} · {item.get('claim','')}",'AtlasNote'))
            story.append(para(item.get('excerpt','')))
    story.append(para('References — extracted, not necessarily verified','AtlasSection'))
    for url in links[:90]:story.append(para(url,'AtlasNote'))
    # Evidence appendix: preserve source figures and extracted tables with page provenance.
    if doc.get('tables'):
        story.append(PageBreak())
        story.append(para('Extracted quantitative tables — source data, verify against original','AtlasSection'))
        for i,item in enumerate(doc['tables'][:24],1):
            story.append(para(f'Table {i}: {item.get("title", "Source table")}', 'AtlasSection'))
            rows=item.get('rows',[])[:24]
            if not rows: continue
            width=min(5,max(len(row) if isinstance(row,(list,tuple)) else 1 for row in rows))
            normalized=[]
            for row in rows:
                values=list(row) if isinstance(row,(list,tuple)) else [row]
                normalized.append([para(str(values[j] if j<len(values) and values[j] is not None else '')[:100],'AtlasNote') for j in range(width)])
            table=Table(normalized,colWidths=[pdf.width/width]*width,repeatRows=1,hAlign='CENTER')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dceced')),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#b7cdd4')),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(table)
            if len(item.get('rows',[]))>24:story.append(para('Table excerpt only; consult original document.','AtlasNote'))
    if doc.get('images'):
        story.append(PageBreak())
        story.append(para('Figures from the source document — original captions and rights to verify','AtlasSection'))
        for i,item in enumerate(doc['images'][:24],1):
            try:
                from PIL import Image as PILImage
                original=PILImage.open(io.BytesIO(item['bytes']))
                factor=min(pdf.width/original.width,105*mm/original.height)
                story.append(para(f'Figure {i}: {item.get("label", "Source image")}', 'AtlasSection'))
                story.append(Image(io.BytesIO(item['bytes']),width=original.width*factor,height=original.height*factor))
                story.append(para('Source: '+doc['name']+' — '+str(item.get('label','')), 'AtlasNote'))
            except Exception: continue
    story.append(para('Methodological transparency','AtlasSection'))
    story.append(para(analysis.get('_coverage','Not specified')))
    for warning in analysis.get('warnings',[]):story.append(para('Warning: '+str(warning),'AtlasNote'))
    def logo(canvas,x,y,size=17):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#24a9b6'));canvas.setLineWidth(2.4)
        canvas.line(x+size*.24,y+size*.20,x+size*.80,y+size*.20)
        canvas.arc(x+size*.28,y+size*.25,x+size*.76,y+size*.72,190,210)
        canvas.line(x+size*.42,y+size*.66,x+size*.67,y+size*.90)
        canvas.setFillColor(colors.HexColor('#73ddcb'))
        path=canvas.beginPath();path.moveTo(x+size*.52,y+size*.72);path.lineTo(x+size*.69,y+size*.93);path.lineTo(x+size*.87,y+size*.75);path.lineTo(x+size*.70,y+size*.56);path.close();canvas.drawPath(path,fill=1,stroke=0)
        canvas.restoreState()
    def footer(canvas,doc_):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#bdd3d9'));canvas.line(19*mm,17*mm,191*mm,17*mm)
        canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#57717e'))
        logo(canvas,19*mm,10*mm,13)
        canvas.drawString(33*mm,12*mm,'ATLAS | Research draft · verify before publication')
        canvas.drawRightString(191*mm,12*mm,str(doc_.page))
        canvas.restoreState()
    pdf.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
