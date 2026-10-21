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
    "degree": "M.Sc. in Remote Sensing & GIS and B.Sc. in GeoInformatics",
    "exp": "5.5+ years of professional experience in GIS/Remote Sensing, Python, SQL, Google Earth Engine (GEE), and spatial modeling",
    "pub": "co-authored peer-reviewed research in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal LULC dynamics and habitat suitability modeling"
}

tab1, tab2 = st.tabs(["📧 1. Generate Targeted Email & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

def clean_pdf_text(text):
    if not isinstance(text, str):
        return ""
    return (text.replace('“', '"').replace('”', '"')
                .replace('‘', "'").replace('’', "'")
                .replace('—', '-').replace('–', '-')
                .replace('•', '-')
                .encode('latin-1', 'replace').decode('latin-1'))

def extract_clean_name(raw_text):
    bad_words = ["assistant", "associate", "professor", "department", "university", "faculty", "gis", "health", "policy", "chair", "director", "dr.", "dr"]
    words = raw_text.split()
    cleaned = [w for w in words if w.lower().strip(".,") not in bad_words and not any(char.isdigit() for char in w)]
    if len(cleaned) >= 2:
        return " ".join(cleaned[:3]).title()
    return ""

def scrape_url_smartly(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        page_full_text = soup.get_text()
        
        email = ""
        mailto_tag = soup.find(href=re.compile(r"^mailto:", re.I))
        if mailto_tag:
            email = mailto_tag['href'].replace("mailto:", "").strip().split('?')[0]
        
        if not email or "@" not in email:
            email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', page_full_text)
            if email_match:
                email = email_match.group(0)
                
        name = ""
        url_slug = url.strip('/').split('/')[-1].replace('~', '').replace('.', ' ')
        if len(url_slug.split()) in [2, 3] and not any(char.isdigit() for char in url_slug):
            name = url_slug.title()
            
        if not name and soup.title:
            title_text = soup.title.get_text().strip()
            clean_title = re.split(r'[-|:|–]', title_text)[0].strip()
            name = extract_clean_name(clean_title)
            
        if not name:
            for h in soup.find_all(['h1', 'h2']):
                candidate = extract_clean_name(h.get_text().strip())
                if candidate:
                    name = candidate
                    break
                    
        if not name:
            name = "Faculty Member"
            
        expertise = "Geospatial Analytics, Remote Sensing, and Spatial Dynamics"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            expertise = meta_desc["content"][:100]
        else:
            for p in soup.find_all('p'):
                p_text = p.get_text().strip()
                if any(kw in p_text.lower() for kw in ["research", "interest", "gis", "remote sensing", "spatial", "demography", "health"]):
                    if 20 < len(p_text) < 150:
                        expertise = p_text
                        break
                        
        expertise = re.sub(r'^(I|My|We|Our)\s+', '', expertise, flags=re.IGNORECASE)
        return {
            "name": clean_pdf_text(name),
            "email": clean_pdf_text(email if email else "prof@university.edu"),
            "expertise": clean_pdf_text(expertise)
        }
    except Exception:
        return None

# ==================== TAB 1 ====================
with tab1:
    st.write("Select input method to extract details or generate precision-tailored emails.")
    input_method = st.radio("Select Input Method:", ["🔗 URL Links Scraping", "📝 Raw Text Paste", "✍️ Direct Manual Input Form"])
    professors = []

    if input_method == "🔗 URL Links Scraping":
        urls_input = st.text_area(
            "Faculty Web Links (One URL per line):",
            placeholder="https://profiles.utdallas.edu/yingyi.lin\nwww.utdallas.edu/~briggs/",
            height=130
        )
        if urls_input.strip():
            raw_urls = [u.strip() for u in re.split(r'[\n,\s]+', urls_input) if u.strip()]
            for url in raw_urls:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                prof_data = scrape_url_smartly(url)
                if prof_data:
                    professors.append(prof_data)
            if professors:
                st.success(f"Extracted {len(professors)} profile(s)!")

    elif input_method == "📝 Raw Text Paste":
        prof_input = st.text_area("Paste Copied Faculty Text/Profile:", placeholder="Yingyi Lin\nYingyi.Lin@UTDallas.edu\nDemography, public health, and spatial population dynamics", height=150)
        if prof_input.strip():
            lines = [l.strip() for l in prof_input.split('\n') if l.strip()]
            p_email = next((l for l in lines if "@" in l), "prof@university.edu")
            p_name = extract_clean_name(lines[0]) if len(lines) > 0 else "Professor"
            if not p_name:
                p_name = lines[0]
            p_exp = lines[2] if len(lines) > 2 else "Geospatial Analytics and Remote Sensing"
            p_exp = re.sub(r'^(I|My|We|Our)\s+', '', p_exp, flags=re.IGNORECASE)
            
            professors.append({
                "name": clean_pdf_text(p_name),
                "email": clean_pdf_text(p_email),
                "expertise": clean_pdf_text(p_exp)
            })
            st.success("Extracted 1 profile from text!")

    else:
        col1, col2 = st.columns(2)
        with col1:
            m_name = st.text_input("Professor Name:", value="Yingyi Lin")
            m_email = st.text_input("Professor Email Address:", value="Yingyi.Lin@UTDallas.edu")
        with col2:
            m_expertise = st.text_input("Core Research Theme / Domain:", value="Demography, public health, and spatial population dynamics")
            
        m_lab = st.text_input("Lab or Research Group Name (Optional):", value="")
        if m_name.strip():
            professors.append({
                "name": clean_pdf_text(m_name),
                "email": clean_pdf_text(m_email),
                "expertise": clean_pdf_text(m_expertise),
                "lab": clean_pdf_text(m_lab)
            })

    if st.button("📥 Generate & Download Excel File"):
        if not professors:
            st.error("No faculty data available to generate Excel.")
        else:
            excel_data = []
            for prof in professors:
                full_name = prof['name'].replace("Dr.", "").replace("Dr", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                theme_clean = prof['expertise'].strip()
                lab_ref = f" in your {prof.get('lab', '').strip()} research group" if prof.get('lab', '').strip() else ""
                
                subject = f"Prospective PhD Inquiry: {theme_clean[:40]} — Faizan Ahmad"
                
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I have been following your scholarly work and publications focusing on {theme_clean}{lab_ref}. Your lab's contributions to spatial analytics provide an inspiring framework for advanced geographical research.\n\n"
                    f"With an M.Sc. in Remote Sensing & GIS, 5.5+ years of spatial analytics experience (Python, SQL, GEE), and peer-reviewed research published in the Journal for Nature Conservation (Elsevier) on spatiotemporal modeling, I am keen to apply quantitative spatial frameworks to your ongoing projects.\n\n"
                    f"Are you currently accepting PhD students with funded positions (RA, TA, or Fellowships) in your lab for upcoming terms? I have attached my CV and a 1-page Statement of Research Interests for your review.\n\n"
                    f"Thank you for your time and consideration.\n\n"
                    f"Sincerely,\n"
                    f"Faizan Ahmad\n"
                    f"GIS Specialist\n"
                    f"WhatsApp/Mob: {FAIZAN_CV_DETAILS['phone']}\n"
                    f"{FAIZAN_CV_DETAILS['linkedin']}"
                )
                
                excel_data.append({
                    "Name": prof['name'],
                    "Email Address": prof['email'],
                    "Email Subject": subject,
                    "Email Body": email_body,
                    "Research Theme": theme_clean
                })

            df = pd.DataFrame(excel_data)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Targeted Email")
            buffer.seek(0)
            
            st.success("Successfully generated tailored email package!")
            st.download_button(
                label="Download .xlsx File",
                data=buffer,
                file_name="Targeted_Faculty_Email.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ==================== TAB 2 ====================
with tab2:
    st.write("Upload your processed Excel file (`Targeted_Faculty_Email.xlsx`) to generate tailored Statement of Research Interest PDFs.")
    
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
                        theme = clean_pdf_text(str(row.get("Research Theme", "Spatial Analysis")))
                        
                        clean_prof_name = prof_name.replace("Dr.", "").replace("Dr", "").replace(".", "").strip().replace(" ", "_")
                        file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                        
                        pdf = FPDF(orientation='P', unit='mm', format='A4')
                        pdf.set_margins(left=15, top=15, right=15)
                        pdf.add_page()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        
                        pdf.set_font("Helvetica", style="B", size=13)
                        pdf.cell(0, 7, "STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, FAIZAN_CV_DETAILS["name"], new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.set_font("Helvetica", size=9)
                        pdf.cell(0, 4, "GIS Specialist", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, f"Mob: {FAIZAN_CV_DETAILS['phone']} | Email: {FAIZAN_CV_DETAILS['email']}", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.cell(0, 4, f"{FAIZAN_CV_DETAILS['linkedin']}", new_x="LMARGIN", new_y="NEXT", align="C")
                        pdf.ln(3)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.multi_cell(0, 4, f"Research Focus: Integrating Spatial Analytics, Python Workflows, and {theme}", align="L")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "1. Academic Foundation & Technical Expertise", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My academic credentials include an M.Sc. in Remote Sensing & GIS and a B.Sc. in GeoInformatics, backed by 5.5+ years of practical GIS experience. My technical competencies span advanced Python, SQL, Google Earth Engine (GEE), and spatial statistical modeling. Demonstrating my academic research capability, I co-authored peer-reviewed research published in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal dynamics and spatial risk assessment.")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, f"2. Alignment with Dr. {prof_name.replace('Dr. ', '')}'s Research Lab", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My doctoral research interests are directly inspired by the scholarly contributions and investigations led by Dr. {prof_name.replace('Dr. ', '')} in the domain of {theme}. The methodological frameworks developed through your research group offer an ideal platform for integrating big data spatial analytics with complex geographical systems. I am eager to contribute my technical background in automated geospatial processing to support and expand upon your ongoing objectives.")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"To synthesize my technical skill set with your lab's mission, I propose focusing my dissertation on three core pillars: (1) integrating multi-decadal observation time-series with spatial metrics to evaluate longitudinal change; (2) developing scalable Python and GEE workflows tailored to {theme.lower()} for rapid spatial mapping; and (3) applying advanced spatial statistics to simulate predictive environmental and social risk surfaces.")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "4. Conclusion & Commitment", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"By combining my rigorous technical competencies in spatial modeling, demonstrated publishing experience, and focused alignment with Dr. {prof_name.replace('Dr. ', '')}'s research themes, I am fully prepared to make an immediate, high-impact contribution as a funded PhD researcher.")
                        
                        pdf_bytes = bytes(pdf.output())
                        zip_file.writestr(file_name, pdf_bytes)
                        
                zip_buffer.seek(0)
                st.success(f"Successfully generated mentor-guided A4 Research Statement PDFs for {len(df_uploaded)} record(s)!")
                st.download_button(
                    label="Download Research Statements (ZIP)",
                    data=zip_buffer,
                    file_name="Research_Statements_ZIP.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
