import streamlit as st
from docx import Document
import io

st.title("🎓 Faizan's PhD Cold Email Generator")
st.write("Yahan professors ki details paste karein aur aik click mein Word file download karein!")

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
    value="Dr. Sophie Norris | Assistant Professor | sophienorris@uvic.ca | Quaternary geomorphology, ice sheet dynamics, glacial erosion, and spatial Earth observation"
)

if st.button("Generate & Download Word File"):
    doc = Document()
    doc.add_heading("UVic Professors Cold Emails", 0)
    
    lines = prof_input.split('\n')
    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        
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
    
    st.success("File tayyar hai!")
    st.download_button(
        label="📥 Download Word Document (.docx)",
        data=buffer,
        file_name="Tailored_Cold_Emails.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
