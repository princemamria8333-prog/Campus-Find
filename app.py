import streamlit as st
import database
import sqlite3
import hashlib
import secrets
from agent import find_matching_item

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="CampusFind AI",
    page_icon="🔎",
    layout="wide"
)

database.create_table()

AUTH_DB = "campusfind_users.db"


# ---------------- USER DATABASE ----------------

def create_users_table():
    with sqlite3.connect(AUTH_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()


def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "Please fill in every field."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if "@" not in email:
        return False, "Please enter a valid email address."

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        with sqlite3.connect(AUTH_DB) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]

            role = "Admin" if count == 0 else "Student"

            conn.execute("""
                INSERT INTO users
                (username, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, role))

        return True, f"Registration successful! Your role is {role}."

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."


def login_user(email, password):
    email = email.strip().lower()

    with sqlite3.connect(AUTH_DB) as conn:
        user = conn.execute("""
            SELECT id, username, email, password_hash, salt, role
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

    if not user:
        return None

    entered_hash = hash_password(password, user[4])

    if secrets.compare_digest(entered_hash, user[3]):
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[5]
        }

    return None


def get_all_users():
    with sqlite3.connect(AUTH_DB) as conn:
        return conn.execute("""
            SELECT id, username, email, role
            FROM users ORDER BY id
        """).fetchall()


create_users_table()


# ---------------- SESSION ----------------

if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- CUSTOM DESIGN ----------------

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f8fc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101c35, #142d50);
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] hr {
    border-color: #344968;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    background: linear-gradient(120deg, #102b50, #087fc5, #06b6d4);
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 8px 25px rgba(0, 80, 150, 0.15);
}

.hero h1 {
    color: white;
    font-size: 36px;
    font-weight: 800;
}

.hero p {
    color: #e4f6ff;
    font-size: 16px;
}

.metric-card {
    background: white;
    padding: 25px;
    border-radius: 16px;
    text-align: center;
    border: 1px solid #e4edf7;
    box-shadow: 0 4px 15px rgba(20, 50, 90, 0.06);
}

.metric-card h2 {
    color: #087fc5;
    font-size: 32px;
    font-weight: 800;
}

.metric-card p {
    color: #64748b;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(100deg, #087fc5, #06b6d4);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    padding: 10px 18px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #075985;
    color: white;
    border: none;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
    border-color: #dce8f5;
}

h1, h2, h3 {
    color: #102b50;
}

[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN / REGISTRATION ----------------

if st.session_state.user is None:

    st.markdown("""
    <div class="hero">
        <h1>🔎 CampusFind AI</h1>
        <p>Smart Campus Lost & Found Platform</p>
        <p>Find lost belongings. Reconnect people.</p>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    with login_tab:
        st.subheader("Welcome Back")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login_button:
                user = login_user(email, password)

                if user:
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with register_tab:
        st.subheader("Create Your Account")

        with st.form("register_form"):
            username = st.text_input("Full Name")
            new_email = st.text_input("Email Address")
            new_password = st.text_input(
                "Create Password",
                type="password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

            if register_button:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(
                        username,
                        new_email,
                        new_password
                    )

                    if success:
                        st.success(message)
                        st.info("Please go to Login and sign in.")
                    else:
                        st.error(message)

    st.caption("CampusFind AI | Secure Campus Lost & Found")
    st.stop()


# ---------------- LOGGED-IN USER ----------------

current_user = st.session_state.user

reports = database.get_reports()

# ---------------- SIDEBAR NAVIGATION ----------------

with st.sidebar:
    st.markdown("# 🔎 CampusFind AI")
    st.caption("Smart Campus Lost & Found")
    st.divider()

    st.write(f"👤 {current_user['username']}")
    st.write(f"Role: {current_user['role']}")

    st.divider()

    pages = [
        "🏠 Dashboard",
        "📝 Report Item",
        "🤖 AI Matching",
        "📋 All Reports"
    ]

    if current_user["role"] == "Admin":
        pages.append("⚙️ Admin Panel")

    page = st.radio(
        "Navigation",
        pages,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

    st.caption("Powered by Ollama")
    st.caption("CampusFind AI")


# ---------------- COMMON HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>CampusFind AI</h1>
    <p>Find lost belongings. Report found items.
    Reconnect people with their possessions.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- DASHBOARD ----------------

if page == "🏠 Dashboard":

    st.subheader("Dashboard")
    st.write(
        f"Welcome, {current_user['username']}!"
    )

    lost_count = sum(
        r["item_type"] == "Lost" for r in reports
    )

    found_count = sum(
        r["item_type"] == "Found" for r in reports
    )

    total_count = len(reports)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f'<div class="metric-card"><h2>{total_count}</h2><p>Total Reports</p></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="metric-card"><h2>{lost_count}</h2><p>Lost Items</p></div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f'<div class="metric-card"><h2>{found_count}</h2><p>Found Items</p></div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.subheader("Recent Reports")

    if reports:
        for report in reports[:5]:
            with st.container(border=True):
                st.markdown(f"**{report['item_name']}**")
                st.write(f"Type: {report['item_type']}")
                st.write(f"Location: {report['location']}")
                st.caption(f"Report ID: {report['id']}")

                if report["image"]:
                    st.image(report["image"], width=180)
    else:
        st.info("No reports yet.")


# ---------------- REPORT ITEM ----------------

elif page == "📝 Report Item":

    st.subheader("Submit an Item Report")

    with st.form("report_form", clear_on_submit=True):

        item_type = st.selectbox(
            "Report Type",
            ["Lost", "Found"]
        )

        item_name = st.text_input("Item Name")

        description = st.text_area(
            "Description"
        )

        location = st.text_input("Location")

        item_image = st.file_uploader(
            "Upload Item Photo (Optional)",
            type=["jpg", "jpeg", "png"]
        )

        submitted = st.form_submit_button(
            "Submit Report",
            use_container_width=True
        )

        if submitted:
            if not item_name.strip() or not description.strip() or not location.strip():
                st.error("Please fill in all required fields.")
            else:
                image_data = (
                    item_image.getvalue()
                    if item_image else None
                )

                database.add_report(
                    item_type,
                    item_name.strip(),
                    description.strip(),
                    location.strip(),
                    image_data
                )

                st.success("Report saved successfully!")
                st.rerun()


# ---------------- AI MATCHING ----------------

elif page == "🤖 AI Matching":

    st.subheader("AI-Powered Item Matching")

    lost_item = st.text_area(
        "Lost Item Description",
        placeholder="Describe the lost item..."
    )

    found_item = st.text_area(
        "Found Item Description",
        placeholder="Describe the found item..."
    )

    if st.button("🔍 Find Match", use_container_width=True):

        if not lost_item.strip() or not found_item.strip():
            st.warning("Enter both descriptions.")
        else:
            with st.spinner("AI is comparing items..."):

                result = find_matching_item(
                    lost_item,
                    found_item
                )

            if "error" in result:
                st.error(result["error"])
            else:
                score = result.get("match_score", 0)

                try:
                    score = max(
                        0,
                        min(100, int(float(score)))
                    )
                except (ValueError, TypeError):
                    score = 0

                st.divider()
                st.metric("AI Match Score", f"{score}%")
                st.progress(score / 100)

                st.subheader(
                    result.get("decision", "Result")
                )

                st.write(
                    result.get("reason", "No explanation.")
                )

                st.warning(
                    "AI matching is only a suggestion. "
                    "Ownership must be verified manually."
                )


# ---------------- ALL REPORTS ----------------

elif page == "📋 All Reports":

    st.subheader("All Campus Reports")

    if reports:

        filter_type = st.selectbox(
            "Filter Reports",
            ["All", "Lost", "Found"]
        )

        search = st.text_input(
            "Search by item, location or description"
        ).lower()

        filtered_reports = []

        for report in reports:

            matches_type = (
                filter_type == "All"
                or report["item_type"] == filter_type
            )

            searchable_text = (
                report["item_name"] + " "
                + report["location"] + " "
                + report["description"]
            ).lower()

            matches_search = search in searchable_text

            if matches_type and matches_search:
                filtered_reports.append(report)

        st.caption(
            f"{len(filtered_reports)} report(s) found"
        )

        for report in filtered_reports:

            with st.container(border=True):

                st.markdown(f"### {report['item_name']}")

                if report["item_type"] == "Lost":
                    st.error("LOST ITEM")
                else:
                    st.success("FOUND ITEM")

                st.write(
                    f"**Description:** {report['description']}"
                )

                st.write(
                    f"**Location:** {report['location']}"
                )

                st.caption(f"Report ID: {report['id']}")

                if report["image"]:
                    st.image(report["image"], width=220)

    else:
        st.info("No reports submitted yet.")


# ---------------- ADMIN PANEL ----------------

elif page == "⚙️ Admin Panel":

    if current_user["role"] != "Admin":
        st.error("Access denied.")
        st.stop()

    st.subheader("⚙️ Admin Panel")

    st.success("Welcome, Administrator!")

    users = get_all_users()

    st.metric("Registered Users", len(users))

    st.divider()
    st.subheader("Registered Accounts")

    if users:

        for user in users:

            with st.container(border=True):

                st.write(f"**{user[1]}**")
                st.write(f"Email: {user[2]}")

                if user[3] == "Admin":
                    st.success("ADMIN")
                else:
                    st.info("STUDENT")

    else:
        st.info("No users found.")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "CampusFind AI | Smart Campus Lost & Found Platform"
)