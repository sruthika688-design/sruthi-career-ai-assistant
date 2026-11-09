import datetime
import random
import string
import sqlite3
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="College Grievance Redressal Portal",
    page_icon="🎓",
    layout="wide",
)

# Custom CSS for Mobile-Friendly Blue and White Theme
st.markdown(
    """
    <style>
    .main {
        background-color: #F8FAFC;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Database Initialization
def init_db():
  conn = sqlite3.connect("grievances.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            tracking_id TEXT PRIMARY KEY,
            student_name TEXT,
            department TEXT,
            category TEXT,
            description TEXT,
            status TEXT,
            date TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


# Generate Unique Tracking ID
def generate_tracking_id():
  letters = string.ascii_uppercase
  digits = "".join(random.choices(string.digits, k=4))
  return f'GRV-{"".join(random.choices(letters, k=3))}-{digits}'


# Sidebar Navigation
st.sidebar.title("🎓 Grievance Portal")
menu = st.sidebar.radio(
    "Navigation", ["Home", "Submit Complaint", "Track Complaint", "Admin Login"]
)

# 1. Home Page
if menu == "Home":
  st.title("🎓 College Grievance Redressal System")
  st.write(
      "Welcome to the official student grievance redressal platform."
      " Transparency, accountability, and quick resolutions are our top"
      " priorities."
  )

  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        """<div class="metric-card"><h3>🔒 Secure & Private</h3><p>Your"
        " submissions are stored securely.</p></div>""",
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        """<div class="metric-card"><h3>⚡ Instant ID</h3><p>Get a unique"
        " tracking code instantly.</p></div>""",
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        """<div class="metric-card"><h3>🤝 Active Tracking</h3><p>Monitor"
        " status updates in real-time.</p></div>""",
        unsafe_allow_html=True,
    )

  st.markdown("---")
  st.subheader("How It Works")
  st.markdown("1. **Submit**: Fill out the complaint form with your details.")
  st.markdown("2. **Save ID**: Note down your automatically generated ID.")
  st.markdown("3. **Track**: Check your grievance status anytime.")

# 2. Student Complaint Submission Form
elif menu == "Submit Complaint":
  st.title("📝 Submit a Complaint")
  st.write("Please provide complete details regarding your issue below.")

  with st.form("complaint_form"):
    student_name = st.text_input("Student Name")
    department = st.selectbox(
        "Department",
        [
            "Computer Science & Engineering",
            "Electronics & Communication",
            "Mechanical Engineering",
            "Civil Engineering",
            "Information Technology",
            "Electrical Engineering",
            "Management Studies",
            "Science & Humanities",
        ],
    )
    category = st.selectbox(
        "Complaint Category",
        [
            "Academic",
            "Infrastructure / Facilities",
            "Hostel & Mess",
            "Examination / Results",
            "Ragging / Harassment",
            "Library",
            "Other",
        ],
    )
    description = st.text_area("Complaint Description")

    submit_btn = st.form_submit_button("Submit Complaint")

    if submit_btn:
      if student_name.strip() and description.strip():
        tracking_id = generate_tracking_id()
        status = "Pending"
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("grievances.db")
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT INTO complaints (tracking_id, student_name, department, category, description, status, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tracking_id,
                student_name,
                department,
                category,
                description,
                status,
                date,
            ),
        )
        conn.commit()
        conn.close()

        st.success("Complaint registered successfully!")
        st.info(f"Your Unique Tracking ID is: **{tracking_id}**")
        st.warning(
            "Please save this tracking ID to check your complaint status later."
        )
      else:
        st.error("Please fill in all required fields.")

# 3. Complaint Status Tracking
elif menu == "Track Complaint":
  st.title("🔍 Track Complaint Status")
  tracking_id_input = st.text_input("Enter Your Unique Tracking ID").strip()

  if st.button("Check Status"):
    if tracking_id_input:
      conn = sqlite3.connect("grievances.db")
      cursor = conn.cursor()
      cursor.execute(
          "SELECT tracking_id, student_name, department, category, description,"
          " status, date FROM complaints WHERE tracking_id = ?",
          (tracking_id_input,),
      )
      row = cursor.fetchone()
      conn.close()

      if row:
        st.success("Complaint Found!")
        st.write(f"**Tracking ID:** {row[0]}")
        st.write(f"**Student Name:** {row[1]}")
        st.write(f"**Department:** {row[2]}")
        st.write(f"**Category:** {row[3]}")
        st.write(f"**Description:** {row[4]}")
        st.write(f"**Submitted On:** {row[6]}")

        status = row[5]
        if status == "Pending":
          st.markdown(f"**Status:** 🟡 **{status}**")
        elif status == "In Progress":
          st.markdown(f"**Status:** 🔵 **{status}**")
        else:
          st.markdown(f"**Status:** 🟢 **{status}**")
      else:
        st.error("No complaint found with this Tracking ID.")
    else:
      st.error("Please enter a valid tracking ID.")

# 4. Admin Login & Dashboard
elif menu == "Admin Login":
  st.title("🔐 Admin Portal")

  if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

  if not st.session_state.admin_logged_in:
    with st.form("login_form"):
      username = st.text_input("Username")
      password = st.text_input("Password", type="password")
      login_btn = st.form_submit_button("Login")

      if login_btn:
        if username == "admin" and password == "admin123":
          st.session_state.admin_logged_in = True
          st.rerun()
        else:
          st.error("Invalid Username or Password (Default: admin / admin123)")
  else:
    if st.button("Logout"):
      st.session_state.admin_logged_in = False
      st.rerun()

    st.markdown("---")
    st.header("📊 Admin Dashboard")

    conn = sqlite3.connect("grievances.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tracking_id, student_name, department, category, description,"
        " status, date FROM complaints"
    )
    rows = cursor.fetchall()
    conn.close()

    total = len(rows)
    pending = sum(1 for r in rows if r[5] == "Pending")
    resolved = sum(1 for r in rows if r[5] == "Resolved")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Complaints", total)
    col2.metric("Pending Complaints", pending)
    col3.metric("Resolved Complaints", resolved)

    st.markdown("---")
    st.subheader("All Registered Complaints")

    if rows:
      df = pd.DataFrame(
          rows,
          columns=[
              "Tracking ID",
              "Student Name",
              "Department",
              "Category",
              "Description",
              "Status",
              "Date",
          ],
      )
      st.dataframe(df, use_container_width=True)

      st.markdown("### Update Complaint Status")
      tracking_ids = [r[0] for r in rows]
      selected_id = st.selectbox("Select Tracking ID to Update", tracking_ids)

      current_row = next(r for r in rows if r[0] == selected_id)
      new_status = st.selectbox(
          "Update Status",
          ["Pending", "In Progress", "Resolved"],
          index=["Pending", "In Progress", "Resolved"].index(current_row[5]),
      )

      if st.button("Save Status"):
        conn = sqlite3.connect("grievances.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE complaints SET status = ? WHERE tracking_id = ?",
            (new_status, selected_id),
        )
        conn.commit()
        conn.close()
        st.success(f"Tracking ID {selected_id} updated to {new_status}!")
        st.rerun()
    else:
      st.info("No complaints submitted yet.")
        
