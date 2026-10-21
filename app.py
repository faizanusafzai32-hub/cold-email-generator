import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import re

st.title("🎓 Faizan's PhD Cold Email & Research Statement Generator")

# Faizan Ahmad's Master Profile Source of Truth
FAIZAN_CV = {
    "name": "Faizan Ahmad",
    "phone": "+92 312 9380985",
    "email": "faizan.usafzai32@gmail.com",
    "linkedin": "www.linkedin.com/in/faizan-ahmad-98990b183",
    "degree": "M.Sc. Remote Sensing & GIS (IST, Islamabad) & B.Sc. Geo-Informatics",
    "exp": "5.5+ years of professional and academic experience in geospatial data analytics, remote sensing, and environmental risk assessment",
    "skills": "advanced Python, SQL, Google Earth Engine (GEE), ArcGIS Pro, QGIS, and spatial statistical modeling (MaxEnt, GLM)",
    "pub": "co-authored peer-reviewed research in the Journal for Nature Conservation (Elsevier) focusing on spatiotemporal LULC dynamics and habitat suitability modeling",
    "thesis": "M.Sc. thesis on assessing the impact of LULC changes on flood risk, alongside extensive project work in hydrological modeling, soil erosion (RUSLE), and spatial risk analysis"
}

tab1, tab2 = st.tabs(["📧 1. Multi-Professor Structured Form & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

def clean_pdf_text(text):
    """
    Robust Unicode Sanitizer to prevent FPDF Helvetica encoding errors.
    Replaces em-dashes, en-dashes, smart quotes, and bullet points with standard ASCII equivalents.
    """
    if not isinstance(text, str):
        return ""
    
    # Replace unicode dashes, quotes, bullets, etc.
    cleaned = (text.replace('—', '-')
                   .replace('–', '-')
                   .replace('“', '"')
                   .replace('”', '"')
                   .replace('‘', "'")
                   .replace('’', "'")
                   .replace('•', '-')
                   .replace('\u2014', '-')
                   .replace('\u2013', '-'))
    
    # Encode to latin-1 safely, replacing unprintable characters
    return cleaned.encode('latin-1', 'replace').decode('latin-1')

def precise_keyword_focus(raw_text):
    if not isinstance(raw_text, str) or not raw_text.strip():
        return "Spatial Analysis and Environmental Modeling"
    
    text = raw_text.lower()
    
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
        return "Political Ecology and Sustainability"
    elif "gis education" in text or "geography education" in text:
        return "GIS Education and Spatial Methods"
    elif "cartography" in text or "geovisualization" in text:
        return "Cartography and Geovisualization"
    
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text)
    words = [w for w in cleaned.split() if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'our', 'are', 'use', 'space']]
    
    if words:
        return " ".join(words[:4]).title()
    
    return "Spatial Analysis and Environmental Modeling"

def get_tailored_statement_content(prof_name, focus_domain):
    domain = focus_domain.lower()
    clean_prof = prof_name.replace("Dr.", "").replace("Dr", "").strip()

    if "cartography" in domain or "geovisualization" in domain:
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

    elif "gis education" in domain or "spatial methods" in domain:
        sec2 = (
            f"I am deeply motivated by Dr. {clean_prof}'s focus on {focus_domain.lower()} and methodological spatial development. "
            f"Having automated complex geospatial workflows across 200+ data sources and developed customized spatial analytical pipelines in Python/SQL, "
            f"I am excited to contribute to reproducible spatial methodologies and open-source geospatial framework development within your research group."
        )
        sec3 = (
            f"Synthesizing my technical skills with your research direction in {focus_domain.lower()}, I propose focusing on: "
            f"(1) constructing open-source, automated Python and GEE modules for complex spatial analytical tasks; "
            f"(2) evaluating reproducible geospatial workflows to enhance data QA/QC and analytical accuracy in big spatial data; and "
            f"(3) developing spatial modeling frameworks that bridge advanced remote sensing techniques with accessible GIS methods."
        )
        sec4 = (
            f"With 5.5+ years of practical GIS experience and a passion for methodological rigour, I am eager to make a strong contribution "
            f"to Dr. {clean_prof}'s ongoing work in spatial methods and reproducible GIS science."
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
            f"(2) developing scalable Python and GEE
