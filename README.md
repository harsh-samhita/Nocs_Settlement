# NOCS Settlement Test Suite

This project implements various test scenarios to validate settlement and report functionality, signature validation, and error handling.

## Overview

This test suite covers multiple test cases (TC_01 through TC_25) that validate:
- **Settlement API** (`/nocs/v2/settle`) - Testing settlement operations
- **Report API** (`/nocs/v2/report`) - Testing report functionality
- **Signature Validation** - Ed25519 signature generation and validation
- **Schema Validation** - Request payload validation
- **Business Logic Validation** - Various business rule validations

## Prerequisites

- Python 3.10 or higher
- Valid ONDC NOCS credentials:
  - `SUBSCRIBER_ID` - Your registered subscriber ID
  - `UNIQUE_KEY_ID` - Unique key identifier for your subscriber
  - `PRIVATE_KEY` - Base64 encoded Ed25519 private key
  - `BAP_ID` - App BAP ID
  - `BAP_URI` - App BAP URI

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Nocs_Settlement
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with your credentials:

```env
SUBSCRIBER_ID=your-subscriber-id.com
UNIQUE_KEY_ID=your-unique-key-id
PRIVATE_KEY=your-base64-encoded-private-key
BAP_ID=your-bap-id.com
BAP_URI=https://your-bap-id.com/ondc/api/v1
```

**Important Notes:**
- Ensure your credentials are active and not expired

### Alternative: Direct Configuration

You can also modify `creds.py` directly to set credentials (not recommended for production):

```python
SUBSCRIBER_ID = "your-subscriber-id.com"
UNIQUE_KEY_ID = "your-unique-key-id"
PRIVATE_KEY = "your-base64-encoded-private-key"
# ... etc
```

## Usage

### Running Individual Test Cases

Each test case can be run independently:

```bash
python TC_01.py  # Test case 1: Missing settlement type
python TC_02.py  # Test case 2: Invalid BAP ID in Authorization header
python TC_25.py  # Test case 25: Report with invalid reference IDs
```

### Test Case Examples

**TC_01 - Schema Validation (Missing Settlement Type)**
```bash
python TC_01.py
```
Expected: NACK with error code 70002 (Invalid Schema)

**TC_02 - Signature Validation (Invalid BAP ID)**
```bash
python TC_02.py
```
Expected: NACK with error code 70000 (Invalid Signature)

**TC_25 - Report with Invalid Reference IDs**
```bash
python TC_25.py
```
Expected: ACK, Failed order settlement with error code 70028

## Project Structure

```
Nocs_Settlement/
├── creds.py              # Configuration and authentication utilities
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore          # Git ignore rules
├── TC_01.py            # Test case 1: Missing settlement type
├── TC_02.py            # Test case 2: Invalid BAP ID
├── TC_03.py            # Test case 3: ...
├── ...                 # Additional test cases
├── TC_25.py            # Test case 25: Report validation
├── Docs/               # Documentation files
│   ├── NOCS - NP Test Scenario_1.1.xlsx
│   └── NOCS Integeration Documentation_v1.2.docx
└── not_required/       # Optional test cases
    ├── TC_17.py
    ├── TC_18.py
    ├── TC_21.py
    └── TC_23.py
```

## References

- ONDC Documentation: See `Docs/` folder
- NOCS Integration Documentation: `Docs/NOCS Integeration Documentation_v1.2.docx`
- Test Scenarios: `Docs/NOCS - NP Test Scenario_1.1.xlsx`
