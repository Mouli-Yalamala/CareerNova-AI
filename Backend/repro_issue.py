
import json
import re

def safe_parse_json(output_obj):
    """Extracts JSON from CrewOutput, dict, or raw strings with commentary."""
    if output_obj is None: return {}
    if isinstance(output_obj, (dict, list)): return output_obj
    
    raw_str = ""
    # CrewOutput has 'raw' or 'tasks_output'
    if hasattr(output_obj, 'json_dict') and output_obj.json_dict:
        return output_obj.json_dict
    if hasattr(output_obj, 'raw'):
        raw_str = str(output_obj.raw)  # Force string conversion
    elif isinstance(output_obj, str):
        raw_str = output_obj
    
    if not raw_str or raw_str.lower() == "none": return {}

    # 1. Clean up invalid escapes that LLMs often produce
    # Replace \' with ' because \' is not valid JSON
    raw_str = raw_str.replace("\\'", "'")

    # Attempt direct parse
    try: 
        print("Attempting direct parse...")
        return json.loads(raw_str)
    except Exception as e: 
        print(f"Direct parse failed: {e}")
        pass

    # Regex fallback for wrapped JSON
    try:
        print("Attempting regex fallback...")
        match = re.search(r'(\{.*\}|\[.*\])', raw_str, re.DOTALL)
        if match: 
            extracted = match.group(1)
            print(f"Extracted string (first 100 chars): {extracted[:100]}...")
            return json.loads(extracted)
        else:
            print("No regex match found.")
    except Exception as e: 
        print(f"Regex fallback failed: {e}")
        pass

    return {}

# The input string from the user's issue
raw_output = """```json
{"application_generator_response": {"application_timestamp": "2026-02-07T20:58:40.947019", "ats_score": 100,
"cover_letter": "Dear Hiring Manager,\\n\\nI am excited to apply for the AI Engineer position at Tata Consultancy Services. With 0 years of experience specializing in General Skill, Skill, Skill, I am particularly drawn to this role due to your focus on Python, TensorFlow. My strengths include , which directly align with your technical requirements. I am actively upskilling in Deep Learning through hands-on projects and I am eager to contribute my expertise to Tata Consultancy Services\\'s innovative projects.\\n\\nBest regards,\\nCandidate", "keywords_used": ["Python", "Natural Language Processing", "Deep Learning", "Ai Engineer", "Keras", "Tensorflow", "General Skill", "Machine Learning"], "linkedin_message": "Hi [Recruiter Name],\\n\\nSaw your AI Engineer opening at Tata Consultancy Services - strong General Skill, Skill background here. Would love to connect about the role!\\n\\nCandidate\\nGeneral Skill Engineer", "recommended_jobs": ["AI Engineer", "AI Engineer", "AI Engineer"], "recruiter_email": "Subject: AI Engineer Application - General Skill Expert | 0% Match\\n\\nHi [Recruiter Name],\\n\\nQuick intro - I\\'m a 0+ year General Skill specialist interested in the AI Engineer role at Tata Consultancy Services.\\n\\nKey highlights:\\n• Expert in General Skill, Skill, Skill\\n• 0% skills match with your requirements\\n• Strengths: N/A\\n\\nAI Engineer requirements I\\'m targeting:\\n✓ Python\\n✓ TensorFlow\\n\\nAvailable for a quick 15-min call this week. Resume attached.\\n\\nBest,\\nCandidate\\nGeneral Skill Engineer | +91-XXXXXXX | linkedin.com/in/candidate\\n\\n[Resume Attached]", "tailored_resume": "Candidate\\nAI Engineer | Python, TensorFlow, Keras, Natural Language Processing, Machine Learning, Deep Learning, General Skill, ai engineer\\n\\nPROFESSIONAL SUMMARY\\nN/A\\nExpert in Python, TensorFlow, Keras, Natural Language Processing, Machine Learning. Proven track record delivering AI Engineer solutions.\\n\\nPROFESSIONAL EXPERIENCE\\n\\nSKILLS\\nPython, TensorFlow, Keras, Natural Language Processing, Machine Learning, Deep Learning, General Skill, ai engineer\\n\\nEDUCATION"}}
```"""

print("-" * 20)
print("Testing parsing with fix...")
parsed = safe_parse_json(raw_output)
print("-" * 20)
print("Parsed Result keys:", parsed.keys())

if "application_generator_response" in parsed:
    inner = parsed["application_generator_response"]
    print("Inner keys:", inner.keys())
else:
    print("Failed to find 'application_generator_response' in parsed result.")
