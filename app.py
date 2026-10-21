import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF

st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")

FAIZAN_CV_DETAILS = {
    "name": "Faizan Ahmad",
    "phone": "+92 349 9343568",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "M.Sc. in Remote Sensing & GIS and B.Sc. in GeoInformatics",
    "exp": "5.5+ years of professional experience in GIS/Remote Sensing, Python, SQL, Google Earth Engine (GEE), and spatial modeling",
    "pub": "co-authored peer-reviewed research in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal LULC dynamics and habitat suitability modeling"
}

tab1, tab2 = st.tabs(["📧 1. Multi-Professor Structured Form & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

def clean_pdf_text(text):
    if not isinstance(text, str):
        return ""
    return (text.replace('“', '"').replace('”', '"')
                .replace('‘', "'").replace('’', "'")
                .replace('—', '-').replace('–', '-')
                .replace('•', '-')
                .encode('latin-1', 'replace').decode('latin-1'))

# ==================== TAB 1 ====================
with tab1:
    st.write("Yahan aap 1 se 5 ya uss se zyada professors ki details sequential form mein enter karke targeted email package (Excel) generate kar sakte hain.")
    
    num_profs = st.number_input("Kitne professors ki details enter karni hain?", min_value=1, max_value=10, value=2, step=1)
    
    professors_data = []
    
    for i in range(int(num_profs)):
        st.markdown(f"---")
        st.subheader(f"👨‍🏫 Professor {i+1} Details")
        
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input(f"Faculty Name {i+1}:", key=f"name_{i}", placeholder="e.g., Dr. Yingyi Lin")
            p_email = st.text_input(f"Email Address {i+1}:", key=f"email_{i}", placeholder="e.g., Yingyi.Lin@UTDallas.edu")
        with col2:
            p_expertise = st.text_input(f"Research Area / Expertise {i+1}:", key=f"exp_{i}", placeholder="e.g., Demography, spatial health, and urban dynamics")
            p_pub = st.text_input(f"Key Publication / Project Reference {i+1} (Optional):", key=f"pub_{i}", placeholder="e.g., Recent work on population health modeling")
            
        p_link = st.text_input(f"Profile Link {i+1} (For your reference/verification):", key=f"link_{i}", placeholder="e.g., https://profiles.utdallas.edu/yingyi.lin")
        
        if p_name.strip() and p_email.strip():
            professors_data.append({
                "name": p_name.strip(),
                "email": p_email.strip(),
                "expertise": p_expertise.strip() if p_expertise.strip() else "Spatial Analysis and Environmental Modeling",
                "pub_ref": p_pub.strip(),
                "link": p_link.strip()
            })

    st.markdown("---")
    if st.button("📥 Generate & Download Excel File (4 Columns)"):
        if not professors_data:
            st.error("Kam az kam aik professor ki valid details (Name & Email) enter karna lazmi hai.")
        else:
            excel_rows = []
            for prof in professors_data:
                full_name = prof['name'].replace("Dr.", "").replace("Dr", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                focus_clean = prof['expertise']
                
                # 1 Professional Subject line targeting professor's specific work
                subject = f"Prospective PhD Inquiry: {focus_clean[:40]} — Faizan Ahmad"
                
                # Strong 2-paragraph professional email body aligned with professor's focus & profile
                pub_mention = f" Building upon my recent co-authored research published in the Journal for Nature Conservation (Elsevier) on spatiotemporal dynamics," if not prof['pub_ref'] else f" Noting your work on {prof['pub_ref']},"
                
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I am writing to express my strong interest in pursuing a doctoral degree under your supervision, focusing on your research domain in {focus_clean}.{pub_mention} Your lab's methodological contributions to spatial analytics provide an ideal framework for advancing empirical geographical research.\n\n"
                    f"With an M.Sc. in Remote Sensing & GIS, 5.5+ years of practical expertise in Python, SQL, and Google Earth Engine (GEE), and a strong foundation in spatial statistical modeling, I am eager to apply quantitative spatial frameworks to your ongoing projects. Are you currently accepting PhD students with funded positions (RA, TA, or Fellowships) in your lab for upcoming terms? I have attached my CV and a 1-page Statement of Research Interests for your review.\n\n"
                    f"Thank you for your time and consideration.\n\n"
                    f"Sincerely,\n"
                    f"Faizan Ahmad\n"
                    f"GIS Specialist\n"
                    f"WhatsApp/Mob: {FAIZAN_CV_DETAILS['phone']}\n"
                    f"{FAIZAN_CV_DETAILS['linkedin']}"
                )
                
                excel_rows.append({
                    "Name": prof['name'],
                    "Email Address": prof['email'],
                    "Email Subject": subject,
                    "Email Body": email_body
                })

            df = pd.DataFrame(excel_rows)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Targeted Emails")
            buffer.seek(0)
            
            st.success(f"Successfully generated targeted email package for {len(excel_rows)} professor(s)!")
            st.download_button(
                label="Download .xlsx File",
                data=buffer,
                file_name="Targeted_Faculty_Emails.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ==================== TAB 2 ====================
with tab2:
    st.write("Upload your processed Excel file (`Targeted_Faculty_Emails.xlsx`) to generate tailored Statement of Research Interest PDFs.")
    
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
                        email_body = clean_pdf_text(str(row.get("Email Body", "")))
                        
                        focus = "Spatial Analysis and Environmental Modeling"
                        if ":" in subject and "—" in subject:
                            focus = subject.split(":")[1].split("—")[0].strip()
                        elif "domain in" in email_body:
                            match = re.search(r"domain in (.*?)\.", email_body)
                            if match:
                                focus = match.group(1).strip()
                                
                        clean_prof_name = prof_name.replace("Dr.", "").replace("Dr", "").replace(".", "").strip().replace(" ", "_")
                        file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                        
                        pdf = FPDF(orientation='P', unit='mm', format='A4')
                        pdf.set_margins(left=15, top=15, right=15)
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        
                        # Header
                        pdf.set_font("Helvetica", style="B", size=13)
                        pdf.cell(0, 7, "STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, FAIZAN_CV_DETAILS["name"], new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.set_font("Helvetica", size=9)
                        pdf.cell(0, 4, "GIS Specialist", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, f"Mob: {FAIZAN_CV_DETAILS['phone']} | Email: {FAIZAN_CV_DETAILS['email']}", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, f"{FAIZAN_CV_DETAILS['linkedin']}", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(3)
                        
                        # Research Focus
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.multi_cell(0, 4, f"Research Focus: Integrating Spatial Analytics, Python Workflows, and {focus}", align="L")
                        pdf.ln(2)
                        
                        # Section 1
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "1. Academic Foundation & Technical Expertise", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My academic credentials include an M.Sc. in Remote Sensing & GIS and a B.Sc. in GeoInformatics, backed by 5.5+ years of practical GIS experience. My technical competencies span advanced Python, SQL, Google Earth Engine (GEE), and spatial statistical modeling. Demonstrating my academic research capability, I co-authored peer-reviewed research published in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal dynamics and spatial risk assessment.")
                        pdf.ln(2)
                        
                        # Section 2
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, f"2. Alignment with Dr. {prof_name.replace('Dr. ', '')}'s Research Lab", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My doctoral research interests are directly inspired by the scholarly contributions and investigations led by Dr. {prof_name.replace('Dr. ', '')} in the domain of {focus}. The methodological frameworks developed through your research group offer an ideal platform for integrating big data spatial analytics with complex geographical systems. I am eager to contribute my technical background in automated geospatial processing to support and expand upon your ongoing objectives.")
                        pdf.ln(2)
                        
                        # Section 3
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"To synthesize my technical skill set with your lab's mission in {focus.lower()}, I propose focusing my dissertation on three core pillars: (1) integrating multi-decadal observation time-series with spatial metrics to evaluate longitudinal change; (2) developing scalable Python and GEE workflows tailored to {focus.lower()} for rapid spatial mapping; and (3) applying advanced spatial statistics to simulate predictive environmental and social risk surfaces.")
                        pdf.ln(2)
                        
                        # Section 4
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "4. Conclusion & Commitment", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"By combining my rigorous technical competencies in spatial modeling, demonstrated publishing experience, and focused alignment with Dr. {prof_name.replace('Dr. ', '')}'s research themes, I am fully prepared to make an immediate, high-impact contribution as a funded PhD researcher.")
                        
                        pdf_bytes = bytes(pdf.output())
                        zip_file.writestr(file_name, pdf_bytes)
                        
                zip_buffer.seek(0)
                st.success(f"Successfully generated unique A4 Research Statement PDFs for {len(df_uploaded)} record(s)!")
                st.download_button(
                    label="Download Research Statements (ZIP)",
                    data=zip_buffer,
                    file_name="Research_Statements_ZIP.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
