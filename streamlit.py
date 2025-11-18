"""
Streamlit UI for Employee Data Management
Allows adding, updating, and viewing employee details
"""
import streamlit as st
from datetime import datetime
import pandas as pd
from db import (
    init_db,
    Employee,
    query_employees,
    query_employee_by_id,
    query_by_aadhaar,
    query_by_pan,
    get_engine,
)
from sqlmodel import Session

# Page configuration
st.set_page_config(
    page_title="Employee Management",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("👥 Employee Management System")
st.markdown("Manage employee details with entity extraction from documents")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select an option:",
        ["📊 Dashboard", "➕ Add Employee", "✏️ Update Employee", "🔍 Search Employee", "📋 View All"]
    )

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
if page == "📊 Dashboard":
    st.subheader("Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    # Get total employees
    employees = query_employees(limit=1000)
    total_employees = len(employees)
    
    with col1:
        st.metric(label="Total Employees", value=total_employees, delta=None)
    
    # Count employees with Aadhaar
    aadhaar_count = sum(1 for e in employees if e.aadhaar_number)
    with col2:
        st.metric(label="Employees with Aadhaar", value=aadhaar_count)
    
    # Count employees with PAN
    pan_count = sum(1 for e in employees if e.pan_number)
    with col3:
        st.metric(label="Employees with PAN", value=pan_count)
    
    # Recent employees table
    st.subheader("Recent Employees")
    if employees:
        df_data = []
        for emp in employees[:20]:
            df_data.append({
                "ID": emp.id,
                "Name": emp.full_name or "N/A",
                "Email": emp.email or "N/A",
                "Aadhaar": emp.aadhaar_number or "N/A",
                "PAN": emp.pan_number or "N/A",
                "Date Added": emp.inserted_at[:10] if emp.inserted_at else "N/A"
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No employees found. Start by adding a new employee.")

# ============================================================================
# ADD EMPLOYEE PAGE
# ============================================================================
elif page == "➕ Add Employee":
    st.subheader("Add New Employee")
    
    with st.form(key="add_employee_form", clear_on_submit=True):
        st.markdown("### Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input(
                "Full Name",
                placeholder="Enter employee full name",
                help="Employee's complete name"
            )
        with col2:
            email = st.text_input(
                "Email Address",
                placeholder="employee@example.com",
                help="Employee's email address"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input(
                "Phone Number",
                placeholder="+91 XXXXXXXXXX",
                help="Employee's contact number"
            )
        with col2:
            dob = st.date_input(
                "Date of Birth",
                help="Employee's date of birth"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox(
                "Gender",
                ["", "Male", "Female", "Other", "Prefer not to say"],
                help="Employee's gender"
            )
        with col2:
            father_name = st.text_input(
                "Father's Name",
                placeholder="Enter father's name",
                help="Employee's father's name"
            )
        
        spouse_name = st.text_input(
            "Spouse Name",
            placeholder="Enter spouse's name (if applicable)",
            help="Employee's spouse name"
        )
        
        address = st.text_area(
            "Address",
            placeholder="Enter complete address",
            height=100,
            help="Employee's residential address"
        )
        
        st.markdown("### Identity Documents")
        
        col1, col2 = st.columns(2)
        with col1:
            aadhaar = st.text_input(
                "Aadhaar Number",
                placeholder="12-digit Aadhaar number",
                help="Indian Aadhaar ID (12 digits)"
            )
        with col2:
            pan = st.text_input(
                "PAN Number",
                placeholder="10-character PAN",
                help="Permanent Account Number (10 characters)"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            passport = st.text_input(
                "Passport Number",
                placeholder="Passport number",
                help="Passport ID if applicable"
            )
        with col2:
            file_path = st.text_input(
                "Source Document Path",
                placeholder="/path/to/document.pdf",
                value="",
                help="Path to the source document (optional)"
            )
        
        # Submit button
        submitted = st.form_submit_button("➕ Add Employee", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not full_name:
                st.error("❌ Full Name is required!")
            else:
                try:
                    # Create new employee
                    engine = get_engine()
                    employee = Employee(
                        file_path=file_path or "Manual Entry",
                        full_name=full_name,
                        full_name_conf=1.0,  # Manual entry has 100% confidence
                        email=email if email else None,
                        email_conf=1.0 if email else None,
                        phone_number=phone if phone else None,
                        phone_conf=1.0 if phone else None,
                        dob=str(dob) if dob else None,
                        dob_conf=1.0 if dob else None,
                        gender=gender if gender else None,
                        gender_conf=1.0 if gender else None,
                        father_name=father_name if father_name else None,
                        father_conf=1.0 if father_name else None,
                        spouse_name=spouse_name if spouse_name else None,
                        spouse_conf=1.0 if spouse_name else None,
                        address=address if address else None,
                        address_conf=1.0 if address else None,
                        aadhaar_number=aadhaar if aadhaar else None,
                        aadhaar_conf=1.0 if aadhaar else None,
                        pan_number=pan if pan else None,
                        pan_conf=1.0 if pan else None,
                        passport_number=passport if passport else None,
                        passport_conf=1.0 if passport else None,
                        entities_json="{}",
                    )
                    
                    with Session(engine) as session:
                        session.add(employee)
                        session.commit()
                        session.refresh(employee)
                        emp_id = employee.id
                    
                    st.success(f"✅ Employee added successfully! (ID: {emp_id})")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error adding employee: {str(e)}")

# ============================================================================
# UPDATE EMPLOYEE PAGE
# ============================================================================
elif page == "✏️ Update Employee":
    st.subheader("Update Employee Details")
    
    # Search for employee
    col1, col2, col3 = st.columns(3)
    with col1:
        search_type = st.radio("Search by:", ["Employee ID", "Aadhaar", "PAN"])
    
    if search_type == "Employee ID":
        emp_id = st.number_input("Enter Employee ID:", min_value=1, step=1)
        employee = query_employee_by_id(emp_id)
        if not employee:
            st.warning("⚠️ Employee not found!")
            employee = None
    
    elif search_type == "Aadhaar":
        aadhaar = st.text_input("Enter Aadhaar Number:")
        if aadhaar:
            results = query_by_aadhaar(aadhaar)
            if results:
                employee = results[0]
            else:
                st.warning("⚠️ No employee found with this Aadhaar!")
                employee = None
        else:
            employee = None
    
    else:  # PAN
        pan = st.text_input("Enter PAN Number:")
        if pan:
            results = query_by_pan(pan)
            if results:
                employee = results[0]
            else:
                st.warning("⚠️ No employee found with this PAN!")
                employee = None
        else:
            employee = None
    
    # Update form
    if employee:
        st.success(f"✅ Employee found: {employee.full_name} (ID: {employee.id})")
        st.divider()
        
        with st.form(key="update_employee_form"):
            st.markdown("### Update Employee Information")
            
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input(
                    "Full Name",
                    value=employee.full_name or "",
                    placeholder="Enter employee full name"
                )
            with col2:
                email = st.text_input(
                    "Email Address",
                    value=employee.email or "",
                    placeholder="employee@example.com"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                phone = st.text_input(
                    "Phone Number",
                    value=employee.phone_number or "",
                    placeholder="+91 XXXXXXXXXX"
                )
            with col2:
                dob = st.text_input(
                    "Date of Birth (YYYY-MM-DD)",
                    value=employee.dob or "",
                    placeholder="2000-01-15"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                gender = st.selectbox(
                    "Gender",
                    ["", "Male", "Female", "Other", "Prefer not to say"],
                    index=(["", "Male", "Female", "Other", "Prefer not to say"].index(employee.gender) 
                           if employee.gender else 0)
                )
            with col2:
                father_name = st.text_input(
                    "Father's Name",
                    value=employee.father_name or "",
                    placeholder="Enter father's name"
                )
            
            spouse_name = st.text_input(
                "Spouse Name",
                value=employee.spouse_name or "",
                placeholder="Enter spouse's name"
            )
            
            address = st.text_area(
                "Address",
                value=employee.address or "",
                placeholder="Enter complete address",
                height=100
            )
            
            st.markdown("### Identity Documents")
            
            col1, col2 = st.columns(2)
            with col1:
                aadhaar = st.text_input(
                    "Aadhaar Number",
                    value=employee.aadhaar_number or "",
                    placeholder="12-digit Aadhaar number"
                )
            with col2:
                pan = st.text_input(
                    "PAN Number",
                    value=employee.pan_number or "",
                    placeholder="10-character PAN"
                )
            
            passport = st.text_input(
                "Passport Number",
                value=employee.passport_number or "",
                placeholder="Passport number"
            )
            
            # Submit button
            submitted = st.form_submit_button("💾 Update Employee", use_container_width=True)
            
            if submitted:
                try:
                    # Update employee
                    engine = get_engine()
                    with Session(engine) as session:
                        db_employee = session.get(Employee, employee.id)
                        
                        if db_employee:
                            db_employee.full_name = full_name
                            db_employee.full_name_conf = 1.0
                            db_employee.email = email if email else None
                            db_employee.email_conf = 1.0 if email else None
                            db_employee.phone_number = phone if phone else None
                            db_employee.phone_conf = 1.0 if phone else None
                            db_employee.dob = dob if dob else None
                            db_employee.dob_conf = 1.0 if dob else None
                            db_employee.gender = gender if gender else None
                            db_employee.gender_conf = 1.0 if gender else None
                            db_employee.father_name = father_name if father_name else None
                            db_employee.father_conf = 1.0 if father_name else None
                            db_employee.spouse_name = spouse_name if spouse_name else None
                            db_employee.spouse_conf = 1.0 if spouse_name else None
                            db_employee.address = address if address else None
                            db_employee.address_conf = 1.0 if address else None
                            db_employee.aadhaar_number = aadhaar if aadhaar else None
                            db_employee.aadhaar_conf = 1.0 if aadhaar else None
                            db_employee.pan_number = pan if pan else None
                            db_employee.pan_conf = 1.0 if pan else None
                            db_employee.passport_number = passport if passport else None
                            db_employee.passport_conf = 1.0 if passport else None
                            
                            session.add(db_employee)
                            session.commit()
                    
                    st.success(f"✅ Employee updated successfully! (ID: {employee.id})")
                    
                except Exception as e:
                    st.error(f"❌ Error updating employee: {str(e)}")

# ============================================================================
# SEARCH EMPLOYEE PAGE
# ============================================================================
elif page == "🔍 Search Employee":
    st.subheader("Search Employees")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_by = st.selectbox(
            "Search By:",
            ["Name", "Email", "Aadhaar", "PAN", "Phone"]
        )
    
    if search_by == "Name":
        name = st.text_input("Enter Name:", placeholder="John Doe")
        if name:
            employees = query_employees(limit=1000)
            results = [e for e in employees if e.full_name and name.lower() in e.full_name.lower()]
    
    elif search_by == "Email":
        email = st.text_input("Enter Email:", placeholder="john@example.com")
        if email:
            employees = query_employees(limit=1000)
            results = [e for e in employees if e.email and email.lower() in e.email.lower()]
    
    elif search_by == "Aadhaar":
        aadhaar = st.text_input("Enter Aadhaar:", placeholder="123456789012")
        if aadhaar:
            results = query_by_aadhaar(aadhaar)
    
    elif search_by == "PAN":
        pan = st.text_input("Enter PAN:", placeholder="ABCDE1234F")
        if pan:
            results = query_by_pan(pan)
    
    else:  # Phone
        phone = st.text_input("Enter Phone:", placeholder="+91 9876543210")
        if phone:
            employees = query_employees(limit=1000)
            results = [e for e in employees if e.phone_number and phone in e.phone_number]
    
    # Display results
    if 'results' in locals() and results:
        st.success(f"Found {len(results)} result(s)")
        for emp in results:
            with st.expander(f"👤 {emp.full_name} (ID: {emp.id})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {emp.email or 'N/A'}")
                    st.write(f"**Phone:** {emp.phone_number or 'N/A'}")
                    st.write(f"**DOB:** {emp.dob or 'N/A'}")
                    st.write(f"**Gender:** {emp.gender or 'N/A'}")
                
                with col2:
                    st.write(f"**Aadhaar:** {emp.aadhaar_number or 'N/A'}")
                    st.write(f"**PAN:** {emp.pan_number or 'N/A'}")
                    st.write(f"**Passport:** {emp.passport_number or 'N/A'}")
                    st.write(f"**Address:** {emp.address or 'N/A'}")
                
                st.write(f"**Added:** {emp.inserted_at[:10] if emp.inserted_at else 'N/A'}")
    elif 'results' in locals():
        st.info("No employees found matching your search criteria.")

# ============================================================================
# VIEW ALL EMPLOYEES PAGE
# ============================================================================
elif page == "📋 View All":
    st.subheader("All Employees")
    
    # Get all employees
    employees = query_employees(limit=1000)
    
    if employees:
        # Create dataframe
        df_data = []
        for emp in employees:
            df_data.append({
                "ID": emp.id,
                "Name": emp.full_name or "N/A",
                "Email": emp.email or "N/A",
                "Phone": emp.phone_number or "N/A",
                "Aadhaar": emp.aadhaar_number or "N/A",
                "PAN": emp.pan_number or "N/A",
                "Gender": emp.gender or "N/A",
                "Date Added": emp.inserted_at[:10] if emp.inserted_at else "N/A"
            })
        
        df = pd.DataFrame(df_data)
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Employees", len(employees))
        with col2:
            st.metric("With Aadhaar", len([e for e in employees if e.aadhaar_number]))
        with col3:
            st.metric("With PAN", len([e for e in employees if e.pan_number]))
        
        st.divider()
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No employees found. Start by adding a new employee.")

if __name__ == "__main__":
    pass
