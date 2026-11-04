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
    "degree": "M.Sc. in Remote Sensing & GIS",
    "exp": "Sr. GIS Analyst at Zoneomics (US-based spatial intelligence company) with over 2 years of direct experience in processing US-scale big spatial databases, alongside 5.5+ years of overall geospatial research and industry experience",
    "skills": "Python, SQL, and Google Earth Engine (GEE)",
    "pub": "peer-reviewed publication in Elsevier's Journal for Nature Conservation",
    "thesis": "M.Sc. thesis on assessing the impact of LULC changes on flood risk"
}

tab1, tab2 = st.tabs(["⚡ 1. One-Click Bulk Data Parser & Excel", "📄 2. Generate Research Statement PDFs (ZIP)"])

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

def generate_dynamic_email_paragraph1(expertise, pub_ref):
    """
    Short, crisp, and direct opening without the generic 'I am writing to express...' sentence.
    """
    has_exp = bool(expertise and len(expertise.strip()) > 2)
    has_pub = bool(pub_ref and len(pub_ref.strip()) > 3)
    
    exp_text = expertise.strip() if has_exp else ""
    pub_text = pub_ref.strip() if has_pub else ""
    
    if has_exp and has_pub:
        return (
            f"While reviewing your recent work in {exp_text} - "
            f"particularly your study on \"{pub_text}\" - "
            f"I found it particularly insightful, especially how it addresses spatial patterns and environmental risks. "
            f"I have been exploring similar spatial modeling questions in my own research."
        )
    elif has_exp:
        return (
            f"While reviewing your recent work in {exp_text}, "
            f"I found your research focus particularly insightful, especially how it addresses spatial patterns and environmental risks. "
            f"I have been exploring similar spatial modeling questions in my own research."
        )
    elif has_pub:
        return (
            f"While reviewing your recent work in spatial data science - "
            f"particularly your study on \"{pub_text}\" - "
            f"I found it particularly insightful, especially how it addresses spatial patterns and environmental risks. "
            f"I have been exploring similar spatial modeling questions in my own research."
        )
    else:
        return (
            f"While reviewing your recent work in spatial data science and spatial analytics, "
            f"I found your lab's research focus particularly insightful, especially how it addresses spatial patterns and environmental risks. "
            f"I have been exploring similar spatial modeling questions in my own research."
        )

def parse_raw_professor_blocks(raw_text):
    professors = []
    raw_blocks = re.split(r'\n\s*\n+(?=(?:Name|Professor Name|Prof\.))\s*', raw_text.strip())
    
    if len(raw_blocks) <= 1:
        raw_blocks = raw_text.strip().split('\n\n')

    for block in raw_blocks:
        if not block.strip():
            continue
            
        prof = {"name": "", "email": "", "expertise": "", "pub_ref": "", "bio": ""}
        lines = block.split('\n')
        current_key = None
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            if re.match(r'^(?:Name|Faculty Name|Professor Name)\s*:', line_str, re.IGNORECASE):
                current_key = 'name'
                prof['name'] = re.sub(r'^(?:Name|Faculty Name|Professor Name)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Email Address|Email)\s*:', line_str, re.IGNORECASE):
                current_key = 'email'
                prof['email'] = re.sub(r'^(?:Email Address|Email)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Research Interests areas or expertise|Research Interests|Expertise|Research Area)\s*:', line_str, re.IGNORECASE):
                current_key = 'expertise'
                prof['expertise'] = re.sub(r'^(?:Research Interests areas or expertise|Research Interests|Expertise|Research Area)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Latest Published Paper 1|Latest Published Paper|Key Publication|Publication|Paper|Ongoing Project|Project)\s*:', line_str, re.IGNORECASE):
                current_key = 'pub_ref'
                prof['pub_ref'] = re.sub(r'^(?:Latest Published Paper 1|Latest Published Paper|Key Publication|Publication|Paper|Ongoing Project|Project)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
            elif re.match(r'^(?:Bio|About Me|Biography|Notes)\s*:', line_str, re.IGNORECASE):
                current_key = 'bio'
                prof['bio'] = re.sub(r'^(?:Bio|About Me|Biography|Notes)\s*:', '', line_str, flags=re.IGNORECASE).strip()
            else:
                if current_key and current_key in prof:
                    if prof[current_key]:
                        prof[current_key] += " " + line_str
                    else:
                        prof[current_key] = line_str
                        
        if not prof['email']:
            em_search = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', block)
            if em_search:
                prof['email'] = em_search.group(0)
                
        if not prof['name']:
            lines_clean = [l.strip() for l in block.split('\n') if l.strip()]
            if lines_clean and "@" not in lines_clean[0] and ":" not in lines_clean[0]:
                prof['name'] = lines_clean[0]

        if prof['name'] or prof['email']:
            professors.append(prof)
            
    return professors

def get_tailored_statement_content(prof_name, focus_domain):
    clean_prof = prof_name.replace("Dr.", "").replace("Dr", "").replace("Prof.", "").replace("Prof", "").strip()
    domain = focus_domain if focus_domain else "Remote Sensing & Spatial Analytics"

    sec2 = (
        f"My doctoral aspirations strongly align with Dr. {clean_prof}'s research focus in {domain}. "
        f"Having conducted my M.Sc. thesis on spatiotemporal environmental modeling, combined with 5.5+ years of quantitative geospatial Python and GEE workflows, "
        f"I am deeply motivated to apply advanced remote sensing and spatial analytics to bridge research gaps in your lab's domain."
    )
    sec3 = (
        f"To synthesize my technical skills with your lab's mission in {domain}, I propose focusing my dissertation on three core pillars: "
        f"(1) developing scalable Python and Google Earth Engine (GEE) automation pipelines for high-resolution satellite time-series analysis; "
        f"(2) applying spatial statistical modeling and machine learning frameworks to evaluate environmental and spatial risk dynamics; and "
        f"(3) integrating multi-sensor spatial datasets to generate predictive simulation surfaces."
    )
    sec4 = (
        f"By combining my solid foundation in spatial data science, workflow automation, and demonstrated Elsevier publishing experience, "
        f"I am fully prepared to make immediate, high-impact contributions to Dr. {clean_prof}'s research program."
    )

    return clean_pdf_text(sec2), clean_pdf_text(sec3), clean_pdf_text(sec4)

# ==================== TAB 1 ====================
with tab1:
    st.subheader("⚡ One-Click Bulk Data Parser (Up to 20+ Professors)")
    st.write("Aap yahan aik sath 10 se 20 professors ka data paste kar sakte hain. Startup box bilkul khali hai:")

    pasted_data = st.text_area("📋 Paste Multiple Professors Raw Data Here (Up to 20+):", height=280, value="")

    if st.button("🚀 Process & Generate Excel Package"):
        parsed_profs = parse_raw_professor_blocks(pasted_data)
        
        if not parsed_profs:
            st.error("Data parse nahi ho saka. Baraye meherbani 'Name:' aur 'Email Address:' labels check karein.")
        else:
            st.success(f"Successfully extracted data for {len(parsed_profs)} professor(s)!")
            
            excel_rows = []
            for prof in parsed_profs:
                full_name = prof['name'].replace("Dr.", "").replace("Dr", "").replace("Prof.", "").replace("Prof", "").strip()
                last_name = full_name.split()[-1] if full_name else "Professor"
                
                # Subject strictly uses ONLY research focus, completely clean of papers/projects
                raw_focus = prof['expertise'] if prof['expertise'] else "Remote Sensing & Spatial Analytics"
                clean_focus = re.split(r'Latest Published|Ongoing Project|Paper:', raw_focus, flags=re.IGNORECASE)[0].strip()
                
                subject = f"Prospective Ph.D. Applicant — {clean_focus} - Faizan Ahmad"
                
                custom_para1 = generate_dynamic_email_paragraph1(prof['expertise'], prof['pub_ref'])
                
                email_body = (
                    f
