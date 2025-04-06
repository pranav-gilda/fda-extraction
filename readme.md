## 🧪 FDA Drug Label DDI & Contraindication Extractor

### 📌 Overview

This project is a data extraction pipeline that parses Drug-Drug Interactions (DDIs) and contraindications from FDA drug product labeling, using a combination of NLP techniques. The data is retrieved using the official FDA Drug Label API and analyzed for interaction patterns.

#### The pipeline integrates:
1. Regex-based extraction
2. Named Entity Recognition (NER) using SciSpaCy
3. LLM-based language understanding using LangChain + HuggingFace

### ⚙️ Features
- Extracts text from the drug_interactions and contraindications sections
- Identifies interacting drugs and possible effects using:
- Handcrafted regex rules
- NER-based chemical entity extraction
- Language model generation using flan-t5-base
- Structures results into a DataFrame for further analysis/export
- Evaluates and logs each method’s output for self-assessment

## 🧪 Methodology
### 1. Data Ingestion
- API used: https://api.fda.gov/drug/label.json
- Limited to 10 records for testing
- Extract fields like drug_interactions, contraindications, and openfda metadata

### 2. Preprocessing
- Cleaned whitespace and special formatting (e.g., bullets)
- Extracted structured drug name using openfda fields or fallback methods

### 3. Extraction Techniques
#### ✅ Regex-Based Extraction
Targets patterns like "Drug1 and Drug2 may cause EFFECT"
Fast but fragile to sentence variability

#### 🧠 Named Entity Recognition (NER)
Used 'en_core_sci_sm' model via SciSpaCy to identify chemical entities in the interaction text.

#### 🤖 LLM via LangChain (HuggingFace)
Used 'google/flan-t5-base' to summarize a cleaned drug label section into a one-line DDI/contraindication summary.
##### Prompt:
You are a pharmacology expert. Given the following section of an FDA drug label, extract a drug interaction or contraindication clearly.

### 4. Output Structuring
For each method, store fields:
- Drug name
- Interaction/contraindication
- Related drug (if available)
- Effect
- Raw text
- Extraction method (regex with NER/LLM)

---

## 📝 Sample Output
| drug     | type             |  effect_or_reason                                | source_method |
|----------|------------------|--------------------------------------------------|----------------|
| Naproxen | interaction      | Increased risk of serious bleeding               | regex         |
| Naproxen | contraindication | Not recommended with aspirin                     | NER           |
| Naproxen | interaction      | Use with SSRIs may increase bleeding risk        | LLM           |

---

## 👨‍💼 Evaluation Summary
| Aspect        | Regex with NER    | LLM                   |
|---------------|-------------------|-----------------------|
| Precision     | ✅ Medium         | ✅ High              |
| Recall        | ❌ Low            | ✅ High              |
| Structure     | ✅ Structured     | ❌ Needs formatting  |
| Generalization| ❌ Weak           | ✅ Strong            |

### Strengths:
- Uses multiple NLP techniques to increase robustness
- Easy to extend or swap models for better accuracy
- Lightweight and reproducible

### Limitations:
- Regex rules are brittle to phrasing changes
- LLM hallucinations possible (needs validation)
- OpenFDA label format is inconsistent across products


### 🔄 Next Steps (Suggestions if Time/Resources Permitted)
- Fine-tune LLM on DDI domain examples for better accuracy
- Add label section classifiers to handle broader label coverage
- Build an evaluation set to compare extraction precision/recall
- Include more structured product labeling (SPL) or DailyMed formats

---

## 🌐 How to Run

### 🔧 Install Dependencies Setup
```bash
pip install -r requirements.txt
```

### ▶️ Run Pipeline
```bash
python main.py
```

### 3. Output
- Extracted records printed and optionally saved as `fda_ddi_contra_output.csv` , other csv's attached as well from trial runs.

---

## 🔍 References
- [openFDA API Documentation](https://open.fda.gov/apis/drug/label/)
- [SPL Standards - FDA](https://www.fda.gov/industry/fda-data-standards-advisory-board/structured-product-labeling-resources)
- [SciSpaCy](https://allenai.github.io/scispacy/)
- [LangChain Documentation](https://docs.langchain.com/)

---
