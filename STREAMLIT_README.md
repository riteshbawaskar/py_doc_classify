# Streamlit Employee Management UI

## Overview
A comprehensive Streamlit web application for managing employee details with the ability to add, update, view, and search employee records stored in the SQLModel/SQLite database.

## Features

### 📊 Dashboard
- View total employee count
- See employees with verified Aadhaar and PAN
- Quick view of recent employees

### ➕ Add Employee
- Form-based employee creation
- Support for all identity fields:
  - Personal info (name, email, phone, DOB, gender)
  - Family details (father's name, spouse's name)
  - Address information
  - Identity documents (Aadhaar, PAN, Passport)
- Automatic confidence scoring (1.0 for manual entries)
- Real-time validation and success notifications

### ✏️ Update Employee
- Search employees by:
  - Employee ID
  - Aadhaar number
  - PAN number
- Pre-populated forms with existing data
- Modify any field and save changes
- Confidence scores automatically set to 1.0 for manual updates

### 🔍 Search Employee
- Multiple search criteria:
  - Name (partial match)
  - Email (partial match)
  - Aadhaar (exact match)
  - PAN (exact match)
  - Phone (partial match)
- Expandable result cards with full details

### 📋 View All
- Paginated table view of all employees
- Statistics on verification status
- CSV export functionality
- Download employee records as CSV file

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run streamlit.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage Examples

### Adding an Employee
1. Navigate to "➕ Add Employee"
2. Fill in the required fields (at minimum: Full Name)
3. Click "➕ Add Employee"
4. Confirmation message with employee ID will appear

### Updating an Employee
1. Navigate to "✏️ Update Employee"
2. Choose search method (ID, Aadhaar, or PAN)
3. Enter the search value
4. Modify desired fields
5. Click "💾 Update Employee"

### Searching
1. Go to "🔍 Search Employee"
2. Select search criteria
3. Enter search term
4. Click expander to view full details

### Exporting Data
1. Navigate to "📋 View All"
2. Click "📥 Download as CSV"
3. File will be downloaded with current timestamp

## Database Schema

The Employee model includes:

**Personal Information:**
- id (Primary Key)
- file_path
- full_name
- email
- phone_number
- dob (Date of Birth)
- gender
- father_name
- spouse_name
- address

**Identity Documents:**
- aadhaar_number
- pan_number
- passport_number

**Confidence Scores:** Each field has a corresponding confidence field (e.g., full_name_conf, aadhaar_conf)

**Metadata:**
- entities_json (Full raw entity extraction)
- inserted_at (Timestamp)

## Keyboard Shortcuts & Tips

- Use Tab to navigate between form fields
- Select search type carefully for faster results
- Aadhaar and PAN searches are exact matches
- Name, Email, and Phone searches support partial matches

## Error Handling

- Required field validation with error messages
- Database operation error reporting
- User-friendly notifications for all actions
- Graceful handling of missing employee records

## Future Enhancements

- Bulk upload via CSV
- Email notifications
- Role-based access control
- Document attachment storage
- Advanced filtering and reporting
- Employee profile photos
