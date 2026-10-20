import streamlit as st
from docx import Document
import io
import zipfile
from fpdf import FPDF

st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")
st.write("Yahan department ka data paste karein. App sirf Professors, Associate/Assistant Professors aur Chairs/Heads ko target karegi!")

FAIZAN_CV_DETAILS = {
    "name": "Faizan Ahmad",
    "phone": "+92 349 9343568",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "MS in Remote Sensing & GIS and Bachelor of Science in GeoInformatics",
    "exp": "5.5+ years of experience in spatial data analytics, Python programming, and Google Earth Engine (GEE)",
    "pub": "co-authored a 2026 peer-reviewed paper in the Journal for Nature Conservation (Elsevier) focused on spatial statistical modeling and ecological dynamics"
}

default_text = """David Atkinson
Status: On leave until January 2027
Professor
Geography
Office: DTB B120
datkinso@uvic.ca
250-721-7332
Area(s) of expertise: Climate, weather and human and natural systems, data analysis, modelling, the Arctic

Chris Bone
Associate professor, Department chair
Geography
Office: DTB B203c
chrisbone@uvic.ca
250-472-5620
Area(s) of expertise: Geospatial technologies, spatial simulation modelling, human-environment interactions"""

prof_input = st.text_area(
    "Professors Data (Multi-line blocks):",
    value=default_text,
    height=300
)

# Allowed Target Titles Filter
ALLOWED_TITLES = ["professor", "assistant professor", "associate professor", "chair", "head"]

professors = []
blocks = [b.strip() for b in prof_input.split('\n\n') if b.strip()]

for block in blocks:
    lines = [l.strip() for l in block.split('\n') if l.strip()]
    if not lines:
        continue
    
    name = lines[0].replace("- ", "").strip()
    designation = ""
    email = "prof@uni.ca"
    expertise = "Geospatial modeling and remote sensing"
    
    is_target_role = False
    
    for line in lines[1:]:
        clean_line = line.replace("- ", "").strip()
        clean_lower = clean_line.lower()
        
        # Check if designation matches target roles
        if any(title in clean_lower for title in ALLOWED_TITLES):
            designation = clean_line
            is_target_role = True
        elif "@" in clean_line:
            email = clean_line
        elif "expertise:" in clean_lower:
            expertise = clean_line.split(":", 1)[1].strip()
        elif any(k in clean_lower for k in ["climate", "modelling", "modeling", "remote", "gis", "spatial", "human", "technologies", "analysis"]):
            if len(clean_line) > 15 and "office" not in clean_lower and "leave" not in clean_lower:
                expertise = clean_line
                
    # Sirf unhi ko add karega jo target roles mein match honge
    if is_target_role:
        professors.append({
            "name": name,
            "designation": designation if designation else "Professor",
            "email": email,
            "expertise": expertise
        })

col1, col2 = st.columns(2)

# Button 1: Emails Word File
with col1:
    if st.button("📥 Download Emails Word File"):
        if not professors:
            st.error("Koi bhi matching Professor/Chair/Head nahi mila. Barah-e-karam theek data paste karein.")
        else:
            doc = Document()
            doc.add_heading("Targeted Professors Cold Emails", 0)
            
            for idx, prof in enumerate(professors, 1):
                full_name = prof['name'].replace("Dr. ", "").replace("Dr ", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                
                topic = prof['expertise'].split(',')[0].title()
                subject = f"Prospective PhD Student: {topic} — Faizan Ahmad"
                
                doc.add_heading(f"{idx}. {prof['name']} ({prof['designation']})", level=2)
                doc.add_paragraph(f"Email: {prof['email']}")
                doc.add_paragraph(f"Email Subject: {subject}")
                
                p = doc.add_paragraph("Email Body:\n")
                run_salutation = p.add_run(f"Dear Dr. {last_name},\n\n")
                run_salutation.bold = True
                
                p.add_run("I hope you are doing well.\n\n")
                p.add_run(f"My name is {FAIZAN_CV_DETAILS['name']}, and I hold an {FAIZAN_CV_DETAILS['degree']} with {FAIZAN_CV_DETAILS['exp']}. I also {FAIZAN_CV_DETAILS['pub']}.\n\n")
                
                p.add_run("I am very interested in your lab’s work on ")
                run_exp = p.add_run(f"{prof['expertise']}")
                run_exp.bold = True
                p.add_run(". My background in processing big spatiotemporal datasets, spatial statistical modeling, Python workflows, and Google Earth Engine (GEE) aligns strongly with your current research focus.\n\n")
                
                p.add_run("Are you currently accepting funded PhD students for upcoming terms? I have attached my CV and a 1-page Statement of Research Interests for your review.\n\n")
                
                p.add_run("With Kind Regards,\n")
                p.add_run("Faizan Ahmad\n")
                p.add_run("GIS Specialist\n")
                p.add_run(f"WhatsApp/Mob: {FAIZAN_CV_DETAILS['phone']}\n")
                p.add_run(f"{FAIZAN_CV_DETAILS['linkedin']}\n")
                doc.add_paragraph("-" * 50)

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.success(f"Kul {len(professors)} targeted professors ki emails tayyar hain!")
            st.download_button(
                label="Download .docx File",
                data=buffer,
                file_name="Tailored_Cold_Emails.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# Button 2: Research Interest PDFs (ZIP)
with col2:
    if st.button("📥 Download Research Interests (ZIP)"):
        if not professors:
            st.error("Koi bhi matching Professor/Chair/Head nahi mila.")
        else:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for idx, prof in enumerate(professors, 1):
                    clean_prof_name = prof['name'].replace("Dr. ", "").replace("Dr ", "").replace(".", "").strip().replace(" ", "_")
                    file_name = f"Faizan-PHD-Statement of research-{clean_prof_name}.pdf"
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Header Title
                    pdf.set_font("Helvetica", style="B", size=13)
                    pdf.cell(0, 7, text="STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                    
                    # Contact Info
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, text="Faizan Ahmad", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.set_font("Helvetica", size=9)
                    pdf.cell(0, 4, text="GIS Specialist", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.cell(0, 4, text=f"Mob: {FAIZAN_CV_DETAILS['phone']} | Email: {FAIZAN_CV_DETAILS['email']}", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.cell(0, 4, text=f"{FAIZAN_CV_DETAILS['linkedin']}", new_x="LMARGIN", new_y="NEXT", align="C")
                    pdf.ln(4)
                    
                    # Research Focus Line
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, text=f"Research Focus: Spatiotemporal Modeling, Remote Sensing, and {prof['expertise'].split(',')[0]}", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(3)
                    
                    # Section 1
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, text="1. Academic & Professional Background", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, text="I hold a Master of Science in Remote Sensing & GIS and a Bachelor of Science in Geoinformatics, complemented by over 5.5 years of professional experience as a GIS Specialist. My core expertise lies in spatiotemporal data analysis, automated geospatial workflows in Python, and cloud-based Earth Observation analytics using Google Earth Engine (GEE). My research capability is demonstrated by a peer-reviewed publication in the Journal for Nature Conservation (Elsevier, 2026), where I utilized spatial statistical modeling to evaluate land dynamics and ecological responses.")
                    pdf.ln(3)
                    
                    # Section 2
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, text="2. My Research Focus", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, text=f"My research focus centers on utilizing satellite remote sensing, spatial statistics, and machine learning to model environmental risks and ecosystem dynamics. I am particularly drawn to the research conducted in {prof['name']}'s lab focusing on {prof['expertise']}. Your pioneering work directly aligns with my analytical background and research ambitions. I am keen to leverage cloud-based Earth Observation and automated geospatial analytics to advance spatial risk mapping and predictive modeling.")
                    pdf.ln(3)
                    
                    # Section 3
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, text="3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, text=f"During my doctoral studies, I aim to contribute to your lab's directions by focusing on:\n1. Spatiotemporal Risk Modeling: Integrating multi-decadal satellite observation time-series with spatial datasets.\n2. Automated Landscape Analytics: Developing Python and GEE-driven workflows for automated mapping and spatial analysis.\n3. Machine Learning & Predictive Risk Assessment: Applying advanced spatial statistics and machine learning algorithms to model environmental interactions.")
                    pdf.ln(3)
                    
                    # Section 4
                    pdf.set_font("Helvetica", style="B", size=10)
                    pdf.cell(0, 5, text="4. Conclusion", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", size=9)
                    pdf.multi_cell(0, 4, text=f"By bringing my 5.5+ years of practical GIS expertise and spatial modeling background to {prof['name']}'s lab, I aim to advance data-driven spatial frameworks that support advanced environmental analytics, risk mitigation, and sustainable landscape management.")
                    
                    pdf_bytes = bytes(pdf.output())
                    zip_file.writestr(file_name, pdf_bytes)
                    
            zip_buffer.seek(0)
            st.success(f"Kul {len(professors)} targeted professors ki Research Statements ka ZIP folder tayyar hai!")
            st.download_button(
                label="Download ZIP File",
                data=zip_buffer,
                file_name="Research_Statements_ZIP.zip",
                mime="application/zip"
            )
