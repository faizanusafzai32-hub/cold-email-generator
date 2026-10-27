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
    "degree": "M.Sc. Remote Sensing & GIS (IST, Islamabad) & B.Sc. Geo-Informatics",
    "exp": "over 5.5 years of professional experience in spatial analytics and Earth Observation",
    "skills": "Python, SQL, and Google Earth Engine (GEE)",
    "pub": "peer-reviewed publication in the Journal for Nature Conservation (Elsevier)",
    "thesis": "M.Sc. thesis on assessing the impact of LULC changes on flood risk"
}

tab1, tab2 = st.tabs(["📧 1. Multi-Professor Structured Form & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

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

def precise_keyword_focus(raw_text, bio_text=""):
    combined = (str(raw_text) + " " + str(bio_text)).strip()
    if not combined:
        return "Remote Sensing & Spatial Analytics"
    
    text = combined.lower()
    fillers = [
        "he focuses on the intersections of", "she focuses on the intersections of",
        "he focuses on", "she focuses on", "his research", "her research",
        "interests include", "research interests", "geography and",
        "interdisciplinary applied gis", "qualitative and quantitative methods",
        "natural resource use", "the building of", "globalization", 
        "territoriality, identity and culture", "academic interests"
    ]
    for f in fillers:
        text = text.replace(f, "")
        
    if "sustainability" in text or "political ecology" in text:
        return "Political Ecology & Sustainability"
    elif "gis education" in text or "geography education" in text:
        return "GIS Education & Spatial Methods"
    elif "cartography" in text or "geovisualization" in text:
        return "Cartography & Geovisualization"
    elif "hydrology" in text or "water" in text or "wetland" in text or "flood" in text:
        return "Satellite Hydrology & Water Resources"
    elif "geodesy" in text or "gps" in text or "meteorology" in text or "climate" in text:
        return "Geodesy & GPS Meteorology"
    elif "geoai" in text or "machine learning" in text or "deep learning" in text:
        return "Remote Sensing & GeoAI"
    
    # Auto-comma/ampersand formatting utility
    words = [w.strip() for w in re.split(r'[,;\n]+', raw_text) if w.strip()]
    if len(words) > 1:
        if len(words) == 2:
            return f"{words[0].title()} & {words[1].title()}"
        return f"{', '.join([w.title() for w in words[:-1]])} & {words[-1].title()}"
        
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = [w for w in cleaned.split() if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'our', 'are', 'use', 'space']]
    
    if tokens:
        if len(tokens) >= 3:
            return f"{tokens[0].title()}, {tokens[1].title()} & {tokens[2].title()}"
        return " ".join([t.title() for t in tokens[:4]])
    
    return "Remote Sensing & Spatial Analytics"

def extract_paper_topic_reference(pub_ref, expertise, bio=""):
    if pub_ref and len(pub_ref.strip()) > 3:
        return pub_ref.strip()
    
    if bio and len(bio.strip()) > 10:
        cleaned_bio = re.sub(r'http\S+', '', bio).strip()
        sentences = [s.strip() for s in re.split(r'[\.\n]', cleaned_bio) if len(s.strip()) > 15]
        if sentences:
            return sentences[0][:80].rstrip(',')
            
    focus = precise_keyword_focus(expertise)
    return f"advancements in {focus.lower()}"

def get_tailored_statement_content(prof_name, focus_domain):
    domain = focus_domain.lower()
    clean_prof = prof_name.replace("Dr.", "").replace("Dr", "").strip()

    if "geodesy" in domain or "gps" in domain or "meteorology" in domain or "climate" in domain:
        sec2 = (
            f"My doctoral aspirations are strongly aligned with Dr. {clean_prof}'s pioneering research in geodesy, GPS meteorology, and climate-induced Earth system variations. "
            f"With my robust background in high-precision spatial positioning, remote sensing time-series, and quantitative geospatial analytics, "
            f"I am eager to apply advanced data processing techniques to measure crustal deformation, atmospheric water vapor, and climate signals using spaceborne geodetic networks."
        )
        sec3 = (
            f"To synthesize my technical skills with your lab's mission in {focus_domain.lower()}, I propose focusing my dissertation on three core pillars: "
            f"(1) processing high-frequency GPS and geodetic time-series data using scalable Python automation frameworks; "
            f"(2) evaluating atmospheric precipitable water vapor and meteorological anomalies to refine climate tracking models; and "
            f"(3) applying spatial-temporal statistical modeling to analyze geodetic deformation and environmental surface responses."
        )
        sec4 = (
            f"By combining my strong quantitative background in spatial modeling, Python workflows, and demonstrated Elsevier publishing experience, "
            f"I am fully prepared to make immediate, high-impact contributions to Dr. {clean_prof}'s geodetic and climate research program."
        )

    elif "hydrology" in domain or "water" in domain or "wetland" in domain:
        sec2 = (
            f"My doctoral aspirations strongly align with Dr. {clean_prof}'s pioneering research in satellite hydrology and surface water elevation dynamics. "
            f"Having conducted my M.Sc. thesis on spatiotemporal flood risk and LULC modeling, combined with 5.5+ years of geospatial Python and GEE workflows, "
            f"I am deeply motivated to apply spaceborne remote sensing to bridge data gaps in complex river basins and ungauged wetland systems."
        )
        sec3 = (
            f"To synthesize my technical skills with your lab's mission in {focus_domain.lower()}, I propose focusing my dissertation on three core pillars: "
            f"(1) fusing multi-sensor satellite altimetry with SAR/optical imagery in GEE to map dynamic surface water storage; "
            f"(2) developing scalable Python workflows to derive continuous river slope and discharge estimates; and "
            f"(3) applying spatial statistics to model hydro-ecological risk and flood inundation scenarios."
        )
        sec4 = (
            f"By combining my solid foundation in satellite time-series analysis, Python geospatial automation, and demonstrated Elsevier publishing experience, "
            f"I am fully prepared to make immediate, innovative contributions to Dr. {clean_prof}'s research program."
        )

    elif "cartography" in domain or "geovisualization" in domain:
        sec2 = (
            f"My doctoral research interests are directly inspired by the cartographic and geovisualization research led by Dr. {clean_prof}. "
            f"With 5.5+ years of practical GIS experience and custom Python tool development, I am eager to bridge quantitative spatial analytics "
            f"with interactive geovisualization methods. Your lab's focus on spatial representation provides an ideal platform for designing "
            f"next-generation dynamic visual frameworks and spatial decision support interfaces."
        )
        sec3 = (
            f"To align my technical competencies with your lab's mission in {focus_domain.lower()}, I propose a dissertation focused on three core pillars: "
            f"(1) developing scalable Python and GEE workflows for real-time web-based geovisualization; "
            f"(2) evaluating cartographic spatial metrics to enhance visual communication of complex spatial risk data; and "
            f"(3) integrating multi-dimensional spatial time-series into interactive visual analytics platforms."
        )
        sec4 = (
            f"By combining my background in automated geospatial processing, remote sensing time-series, and demonstrated publishing record, "
            f"I am fully prepared to make immediate, innovative contributions to Dr. {clean_prof}'s cartographic and geovisualization research program."
        )

    elif "political ecology" in domain or "sustainability" in domain or "environment" in domain:
        sec2 = (
            f"My doctoral aspirations strongly align with Dr. {clean_prof}'s research in {focus_domain.lower()}. "
            f"My background in remote sensing, spatiotemporal land-use modeling, and habitat dynamics-highlighted by my publication in the "
            f"Journal for Nature Conservation (Elsevier)-directly complements your lab's focus on human-environment interactions. "
            f"I am keen to integrate satellite observation time-series with socio-ecological frameworks to evaluate regional sustainability."
        )
        sec3 = (
            f"To support your lab's ongoing research in {focus_domain.lower()}, my proposed dissertation directions include: "
            f"(1) leveraging multi-decadal Landsat/Sentinel observations in GEE to quantify environmental change and land degradation; "
            f"(2) applying spatial statistical modeling (MaxEnt/GLM) to evaluate ecological risk and sustainable resource allocation; and "
            f"(3) modeling multi-criteria spatial scenarios to guide evidence-based regional sustainability policies."
        )
        sec4 = (
            f"Leveraging my strong technical foundation in GIS, Python automation, and environmental modeling, I am committed to advancing "
            f"high-impact, policy-relevant ecological research under Dr. {clean_prof}'s mentorship."
        )

    else:
        sec2 = (
            f"My doctoral research interests are directly inspired by the scholarly contributions led by Dr. {clean_prof} in {focus_domain.lower()}. "
            f"My academic foundation in M.Sc. Remote Sensing & GIS, combined with 5.5+ years of quantitative spatial analytics, offers an ideal alignment "
            f"with your research group. I am eager to apply big data spatial analytics, Python automation, and satellite time-series analysis "
            f"to advance empirical spatial research in your ongoing projects."
        )
        sec3 = (
            f"To synthesize my technical skill set with your lab's mission in {focus_domain.lower()}, I propose a dissertation structured around: "
            f"(1) integrating multi-decadal satellite observation time-series with spatial metrics to evaluate longitudinal change; "
            f"(2) developing scalable Python and GEE computational workflows tailored to {focus_domain.lower()}; and "
            f"(3) applying advanced spatial statistics to simulate predictive environmental and spatial risk surfaces."
        )
        sec4 = (
            f"By combining my technical competencies in spatial modeling, demonstrated publishing experience in Elsevier journals, and focused alignment "
            f"with Dr. {clean_prof}'s research vision, I am fully prepared to contribute effectively as a funded PhD researcher."
        )

    return clean_pdf_text(sec2), clean_pdf_text(sec3), clean_pdf_text(sec4)

# ==================== TAB 1 ====================
with tab1:
    st.subheader("📝 Enter Professor Details & Generate Targeted Email Package")
    st.write("Enter professor details below. System generates customized email subjects & bodies aligned with your profile.")
    
    num_profs = st.number_input("Kitne professors ki details enter karni hain?", min_value=1, max_value=10, value=2, step=1)
    
    professors_data = []
    
    for i in range(int(num_profs)):
        st.markdown(f"---")
        st.markdown(f"#### 👨‍🏫 Professor Entry {i+1}")
        
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input(f"Professor Name {i+1}:", key=f"name_{i}", placeholder="e.g., Dr. Michael Bevis")
            p_email = st.text_input(f"Email Address {i+1}:", key=f"email_{i}", placeholder="e.g., bevis.6@osu.edu")
        with col2:
            p_expertise = st.text_input(f"Research Area / Expertise {i+1}:", key=f"exp_{i}", placeholder="e.g., Geodesy, GPS Meteorology, Climate")
            p_pub = st.text_input(f"Key Publication / Project Reference {i+1} (Optional):", key=f"pub_{i}", placeholder="e.g., spaceborne geodetic tracking")
            
        p_link = st.text_input(f"Profile Link {i+1} (For verification):", key=f"link_{i}", placeholder="e.g., https://earthsciences.osu.edu/people/bevis.6")
        p_bio = st.text_area(f"Professor Bio / About Me Text {i+1} (Optional - Copy paste from website):", key=f"bio_{i}", placeholder="e.g., Paste biography, lab summary, or paper title here...")
        
        if p_name.strip() and p_email.strip():
            professors_data.append({
                "name": p_name.strip(),
                "email": p_email.strip(),
                "expertise": p_expertise.strip() if p_expertise.strip() else "Remote Sensing & Spatial Analytics",
                "pub_ref": p_pub.strip(),
                "link": p_link.strip(),
                "bio": p_bio.strip()
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
                focus_clean = precise_keyword_focus(prof['expertise'], prof['bio'])
                paper_ref = extract_paper_topic_reference(prof['pub_ref'], prof['expertise'], prof['bio'])
                
                subject = f"Prospective Ph.D. Applicant — {focus_clean} - Faizan Ahmad"
                
                # Updated Email Body Structure with Quotes/Italics for Paper & Proper Spacing
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I hope you are doing well.\n\n"
                    f"I am writing to express my strong interest in joining your research group as a Ph.D. candidate. Having read your recent work on *'{paper_ref}'*, I am deeply impressed by how your lab integrates quantitative spatial analytics with Earth Observation.\n\n"
                    f"I hold an M.Sc. in Remote Sensing & GIS and bring over 5.5 years of professional experience in spatial analytics and Earth Observation. My core technical expertise includes Python, SQL, and Google Earth Engine (GEE), alongside a peer-reviewed publication in the Journal for Nature Conservation (Elsevier).\n\n"
                    f"Given my strong background, I am eager to apply my skills to your lab's ongoing projects.\n\n"
                    f"Could you please let me know if you are accepting Ph.D. students for upcoming terms with funded Graduate Assistantships (RA/TA)?\n\n"
                    f"I have attached my CV for your review. Thank you very much for your time and consideration, and I look forward to hearing from you.\n\n\n"
                    f"Best Regards,\n"
                    f"Faizan Ahmad\n"
                    f"GIS Specialist\n"
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
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Targeted Emails")
            buffer.seek(0)
            
            st.success(f"Successfully generated targeted email package for {len(excel_rows)} professor(s)!")
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
                        email_body = clean_pdf_text(str(row.get("Email Body", "")))
                        
                        focus = "Remote Sensing & Spatial Analytics"
                        if "—" in subject and "-" in subject:
                            focus = subject.split("—")[1].split("-")[0].strip()
                        elif "-" in subject:
                            parts = subject.split("-")
                            if len(parts) >= 2:
                                focus = parts[0].replace("Prospective Ph.D. Applicant", "").replace(":", "").strip()
                                
                        focus = clean_pdf_text(precise_keyword_focus(focus))
                        sec2_text, sec3_text, sec4_text = get_tailored_statement_content(prof_name, focus)
                        
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
                        pdf.cell(0, 5, clean_pdf_text(FAIZAN_CV["name"]), new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.set_font("Helvetica", style="B", size=9)
                        pdf.cell(0, 4, "GIS Specialist", new_x="LMARGIN", new_y="NEXT", align="C")
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
                        pdf.multi_cell(0, 3.8, clean_pdf_text("My academic credentials include an M.Sc. in Remote Sensing & GIS and a B.Sc. in GeoInformatics, backed by 5.5+ years of practical GIS experience. My technical competencies span advanced Python, SQL, Google Earth Engine (GEE), and spatial statistical modeling. Demonstrating my academic research capability, I co-authored peer-reviewed research published in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal dynamics and spatial risk assessment."))
                        pdf.ln(2)
                        
                        # Section 2: Unique Domain Alignment
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, clean_pdf_text(f"2. Alignment with Dr. {prof_name.replace('Dr. ', '')}'s Research Lab"), new_x="LMARGIN", new_y="NEXT")
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
