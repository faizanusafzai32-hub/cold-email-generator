import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import re

st.set_page_config(page_title="Faizan's PhD Assistant", layout="wide")
st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")

# Faizan Ahmad's Master Profile Source of Truth
FAIZAN_CV = {
    "name": "Faizan Ahmad",
    "phone": "+92 312 9380985",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "M.Sc. in Remote Sensing & GIS",
    "exp": "Sr. GIS Analyst at Zoneomics (US-based spatial intelligence company) with over 2 years of direct experience in processing US-scale big spatial databases, alongside 5.5+ years of overall geospatial research and industry experience",
    "skills": "Python, SQL, and Google Earth Engine (GEE)",
    "pub": "peer-reviewed publication in Elsevier's Journal for Nature Conservation",
    "thesis": "M.Sc. thesis on assessing the impact of LULC changes on flood risk"
}

tab1, tab2 = st.tabs(["⚡ 1. One-Click Bulk Data Parser & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

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

def generate_dynamic_email_paragraph1(expertise, pub_ref):
    """
    Constructs Paragraph 1 using 'Ongoing Project' wording instead of Latest Published Papers.
    """
    exp_text = expertise.strip() if expertise and len(expertise.strip()) > 2 else "spatio-temporal models and spatial analysis"
    pub_text = pub_ref.strip() if pub_ref and len(pub_ref.strip()) > 3 else ""
    
    if pub_text:
        return (
            f"I have been closely following your work in {exp_text} - "
            f"particularly your ongoing projects and studies, such as \"{pub_text}\". "
            f"I am deeply impressed by how your lab integrates quantitative spatial analytics with Earth Observation."
        )
    else:
        return (
            f"I have been closely following your work in {exp_text}. "
            f"I am deeply impressed by how your lab integrates quantitative spatial analytics with Earth Observation."
        )

def parse_raw_professor_blocks(raw_text):
    professors = []
    raw_blocks = re.split(r'\n\s*\n+(?=(?:Name|Professor Name|Prof\.))\s*', raw_text.strip())
    
    if len(raw_blocks) <= 1:
        raw_blocks = raw_text.strip().split('\n\n')

    for block in raw_blocks:
        if not block.strip():
            continue
            
        prof = {"name": "", "email": "", "expertise": "", "pub_ref": "", "bio": ""}
        lines = block.split('\n')
        current_key = None
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            if re.match(r'^(?:Name|Faculty Name|Professor Name)\s*:', line_str, re.IGNORECASE):
                current_key = 'name'
                prof['name'] = re.sub(r'^(?:Name|Faculty Name|Professor Name)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Email Address|Email)\s*:', line_str, re.IGNORECASE):
                current_key = 'email'
                prof['email'] = re.sub(r'^(?:Email Address|Email)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Research Interests areas or expertise|Research Interests|Expertise|Research Area)\s*:', line_str, re.IGNORECASE):
                current_key = 'expertise'
                prof['expertise'] = re.sub(r'^(?:Research Interests areas or expertise|Research Interests|Expertise|Research Area)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Latest Published Paper 1|Latest Published Paper|Key Publication|Publication|Paper|Ongoing Project|Project)\s*:', line_str, re.IGNORECASE):
                current_key = 'pub_ref'
                prof['pub_ref'] = re.sub(r'^(?:Latest Published Paper 1|Latest Published Paper|Key Publication|Publication|Paper|Ongoing Project|Project)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Bio|About Me|Biography|Notes)\s*:', line_str, re.IGNORECASE):
                current_key = 'bio'
                prof['bio'] = re.sub(r'^(?:Bio|About Me|Biography|Notes)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            else:
                if current_key and current_key in prof:
                    if prof[current_key]:
                        prof[current_key] += " " + line_str
                    else:
                        prof[current_key] = line_str
                        
        if not prof['email']:
            em_search = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', block)
            if em_search:
                prof['email'] = em_search.group(0)
                
        if not prof['name']:
            lines_clean = [l.strip() for l in block.split('\n') if l.strip()]
            if lines_clean and "@" not in lines_clean[0] and ":" not in lines_clean[0]:
                prof['name'] = lines_clean[0]

        if prof['name'] or prof['email']:
            professors.append(prof)
            
    return professors

def get_tailored_statement_content(prof_name, focus_domain):
    clean_prof = prof_name.replace("Dr.", "").replace("Dr", "").replace("Prof.", "").replace("Prof", "").strip()
    domain = focus_domain if focus_domain else "Remote Sensing & Spatial Analytics"

    sec2 = (
        f"My doctoral aspirations strongly align with Dr. {clean_prof}'s research focus in {domain}. "
        f"Having conducted my M.Sc. thesis on spatiotemporal environmental modeling, combined with 5.5+ years of quantitative geospatial Python and GEE workflows, "
        f"I am deeply motivated to apply advanced remote sensing and spatial analytics to bridge research gaps in your lab's domain."
    )
    sec3 = (
        f"To synthesize my technical skills with your lab's mission in {domain}, I propose focusing my dissertation on three core pillars: "
        f"(1) developing scalable Python and Google Earth Engine (GEE) automation pipelines for high-resolution satellite time-series analysis; "
        f"(2) applying spatial statistical modeling and machine learning frameworks to evaluate environmental and spatial risk dynamics; and "
        f"(3) integrating multi-sensor spatial datasets to generate predictive simulation surfaces."
    )
    sec4 = (
        f"By combining my solid foundation in spatial data science, workflow automation, and demonstrated Elsevier publishing experience, "
        f"I am fully prepared to make immediate, high-impact contributions to Dr. {clean_prof}'s research program."
    )

    return clean_pdf_text(sec2), clean_pdf_text(sec3), clean_pdf_text(sec4)

# ==================== TAB 1 ====================
with tab1:
    st.subheader("⚡ One-Click Bulk Data Parser (Up to 20+ Professors)")
    st.write("Aap yahan aik sath 10 se 20 professors ka data paste kar sakte hain. Startup box bilkul khali hai:")

    pasted_data = st.text_area("📋 Paste Multiple Professors Raw Data Here (Up to 20+):", height=280, value="")

    if st.button("🚀 Process & Generate Excel Package"):
        parsed_profs = parse_raw_professor_blocks(pasted_data)
        
        if not parsed_profs:
            st.error("Data parse nahi ho saka. Baraye meherbani 'Name:' aur 'Email Address:' labels check karein.")
        else:
            st.success(f"Successfully extracted data for {len(parsed_profs)} professor(s)!")
            
            excel_rows = []
            for prof in parsed_profs:
                full_name = prof['name'].replace("Dr.", "").replace("Dr", "").replace("Prof.", "").replace("Prof", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                
                # Subject strictly uses only the exact research area/expertise (no papers or projects in subject)
                exact_focus = prof['expertise'] if prof['expertise'] else "Remote Sensing & Spatial Analytics"
                subject = f"Prospective Ph.D. Applicant — {exact_focus} - Faizan Ahmad"
                
                # Dynamically constructs paragraph 1 using 'Ongoing Project' wording
                project_mention = generate_dynamic_email_paragraph1(prof['expertise'], prof['pub_ref'])
                
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I hope you are doing well.\n\n"
                    f"I am writing to express my strong interest in joining your research group as a Ph.D. candidate. "
                    f"{project_mention}\n\n"
                    f"I hold an M.Sc. in Remote Sensing & GIS and currently serve as a Sr. GIS Analyst for a US-based spatial intelligence company (Zoneomics). "
                    f"I bring over 2 years of direct experience in processing US-scale big spatial databases alongside 5.5+ years of overall geospatial research and industry experience, "
                    f"which is complemented by my peer-reviewed publication in Elsevier's Journal for Nature Conservation.\n\n"
                    f"Given the close alignment between your lab’s work and my background in geospatial data and spatial analysis, I am very keen to contribute to your ongoing research initiatives.\n\n"
                    f"Could you please let me know if you are accepting Ph.D. students for upcoming terms with funded Graduate Assistantships (RA/TA)?\n\n"
                    f"I have attached my CV for your review. Thank you very much for your time and guidance.\n\n\n"
                    f"Best Regards,\n"
                    f"Faizan Ahmad\n"
                    f"Sr. GIS Analyst\n"
                    f"WhatsApp/Mob: {FAIZAN_CV['phone']}\n"
                    f"{FAIZAN_CV['linkedin']}"
                )
                
                excel_rows.append({
                    "Name": prof['name'],
                    "Email Address": prof['email'],
                    "Email Subject": clean_pdf_text(subject),
                    "Email Body": clean_pdf_text(email_body)
                })

            df = pd.DataFrame(excel_rows)
            st.dataframe(df[["Name", "Email Address", "Email Subject"]])
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Targeted Emails")
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Targeted_Faculty_Emails.xlsx",
                data=buffer,
                file_name="Targeted_Faculty_Emails.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ==================== TAB 2 ====================
with tab2:
    st.subheader("📄 Bulk Generate Tailored Research Statement PDFs")
    st.write("Upload your Excel file (`Targeted_Faculty_Emails.xlsx`) to generate unique A4 PDFs.")
    
    uploaded_file = st.file_uploader("Upload Faculty Excel File (.xlsx):", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded Excel file with {len(df_uploaded)} record(s)!")
            st.dataframe(df_uploaded[["Name", "Email Address", "Email Subject"]].head())
            
            if st.button("📥 Generate & Download Research Statements (ZIP)"):
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, row in df_uploaded.iterrows():
                        prof_name = clean_pdf_text(str(row.get("Name", f"Professor_{idx+1}")))
                        subject = clean_pdf_text(str(row.get("Email Subject", "")))
                        
                        focus = "Remote Sensing & Spatial Analytics"
                        if "—" in subject and "-" in subject:
                            focus = subject.split("—")[1].split("-")[0].strip()
                        elif "-" in subject:
                            parts = subject.split("-")
                            if len(parts) >= 2:
                                focus = parts[0].replace("Prospective Ph.D. Applicant", "").replace(":", "").strip()
                                
                        sec2_text, sec3_text, sec4_text = get_tailored_statement_content(prof_name, focus)
                        
                        clean_prof_name = prof_name.replace("Dr.", "").replace("Dr", "").replace("Prof.", "").replace(".", "").strip().replace(" ", "_")
                        file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                        
                        pdf = FPDF(orientation='P', unit='mm', format='A4')
                        pdf.set_margins(left=15, top=15, right=15)
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        
                        # Header
                        pdf.set_font("Helvetica", style="B", size=13)
                        pdf.cell(0, 7, "STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, clean_pdf_text(FAIZAN_CV["name"]), new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.set_font("Helvetica", style="B", size=9)
                        pdf.cell(0, 4, "Sr. GIS Analyst", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, clean_pdf_text(f"Mob: {FAIZAN_CV['phone']} | Email: {FAIZAN_CV['email']}"), new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, clean_pdf_text(f"{FAIZAN_CV['linkedin']}"), new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(3)
                        
                        # Research Focus Header
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.multi_cell(0, 4, clean_pdf_text(f"Research Focus: Integrating Spatial Analytics, Python Workflows, and {focus}"), align="L")
                        pdf.ln(2)
                        
                        # Section 1: Academic Foundation
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "1. Academic Foundation & Technical Expertise", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, clean_pdf_text("My academic credentials include an M.Sc. in Remote Sensing & GIS, backed by over 5.5 years of professional and research experience, including roles as a Sr. GIS Analyst working with US-scale spatial databases. My technical competencies span Python, SQL, GEE, and spatial statistical modeling. Demonstrating my academic research capability, I co-authored peer-reviewed research published in the Journal for Nature Conservation (Elsevier)."))
                        pdf.ln(2)
                        
                        # Section 2: Unique Domain Alignment
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, clean_pdf_text(f"2. Alignment with Dr. {prof_name.replace('Dr. ', '').replace('Prof. ', '')}'s Research Lab"), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, sec2_text)
                        pdf.ln(2)
                        
                        # Section 3: Unique Proposed Directions
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, sec3_text)
                        pdf.ln(2)
                        
                        # Section 4: Dynamic Conclusion
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "4. Conclusion & Commitment", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, sec4_text)
                        
                        pdf_bytes = bytes(pdf.output())
                        zip_file.writestr(file_name, pdf_bytes)
                        
                zip_buffer.seek(0)
                st.success(f"Successfully generated 100% unique, domain-tailored A4 Research Statement PDFs for {len(df_uploaded)} record(s)!")
                st.download_button(
                    label="📥 Download Research Statements (ZIP)",
                    data=zip_buffer,
                    file_name="Research_Statements_ZIP.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
