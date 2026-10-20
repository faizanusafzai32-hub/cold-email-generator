import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import re

st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")

FAIZAN_CV_DETAILS = {
    "name": "Faizan Ahmad",
    "phone": "+92 349 9343568",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "MS in Remote Sensing & GIS and Bachelor of Science in GeoInformatics",
    "exp": "5.5+ years of experience in spatial data analytics, Python programming, and Google Earth Engine (GEE)",
    "pub": "co-authored a 2026 peer-reviewed paper in the Journal for Nature Conservation (Elsevier) focused on spatial statistical modeling and ecological dynamics"
}

tab1, tab2 = st.tabs(["📧 1. Extract Faculty & Download Excel", "📄 2. Upload Excel & Generate Research Statements (ZIP)"])

def clean_pdf_text(text):
    if not isinstance(text, str):
        return ""
    return (text.replace('“', '"').replace('”', '"')
                .replace('‘', "'").replace('’', "'")
                .replace('—', '-').replace('–', '-')
                .replace('•', '-')
                .encode('latin-1', 'replace').decode('latin-1'))

def scrape_url_smartly(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        email = ""
        mailto_tag = soup.find(href=re.compile(r"^mailto:"))
        if mailto_tag:
            email = mailto_tag['href'].replace("mailto:", "").strip().split('?')[0]
        
        if not email or "@" not in email:
            page_full_text = soup.get_text()
            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', page_full_text)
            if email_match:
                email = email_match.group(0)
            else:
                email = "contact@university.edu"
                
        name = ""
        for h in soup.find_all(['h1', 'h2']):
            text = h.get_text().strip()
            if len(text.split()) in [2, 3, 4] and not any(char.isdigit() for char in text):
                if not any(w in text.lower() for w in ["home", "department", "faculty", "welcome", "research", "university"]):
                    name = text.replace("Dr.", "").replace("Prof.", "").strip()
                    break
                    
        if not name and soup.title:
            title_text = soup.title.get_text().strip()
            clean_title = re.split(r'[-|:]', title_text)[0].strip()
            if len(clean_title.split()) in [2, 3]:
                name = clean_title.replace("Dr.", "").replace("Prof.", "").strip()
                
        if not name:
            name = "Faculty Member"
            
        expertise = "Geospatial modeling and remote sensing"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            expertise = meta_desc["content"][:120]
        else:
            for p in soup.find_all('p'):
                p_text = p.get_text().strip()
                if any(kw in p_text.lower() for kw in ["research", "interest", "gis", "remote sensing", "spatial", "modeling", "climate"]):
                    if len(p_text) > 20 and len(p_text) < 150:
                        expertise = p_text
                        break
                        
        return {
            "name": clean_pdf_text(name),
            "email": clean_pdf_text(email),
            "expertise": clean_pdf_text(expertise)
        }
    except Exception as e:
        return None


# ==================== TAB 1 ====================
with tab1:
    st.write("Extract targeted faculty profiles or personal website details, then download the structured Excel sheet.")
    input_method = st.radio("Select Input Method:", ["🔗 URL Links (Multiple Web Scraping)", "📝 Manual Text Paste"])
    professors = []

    if input_method == "🔗 URL Links (Multiple Web Scraping)":
        urls_input = st.text_area(
            "University / Personal Website Links (One URL per line or separated by commas):",
            placeholder="www.utdallas.edu/~briggs/\nhttps://profiles.utdallas.edu/ywchun",
            height=150
        )
        
        if urls_input.strip():
            raw_urls = [u.strip() for u in re.split(r'[\n,\s]+', urls_input) if u.strip()]
            extracted_profs = []
            for url in raw_urls:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                prof_data = scrape_url_smartly(url)
                if prof_data:
                    extracted_profs.append(prof_data)

            seen_global = set()
            for p in extracted_profs:
                ident = (p['name'].lower(), p['email'].lower())
                if ident not in seen_global:
                    seen_global.add(ident)
                    professors.append(p)

            if professors:
                st.success(f"Successfully processed {len(raw_urls)} URL(s) and extracted {len(professors)} profile(s) accurately!")
            else:
                st.warning("Could not extract profiles automatically from these links.")
    else:
        prof_input = st.text_area("Faculty Directory Text:", placeholder="Paste copied faculty text here...", height=200)
        if prof_input.strip():
            lines = [l.strip() for l in prof_input.split('\n') if l.strip()]
            professors.append({
                "name": clean_pdf_text(lines[0] if lines else "Professor"),
                "email": clean_pdf_text(next((l for l in lines if "@" in l), "prof@uni.ca")),
                "expertise": "Geospatial modeling and remote sensing"
            })
            if professors:
                st.success(f"Extracted {len(professors)} profile(s) from text!")

    if st.button("📥 Download Emails Excel File"):
        if not professors:
            st.error("No faculty data available.")
        else:
            excel_data = []
            for prof in professors:
                full_name = prof['name'].replace("Dr. ", "").replace("Dr ", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                topic = prof['expertise'].split(',')[0][:35].title()
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
                    "Email Address": prof['email'],
                    "Email Subject": subject,
                    "Email Body": email_body
                })

            df = pd.DataFrame(excel_data)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Targeted Emails")
            buffer.seek(0)
            
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
                        email_body = clean_pdf_text(str(row.get("Email Body", "")))
                        
                        expertise_match = re.search(r"lab’s work on (.*?)\. My background", email_body, re.DOTALL)
                        if expertise_match:
                            expertise = clean_pdf_text(expertise_match.group(1))
                        else:
                            subj = clean_pdf_text(str(row.get("Email Subject", "")))
                            expertise = subj.split(":")[1].split("—")[0].strip() if ":" in subj else "Geospatial Modeling & Remote Sensing"
                            
                        expertise = re.sub(r'\s*[-–—]\s*Faizan.*$', '', expertise, flags=re.IGNORECASE).strip()
                            
                        clean_prof_name = prof_name.replace("Dr. ", "").replace("Dr ", "").replace(".", "").strip().replace(" ", "_")
                        file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                        
                        # Standard A4 Page Setup with proper margins
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
                        pdf.multi_cell(0, 4, f"Research Focus: Advanced Spatiotemporal Modeling, Remote Sensing Analytics, and {expertise}", align="L")
                        pdf.ln(2)
                        
                        # Section 1
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "1. Academic & Professional Background", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, "I hold a Master of Science in Remote Sensing & GIS and a Bachelor of Science in Geoinformatics, complemented by over 5.5 years of professional experience as a GIS Specialist. My technical competencies span advanced spatiotemporal data analysis, automated geospatial processing workflows in Python, and cloud-based Earth Observation analytics via Google Earth Engine (GEE). My foundational research capability is explicitly demonstrated by my 2026 peer-reviewed publication in the Journal for Nature Conservation (Elsevier), where I utilized rigorous spatial statistical modeling to evaluate environmental land dynamics and ecological responses.")
                        pdf.ln(2)
                        
                        # Section 2
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "2. Motivation & Alignment with Lab Research", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My doctoral research aspirations center on leveraging high-resolution satellite remote sensing, spatial statistics, and machine learning algorithms to model complex environmental interactions and risk surfaces. I am particularly drawn to the pioneering work conducted in {prof_name}'s research lab focusing specifically on {expertise}. Your lab's contributions to spatial analytics and regional dynamics resonate seamlessly with my professional background and long-term academic goals. I am eager to integrate cloud-based big data analytics with your ongoing projects to push the boundaries of predictive environmental modeling.")
                        pdf.ln(2)
                        
                        # Section 3
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"To contribute meaningfully to {prof_name}'s laboratory objectives, I propose focusing my doctoral research on the following interconnected directions:\n- High-Resolution Spatiotemporal Modeling: Synthesizing multi-decadal satellite observation time-series with high-density spatial vector datasets to evaluate long-term environmental trends.\n- Automated Cloud-Native Geospatial Workflows: Developing scalable Python and Google Earth Engine (GEE) pipelines tailored to {expertise.split(',')[0].lower()} for rapid, large-scale spatial mapping.\n- Predictive Machine Learning Frameworks: Applying advanced spatial statistical techniques and machine learning algorithms to quantify environmental risks and support evidence-based decision making.")
                        pdf.ln(2)
                        
                        # Section 4
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "4. Conclusion", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"By bringing my 5.5+ years of practical GIS expertise, robust Python programming skills, and a proven publication record to {prof_name}'s lab, I am fully prepared to drive impactful research. I aim to develop robust spatial frameworks that advance environmental analytics, risk mitigation, and sustainable landscape management.")
                        
                        pdf_bytes = bytes(pdf.output())
                        zip_file.writestr(file_name, pdf_bytes)
                        
                zip_buffer.seek(0)
                st.success(f"Successfully generated professional A4 Research Statement PDFs for {len(df_uploaded)} record(s)!")
                st.download_button(
                    label="Download Research Statements (ZIP)",
                    data=zip_buffer,
                    file_name="Research_Statements_ZIP.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
