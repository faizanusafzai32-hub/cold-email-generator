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

def parse_profile_text(raw_text):
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    name = "Faculty Member"
    email = "prof@university.edu"
    focus = "Spatial Analysis and Environmental Modeling"
    
    for line in lines:
        if "@" in line:
            email = line.strip()
        elif any(title in line.lower() for title in ["dr.", "prof", "ph.d"]):
            name = line.replace("Dr.", "").replace("Prof.", "").strip()
        elif len(line.split()) in [2, 3] and name == "Faculty Member" and not any(char.isdigit() for char in line):
            name = line.strip()
        elif len(line) > 10 and "http" not in line.lower() and "@" not in line:
            focus = line
            
    focus = re.sub(r'^(I|My|We|Our)\s+', '', focus, flags=re.IGNORECASE)
    return clean_pdf_text(name), clean_pdf_text(email), clean_pdf_text(focus)

def scrape_url_smartly(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
            words = clean_title.split()
            cleaned = [w for w in words if w.lower().strip(".,") not in ["assistant", "associate", "professor", "department", "university"] and not any(char.isdigit() for char in w)]
            if len(cleaned) >= 2:
                name = " ".join(cleaned[:3]).title()
                
        if not name:
            name = "Faculty Member"
            
        focus = "Spatial Analysis and Environmental Modeling"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            focus = meta_desc["content"][:100]
        else:
            for p in soup.find_all('p'):
                p_text = p.get_text().strip()
                if any(kw in p_text.lower() for kw in ["research", "interest", "gis", "remote sensing", "spatial", "demography", "health", "urban"]):
                    if 15 < len(p_text) < 120:
                        focus = p_text
                        break
                        
        focus = re.sub(r'^(I|My|We|Our)\s+', '', focus, flags=re.IGNORECASE)
        return {
            "name": clean_pdf_text(name),
            "email": clean_pdf_text(email if email else "prof@university.edu"),
            "focus": clean_pdf_text(focus)
        }
    except Exception:
        return None

# ==================== TAB 1 ====================
with tab1:
    st.write("Sirf Professor Name, Email, aur Research Focus ke sath precision-tailored email package banayein.")
    input_method = st.radio("Select Input Method:", ["✍️ Direct Manual Form (Recommended)", "🔗 URL Link Scraping", "📝 Raw Text Paste"])
    professors = []

    if input_method == "✍️ Direct Manual Form (Recommended)":
        col1, col2 = st.columns(2)
        with col1:
            m_name = st.text_input("Professor Name:", value="Yingyi Lin")
            m_email = st.text_input("Professor Email Address:", value="Yingyi.Lin@UTDallas.edu")
        with col2:
            m_focus = st.text_input("Research Focus / Expertise Area:", value="Demography, public health, and spatial population dynamics")
            
        m_lab = st.text_input("Lab or Research Group Name (Optional):", value="")
        if m_name.strip():
            professors.append({
                "name": clean_pdf_text(m_name),
                "email": clean_pdf_text(m_email),
                "focus": clean_pdf_text(m_focus),
                "lab": clean_pdf_text(m_lab)
            })

    elif input_method == "🔗 URL Link Scraping":
        url_input = st.text_input("Faculty Web Link:", placeholder="https://profiles.utdallas.edu/yingyi.lin")
        if url_input.strip():
            url = url_input.strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            res = scrape_url_smartly(url)
            if res:
                professors.append({
                    "name": res["name"],
                    "email": res["email"],
                    "focus": res["expertise"] if "expertise" in res else res["focus"],
                    "lab": ""
                })
                st.success(f"Successfully scraped: {res['name']} ({res['email']})")
            else:
                st.error("Could not scrape this URL. Please use Manual Form or Text Paste.")

    else:
        prof_input = st.text_area("Paste Professor Details (Name, Email, Focus):", placeholder="Yingyi Lin\nYingyi.Lin@UTDallas.edu\nDemography, public health, and spatial population dynamics", height=130)
        if prof_input.strip():
            p_name, p_email, p_focus = parse_profile_text(prof_input)
            professors.append({
                "name": p_name,
                "email": p_email,
                "focus": p_focus,
                "lab": ""
            })
            st.success("Extracted 1 profile successfully!")

    if st.button("📥 Generate & Download Excel File"):
        if not professors:
            st.error("No faculty data available.")
        else:
            excel_data = []
            for prof in professors:
                full_name = prof['name'].replace("Dr.", "").replace("Dr", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                focus_clean = prof['focus'].strip()
                lab_ref = f" in your {prof.get('lab', '').strip()} research group" if prof.get('lab', '').strip() else ""
                
                subject = f"Prospective PhD Inquiry: {focus_clean[:40]} — Faizan Ahmad"
                
                email_body = (
                    f"Dear Dr. {last_name},\n\n"
                    f"I have been following your scholarly work and publications focusing on {focus_clean}{lab_ref}. Your lab's contributions to spatial analytics provide an inspiring framework for advanced geographical research.\n\n"
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
                    "Email Body": email_body
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
                        subject = clean_pdf_text(str(row.get("Email Subject", "")))
                        
                        if ":" in subject and "—" in subject:
                            focus = subject.split(":")[1].split("—")[0].strip()
                        else:
                            focus = "Spatial Analysis and Environmental Modeling"
                            
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
                        pdf.multi_cell(0, 4, f"Research Focus: Integrating Spatial Analytics, Python Workflows, and {focus}", align="L")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "1. Academic Foundation & Technical Expertise", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My academic credentials include an M.Sc. in Remote Sensing & GIS and a B.Sc. in GeoInformatics, backed by 5.5+ years of practical GIS experience. My technical competencies span advanced Python, SQL, Google Earth Engine (GEE), and spatial statistical modeling. Demonstrating my academic research capability, I co-authored peer-reviewed research published in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal dynamics and spatial risk assessment.")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, f"2. Alignment with Dr. {prof_name.replace('Dr. ', '')}'s Research Lab", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"My doctoral research interests are directly inspired by the scholarly contributions and investigations led by Dr. {prof_name.replace('Dr. ', '')} in the domain of {focus}. The methodological frameworks developed through your research group offer an ideal platform for integrating big data spatial analytics with complex geographical systems. I am eager to contribute my technical background in automated geospatial processing to support and expand upon your ongoing objectives.")
                        pdf.ln(2)
                        
                        pdf.set_font("Helvetica", style="B", size=10)
                        pdf.cell(0, 5, "3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", size=9)
                        pdf.multi_cell(0, 3.8, f"To synthesize my technical skill set with your lab's mission, I propose focusing my dissertation on three core pillars: (1) integrating multi-decadal observation time-series with spatial metrics to evaluate longitudinal change; (2) developing scalable Python and GEE workflows tailored to {focus.lower()} for rapid spatial mapping; and (3) applying advanced spatial statistics to simulate predictive environmental and social risk surfaces.")
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
