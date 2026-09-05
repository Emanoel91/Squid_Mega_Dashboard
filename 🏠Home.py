import streamlit as st

# --- Page Config: Tab Title & Icon ---
st.set_page_config(
    page_title="Squid",
    page_icon="https://axelarscan.io/logos/accounts/squid.svg",
    layout="wide"
)

# =========================================================
# BACKGROUND
# =========================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        180deg,
        #E2C6F1 0%,
        #D1A4E8 100%
    );
}
</style>
""", unsafe_allow_html=True)


# --- Title with Logo ---
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px;">
        <img src="https://axelarscan.io/logos/accounts/squid.svg" alt="Squid Logo" style="width:60px; height:60px;">
        <h1 style="margin: 0;">Squid</h1>
    </div>
    """,
    unsafe_allow_html=True
)


# --- Builder Info ---
st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://pbs.twimg.com/profile_images/2060406047391559681/sA9zPNKM_400x400.jpg" alt="Eman Raz" style="width:25px; height:25px; border-radius: 50%;">
            <span>Built by: <a href="https://x.com/0xeman_raz" target="_blank">Eman Raz</a></span>
        </div>
        
    </div>
    """,
    unsafe_allow_html=True
)


# --- Links with Logos ---
st.markdown(
    """
    <div style="font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://axelarscan.io/logos/accounts/squid.svg" alt="Squid" style="width:20px; height:20px;">
            <a href="https://www.squidrouter.com/" target="_blank">Squid Website</a>
        </div>
        
    </div>
    """,
    unsafe_allow_html=True
)
