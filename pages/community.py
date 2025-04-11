import streamlit as st

# Set page config
st.set_page_config(page_title="AgroSphere Community", layout="wide")

# State-city data
states = {
    "Maharashtra": ["Nashik", "Pune", "Nagpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Patiala"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi"]
}

# Init post list
if "posts" not in st.session_state:
    st.session_state.posts = []

# Page Title & Intro
with st.container():
    st.title("👥 AgroSphere Community")
    st.markdown("""
    Welcome to the **AgroSphere Community Forum** – a local help network for farmers.

    Use this space to:
    - Request tools, labor, or help
    - Offer equipment or services
    - Collaborate with other farmers in your area
    """)
    st.divider()

# ============================
# 🌍 Location Selectors
# ============================
with st.container():
    st.markdown("### 📍 Select Your Location for This Post")
    col1, col2 = st.columns(2)
    with col1:
        selected_state = st.selectbox("Select State", list(states.keys()))
    with col2:
        selected_city = st.selectbox("Select City", states[selected_state])
    st.divider()

# ============================
# 📬 Post Form
# ============================
with st.expander("📩 Post a Request or Offer", expanded=True):
    st.markdown("### 📝 Share Your Post")
    with st.form(key="post_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Your Name")
        with col2:
            phone = st.text_input("📞 Phone Number")
        message = st.text_area("📝 What do you need or offer? (e.g., 'Need tractor for 2 days')")

        submit = st.form_submit_button("📤 Share Post")

        if submit:
            if name.strip() and message.strip():
                st.session_state.posts.append({
                    "name": name,
                    "phone": phone,
                    "city": selected_city,
                    "state": selected_state,
                    "message": message
                })
                st.success("✅ Your post has been shared with the community.")
            else:
                st.error("⚠️ Please enter both your name and message.")

st.divider()

# ============================
# 🧾 Community Feed
# ============================
with st.container():
    st.subheader("📢 Latest Community Posts")
    if st.session_state.posts:
        for post in reversed(st.session_state.posts):
            with st.container():
                st.markdown(f"**🧑‍🌾 {post['name']}** from 📍 *{post['city']}, {post['state']}*")
                st.markdown(f"📣 _{post['message']}_")
                if post['phone']:
                    st.markdown(f"📞 Contact: `{post['phone']}`")
                st.markdown("---")
    else:
        st.info("No posts yet. Be the first to help or ask in your local farming network.")

