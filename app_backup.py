import streamlit as st
from agent import find_matching_item

# Page settings
st.set_page_config(
    page_title="CampusFind AI",
    page_icon="🔎",
    layout="wide"
)

# Store reports during the session
if "reports" not in st.session_state:
    st.session_state.reports = []

# Website heading
st.title("🔎 CampusFind AI")
st.subheader("Smart Campus Lost & Found Assistant")
st.write(
    "Lost something on campus? Found something? "
    "Let AI help connect the reports."
)

st.divider()

# Three sections
report_tab, matching_tab, reports_tab = st.tabs(
    ["📝 Report Item", "🤖 AI Matching", "📋 All Reports"]
)

# TAB 1: Report an item
with report_tab:
    st.header("Report a Lost or Found Item")

    with st.form("report_form"):
        item_type = st.selectbox(
            "Report type",
            ["Lost", "Found"]
        )

        item_name = st.text_input(
            "Item name",
            placeholder="Example: Black Boat earbuds"
        )

        description = st.text_area(
            "Item description",
            placeholder="Describe the item, colour, brand, etc."
        )

        location = st.text_input(
            "Location",
            placeholder="Example: College library"
        )

        submitted = st.form_submit_button("Submit Report")

        if submitted:
            if item_name.strip() and description.strip() and location.strip():
                st.session_state.reports.append({
                    "type": item_type,
                    "name": item_name,
                    "description": description,
                    "location": location
                })
                st.success("Your report has been submitted!")
            else:
                st.warning("Please fill in all the fields.")

# TAB 2: AI matching
with matching_tab:
    st.header("Find a Possible Match")
    st.write("Enter details of the lost and found items.")

    lost_item = st.text_area(
        "Lost item details",
        placeholder="Black Boat earbuds lost near the library"
    )

    found_item = st.text_area(
        "Found item details",
        placeholder="Black wireless earbuds found outside the library"
    )

    if st.button("🤖 Find Match", type="primary"):
        if lost_item.strip() and found_item.strip():
            with st.spinner("AI is comparing both reports..."):
                result = find_matching_item(lost_item, found_item)

            if "error" in result:
                st.error(result["error"])
            else:
                score = result.get("match_score", 0)
                st.metric("AI Match Score", f"{score}%")
                st.subheader(result.get("decision", "Result"))
                st.write("**Reason:**")
                st.write(result.get("reason", "No explanation provided."))

                st.info(
                    "This is an AI-generated suggestion. "
                    "Ownership must be verified manually."
                )
        else:
            st.warning("Please enter both item descriptions.")

# TAB 3: All reports
with reports_tab:
    st.header("Campus Lost & Found Reports")

    if st.session_state.reports:
        for number, report in enumerate(
            st.session_state.reports, start=1
        ):
            with st.container(border=True):
                st.subheader(f"{number}. {report['name']}")
                st.write(f"**Type:** {report['type']}")
                st.write(f"**Description:** {report['description']}")
                st.write(f"**Location:** {report['location']}")
    else:
        st.info("No reports submitted yet. Be the first!")