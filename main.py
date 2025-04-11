import requests
import json
import scispacy
import spacy
import re
import pandas as pd
import torch
from huggingface_hub import InferenceClient
from spacy.lang.en.stop_words import STOP_WORDS
# from nltk.stem import WordNetLemmatizer

# --- CONFIG ---
API_URL = "https://api.fda.gov/drug/label.json"
PARAMS = {'limit': 50}  # Limit for testing

# --- HUGGINGFACE INFERENCE CLIENT ---
client = InferenceClient("google/flan-t5-base")  # Stable public model

# --- TEXT CLEANING ---
# lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('•', '\n•')
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    filtered = [word for word in words if word not in STOP_WORDS]
    return ' '.join(filtered)

# --- FDA API ---
def fetch_drug_labels(api_url, params):
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# --- NLP ---
nlp = spacy.load("en_core_sci_sm")

def extract_drug_entities(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "CHEMICAL"]

interaction_phrases = [
    r'(?P<drug1>[A-Z][a-zA-Z]{2,})\b.*?\b(?:and|with)\b.*?\b(?P<drug2>[A-Z][a-zA-Z]{2,})\b.*?\b(?:increase|reduce|inhibit|enhance)\b.*?(?P<effect>[^\.]+)\.',
    r'concomitant use of (?P<drug1>[A-Z][a-zA-Z\s]{2,}?) and (?P<drug2>[A-Z][a-zA-Z\s]{2,}?).*?\b(?:may|can|will)\b (?P<effect>[^\.]+)\.',
]

def extract_interactions(text):
    results = []
    for pattern in interaction_phrases:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            results.append(match.groupdict())
    return results

# --- DRUG NAME RESOLUTION ---
def resolve_drug_name(entry):
    openfda = entry.get('openfda', {})
    fallback_name = entry.get('id') or entry.get('set_id') or "Unknown Drug"
    for field in ['brand_name', 'generic_name', 'substance_name']:
        names = openfda.get(field)
        if names:
            return names[0] if isinstance(names, list) else names
    for section in ['description', 'indications_and_usage']:
        texts = entry.get(section, [])
        if texts:
            match = re.search(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b', texts[0])
            if match and match.group(1).lower() not in {"uses", "directions", "indications", "purpose", "the"}:
                return match.group(1)
    return fallback_name

# --- RECORD STRUCTURE ---
def build_extraction_record(drug, type, effect, method, raw_text):
    return {
        "drug": drug,
        "type": type,
        "effect_or_reason": effect,
        "source_method": method,
        "raw_text": raw_text
    }

# --- HUGGINGFACE MODEL WRAPPER ---
def call_hf_model(prompt):
    try:
        response = client.text_generation(prompt, max_new_tokens=200)
        print("\n🧾 HF Output:", response)
        return response.strip()
    except Exception as e:
        print("HF inference error:", e)
        return ""

# --- EXTRACTION WRAPPER ---
def aggregate_all_extractions(result):
    drug_name = resolve_drug_name(result)
    records = []
    if drug_name == "Unknown Drug":
        return records

    for section_type in ["drug_interactions", "contraindications"]:
        for text in result.get(section_type, []):
            cleaned = clean_text(text)
            section_label = "interaction" if section_type == "drug_interactions" else "contraindication"

            # Regex
            if section_type == "drug_interactions":
                regex_matches = extract_interactions(cleaned)
                for match in regex_matches:
                    records.append(build_extraction_record(drug_name, section_label, match['effect'], "regex", cleaned))

            # NER
            entities = extract_drug_entities(cleaned)
            for ent in entities:
                records.append(build_extraction_record(drug_name, section_label, ent, "NER", cleaned))

            # HuggingFace LLM - structured plain text format
            prompt = f"""
            You are a biomedical extraction expert.

            Given this text, extract structured data in plain text format. Return:
            Drugs: DrugA, DrugB
            Type: DDI or contraindication
            Reason: Short sentence explaining the interaction or contraindication.

            Text: {text}
            """
            hf_output = call_hf_model(prompt)
            try:
                drugs_match = re.search(r"Drugs:\s*(.+)", hf_output)
                type_match = re.search(r"Type:\s*(DDI|contraindication)", hf_output, re.IGNORECASE)
                reason_match = re.search(r"Reason:\s*(.+)", hf_output)
                if drugs_match and type_match and reason_match:
                    records.append(build_extraction_record(
                        drug_name,
                        type_match.group(1).lower(),
                        reason_match.group(1),
                        "LLM",
                        cleaned
                    ))
                else:
                    raise ValueError("Missing one or more fields")
            except Exception as e:
                print("⚠️ Could not parse structured output from LLM:", hf_output)
                records.append(build_extraction_record(drug_name, section_label, hf_output, "LLM", cleaned))

    return records

# --- MAIN ---
def main():
    data = fetch_drug_labels(API_URL, PARAMS)
    if not data:
        return

    all_records = []
    for entry in data.get("results", []):
        extracted = aggregate_all_extractions(entry)
        all_records.extend(extracted)

    df = pd.DataFrame(all_records)
    print("\n Final Extracted Data Preview:")
    print(df.head())
    df.to_csv("fda_ddi_contra_output.csv", index=False)
    print("\n Saved output to fda_ddi_contra_output.csv")

# --- RUN ---
if __name__ == "__main__":
    main()
