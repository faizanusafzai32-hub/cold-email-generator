import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import re

st.set_page_config(page_title="Faizan's PhD Assistant", layout="wide")
st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")

# Candidate Facts - Source of Truth
FAIZAN_FACTS = {
    "name": "Faizan Ahmad",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "linkedin.com/in/faizan-ahmad-98990b183",
    "education": "MS Remote Sensing and GIS, Institute of Space Technology, Islamabad; BS Geo-Informatics, Pir Mehr Ali Shah Arid Agriculture University, Rawalpindi.",
    "current_job": "GIS Analyst at Zoneomics (US-based company, offshore partner Nook Office Solutions) since April 2025. Builds Python and spatial SQL pipelines for large US parcel and zoning datasets, with automated QA/QC.",
    "total_exp": "more than five years (R2V, OGDCL, Glanz Energy, Zoneomics)",
    "thesis": "MS thesis on how land use and land cover (LULC) change affects flood risk in Islamabad, Pakistan (under review at Urban Climate)",
    "publication": "Co-author of 'Spatiotemporal dynamics of land use and Indian pangolin habitat in western Pakistan: insights from Landsat imagery and generalized linear models', Journal for Nature Conservation, 2026, vol. 90",
    "skills": "Python, SQL, Google Earth Engine, ArcGIS, QGIS, ERDAS Imagine",
    "fields": ["remote sensing", "gis", "lulc", "land use", "flood", "hazard", "risk", "geospatial", "spatial analytics", "spatial sql", "pipeline"]
}

tab1, tab2 = st.tabs(["⚡ 1. Bulk Professor Email Generator", "📄 2. Generate Research Statement PDFs (ZIP)"])

def clean_pdf_text(text):
    if not isinstance(text, str):
        return ""
    cleaned = (text.replace('—', '-')
                   .replace('–', '-')
                   .replace('“', '"')
                   .replace('”', '"')
                   .replace('‘', "'")
                   .replace('’', "'")
                   .replace('•', '-')
                   .replace('\u2014', '-')
                   .replace('\u2013', '-'))
    return cleaned.encode('latin-1', 'replace').decode('latin-1')

def check_field_overlap(research_summary, expertise):
    combined_text = f"{research_summary} {expertise}".lower()
    for field in FAIZAN_FACTS["fields"]:
        if field in combined_text:
            return True
    return False

def generate_strict_cold_email(prof_name, university, program, research_summary, paper_title, paper_journal_year, paper_abstract, connection_note):
    clean_prof = prof_name.replace("Dr.", "").replace("Prof.", "").strip()
    last_name = clean_prof.split()[-1] if clean_prof else "Professor"
    
    checklist = []
    
    has_overlap = check_field_overlap(research_summary, "")
    if not has_overlap:
        checklist.append("WARNING: this professor's field does not clearly overlap with your work.")
        
    words = research_summary.split() if research_summary else []
    topic_str = " ".join(words[:2]) if words else "Spatial Analytics"
    subject = f"PhD Inquiry (Fall 2027) - {topic_str}"
    
    if program and program.strip() and not any(word in program.lower() for word in ["school", "college", "department"]):
        program_ref = f"the PhD program in {program.strip()}"
    elif university and university.strip():
        program_ref = f"a PhD at the {university.strip()}"
    else:
        program_ref = "a PhD program"

    has_paper = bool(paper_title and paper_title.strip())
    has_abstract = bool(paper_abstract and len(paper_abstract.strip()) > 10)
    has_connection = bool(connection_note and connection_note.strip())
    
    if has_paper:
        year_str = f" ({paper_journal_year.strip()})" if paper_journal_year and paper_journal_year.strip() else ""
        if has_abstract:
            paper_sentence = f"In your paper {paper_title.strip()}{year_str}, the research explores key spatial dynamics using quantitative methods."
        else:
            paper_sentence = f"In your paper {paper_title.strip()}{year_str}, the research addresses key spatial analysis questions."
            
        if has_connection:
            connection_sentence = f" {connection_note.strip()}"
        else:
            connection_sentence = " [NEEDS INPUT: add one sentence connecting your work to this paper]"
            checklist.append("[NEEDS INPUT: add one sentence connecting your work to this paper]")
            
        paper_block = paper_sentence + connection_sentence
    else:
        paper_block = "[NEEDS INPUT: paste the paper abstract]"
        checklist.append("[NEEDS INPUT: paste the paper abstract]")

    candidate_block = (
        "My relevant research includes my M.S. thesis at the Institute of Space Technology on how land use and land cover change "
        "affects flood risk in Islamabad (currently under review at Urban Climate), and my co-authored work in the Journal for Nature Conservation (2026) "
        "analyzing spatiotemporal habitat dynamics using Landsat imagery. Professionally, I work as a GIS Analyst at Zoneomics, building Python and spatial SQL pipelines for large spatial datasets."
    )
    
    body = (
        f"Dear Dr. {last_name},\n\n"
        f"I am writing to inquire about joining {program_ref} starting Fall 2027.\n\n"
        f"{paper_block}\n\n"
        f"{candidate_block}\n\n"
        f"Are you accepting PhD students for Fall 2027 with funded assistantships (RA/TA)? My CV is attached for your review.\n\n"
        f"Best regards,\n"
        f"{FAIZAN_FACTS['name']}\n"
        f"{FAIZAN_FACTS['email']}\n"
        f"{FAIZAN_FACTS['linkedin']}"
    )

    checklist.append("Verify professor's active recruitment status for Fall 2027.")

    return subject, body, checklist

def parse_professors_input(raw_text):
    professors = []
    blocks = re.split(r'\n\s*\n+(?=(?:Name|Professor Name|Prof\.))\s*', raw_text.strip())
    if len(blocks) <= 1:
        blocks = raw_text.strip().split('\n\n')
        
    for block in blocks:
        if not block.strip():
            continue
        p = {
            "name": "", "university": "", "program": "", "research_summary": "",
            "paper_title": "", "paper_journal_year": "", "paper_abstract": "",
            "connection_note": "", "email": ""
        }
        lines = block.split('\n')
        for line in lines:
            l = line.strip()
            if re.match(r'^(?:Name|Professor Name|Prof)\s*:', l, re.IGNORECASE):
                p['name'] = re.sub(r'^(?:Name|Professor Name|Prof)\s*:\s*', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^University\s*:', l, re.IGNORECASE):
                p['university'] = re.sub(r'^University\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Program\s*:', l, re.IGNORECASE):
                p['program'] = re.sub(r'^Program\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Research Interests|Research Summary|Research)\s*:', l, re.IGNORECASE):
                p['research_summary'] = re.sub(r'^(?:Research Interests|Research Summary|Research)\s*:\s*', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Paper Title|Latest Published Papers|Latest Published Paper|Paper)\s*:', l, re.IGNORECASE):
                p['paper_title'] = re.sub(r'^(?:Paper Title|Latest Published Papers|Latest Published Paper|Paper)\s*:\s*', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Year|Paper Year)\s*:', l, re.IGNORECASE):
                p['paper_journal_year'] = re.sub(r'^(?:Year|Paper Year)\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Abstract\s*:', l, re.IGNORECASE):
                p['paper_abstract'] = re.sub(r'^Abstract\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Connection Note|Connection)\s*:', l, re.IGNORECASE):
                p['connection_note'] = re.sub(r'^(?:Connection Note|Connection)\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Email Address|Email)\s*:', l, re.IGNORECASE):
                p['email'] = re.sub(r'^(?:Email Address|Email)\s*:\s*', '', l, flags=re.IGNORECASE).strip()
                
        if not p['name']:
            clean_lines = [ln.strip() for ln in lines if ln.strip()]
            if clean_lines:
                p['name'] = clean_lines[0]
        professors.append(p)
    return professors

# ==================== TAB 1 ====================
with tab1:
    st.subheader("⚡ Strict Fact-Checked PhD Cold Email Generator")
    st.write("Paste professor details below:")
    
    sample_input = """Name: Dr. Linke
University: University of Utah
Program: Geography
Research Interests: Environmental stress, global agricultural landownership
Paper Title: The effects of environmental stress on global agricultural landownership
Year: 2023
Abstract: We analyze environmental stress factors impacting global agricultural landownership.
Connection Note: 
Email: linke@geog.utah.edu"""

    pasted_data = st.text_area("📋 Paste Professor Data Here:", height=260, value=sample_input)

    if st.button("🚀 Generate Clean Emails & Excel"):
        try:
            profs = parse_professors_input(pasted_data)
            if not profs:
                st.error("Could not parse professor records. Please check format.")
            else:
                st.success(f"Successfully processed {len(profs)} professor record(s)!")
                
                rows = []
                for prof in profs:
                    subj, bdy, chk = generate_strict_cold_email(
                        prof.get('name', ''),
                        prof.get('university', ''),
                        prof.get('program', ''),
                        prof.get('research_summary', ''),
                        prof.get('paper_title', ''),
                        prof.get('paper_journal_year', ''),
                        prof.get('paper_abstract', ''),
                        prof.get('connection_note', '')
                    )
                    
                    rows.append({
                        "Name": prof.get('name'),
                        "Email Address": prof.get('email', ''),
                        "Email Subject": clean_pdf_text(subj),
                        "Email Body": clean_pdf_text(bdy),
                        "Checklist Notes": "; ".join(chk)
                    })
                    
                    with st.expander(f"Email Preview: {prof.get('name', 'Professor')} ({prof.get('university', '')})"):
                        st.write(f"**Subject:** {subj}")
                        st.text(bdy)
                        st.write("**Checklist (Internal Notes):**")
                        for item in chk:
                            st.write(f"- {item}")

                df = pd.DataFrame(rows)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Clean_Emails")
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Clean_Emails.xlsx",
                    data=buffer,
                    file_name="Clean_Emails.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Error: {e}")

# ==================== TAB 2 ====================
with tab2:
    st.subheader("📄 Bulk Generate Tailored Research Statement PDFs")
    st.write("Upload your Excel file (`Clean_Emails.xlsx`) to generate A4 research statements.")
    
    uploaded_file = st.file_uploader("Upload Faculty Excel File (.xlsx):", type=["xlsx"])
    if uploaded_file is not None:
        try:
            df_up = pd.read_excel(uploaded_file)
            st.success(f"Loaded {len(df_up)} records.")
            if st.button("📥 Download Research Statements (ZIP)"):
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for idx, row in df_up.iterrows():
                        p_name = clean_pdf_text(str(row.get("Name", f"Professor_{idx+1}")))
                        clean_p_name = p_name.replace("Dr.", "").replace(".", "").strip().replace(" ", "_")
                        file_name = f"Faizan-PHD-Statement-{clean_p_name}.pdf"
                        
                        pdf = FPDF(orientation='P', unit='mm', format='A4')
                        pdf.set_margins(left=15, top=15, right=15)
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        
                        pdf.set_font("Helvetica", style="B", size=12)
                        pdf.cell(0, 6, "STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.set_font("Helvetica", style="B", size=9)
                        pdf.cell(0, 4, clean_pdf_text(FAIZAN_FACTS['name']), new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, clean_pdf_text(f"Email: {FAIZAN_FACTS['email']} | {FAIZAN_FACTS['linkedin']}"), new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(4)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, f"Alignment with Dr. {p_name}", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, clean_pdf_text("My research background in remote sensing and spatial data science aligns closely with ongoing initiatives. Having completed my M.S. thesis at IST on LULC dynamics and flood risk (under review at Urban Climate), alongside professional Python and SQL pipeline development at Zoneomics, I am well-prepared to contribute effectively to your lab's goals."))
                        
                        pdf_bytes = bytes(pdf.output())
                        zf.writestr(file_name, pdf_bytes)
                zip_buf.seek(0)
                st.download_button("📥 Download ZIP Package", data=zip_buf, file_name="Research_Statements.zip", mime="application/zip")
        except Exception as e:
            st.error(f"Error: {e}")
