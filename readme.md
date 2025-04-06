# Project: Drug-Drug Interaction Extraction from FDA Labels

## 🔎 Objective
Extract structured information about drug-drug interactions (DDIs) and contraindications from FDA drug labeling data using a combination of natural language processing (NLP) techniques.

---

## 🎓 Background
FDA drug labels are essential safety documents, but much of their content exists in unstructured text. Extracting DDIs and contraindications from these labels can:
- Enhance clinical decision support systems
- Power pharmacovigilance platforms
- Enable downstream analysis of drug safety

---

## 📊 Methodology

### 1. Data Ingestion
- Source: [`https://api.fda.gov/drug/label.json`](https://api.fda.gov/drug/label.json)
- Retrieved a subset of labels via API (10 per run for testing).

### 2. Preprocessing
- Normalized and cleaned sections like `drug_interactions`, `contraindications`
- Added bullet breaks and stripped excess whitespace

### 3. Extraction Techniques
#### ✅ Regex-Based Extraction
- Targets patterns like "Drug1 and Drug2 may cause EFFECT"
- Fast but fragile to sentence variability

#### ✅ Named Entity Recognition (NER)
- Tool: `spaCy` + `en_core_sci_sm`
- Extracts chemicals and drug mentions

#### ✅ Language Model (LLM) Extraction
- Model: `google/flan-t5-base` via LangChain
- Prompted to extract clean, plain-English interaction summaries
- Helps when regex/NER fall short

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

---

## 🔄 Future Work (Suggestions if Time/Resources Permitted)

### 1. **Fine-Tune an Extraction LLM**
Train a model (e.g., BioGPT, SciBERT) on annotated FDA labels for consistent DDI/contraindication tuples.

### 2. **RAG-Augmented Retrieval**
Use LangChain RAG pipeline to pre-index sections, then query and extract in context-aware fashion.

### 3. **Improve Regex + NLP Ensemble**
- Expand regex grammar for passive voice or bullet lists
- Use relation extraction (REBEL or SpaCy's `dep` parser) to improve context linkage

### 4. **Expand to SPL XML**
- Support Structured Product Labeling (SPL) XML documents
- Parse by LOINC section codes (e.g., 34067-9 for Indications)

### 5. **Interactive Visualizations**
- Drug interaction graphs
- Temporal timeline of label revisions (warnings added/removed)

---

## 🌐 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Pipeline
```bash
python main.py
```

### 3. Output
- Extracted records printed and optionally saved as `fda_ddi_contra_output.csv`

---

## 🔍 References
- [openFDA API Documentation](https://open.fda.gov/apis/drug/label/)
- [SPL Standards - FDA](https://www.fda.gov/industry/fda-data-standards-advisory-board/structured-product-labeling-resources)
- [SciSpaCy](https://allenai.github.io/scispacy/)
- [LangChain Documentation](https://docs.langchain.com/)

---