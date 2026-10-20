import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import re

st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")
st.write("Choose your input method below: either provide a university faculty directory link or manually paste the copied text block.")

FAIZAN_CV_DETAILS = {
    "name": "Faizan Ahmad",
    "phone": "+92 349 9343568",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "MS in Remote Sensing & GIS and Bachelor of Science in GeoInformatics",
    "exp": "5.5+ years of experience in spatial data analytics, Python programming, and Google Earth Engine (GEE)",
    "pub": "co-authored a 2026 peer-reviewed paper in the Journal for Nature Conservation (Elsevier) focused on spatial statistical modeling and ecological dynamics"
}

# Radio button to select input method
input_method = st.radio("Select Input Method:", ["🔗 URL Link (Web Scraping)", "📝 Manual Text Paste"])

ALLOWED_TITLES = ["professor", "assistant professor", "associate professor", "chair", "head"]
professors = []
source_link_used = ""

if input_method == "🔗 URL Link (Web Scraping)":
    faculty_url = st.text_input(
        "University Faculty Directory Link (URL):",
        value="",
        placeholder="https://www.uvic.ca/geography/people/faculty/index.php"
    )
    source_link_used = faculty_url
    
    if faculty_url.strip():
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(faculty_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for script in soup(["script", "style"]):
                    script.extract()
                    
                page_text = soup.get_text(separator='\n')
                lines = [l.strip() for l in page_text.split('\n') if l.strip()]
                
                current_prof = None
                for line in lines:
                    clean_lower = line.lower()
                    is_title_match = any(title in clean_lower for title in ALLOWED_TITLES)
                    
                    if is_title_match:
                        if current_prof:
                            professors.append(current_prof)
                        
                        prev_line = lines[lines.index(line) - 1] if lines.index(line) > 0 else "Professor"
                        current_prof = {
                            "name": prev_line.replace("- ", "").strip(),
                            "designation": line,
                            "email": "prof@uni.ca",
                            "expertise": "Geospatial modeling and remote sensing"
                        }
                    elif current_prof:
                        if "@" in line:
                            current_prof["email"] = line
                        elif "expertise:" in clean_lower:
                            current_prof["expertise"] = line.split(":", 1)[1].strip()
                        elif any(k in clean_lower for k in ["climate", "modelling", "modeling", "remote", "gis", "spatial", "human", "technologies", "analysis", "cryosphere"]):
                            if len(line) > 12 and "office" not in clean_lower and "leave" not in clean_lower:
                                current_prof["expertise"] = line
                                
                if current_prof:
                    professors.append(current_prof)
                    
                seen_names = set()
                unique_professors = []
                for p in professors:
                    if p['name'] not in seen_names and len(p['name']) < 40:
                        seen_names.add(p['name'])
                        unique_professors.append(p)
                professors = unique_professors
                
                if professors:
                    st.success(f"Successfully scraped and found {len(professors)} targeted faculty member(s) from the link!")
                else:
                    st.warning("Could not automatically extract profiles from this link due to website restrictions. Please switch to 'Manual Text Paste'.")
            else:
                st.error(f"Failed to access URL. Status Code: {response.status_code}")
        except Exception as e:
            st.error(f"An error occurred while fetching the link: {e}")

else:
    prof_input = st.text_area(
        "Faculty Directory Text:",
        value="",
        placeholder="Paste copied faculty text here...",
        height=250
    )
    source_link_used = "Manual Text Paste"
    
    if prof_input.strip():
        lines = [l.strip() for l in prof_input.split('\n') if l.strip()]
        current_prof = None

        for line in lines:
            clean_lower = line.lower()
            is_title_match = any(title in clean_lower for title in ALLOWED_TITLES)
            
            if is_title_match:
                if current_prof:
                    professors.append(current_prof)
                
                prev_line = lines[lines.index(line) - 1] if lines.index(line) > 0 else "Professor"
                current_prof = {
                    "name": prev_line.replace("- ", "").strip(),
                    "designation": line,
                    "email": "prof@uni.ca",
                    "expertise": "Geospatial modeling and remote sensing"
                }
            elif current_prof:
                if "@" in line:
                    current_prof["email"] = line
                elif "expertise:" in clean_lower:
                    current_prof["expertise"] = line.split(":", 1)[1].strip()
                elif any(k in clean_lower for k in ["climate", "modelling", "modeling", "remote", "gis", "spatial", "human", "technologies", "analysis", "cryosphere"]):
                    if len(line) > 12 and "office" not in clean_lower and "leave" not in clean_lower:
                        current_prof["expertise"] = line

        if current_prof:
            professors.append(current_prof)
            
        if professors:
            st.success(f"Successfully parsed {len(professors)} targeted faculty member(s) from pasted text!")
        else:
            st.warning("No matching faculty roles found in the pasted text.")

col1, col2 = st.columns(2)

# Button 1: Download Emails Excel File
with col1:
    if st.button("📥 Download Emails Excel File"):
        if not professors:
            st.error("No faculty data available. Please provide a valid link or paste text.")
        else:
            excel_data = []
            for idx, prof in enumerate(professors, 1):
                full_name = prof['name'].replace("Dr. ", "").replace("Dr ", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                
                topic = prof['expertise'].split(',')[0].title()
                subject = f"Prospective PhD Student: {topic} — Faizan Ahmad"
                
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I hope you are doing well.\n\n"
                    f"My name is {FAIZAN_CV_DETAILS['name']}, and I hold an {FAIZAN_CV_DETAILS['degree']} with {FAIZAN_CV_DETAILS['exp']}. I also {FAIZAN_CV_DETAILS['pub']}.\n\n"
                    f"I am very interested in your lab’s work on {prof['expertise']}. My background in processing big spatiotemporal datasets, spatial statistical modeling, Python workflows, and Google Earth Engine (GEE) aligns strongly with your current research focus.\n\n"
                    f"Are you currently accepting funded PhD students for upcoming terms? I have attached my CV and a 1-page Statement of Research Interests for your review.\n\n"
                    f"With Kind Regards,\n"
                    f"Faizan Ahmad\n"
                    f"GIS Specialist\n"
                    f"WhatsApp/Mob: {FAIZAN_CV_DETAILS['phone']}\n"
                    f"{FAIZAN_CV_DETAILS['linkedin']}"
                )
                
                excel_data.append({
                    "Name": prof['name'],
                    "Source Link": source_link_used,
                    "Email Address": prof['email'],
                    "Designation": prof['designation'],
                    "Expertise": prof['expertise'],
                    "Email Subject": subject,
                    "Email Body": email_body
                })

            df = pd.DataFrame(excel_data)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Targeted Emails")
            buffer.seek(0)
            
            st.success(f"Successfully generated Excel sheet for {len(professors)} faculty member(s)!")
            st.download_button(
                label="Download .xlsx File",
                data=buffer,
                file_name="Targeted_Faculty_Emails.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Button 2: Download Research Statements ZIP File
with col2:
    if st.button("📥 Download Research Interests (ZIP)"):
        if not professors:
            st.error("No faculty data available. Please provide a valid link or paste text.")
        else:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for idx, prof in enumerate(professors, 1):
                    clean_prof_name = prof['name'].replace("Dr. ", "").replace("Dr ", "").replace(".", "").strip().replace(" ", "_")
                    file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Title Header
                    pdf.set_font("Helvetica", style="B", size=13)
                    pdf.cell(0, 7, "STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                    
                    # Contact Info Header
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, "Faizan Ahmad", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.set_font("Helvetica", size=9)
                    pdf.cell(0, 4, "GIS Specialist", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.cell(0, 4, f"Mob: {FAIZAN_CV_DETAILS['phone']} | Email: {FAIZAN_CV_DETAILS['email']}", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.cell(0, 4, f"{FAIZAN_CV_DETAILS['linkedin']}", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.ln(4)
                    
                    # Research Focus Line
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, f"Research Focus: Spatiotemporal Modeling, Remote Sensing, and {prof['expertise'].split(',')[0]}", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(3)
                    
                    # Section 1
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, "1. Academic & Professional Background", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, "I hold a Master of Science in Remote Sensing & GIS and a Bachelor of Science in Geoinformatics, complemented by over 5.5 years of professional experience as a GIS Specialist. My core expertise lies in spatiotemporal data analysis, automated geospatial workflows in Python, and cloud-based Earth Observation analytics using Google Earth Engine (GEE). My research capability is demonstrated by a peer-reviewed publication in the Journal for Nature Conservation (Elsevier, 2026), where I utilized spatial statistical modeling to evaluate land dynamics and ecological responses.")
                    pdf.ln(3)
                    
                    # Section 2
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, "2. My Research Focus", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, f"My research focus centers on utilizing satellite remote sensing, spatial statistics, and machine learning to model environmental risks and ecosystem dynamics. I am particularly drawn to the research conducted in {prof['name']}'s lab focusing on {prof['expertise']}. Your pioneering work directly aligns with my analytical background and research ambitions. I am keen to leverage cloud-based Earth Observation and automated geospatial analytics to advance spatial risk mapping and predictive modeling.")
                    pdf.ln(3)
                    
                    # Section 3
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, "3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, "During my doctoral studies, I aim to contribute to your lab's directions by focusing on:\n1. Spatiotemporal Risk Modeling: Integrating multi-decadal satellite observation time-series with spatial datasets.\n2. Automated Landscape Analytics: Developing Python and GEE-driven workflows for automated mapping and spatial analysis.\n3. Machine Learning & Predictive Risk Assessment: Applying advanced spatial statistics and machine learning algorithms to model environmental interactions.")
                    pdf.ln(3)
                    
                    # Section 4
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, "4. Conclusion", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, f"By bringing my 5.5+ years of practical GIS expertise and spatial modeling background to {prof['name']}'s lab, I aim to advance data-driven spatial frameworks that support advanced environmental analytics, risk mitigation, and sustainable landscape management.")
                    
                    pdf_bytes = bytes(pdf.output())
                    zip_file.writestr(file_name, pdf_bytes)
                    
            zip_buffer.seek(0)
            st.success(f"Successfully generated a ZIP archive containing Statements of Research Interests for {len(professors)} faculty member(s)!")
            st.download_button(
                label="Download ZIP File",
                data=zip_buffer,
                file_name="Research_Statements_ZIP.zip",
                mime="application/zip"
            )
