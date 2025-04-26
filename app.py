import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import pandas as pd

# Setup Google Sheets Connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Your sheet ID
sheet_id = "1Kr6-Yhpiz9g2u3AAo-VYVR27LI-ao5Opb1aIGLKJ5DY"

# Open tabs
teachers_sheet = client.open_by_key(sheet_id).worksheet("Teachers")
students_sheet = client.open_by_key(sheet_id).worksheet("Students")
categories_sheet = client.open_by_key(sheet_id).worksheet("Categories")
logs_sheet = client.open_by_key(sheet_id).worksheet("2425")

# Fetch teachers and students
teacher_list = teachers_sheet.col_values(1)
student_list = students_sheet.col_values(1)
category_list = categories_sheet.col_values(1)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Add New Entry", "View All Logs"])

# -----------------------
if page == "Add New Entry":
    st.title("📒 Add New Task/Event")
    
    with st.form("log_form", clear_on_submit=True):
        log_date = st.date_input("Date", value=date.today())
        title = st.text_input("Title (Optional)")
        description = st.text_area("Description")
        teachers = st.multiselect("Teacher (Optional)", teacher_list)
        students = st.multiselect("Student (Optional)", student_list)
        category = st.selectbox("Category", category_list)


        submitted = st.form_submit_button("Save Entry")

        if submitted:
            new_entry = [
                str(log_date),
                title,
                description,
                ", ".join(teachers),
                ", ".join(students),
                category
            ]
            logs_sheet.append_row(new_entry)
            st.success("✅ Entry saved to Google Sheets!")

# -----------------------
elif page == "View All Logs":
    st.title("📄 All Logs")

    # Fetch data
    data = logs_sheet.get_all_records()

    if data:
        df = pd.DataFrame(data)
        
        # Ensure the "Date" column is datetime
        df["Date"] = pd.to_datetime(df["Date"])

        # --- FILTERS ---
        st.sidebar.subheader("🔎 Filters")

        # Teacher Filter
        teacher_filter = st.sidebar.multiselect("Filter by Teacher", teacher_list)

        # Student Filter
        student_filter = st.sidebar.multiselect("Filter by Student", student_list)

        # Category Filter (based on available categories in the logs)
        available_categories = category_list
        category_filter = st.sidebar.multiselect("Filter by Category", available_categories)

        # Date Range Filter
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        date_range = st.sidebar.date_input("Filter by Date Range", [min_date, max_date])

        # --- APPLY FILTERS ---

        # Filter by teachers
        if teacher_filter:
            df = df[df["Teacher"].str.contains('|'.join(teacher_filter))]

        # Filter by students
        if student_filter:
            df = df[df["Student"].str.contains('|'.join(student_filter))]

        # Filter by category
        if category_filter:
            df = df[df["Category"].isin(category_filter)]

        # Filter by date range
        if isinstance(date_range, list) and len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

        # Show filtered results
        st.dataframe(df)

    else:
        st.info("No entries yet. Add your first one!")
