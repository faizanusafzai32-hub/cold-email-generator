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

ALLOWED_TITLES = ["professor", "assistant professor", "associate professor", "chair", "head", "dr", "ph.d"]

def scrape_url_smartly(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted script/style tags
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        # 1. Extract Email Address (Look for mailto links first, then regex in text)
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
                
        # 2. Extract Name (Check page title or main heading h1/h2)
        name = ""
        for h in soup.find_all(['h1', 'h2']):
            text = h.get_text().strip()
            if len(text.split()) in [2, 3, 4] and not any(char.isdigit() for char in text):
                if not any(w in text.lower() for w in ["home", "department", "faculty", "welcome", "research", "university", "ut dallas"]):
                    name = text.replace("Dr.", "").replace("Prof.", "").strip()
                    break
                    
        if not name and soup.title:
            title_text = soup.title.get_text().strip()
            # Clean title text to find name
            clean_title = re.split(r'[-|:]', title_text)[0].strip()
            if len(clean_title.split()) in [2, 3]:
                name = clean_title.replace("Dr.", "").replace("Prof.", "").strip()
                
        if not name:
            name = "Faculty Member"
            
        # 3. Extract Expertise / Research Area
        expertise = "Geospatial modeling and remote sensing"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            expertise = meta_desc["content"][:100]
        else:
            for p in soup.find_all('p'):
                p_text = p.get_text().strip()
                if any(kw in p_text.lower() for kw in ["research", "interest", "gis", "remote sensing", "spatial", "modeling", "climate"]):
                    if len(p_text) > 20 and len(p_text) < 150:
                        expertise = p_text
                        break
                        
        return {
            "name": name,
            "email": email,
            "expertise": expertise
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

            # Global deduplication
            seen_global = set()
            for p in extracted_profs:
                ident = (p['name'].lower(), p['email'].lower())
                if ident not in seen_global:
                    seen_global.add(ident)
                    professors.append(p)

            if professors:
                st.success(f"Successfully processed {len(raw_urls)} URL(s) and extracted {len(professors)} profile(s) accurately!")
            else:
                st.warning("Could not extract profiles automatically from these links. Please check the URLs or use 'Manual Text Paste'.")
    else:
        prof_input = st.text_area("Faculty Directory Text:", placeholder="Paste copied faculty text here...", height=200)
        if prof_input.strip():
            # Basic manual parsing fallback
            lines = [l.strip() for l in prof_input.split('\n') if l.strip()]
            # Quick processing for pasted text
            professors.append({
                "name": lines[0] if lines else "Professor",
                "email": next((l for l in lines if "@" in l), "prof@uni.ca"),
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
                topic = prof['expertise'].split(',')[0][:30].title()
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
                        prof_name = str(row.get("Name", f"Professor_{idx+1}")).strip()
                        email_body = str(row.get("Email Body", ""))
                        
                        expertise_match = re.search(r"lab’s work on (.*?)\. My background", email_body, re.DOTALL)
                        if expertise_match:
                            expertise = expertise_match.group(1).strip()
                        else:
                            subj = str(row.get("Email Subject", ""))
                            expertise = subj.split(":")[1].split("—")[0].strip() if ":" in subj else "Geospatial Modeling & Remote Sensing"
                            
                        clean_prof_name = prof_name.replace("Dr. ", "").replace("Dr ", "").replace(".", "").strip().replace(" ", "_")
                        file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                        
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        
                        # PDF Header
                        pdf.set_font("Helvetica", style="B", size=13)
                        pdf.cell(0, 7, "STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "Faizan Ahmad", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.set_font("Helvetica", size=9)
                        pdf.cell(0, 4, "GIS Specialist", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, f"Mob: {FAIZAN_CV_DETAILS['phone']} | Email: {FAIZAN_CV_DETAILS['email']}", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, f"{FAIZAN_CV_DETAILS['linkedin']}", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(4)
                        
                        # Research Focus
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, f"Research Focus: Spatiotemporal Modeling, Remote Sensing, and {expertise.split(',')[0]}", new_x="LMARGIN", new_y="NEXT")
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
                        pdf.multi_cell(0, 4, f"My research focus centers on utilizing satellite remote sensing, spatial statistics, and machine learning to model environmental risks and ecosystem dynamics. I am particularly drawn to the research conducted in {prof_name}'s lab focusing on {expertise}. Your pioneering work directly aligns with my analytical background and research ambitions. I am keen to leverage cloud-based Earth Observation and automated geospatial analytics to advance spatial risk mapping and predictive modeling.")
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
                        pdf.multi_cell(0, 4, f"By bringing my 5.5+ years of practical GIS expertise and spatial modeling background to {prof_name}'s lab, I aim to advance data-driven spatial frameworks that support advanced environmental analytics, risk mitigation, and sustainable landscape management.")
                        
                        pdf_bytes = bytes(pdf.output())
                        zip_file.writestr(file_name, pdf_bytes)
                        
                zip_buffer.seek(0)
                st.success(f"Successfully generated Research Statement PDFs for {len(df_uploaded)} record(s)!")
                st.download_button(
                    label="Download Research Statements (ZIP)",
                    data=zip_buffer,
                    file_name="Research_Statements_ZIP.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
