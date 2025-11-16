# CLAUDE.md - AI Assistant Development Guide

> **Last Updated**: 2025-11-16
> **Purpose**: Comprehensive guide for AI assistants working with the CSVSheetsBridge codebase

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture & Design](#architecture--design)
- [Codebase Structure](#codebase-structure)
- [Key Modules & Components](#key-modules--components)
- [Development Workflows](#development-workflows)
- [Coding Conventions](#coding-conventions)
- [Common Patterns](#common-patterns)
- [Testing & Debugging](#testing--debugging)
- [Deployment](#deployment)
- [Security Considerations](#security-considerations)
- [Troubleshooting Guide](#troubleshooting-guide)
- [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Overview

**CSVSheetsBridge** is an automated system that processes AppsFlyer CSV data and updates Google Sheets with calculated KPIs and analytics.

### Core Purpose
- **Input**: AppsFlyer raw CSV data (advertising campaign metrics)
- **Processing**: Calculate KPIs (D1 Retained CAC, CPI, CTR, etc.)
- **Output**: Structured Google Sheets with multiple analytical views

### Key Features
1. **Full Automation**: CSV → Processing → Google Sheets update
2. **Smart Analysis**: Automatic KPI calculation and performance grading (A-D)
3. **Formula-Based Updates**: Efficient sheet updates using Google Sheets formulas
4. **Auto Sheet Detection**: Automatically detects and uses existing sheet names
5. **No OAuth Required**: Uses Google Apps Script web app for simplified authentication

### Technology Stack
- **Python**: 3.7+ (pandas, numpy, requests, python-dotenv)
- **Google Apps Script**: JavaScript-based web app for Sheets API
- **Data Processing**: pandas for data manipulation and analysis
- **API Communication**: HTTP requests to Apps Script endpoint

---

## Architecture & Design

### System Architecture

```
┌─────────────────┐
│   CSV File      │ (AppsFlyer raw data)
│  Data_dua.csv   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Python Processing Layer                    │
│  ┌─────────────────────────────────────┐   │
│  │ appsflyer_processor_adapted.py      │   │
│  │ - Load & validate CSV               │   │
│  │ - Media filtering (TikTok, Meta)    │   │
│  │ - KPI calculation                   │   │
│  │ - Performance ranking               │   │
│  └─────────────┬───────────────────────┘   │
│                │                             │
│  ┌─────────────▼───────────────────────┐   │
│  │ sheets_updater.py                   │   │
│  │ - Format data for Sheets            │   │
│  │ - Create summary statistics         │   │
│  │ - Generate formulas                 │   │
│  └─────────────┬───────────────────────┘   │
└────────────────┼─────────────────────────────┘
                 │
                 ▼ HTTP POST/GET
┌─────────────────────────────────────────────┐
│  Google Apps Script Layer                   │
│  ┌─────────────────────────────────────┐   │
│  │ Code.gs (Web App)                   │   │
│  │ - doGet(): Read sheet data          │   │
│  │ - doPost(): Update/append/overwrite │   │
│  │ - Authentication & permissions      │   │
│  └─────────────┬───────────────────────┘   │
└────────────────┼─────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Google Sheets                              │
│  ┌─────────────┐  ┌──────────────┐         │
│  │ 메인데이터   │  │ 요약         │         │
│  └─────────────┘  └──────────────┘         │
│  ┌─────────────┐  ┌──────────────┐         │
│  │ 상위성과     │  │ 피벗테이블   │         │
│  └─────────────┘  └──────────────┘         │
└─────────────────────────────────────────────┘
```

### Two Update Strategies

#### 1. Standard Approach (`appsflyer_automation_real.py`)
- **All sheets**: Real calculated values
- **Pros**: Independent, stable, offline-friendly
- **Cons**: Data duplication, manual sync needed

#### 2. Formula-Based Approach (`appsflyer_automation_formula.py`) ⭐ **Recommended**
- **Main data**: Real values
- **Other sheets**: Google Sheets formulas referencing main data
- **Pros**: Auto-sync, real-time updates, efficient
- **Cons**: Requires Google Sheets to recalculate

---

## Codebase Structure

```
CSVSheetsBridge/
├── 📄 Main Automation Scripts
│   ├── appsflyer_automation_real.py        # Standard approach (all real values)
│   ├── appsflyer_automation_formula.py     # Formula-based approach ⭐
│   └── appsflyer_automation.py             # Legacy/generic version
│
├── 📁 src/                                 # Core source modules
│   ├── appsflyer_processor.py              # Generic AppsFlyer data processor
│   ├── appsflyer_processor_adapted.py      # Adapted for real Data_dua.csv format
│   ├── sheets_client.py                    # Google Sheets HTTP client
│   ├── oauth_sheets_client.py              # OAuth-based client (alternative)
│   ├── token_sheets_client.py              # Token-based client (alternative)
│   ├── sheets_updater.py                   # Sheet update orchestration
│   └── sheets_detector.py                  # Auto-detect existing sheet names
│
├── 📁 apps_script/                         # Google Apps Script code
│   ├── Code.gs                             # Main web app (recommended)
│   ├── Code_GET_Only.gs                    # Read-only variant
│   ├── Code_Secure.gs                      # With API key authentication
│   ├── Code_Token.gs                       # Token-based authentication
│   └── DEPLOYMENT.md                       # Apps Script deployment guide
│
├── 📁 config/
│   └── settings.py                         # Configuration management
│
├── 📁 examples/
│   ├── basic_usage.py                      # Basic API usage examples
│   └── csv_integration.py                  # CSV integration examples
│
├── 📁 Documentation
│   ├── README.md                           # Main user documentation
│   ├── PROJECT_SUMMARY.md                  # Project completion report
│   ├── SECURITY_GUIDE.md                   # Security configuration guide
│   ├── TROUBLESHOOTING.md                  # Common issues and solutions
│   ├── README_APPSFLYER.md                 # AppsFlyer-specific docs
│   └── CLAUDE.md                           # This file (AI assistant guide)
│
├── 📁 Utility Scripts
│   ├── find_sheet_names.py                 # List all sheet names
│   ├── setup_guide.py                      # Interactive setup
│   ├── test_token_auth.py                  # Test token authentication
│   ├── test_post_auth.py                   # Test POST requests
│   └── debug_test.py                       # Debugging utilities
│
├── 📄 Configuration Files
│   ├── requirements.txt                    # Python dependencies
│   ├── setup.py                            # Package setup
│   ├── .env                                # Environment variables (git-ignored)
│   └── .gitignore                          # Git ignore patterns
│
└── 📄 Data Files (git-ignored)
    ├── Data_dua.csv                        # AppsFlyer input data
    └── *.log                                # Log files
```

### File Naming Conventions
- **Automation scripts**: `appsflyer_automation_*.py`
- **Core modules**: `snake_case.py` in `src/`
- **Apps Script**: `Code*.gs` variants
- **Docs**: `SCREAMING_SNAKE_CASE.md`

---

## Key Modules & Components

### 1. `src/sheets_client.py`

**Purpose**: HTTP client for communicating with Google Apps Script web app

**Key Classes**:
- `GoogleSheetsClient`: Base client with core CRUD operations
- `RobustGoogleSheetsClient`: Extends base with retry logic and rate limiting

**Core Methods**:
```python
# Read operations
read_sheet(sheet_id: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]
get_sheet_names(sheet_id: str) -> Dict[str, Any]

# Write operations
update_range(sheet_id, range_str, data, sheet_name) -> Dict[str, Any]
append_rows(sheet_id, data, sheet_name) -> Dict[str, Any]
overwrite_sheet(sheet_id, data, sheet_name) -> Dict[str, Any]
clear_sheet(sheet_id, range_str, sheet_name) -> Dict[str, Any]

# Sheet management
create_sheet(sheet_id, sheet_name) -> Dict[str, Any]
```

**Important Patterns**:
- Uses `@retry_on_failure` decorator (max 3 retries)
- Special handling for 429 rate limit errors (longer backoff)
- Exponential backoff: 2^n seconds for general errors, 3^n+2 for rate limits
- Returns dict with `{'success': bool, 'error': str, ...}`

### 2. `src/sheets_updater.py`

**Purpose**: High-level orchestration for updating Google Sheets

**Key Class**: `SheetsUpdater`

**Core Responsibilities**:
1. Auto-detect sheet names via `sheets_detector.py`
2. Format pandas DataFrames for Google Sheets (2D lists)
3. Handle data type conversions (Categorical → str, NaN → '', inf → 'N/A')
4. Create summary statistics and pivot tables
5. Ensure sheets exist before updating

**Key Methods**:
```python
update_main_data_sheet(df: pd.DataFrame, sheet_name: str = None) -> Dict
update_summary_sheet(stats: Dict, sheet_name: str = None) -> Dict
update_top_performers_sheet(stats: Dict, sheet_name: str = None) -> Dict
update_pivot_sheet(df: pd.DataFrame, sheet_name: str = None) -> Dict
update_all_sheets(df: pd.DataFrame, stats: Dict) -> Dict

# Data preparation
prepare_data_for_sheets(df: pd.DataFrame) -> List[List]
create_summary_sheet_data(stats: Dict) -> List[List]
create_top_performers_data(stats: Dict) -> List[List]
create_pivot_table_data(df: pd.DataFrame) -> List[List]

# Utilities
ensure_sheet_exists(sheet_name: str) -> bool
backup_current_data(backup_sheet_name: str = None) -> Dict
```

**Critical Data Conversion**:
```python
# Categorical columns → string (Google Sheets compatibility)
if pd.api.types.is_categorical_dtype(df_clean[col]):
    df_clean[col] = df_clean[col].astype(str)

# NaN → empty string
df_clean = df_clean.fillna('')

# Infinity → 'N/A'
df_clean = df_clean.replace([float('inf'), float('-inf')], 'N/A')
```

### 3. `src/appsflyer_processor.py` & `appsflyer_processor_adapted.py`

**Purpose**: Process AppsFlyer CSV data and calculate KPIs

**Key Class**: `AppsflyerDataProcessor` / `AppsflyerDataProcessorAdapted`

**Processing Pipeline**:
```python
def process() -> pd.DataFrame:
    1. load_csv()                    # Load with multiple encoding attempts
    2. validate_data()               # Check required columns
    3. filter_target_media()         # Filter TikTok, Meta campaigns
    4. create_content_mapping()      # Map campaign/adset/ad to content_name
    5. aggregate_by_content()        # Group by content
    6. calculate_kpis()              # Calculate all KPIs
    7. rank_content_performance()    # Rank and grade (A-D)
    return processed_data
```

**KPI Calculations**:
```python
# CPC (Cost Per Click)
cpc = cost / clicks

# CPI (Cost Per Install)
cpi = cost / installs

# CTR (Click Through Rate)
ctr = (clicks / impressions) * 100

# D1 Retained CAC (primary KPI)
d1_retained_cac = cost / d1_retained_users

# D1 Retention Rate
d1_retention_rate = (d1_retained_users / installs) * 100
```

**Performance Grading**:
```python
# Composite score with weighted ranks
weights = {
    'rank_d1_cac': 0.5,    # 50% - Primary KPI
    'rank_cpi': 0.2,       # 20%
    'rank_cpc': 0.15,      # 15%
    'rank_ctr': 0.15       # 15%
}

# Grade distribution (percentile-based)
A: Top 20% (best performers)
B: 21-50% (good performers)
C: 51-80% (average performers)
D: Bottom 20% (needs improvement)
```

**Column Mapping** (Data_dua.csv format):
```python
column_mapping = {
    'Ad': 'ad_name',
    'Cost (sum)': 'cost',
    'Impressions (sum)': 'impressions',
    'Clicks (sum)': 'clicks',
    'Installs (sum)': 'installs',
    'Unique Users - etc_sign_up (sum)': 'signups',
    'Retention Day 01 (sum)': 'd1_retained_users'
}
```

### 4. `src/sheets_detector.py`

**Purpose**: Auto-detect existing sheet names in Google Sheets

**Key Function**:
```python
def detect_sheets_auto() -> Dict[str, str]:
    """
    Returns mapping like:
    {
        'main_data_sheet': 'Sheet1',
        'summary_sheet': 'Sheet1',
        'top_performers_sheet': 'Sheet1',
        'pivot_table_sheet': 'Sheet1'
    }
    """
```

**Priority-based Detection**:
1. Tries common names: `['시트1', 'Sheet1', 'Sheet 1']`
2. Falls back to first available sheet
3. Uses single sheet for all purposes initially

### 5. `apps_script/Code.gs`

**Purpose**: Google Apps Script web app for Sheets API

**Key Functions**:

```javascript
function doGet(e) {
    // Handle GET requests (read operations)
    // Parameters: sheetId, sheetName
    // Returns: JSON with sheet data
}

function doPost(e) {
    // Handle POST requests (write operations)
    // Actions: update, append, clear, overwrite, create_sheet, get_sheet_names
    // Returns: JSON with operation result
}

function createResponse(data, statusCode) {
    // Helper to create JSON responses with status codes
}
```

**Supported Actions**:
- `update`: Update specific range
- `append`: Append rows to end
- `clear`: Clear range or entire sheet
- `overwrite`: Clear sheet then write new data
- `create_sheet`: Create new sheet (idempotent)
- `get_sheet_names`: List all sheet names

**Error Handling**:
```javascript
try {
    // Operation logic
    return createResponse({success: true, ...}, 200);
} catch (error) {
    return createResponse({error: error.toString()}, 500);
}
```

### 6. `config/settings.py`

**Purpose**: Configuration management

**Key Class**:
```python
class SheetsConfig:
    def __init__(self, web_app_url=None, sheet_id=None):
        self.web_app_url = web_app_url or os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEETS_SHEET_ID')

    def validate(self):
        # Validates configuration completeness and format
```

---

## Development Workflows

### Environment Setup

```bash
# 1. Clone repository
git clone https://github.com/ben-spoonradio/CSVSheetsBridge.git
cd CSVSheetsBridge

# 2. Install dependencies
pip install -r requirements.txt
# OR
pip install pandas numpy python-dotenv requests

# 3. Configure environment
cp .env.example .env  # If example exists
nano .env  # Edit configuration

# Required .env variables:
GOOGLE_SHEETS_WEB_APP_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
GOOGLE_SHEETS_SHEET_ID=YOUR_SPREADSHEET_ID
GOOGLE_SHEETS_ACCESS_TOKEN=YourOptionalToken  # Optional
```

### Google Apps Script Deployment

```bash
# See apps_script/DEPLOYMENT.md for detailed guide

# Quick checklist:
1. Go to https://script.google.com
2. Create new project
3. Paste Code.gs content
4. Deploy as Web App
   - Execute as: Me
   - Access: Anyone (or as needed)
5. Copy web app URL → .env file
```

### Running the Automation

```bash
# Standard approach (all real values)
python appsflyer_automation_real.py --csv Data_dua.csv

# Formula-based approach (recommended)
python appsflyer_automation_formula.py --csv Data_dua.csv

# With options
python appsflyer_automation_formula.py \
    --csv Data_dua.csv \
    --backup \          # Backup before update
    --export \          # Export processed data to CSV
    --verbose           # Verbose logging
```

### Git Workflow

**Branch Naming**:
- Feature: `feature/description`
- Bugfix: `bugfix/description`
- Claude sessions: `claude/claude-md-{session-id}`

**Commit Messages**:
```
# Format (Korean or English)
<Type>: <Short description>

<Detailed explanation>
<What changed and why>

# Examples from repo:
시트 생성/조회 API 추가 및 클라이언트 재시도/존재확인 로직 강화
AppsFlyer 자동화 포뮬러 추가 및 README 업데이트
README 구조 정리 및 설치 안내 추가
```

**Working with Claude**:
```bash
# Development should happen on Claude-specific branches
git checkout -b claude/claude-md-mi1opq8e0rseolpu-017PJYPAzQv23APmo6WcEiZy

# Commit changes
git add .
git commit -m "Description of changes"

# Push to remote
git push -u origin claude/claude-md-mi1opq8e0rseolpu-017PJYPAzQv23APmo6WcEiZy
```

### Testing Workflow

```bash
# Test individual components
python test_token_auth.py           # Test authentication
python test_post_auth.py            # Test POST requests
python debug_test.py                # Debug utilities

# Test with sample data
python src/appsflyer_processor.py   # Has create_sample_data() function

# Find existing sheet names
python find_sheet_names.py
```

---

## Coding Conventions

### Python Style
- **Standard**: PEP 8 compliant
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `SCREAMING_SNAKE_CASE`
  - Private: `_leading_underscore`

### Imports Organization
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

# Local modules
from sheets_client import GoogleSheetsClient
from appsflyer_processor import AppsflyerDataProcessor
```

### Logging Pattern
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Usage
logger.info("Processing started")
logger.warning("Potential issue detected")
logger.error(f"Operation failed: {error}")
```

### Error Handling
```python
# Pattern 1: Return dict with error status
def operation() -> Dict[str, Any]:
    try:
        # Logic
        return {'success': True, 'data': result}
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return {'success': False, 'error': str(e)}

# Pattern 2: Raise with context
def critical_operation():
    try:
        # Logic
    except SpecificError as e:
        logger.error(f"Critical failure: {e}")
        raise ValueError(f"Context: {e}") from e
```

### Type Hints
```python
from typing import Dict, List, Optional, Any, Tuple

def process_data(
    data: pd.DataFrame,
    options: Optional[Dict[str, Any]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Process data with optional configuration.

    Args:
        data: Input DataFrame
        options: Optional processing options

    Returns:
        Tuple of (processed_data, statistics)
    """
    # Implementation
```

### Docstrings
```python
"""
Module-level docstring explaining purpose.
"""

class MyClass:
    """Class-level docstring."""

    def method(self, param: str) -> bool:
        """
        Method description.

        Args:
            param: Parameter description

        Returns:
            Return value description
        """
```

---

## Common Patterns

### 1. Retry Decorator Pattern

**Location**: `src/sheets_client.py:8-42`

```python
def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff and rate limit handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                result = func(*args, **kwargs)

                if 'error' not in result:
                    return result

                error_msg = result.get('error', '')

                # Special handling for 429 rate limiting
                if '429' in str(error_msg) or 'rate' in str(error_msg).lower():
                    wait_time = delay * (3 ** attempt) + 2  # Longer wait
                else:
                    wait_time = delay * (2 ** attempt)  # Standard backoff

                if attempt < max_retries - 1:
                    time.sleep(wait_time)

            return result
        return wrapper
    return decorator

# Usage
@retry_on_failure(max_retries=3, delay=1.0)
def api_call(self, ...):
    return super().api_call(...)
```

### 2. Sheet Existence Pattern

**Location**: `src/sheets_updater.py:60-102`

```python
def ensure_sheet_exists(self, sheet_name: str) -> bool:
    """Ensure sheet exists, create if not, handle rate limiting"""
    try:
        time.sleep(0.5)  # Prevent rate limiting

        result = self.client.create_sheet(self.sheet_id, sheet_name)

        if result.get('success'):
            return True

        # Rate limiting retry
        if '429' in str(result.get('error')) or 'rate' in str(result.get('error')).lower():
            time.sleep(3)
            retry_result = self.client.create_sheet(self.sheet_id, sheet_name)
            if retry_result.get('success'):
                return True

        # Sheet already exists is success
        if 'already exists' in str(result.get('error')).lower():
            return True

        return False
    except Exception as e:
        logger.error(f"Error ensuring sheet exists: {e}")
        return False
```

**Usage**: Always call before updating a sheet to prevent errors.

### 3. Data Preparation Pattern

**Location**: `src/sheets_updater.py:104-146`

```python
def prepare_data_for_sheets(self, df: pd.DataFrame) -> List[List]:
    """Convert DataFrame to Google Sheets-compatible format"""
    df_clean = df.copy()

    # 1. Convert Categorical to string
    for col in df_clean.columns:
        if pd.api.types.is_categorical_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].astype(str)

    # 2. Handle special values
    df_clean = df_clean.fillna('')
    df_clean = df_clean.replace([float('inf'), float('-inf')], 'N/A')

    # 3. Format numbers based on column type
    for col in df_clean.columns:
        if df_clean[col].dtype in ['float64', 'int64']:
            if col in ['cost', 'cpc', 'cpi', 'd1_retained_cac']:
                df_clean[col] = df_clean[col].apply(
                    lambda x: f"{float(x):.2f}" if str(x) not in ['N/A', ''] else x
                )
            elif col in ['ctr', 'd1_retention_rate']:
                df_clean[col] = df_clean[col].apply(
                    lambda x: f"{float(x):.1f}%" if str(x) not in ['N/A', ''] else x
                )

    # 4. Convert to 2D list with headers
    headers = list(df_clean.columns)
    data_rows = df_clean.values.tolist()
    return [headers] + data_rows
```

### 4. Environment Configuration Pattern

**Location**: `config/settings.py`, used throughout

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access with fallback
web_app_url = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')
token = os.getenv('GOOGLE_SHEETS_ACCESS_TOKEN', '')  # Optional with default

# Validation
if not web_app_url or not sheet_id:
    raise ValueError("Required environment variables not set")
```

### 5. Response Format Pattern

**All API responses follow this format**:

```python
# Success response
{
    'success': True,
    'data': ...,        # Optional: response data
    'rows': 100,        # Optional: affected rows
    'message': '...'    # Optional: success message
}

# Error response
{
    'success': False,   # May be omitted
    'error': 'Error description'
}
```

---

## Testing & Debugging

### Debug Logging

Enable verbose logging in automation scripts:

```bash
python appsflyer_automation_formula.py --csv Data_dua.csv --verbose
```

### Test Scripts

```python
# test_token_auth.py - Test authentication
python test_token_auth.py

# test_post_auth.py - Test POST operations
python test_post_auth.py

# debug_test.py - Debug specific issues
python debug_test.py
```

### Apps Script Debugging

```javascript
// Add logging to Code.gs
function doPost(e) {
    Logger.log('Request received: ' + JSON.stringify(e));
    try {
        // ... logic
        Logger.log('Success: ' + JSON.stringify(result));
    } catch (error) {
        Logger.log('Error: ' + error.toString());
    }
}

// View logs: Apps Script Editor → Execution log
```

### Common Debug Points

```python
# 1. Check data loading
print(f"CSV shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())

# 2. Verify processing
print(f"Processed records: {len(processed_data)}")
print(f"KPIs calculated: {processed_data.columns.tolist()}")

# 3. Check API responses
result = client.read_sheet(sheet_id, sheet_name)
print(f"API Success: {result.get('success')}")
print(f"Error: {result.get('error')}")

# 4. Validate data conversion
sheet_data = updater.prepare_data_for_sheets(df)
print(f"Sheet data rows: {len(sheet_data)}")
print(f"First row: {sheet_data[0]}")
```

---

## Deployment

### Google Apps Script Deployment

**See**: `apps_script/DEPLOYMENT.md` for complete guide

**Quick Steps**:
1. Go to https://script.google.com
2. Create new project → Paste `Code.gs`
3. Deploy → New deployment → Web app
4. Settings:
   - Execute as: Me
   - Who has access: Anyone (or as needed for security)
5. Copy web app URL

**Security Levels** (see `SECURITY_GUIDE.md`):
- Development: "Anyone" (quick testing)
- Production: "Anyone with Google account" or "Specific users"
- High Security: Specific users + API key authentication

### Python Environment

**Production Setup**:
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install exact versions
pip install -r requirements.txt

# Set production environment variables
# Use secure methods (not .env file in production)
export GOOGLE_SHEETS_WEB_APP_URL="..."
export GOOGLE_SHEETS_SHEET_ID="..."
```

### Scheduling Automation

**Cron (Linux/Mac)**:
```bash
# Edit crontab
crontab -e

# Run daily at 9 AM
0 9 * * * cd /path/to/CSVSheetsBridge && /path/to/venv/bin/python appsflyer_automation_formula.py --csv Data_dua.csv >> /var/log/appsflyer.log 2>&1
```

**Task Scheduler (Windows)**:
```powershell
# Create scheduled task
schtasks /create /tn "AppsFlyer Update" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\appsflyer_automation_formula.py --csv Data_dua.csv" /sc daily /st 09:00
```

---

## Security Considerations

### Critical Security Rules

**See**: `SECURITY_GUIDE.md` for comprehensive guide

1. **Never commit secrets**:
   ```bash
   # .gitignore already includes:
   .env
   .env.*
   config.json
   credentials.json
   *.log
   Data_*.csv
   ```

2. **Environment variables only**:
   ```python
   # ❌ BAD - Hardcoded
   SHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

   # ✅ GOOD - Environment variable
   SHEET_ID = os.getenv('GOOGLE_SHEETS_SHEET_ID')
   ```

3. **Apps Script access control**:
   - Development: "Anyone" (testing only)
   - Production: "Anyone with Google account" or "Specific users"
   - See `SECURITY_GUIDE.md` for API key authentication

4. **HTTPS only**:
   ```python
   if not web_app_url.startswith('https://'):
       raise ValueError("HTTPS required for security")
   ```

### Security Levels

| Level | Access Control | API Key | IP Restrict | Risk |
|-------|---------------|---------|-------------|------|
| **Development** | Anyone | Optional | No | 🔴 High |
| **Production** | Google Account | Recommended | Optional | 🟡 Medium |
| **High Security** | Specific Users | Required | Yes | 🟢 Low |

**Implement API Key** (see `apps_script/Code_Secure.gs`):
```javascript
// Apps Script
function doGet(e) {
    var apiKey = e.parameter.apiKey;
    var validKey = PropertiesService.getScriptProperties().getProperty('API_KEY');

    if (!apiKey || apiKey !== validKey) {
        return createResponse({error: 'Invalid API key'}, 401);
    }
    // ... rest of logic
}
```

---

## Troubleshooting Guide

**See**: `TROUBLESHOOTING.md` for complete guide

### Common Issues

#### 1. "401 Unauthorized" Error

**Cause**: Apps Script access permissions
**Solution**:
```bash
1. Apps Script → Deploy → Manage deployments
2. Edit deployment
3. Access: Change to "Anyone"
4. Redeploy and copy new URL
```

#### 2. "시트를 찾을 수 없습니다" (Sheet not found)

**Cause**: Sheet name doesn't exist
**Solution**:
```bash
# Find existing sheet names
python find_sheet_names.py

# Or check detector results
from sheets_detector import detect_sheets_auto
print(detect_sheets_auto())
```

#### 3. "Categorical dtype error"

**Cause**: Pandas Categorical columns not converted
**Already fixed** in `sheets_updater.py:112-115`:
```python
if pd.api.types.is_categorical_dtype(df_clean[col]):
    df_clean[col] = df_clean[col].astype(str)
```

#### 4. Rate Limiting (429 errors)

**Cause**: Too many API requests
**Solution**: Already handled via retry decorator with backoff
```python
# In sheets_client.py - automatic handling
@retry_on_failure(max_retries=3, delay=1.0)
def operation(...):
    # 429 errors get 3^n+2 second backoff automatically
```

#### 5. CSV Encoding Issues

**Cause**: Non-UTF-8 encoding
**Solution**: Already handled in processor:
```python
# appsflyer_processor.py tries multiple encodings
encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']
for encoding in encodings:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

### Debug Checklist

```bash
✓ Check .env file exists and is complete
✓ Verify Apps Script deployment is active
✓ Test Apps Script URL in browser (should return JSON)
✓ Check Google Sheets ID is correct
✓ Verify CSV file path and format
✓ Check Python dependencies are installed
✓ Review logs: appsflyer_automation_*.log
✓ Test with --verbose flag for detailed output
```

---

## AI Assistant Guidelines

### When Working on This Codebase

#### 1. Understanding Context
- **Read first**: Always check README.md, PROJECT_SUMMARY.md for project context
- **Check conventions**: Review this CLAUDE.md before making changes
- **Understand architecture**: Review the architecture diagram above
- **Know the data flow**: CSV → Processor → Updater → Apps Script → Sheets

#### 2. Making Code Changes

**DO**:
- ✅ Follow existing patterns (retry decorator, error dict format, logging)
- ✅ Update documentation when changing behavior
- ✅ Test with real Data_dua.csv format
- ✅ Handle errors gracefully (return dicts, log details)
- ✅ Use environment variables for configuration
- ✅ Add logging statements for debugging
- ✅ Preserve existing error handling patterns
- ✅ Use type hints and docstrings

**DON'T**:
- ❌ Hardcode credentials or IDs
- ❌ Remove existing error handling
- ❌ Change API response formats without checking dependencies
- ❌ Skip data type conversion in sheets_updater
- ❌ Ignore rate limiting considerations
- ❌ Remove retry logic
- ❌ Change column mapping without testing

#### 3. Adding New Features

**Checklist**:
```
1. [ ] Does it fit the project architecture?
2. [ ] Is error handling included?
3. [ ] Does it need retry logic?
4. [ ] Is logging added?
5. [ ] Are type hints included?
6. [ ] Is documentation updated?
7. [ ] Does it handle rate limiting?
8. [ ] Is it tested with real data?
```

**Example - Adding new KPI**:
```python
# 1. Add to appsflyer_processor.py calculate_kpis()
def calculate_kpis(self, data: pd.DataFrame) -> pd.DataFrame:
    # ... existing KPIs ...

    # New KPI
    processed_data['new_kpi'] = np.where(
        processed_data['denominator'] > 0,
        processed_data['numerator'] / processed_data['denominator'],
        0
    )
    logger.info("New KPI calculated")
    return processed_data

# 2. Update formatting in sheets_updater.py prepare_data_for_sheets()
if col in ['cost', 'cpc', 'cpi', 'd1_retained_cac', 'new_kpi']:  # Add here
    df_clean[col] = df_clean[col].apply(
        lambda x: f"{float(x):.2f}" if str(x) not in ['N/A', ''] else x
    )

# 3. Update documentation in README.md
```

#### 4. Debugging User Issues

**Step-by-step**:
```
1. Ask for error message and context
2. Check which script they're running
3. Verify .env configuration
4. Check Apps Script deployment status
5. Look at log files (*.log)
6. Test with --verbose flag
7. Verify CSV format matches expected columns
8. Check sheet names exist
```

**Quick diagnosis**:
```python
# Test connectivity
from src.sheets_client import GoogleSheetsClient
client = GoogleSheetsClient(os.getenv('GOOGLE_SHEETS_WEB_APP_URL'))
result = client.get_sheet_names(os.getenv('GOOGLE_SHEETS_SHEET_ID'))
print(result)  # Should show success: True

# Test CSV loading
from src.appsflyer_processor_adapted import AppsflyerDataProcessorAdapted
processor = AppsflyerDataProcessorAdapted('Data_dua.csv')
df = processor.load_csv()
print(df.columns.tolist())  # Should show expected columns
```

#### 5. Documentation Updates

**When to update**:
- New feature added → Update README.md + this file
- Bug fix affecting behavior → Update TROUBLESHOOTING.md
- API changes → Update this file's Key Modules section
- New security consideration → Update SECURITY_GUIDE.md
- Deployment changes → Update apps_script/DEPLOYMENT.md

**Documentation locations**:
- User guide → `README.md`
- AI assistant guide → `CLAUDE.md` (this file)
- Project completion → `PROJECT_SUMMARY.md`
- Security → `SECURITY_GUIDE.md`
- Issues → `TROUBLESHOOTING.md`
- Apps Script → `apps_script/DEPLOYMENT.md`

#### 6. Code Review Checklist

Before suggesting code changes:
```
✓ Does it follow existing patterns?
✓ Is error handling included?
✓ Are type hints present?
✓ Is logging appropriate?
✓ Does it handle edge cases (NaN, inf, empty, None)?
✓ Is it compatible with Google Sheets data types?
✓ Does it respect rate limiting?
✓ Are environment variables used (not hardcoded)?
✓ Is documentation updated?
✓ Does it maintain backward compatibility?
```

#### 7. Testing Approach

**Levels of testing**:
```python
# 1. Unit - Individual functions
result = prepare_data_for_sheets(test_df)
assert isinstance(result, list)

# 2. Integration - Module interaction
processor = AppsflyerDataProcessorAdapted('test.csv')
df = processor.process()
updater = SheetsUpdater()
result = updater.update_main_data_sheet(df)
assert result.get('success')

# 3. End-to-end - Full automation
# Run: python appsflyer_automation_formula.py --csv Data_dua.csv
# Check: Google Sheets updated correctly

# 4. Error scenarios
# Test with: missing columns, empty CSV, invalid credentials, etc.
```

#### 8. Performance Considerations

**Watch for**:
- Multiple sequential API calls (can batch?)
- Large DataFrames (pandas memory usage)
- Rate limiting (use delays between requests)
- Apps Script 6-minute execution limit

**Optimization patterns**:
```python
# BAD - Multiple sequential calls
for sheet in sheets:
    update_sheet(sheet)  # Each waits for previous

# GOOD - Prepare all data first
all_data = {sheet: prepare_data(sheet) for sheet in sheets}
for sheet, data in all_data.items():
    update_sheet(sheet, data)  # At least data is ready

# BETTER - Use formula-based approach
# Only update main data, let formulas handle the rest
```

### Quick Reference Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env && nano .env

# Run automation
python appsflyer_automation_formula.py --csv Data_dua.csv --backup

# Debug
python find_sheet_names.py
python test_token_auth.py
python appsflyer_automation_formula.py --csv Data_dua.csv --verbose

# Check logs
tail -f appsflyer_automation_formula.log

# Test Apps Script
curl "https://script.google.com/.../exec?sheetId=YOUR_ID"
```

---

## Version History

- **2025-11-16**: Initial CLAUDE.md creation with comprehensive codebase documentation
- Project started: ~2024 (based on commit history)
- Current version: 1.0.0 (from setup.py)

---

## Additional Resources

- **Main Docs**: [README.md](README.md)
- **Security**: [SECURITY_GUIDE.md](SECURITY_GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Apps Script**: [apps_script/DEPLOYMENT.md](apps_script/DEPLOYMENT.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**For questions or clarifications about this guide, check the main README.md or create a GitHub issue.**
