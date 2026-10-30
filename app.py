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

tab1, tab2 = st.tabs(["📧 1. Dedicated Multi-Professor Sections & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

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
    100% custom tailoring based strictly on the user-provided Research Interests and Paper.
    """
    has_pub = bool(pub_ref and len(pub_ref.strip()) > 3)
    has_exp = bool(expertise and len(expertise.strip()) > 2)
    
    if has_exp and has_pub:
        return (
            f"I am writing to express my strong interest in joining your research group as a Ph.D. candidate. "
            f"Having followed your research focus in {expertise.strip()}, I was particularly drawn to your publication, \"{pub_ref.strip()}\". "
            f"I am deeply impressed by how your lab integrates advanced spatial analytics with Earth Observation."
        )
    elif has_pub:
        return (
            f"I am writing to express my strong interest in joining your research group as a Ph.D. candidate. "
            f"Having read your publication, \"{pub_ref.strip()}\", I am deeply impressed by how your lab leverages quantitative spatial analytics with Earth Observation."
        )
    elif has_exp:
        return (
            f"I am writing to express my strong interest in joining your research group as a Ph.D. candidate. "
            f"Having followed your work in {expertise.strip()}, I am deeply impressed by how your lab integrates quantitative spatial analytics with Earth Observation."
        )
    else:
        return (
            f"I am writing to express my strong interest in joining your research group as a Ph.D. candidate. "
            f"Having followed your academic contributions, I am deeply impressed by how your lab integrates quantitative spatial analytics with Earth Observation."
        )

def get_tailored_statement_content(prof_name, focus_domain):
    clean_prof = prof_name.replace("Dr.", "").replace("Dr", "").strip()

    sec2 = (
        f"My doctoral aspirations strongly align with Dr. {clean_prof}'s research focus in {focus_domain}. "
        f"Having conducted my M.Sc. thesis on spatiotemporal environmental modeling, combined with 5.5+ years of quantitative geospatial Python and GEE workflows, "
        f"I am deeply motivated to apply advanced remote sensing and spatial analytics to bridge research gaps in your lab's domain."
    )
    sec3 = (
        f"To synthesize my technical skills with your lab's mission in {focus_domain}, I propose focusing my dissertation on three core pillars: "
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
    st.subheader("📝 Dedicated Sections for Each Professor")
    st.write("Har professor ke liye bilkul alag section diya gaya hai. Aap jitne marzi professors select karein, sabka data alag rahega aur email subject 100% unke research interests ke mutabiq aayega.")
    
    num_profs = st.number_input("Kitne professors ki details enter karni hain?", min_value=1, max_value=20, value=2, step=1)
    
    professors_data = []
    
    for i in range(int(num_profs)):
        st.markdown(f"---")
        st.markdown(f"### 👨‍🏫 Professor Section {i+1}")
        
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input(f"Professor Name {i+1}:", key=f"name_{i}", placeholder="e.g., Prof. Sunil Bhaskaran")
            p_email = st.text_input(f"Email Address {i+1}:", key=f"email_{i}", placeholder="e.g., Sbhaskaran@gc.cuny.edu")
        with col2:
            p_expertise = st.text_input(f"Research Interests / Expertise {i+1}:", key=f"exp_{i}", placeholder="e.g., Applications of geospatial techniques, spatial-temporal models")
            p_pub = st.text_input(f"Latest Published Paper {i+1} (Optional):", key=f"pub_{i}", placeholder="e.g., Modelling urban heat island (UHI)...")
            
        p_bio = st.text_area(f"Bio / Additional Notes {i+1} (Optional):", key=f"bio_{i}", placeholder="e.g., Additional background or lab notes...")
        
        if p_name.strip() and p_email.strip():
            professors_data.append({
                "name": p_name.strip(),
                "email": p_email.strip(),
                "expertise": p_expertise.strip(),
                "pub_ref": p_pub.strip(),
                "bio": p_bio.strip()
            })

    st.markdown("---")
    if st.button("📥 Generate & Download Excel File (Clean 4-Columns)"):
        if not professors_data:
            st.error("Kam az kam aik professor ki valid details (Name & Email) enter karna lazmi hai.")
        else:
            excel_rows = []
            for prof in professors_data:
                full_name = prof['name'].replace("Dr.", "").replace("Dr", "").replace("Prof.", "").replace("Prof", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                
                # Subject strictly uses what the user typed in Research Interests
                exact_focus = prof['expertise'] if prof['expertise'] else "Remote Sensing & Spatial Analytics"
                subject = f"Prospective Ph.D. Applicant — {exact_focus} - Faizan Ahmad"
                
                para1 = generate_dynamic_email_paragraph1(prof['expertise'], prof['pub_ref'])
                
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I hope you are doing well.\n\n"
                    f"{para1}\n\n"
                    f"I hold an M.Sc. in Remote Sensing & GIS and currently serve as a Sr. GIS Analyst for a US-based spatial intelligence company (Zoneomics), bringing over 2 years of direct experience in processing US-scale big spatial databases alongside 5.5+ years of overall geospatial research and industry experience-complemented by a peer-reviewed publication in Elsevier's Journal for Nature Conservation.\n\n"
                    f"Given the strong overlap between your work and my background in spatial analytics, I am eager to contribute to your ongoing research projects.\n\n"
                    f"Could you please let me know if you are accepting Ph.D. students for upcoming terms with funded Graduate Assistantships (RA/TA)?\n\n"
                    f"I have attached my CV for your review and would welcome the opportunity to connect. Thank you very much for your time and leadership.\n\n\n"
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
            st.success(f"Successfully generated clean targeted email package for {len(excel_rows)} professor(s)!")
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
