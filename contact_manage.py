import streamlit as st
import smtplib
import sqlite3
from datetime import datetime
from email.message import EmailMessage

# Database connection
def connectdb():
    return sqlite3.connect("myydb.db")

EMAIL_ADDRESS = "email_my"
EMAIL_PASSWORD = "password_my"



st.title("💡RemindConnect – Never Miss a Special Day!")
st.markdown("Stay Organized, Stay Connected, Stay Reminded! 🎉")
st.markdown("""
    <style>
    /* Sidebar background and padding */
    [data-testid="stSidebar"] {
        background-color: #ffdde1; /* Light pink background */
        padding:50px;
    }
    
    

    /* Sidebar Radio Buttons */
    div[data-testid="stSidebar"] div[role="radiogroup"] label {
        display: block;
        background: linear-gradient(135deg, #ff758c, #ff7eb3); /* Gradient background */
        color: white;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 10px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        transition: 0.3s ease-in-out;
        cursor: pointer;
    }

    /* Selected Option */
    div[data-testid="stSidebar"] div[role="radiogroup"] label[data-testid="stWidgetLabel"] {
        background: linear-gradient(135deg, #ff4b4b, #ff758c);
        font-weight: bold;
        transform: scale(1.1);
    }
    </style>
""", unsafe_allow_html=True)
# Sidebar Navigation
st.sidebar.header("Navigation")
options = ["Add Contact", "View Contacts", "Delete Contact", "Update Contact", "Search Contact", "Upcoming Events"]
selected_option = st.sidebar.radio("Choose an Option:", options)



# Database Table Creation
def createTable():
    with connectdb() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS person (
                name TEXT,
                Email TEXT,
                contacts INTEGER PRIMARY KEY,
                date_of_birth TEXT,
                anniversary_date TEXT
            )
        """)
        conn.commit()

createTable()

# Functions for Contact Management
def addRecord(data):
    with connectdb() as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO person (name, Email, contacts, date_of_birth, anniversary_date) VALUES (?, ?, ?, ?, ?)", data)
            conn.commit()
            st.success("✅ Contact stored successfully!")
        except sqlite3.IntegrityError:
            st.error("⚠️ Contact already stored!")

def View():
    with connectdb() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM person")
        data = cur.fetchall()
    if data:
        st.write("### 📋 Contact List")
        st.table(data)
    else:
        st.warning("⚠️ No contacts found!")

def delete_person(contacts):
    with connectdb() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM person WHERE contacts = ?", (contacts,))
        conn.commit()
        st.success("✅ Contact deleted successfully!")

def search_contacts(contacts):
    with connectdb() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM person WHERE contacts = ?", (contacts,))
        return cur.fetchone()

def reset_contacts(contacts, new_contacts):
    with connectdb() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE person SET contacts = ? WHERE contacts = ?", (new_contacts, contacts))
        conn.commit()
        st.success("✅ Contact updated successfully!")

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def check_upcoming_events():
    today = datetime.today().strftime('%Y-%m-%d')
    
    with connectdb() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, Email, date_of_birth, anniversary_date FROM person")
        contacts = cur.fetchall()
    
    for contact in contacts:
        name, email, dob, anniversary = contact
        if dob and dob[-5:] == today[-5:]:
            st.warning(f"🎉 It's {name}'s Birthday today!")
            send_email(email, "Happy Birthday!", f"Dear {name},\n\nWishing you a joyous birthday! 🎉")
        
        if anniversary and anniversary[-5:] == today[-5:]:
            st.info(f"💍 It's {name}'s Anniversary today!")
            send_email(email, "Happy Anniversary!", f"Dear {name},\n\nWishing you a wonderful anniversary! 💖")

# Page Logic
if selected_option == 'Add Contact':
    st.header("➕ Add a New Contact")
    name = st.text_input("Enter Name")
    email = st.text_input("Enter Email")
    contacts = st.number_input("Enter Contact Number", format="%0.0f")
    date_of_birth = st.date_input("Select Date of Birth")
    anniversary_date = st.date_input("Select Anniversary Date (if applicable)")
    
    if st.button("Add Contact"):
        addRecord((name, email, contacts, date_of_birth, anniversary_date))

elif selected_option == 'View Contacts':
    View()

elif selected_option == 'Delete Contact':
    st.header("❌ Delete a Contact")
    contacts = st.number_input("Enter Contact Number to Delete", format="%0.0f")
    if st.button("Delete Contact"):
        delete_person(contacts)

elif selected_option == 'Update Contact':
    st.header("🔄 Update Contact")
    contacts = st.number_input("Enter Contact Number", format="%0.0f")
    new_contacts = st.number_input("Enter New Contact Number", format="%0.0f")
    if st.button("Update Contact"):
        reset_contacts(contacts, new_contacts)

elif selected_option == 'Search Contact':
    st.header("🔍 Search for a Contact")
    contacts = st.number_input("Enter Contact Number", format="%0.0f")
    if st.button("Search Contact"):
        result = search_contacts(contacts)
        if result:
            st.success(f"✅ Contact Found: {result}")
        else:
            st.error("⚠️ No such contact stored!")

elif selected_option == 'Upcoming Events':
    check_upcoming_events()
