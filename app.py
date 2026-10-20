import streamlit as st
from docx import Document
import io
import zipfile
from fpdf import FPDF

st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")
st.write("Yahan professors ki details paste karein aur emails ya research statements alag alag download karein!")

FAIZAN_CV_DETAILS = {
    "name": "Faizan Ahmad",
    "phone": "+92 349 9343568",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "MS in Remote Sensing & GIS and Bachelor of Science in GeoInformatics",
    "exp": "5.5+ years of experience in spatial data analytics, Python programming, and Google Earth Engine (GEE)",
    "pub": "co-authored a 2026 peer-reviewed paper in the Journal for Nature Conservation (Elsevier) focused on spatial statistical modeling and ecological dynamics"
}

prof_input = st.text_area(
    "Professors ki details yahan paste karein (Name | Designation | Email | Expertise):",
    value="Dr. Jen Beverly | Professor | jbeverly@ualberta.ca | Wildfire risk assessment, fire-climate interactions, and landscape values-at-risk mapping"
)

lines = [l.strip() for l in prof_input.split('\n') if l.strip()]

col1, col2 = st.columns(2)

# Button 1: Emails Word File
with col1:
    if st.button("📥 Download Emails Word File"):
        doc = Document()
        doc.add_heading("Professors Cold Emails", 0)
        
        for idx, line in enumerate(lines, 1):
            parts = [p.strip() for p in line.split('|')]
            name = parts[0] if len(parts) > 0 else "Dr. Professor"
            designation = parts[1] if len(parts) > 1 else "Professor"
            email = parts[2] if len(parts) > 2 else "prof@uni.ca"
            expertise = parts[3] if len(parts) > 3 else "Geospatial modeling and remote sensing"
            
            full_name = name.replace("Dr. ", "").strip()
            last_name = full_name.split()[-1]
            
            topic = expertise.split(',')[0].title()
            subject = f"Prospective PhD Student: {topic} — Faizan Ahmad"
            
            doc.add_heading(f"{idx}. {name} ({designation})", level=2)
            doc.add_paragraph(f"Email: {email}")
            doc.add_paragraph(f"Email Subject: {subject}")
            
            p = doc.add_paragraph("Email Body:\n")
            run_salutation = p.add_run(f"Dear Dr. {last_name},\n\n")
            run_salutation.bold = True
            
            p.add_run("I hope you are doing well.\n\n")
            p.add_run(f"My name is {FAIZAN_CV_DETAILS['name']}, and I hold an {FAIZAN_CV_DETAILS['degree']} with {FAIZAN_CV_DETAILS['exp']}. I also {FAIZAN_CV_DETAILS['pub']}.\n\n")
            
            p.add_run("I am very interested in your lab’s work on ")
            run_exp = p.add_run(f"{expertise}")
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
        
        st.success("Emails Word file tayyar hai!")
        st.download_button(
            label="Download .docx File",
            data=buffer,
            file_name="Tailored_Cold_Emails.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# Button 2: Research Interest PDFs (ZIP)
with col2:
    if st.button("📥 Download Research Interests (ZIP)"):
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, line in enumerate(lines, 1):
                parts = [p.strip() for p in line.split('|')]
                name = parts[0] if len(parts) > 0 else "Professor"
                expertise = parts[3] if len(parts) > 3 else "Spatiotemporal Modeling and Remote Sensing"
                
                clean_name = name.replace("Dr. ", "").replace(" ", "_")
                
                # Generate PDF for each professor
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=11)
                
                # Header
                pdf.set_font("Helvetica", style="B", size=14)
                pdf.cell(0, 8, text="STATEMENT OF RESEARCH INTERESTS", new_x="LMARGIN", new_y="NEXT", align="C")
                pdf.set_font("Helvetica", size=10)
                pdf.cell(0, 5, text=f"Faizan Ahmad | Mob: {FAIZAN_CV_DETAILS['phone']}", new_x="LMARGIN", new_y="NEXT", align="C")
                pdf.cell(0, 5, text=f"{FAIZAN_CV_DETAILS['linkedin']}", new_x="LMARGIN", new_y="NEXT", align="C")
                pdf.ln(8)
                
                # Section Title
                pdf.set_font("Helvetica", style="B", size=11)
                pdf.cell(0, 6, text=f"Target Lab / Research Focus: {expertise}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(4)
                
                # Section 1
                pdf.set_font("Helvetica", style="B", size=11)
                pdf.cell(0, 6, text="1. Academic & Professional Background", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(0, 5, text="I hold a Master of Science in Remote Sensing & GIS and a Bachelor of Science in Geoinformatics, complemented by over 5.5 years of professional experience as a GIS Specialist. My core expertise lies in spatiotemporal data analysis, automated geospatial workflows in Python, and cloud-based Earth Observation analytics using Google Earth Engine (GEE). My research capability is demonstrated by a peer-reviewed publication in the Journal for Nature Conservation (Elsevier, 2026).")
                pdf.ln(4)
                
                # Section 2
                pdf.set_font("Helvetica", style="B", size=11)
                pdf.cell(0, 6, text="2. My Research Focus & Alignment", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(0, 5, text=f"My research centers on utilizing satellite remote sensing, spatial statistics, and machine learning to model environmental risks and ecosystem dynamics. I am particularly drawn to {name}'s lab and work focusing on {expertise}. I am keen to leverage cloud-based Earth Observation and automated geospatial analytics to advance risk mapping and spatial modeling.")
                pdf.ln(4)
                
                # Section 3
                pdf.set_font("Helvetica", style="B", size=11)
                pdf.cell(0, 6, text="3. Proposed PhD Research Directions", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=10)
                pdf.multi_cell(0, 5, text="1. Spatiotemporal Risk Modeling: Integrating multi-decadal satellite observation time-series with spatial datasets.\n2. Automated Landscape Analytics: Developing Python and GEE-driven workflows for automated mapping across large spatial scales.\n3. Machine Learning & Predictive Analytics: Applying advanced spatial statistics and machine learning algorithms.")
                
                # Output PDF byte array directly
                pdf_bytes = bytes(pdf.output())
                zip_file.writestr(f"{idx}_{clean_name}_Research_Statement.pdf", pdf_bytes)
                
        zip_buffer.seek(0)
        st.success("Research statements ka ZIP folder tayyar hai!")
        st.download_button(
            label="Download ZIP File",
            data=zip_buffer,
            file_name="Research_Statements_ZIP.zip",
            mime="application/zip"
        )
