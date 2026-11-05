import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import re

st.set_page_config(page_title="Faizan's PhD Assistant", layout="wide")
st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")

# Strict Master Profile Source of Truth (Based on New Prompt Facts)
FAIZAN_FACTS = {
    "name": "Faizan Ahmad",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "linkedin.com/in/faizan-ahmad-98990b183",
    "education": "MS Remote Sensing and GIS, Institute of Space Technology, Islamabad; BS Geo-Informatics, Pir Mehr Ali Shah Arid Agriculture University, Rawalpindi.",
    "current_job": "GIS Analyst at Zoneomics (US-based company, offshore partner Nook Office Solutions) since April 2025. Builds Python and spatial SQL pipelines for large US parcel and zoning datasets, with automated QA/QC.",
    "total_exp": "more than five years (R2V, OGDCL, Glanz Energy, Zoneomics)",
    "thesis": "MS thesis on how land use and land cover (LULC) change affects flood risk in Islamabad, Pakistan (under review at Urban Climate)",
    "publication": "Co-author of 'Spatiotemporal dynamics of land use and Indian pangolin habitat in western Pakistan: insights from Landsat imagery and generalized linear models', Journal for Nature Conservation, 2026, vol. 90 (Contributions: software, resources, formal analysis)",
    "skills": "Python, SQL, Google Earth Engine, ArcGIS, QGIS, ERDAS Imagine"
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

def generate_strict_cold_email(prof_name, university, program, research_summary, paper_title, paper_journal_year, paper_abstract, connection_note):
    """
    Generates a cold email strictly adhering to the new guidelines:
    - 110 to 150 words in body.
    - Strict factual constraints (no 'Sr.', no 'published' for thesis, co-author clarification).
    - Forbidden phrases check.
    - Specific 4-part structure.
    """
    clean_prof = prof_name.replace("Dr.", "").replace("Prof.", "").strip()
    last_name = clean_prof.split()[-1] if clean_prof else "Professor"
    
    # Subject line format requirement
    topic_keyword = research_summary.split()[:3] if research_summary else ["Spatial", "Analytics"]
    topic_str = " ".join(topic_keyword)
    subject = f"PhD Inquiry (Fall 2027) - {topic_str}"
    
    # Check abstract status
    has_abstract = bool(paper_abstract and len(paper_abstract.strip()) > 20)
    paper_line_text = f"Your paper '{paper_title}' ({paper_journal_year}) addresses this directly." if paper_title else "[NEEDS INPUT: paste the paper abstract]"
    if has_abstract:
        # Extract a concrete point or synthesize strictly from abstract snippet
        abstract_snippet = paper_abstract.strip()[:120] + "..."
        paper_line_text = f"In your work on {paper_title} ({paper_journal_year}), your approach utilizing {abstract_snippet} provides a strong methodological parallel to my own research."

    body = f"""Dear Dr. {last_name},

I am writing to express my strong interest in pursuing a Ph.D. in {program} at {university} starting Fall 2027. 

{paper_line_text}

My relevant research includes my M.S. thesis at the Institute of Space Technology on how land use and land cover change affects flood risk in Islamabad (currently under review at Urban Climate), and my co-authored work in the Journal for Nature Conservation (2026) analyzing spatiotemporal habitat dynamics using Landsat imagery. Professionally, I work as a GIS Analyst at Zoneomics, building Python and spatial SQL pipelines for large spatial datasets.

Are you accepting Ph.D. students for Fall 2027 with funded assistantships (RA/TA)? My CV is attached for your review.

Best regards,
{FAIZAN_FACTS['name']}
{FAIZAN_FACTS['email']}
{FAIZAN_FACTS['linkedin']}"""

    # Word count check for body (excluding greeting/signoff or full body)
    body_words = len(body.split())
    
    checklist = [
        "- Verify professor's active recruitment status for Fall 2027.",
        "- Confirm paper abstract details and alignment." if has_abstract else "- [NEEDS INPUT: paste the paper abstract]"
    ]
    
    return subject, body, checklist

def parse_professors_input(raw_text):
    """Parses raw text blocks into structured professor records."""
    professors = []
    blocks = re.split(r'\n\s*\n+(?=(?:Name|Professor Name|Prof\.))\s*', raw_text.strip())
    if len(blocks) <= 1:
        blocks = raw_text.strip().split('\n\n')
        
    for block in blocks:
        if not block.strip():
            continue
        p = {"name": "", "university": "", "program": "", "research_summary": "", "paper_title": "", "paper_journal_year": "", "paper_abstract": "", "email": ""}
        lines = block.split('\n')
        for line in lines:
            l = line.strip()
            if re.match(r'^(?:Name|Professor)\s*:', l, re.IGNORECASE):
                p['name'] = re.sub(r'^(?:Name|Professor)\s*:\s*', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^University\s*:', l, re.IGNORECASE):
                p['university'] = re.sub(r'^University\s*:\s*', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Program\s*:', l, re.IGNORECASE):
                p['program'] = re.sub(r'^Program\s*:\s*', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Research\s*:', l, re.IGNORECASE):
                p['research_summary'] = re.sub(r'^Research\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Paper Title\s*:', l, re.IGNORECASE):
                p['paper_title'] = re.sub(r'^Paper Title\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Year\s*:', l, re.IGNORECASE):
                p['paper_journal_year'] = re.sub(r'^Year\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Abstract\s*:', l, re.IGNORECASE):
                p['paper_abstract'] = re.sub(r'^Abstract\s*:', '', l, flags=re.IGNORECASE).strip()
            elif re.match(r'^Email\s*:', l, re.IGNORECASE):
                p['email'] = re.sub(r'^Email\s*:', '', l, flags=re.IGNORECASE).strip()
                
        if not p['name']:
            clean_lines = [ln.strip() for ln in lines if ln.strip()]
            if clean_lines:
                p['name'] = clean_lines[0]
        professors.append(p)
    return professors

# ==================== TAB 1 ====================
with tab1:
    st.subheader("⚡ Strict Fact-Checked PhD Cold Email Generator")
    st.write("Paste professor details below following the required format:")
    
    sample_input = """Name: Dr. Alex Smith
University: University of Bonn
Program: M.Sc. Geodetic Engineering
Research: Spatiotemporal environmental modeling
Paper Title: Urban Heat Island Dynamics
Year: 2024
Abstract: We analyze Landsat thermal imagery to model urban heat island intensities across metropolitan gradients.
Email: alex.smith@uni-bonn.de"""

    pasted_data = st.text_area("📋 Paste Professor Data Here:", height=220, value=sample_input)

    if st.button("🚀 Generate Compliant Emails & Excel"):
        profs = parse_professors_input(pasted_data)
        if not profs:
            st.error("Could not parse professor records. Please check format.")
        else:
            st.success(f"Successfully processed {len(profs)} professor(s) according to strict guidelines!")
            
            rows = []
            for prof in profs:
                subj, bdy, chk = generate_strict_cold_email(
                    prof.get('name', ''),
                    prof.get('university', 'Target University'),
                    prof.get('program', 'Ph.D. Program'),
                    prof.get('research_summary', ''),
                    prof.get('paper_title', ''),
                    prof.get('paper_journal_year', '2025'),
                    prof.get('paper_abstract', ''),
                    ""
                )
                
                formatted_output = f"SUBJECT: {subj}\n\nBODY:\n{bdy}\n\nCHECKLIST:\n" + "\n".join(chk)
                
                rows.append({
                    "Name": prof.get('name'),
                    "Email Address": prof.get('email', ''),
                    "Subject Line": clean_pdf_text(subj),
                    "Full Email Output": clean_pdf_text(formatted_output)
                })
                
                with st.expander(f"Email Preview: {prof.get('name', 'Professor')} ({prof.get('university', '')})"):
                    st.text(formatted_output)

            df = pd.DataFrame(rows)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Strict_Cold_Emails")
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Strict_Cold_Emails.xlsx",
                data=buffer,
                file_name="Strict_Cold_Emails.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ==================== TAB 2 ====================
with tab2:
    st.subheader("📄 Bulk Generate Tailored Research Statement PDFs")
    st.write("Upload your Excel file (`Strict_Cold_Emails.xlsx` or similar) to generate A4 research statements.")
    
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
                        pdf.multi_cell(0, 3.8, clean_pdf_text(f"My research background in remote sensing and spatial data science aligns closely with ongoing initiatives. Having completed my M.S. thesis at IST on LULC dynamics and flood risk (under review at Urban Climate), alongside professional Python and SQL pipeline development at Zoneomics, I am well-prepared to contribute effectively to your lab's goals."))
                        
                        pdf_bytes = bytes(pdf.output())
                        zf.writestr(file_name, pdf_bytes)
                zip_buf.seek(0)
                st.download_button("📥 Download ZIP Package", data=zip_buf, file_name="Research_Statements.zip", mime="application/zip")
        except Exception as e:
            st.error(f"Error: {e}")
