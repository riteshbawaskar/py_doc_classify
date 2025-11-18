# Entity Extractor Agent - LangGraph Workflow

## Overview
Added an `entity_extractor` agent to the LangGraph workflow that extracts various entities from documents with confidence scores.

## Changes Made

### 1. **Updated DocumentState TypedDict**
Added `entities` field to store extracted entities:
```python
class DocumentState(TypedDict):
    file_path: str
    document_text: str
    document_type: str
    confidence: str
    entities: dict  # Extracted entities with confidence scores
```

### 2. **New extract_entities() Function**
- Extracts the following entities from documents:
  - **AADHAAR_NUMBER** - 12-digit Indian ID
  - **PAN_NUMBER** - 10-character tax ID
  - **PASSPORT_NUMBER** - Passport identifier
  - **PHONE_NUMBER** - Contact number
  - **EMAIL_ADDRESS** - Email
  - **FULL_NAME** - Person's name
  - **DATE_OF_BIRTH** - Birth date
  - **ADDRESS** - Full address
  - **GENDER** - Gender information
  - **FATHER_NAME** - Father's name
  - **SPOUSE_NAME** - Spouse's name

- Returns extracted entities with confidence scores (0.0 to 1.0)
- Validates and normalizes confidence scores
- Uses Gemini AI for accurate entity extraction

### 3. **Updated LangGraph Workflow**
Modified the workflow to include the new node:

```
extract_text 
    ↓
classify_document 
    ↓
extract_entities (NEW)
    ↓
END
```

### 4. **Enhanced Output Display**
Both `classifier.py` and `run.py` now display extracted entities with confidence percentages.

## Example Output

```
============================================================
CLASSIFICATION RESULT
============================================================
Document Type: AADHAAR
Confidence: HIGH

Text Preview: Unique Identification Authority of India AADHAAR...

============================================================
EXTRACTED ENTITIES
============================================================
FULL_NAME:
  Value: Rajesh Kumar
  Confidence: 0.95 (95%)
AADHAAR_NUMBER:
  Value: 123456789012
  Confidence: 0.98 (98%)
ADDRESS:
  Value: 123 Main Street, New Delhi, India
  Confidence: 0.92 (92%)
DATE_OF_BIRTH:
  Value: 15-01-1990
  Confidence: 0.89 (89%)
GENDER:
  Value: Male
  Confidence: 0.96 (96%)
FATHER_NAME:
  Value: Suresh Kumar
  Confidence: 0.88 (88%)
============================================================
```

## Usage

### Command Line
```bash
python classifier.py path/to/document.pdf
```

### Batch Processing
```bash
python run.py
```

## Entity Extraction Features

1. **Selective Extraction**: Only extracts entities that are found in the document
2. **Confidence Scoring**: Each extracted entity includes a confidence score (0.0-1.0)
3. **Validation**: Confidence scores are automatically validated and clamped
4. **Error Handling**: Malformed responses are gracefully skipped
5. **AI-Powered**: Uses Gemini 2.5 Flash for accurate and context-aware extraction

## Integration with Existing Workflow

The entity extractor agent:
- ✅ Runs after document classification
- ✅ Uses extracted document text from the previous stage
- ✅ Maintains state across the workflow
- ✅ Provides structured output for downstream processing

## Customization

To add or modify entities, edit the `extract_entities()` function:

```python
Entities to extract:
- YOUR_CUSTOM_ENTITY (description)
```

## Notes

- Entity extraction works best when the document text is clearly extracted
- Confidence scores reflect the AI model's certainty about the extraction
- The system handles multiple document formats (PDF, images, Word docs)
