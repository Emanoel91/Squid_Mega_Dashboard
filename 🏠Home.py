import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Squid",
    page_icon="https://axelarscan.io/logos/accounts/squid.svg",
    layout="wide"
)


# =========================================================
# TITLE WITH LOGO
# =========================================================

st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px;">
        <img
            src="https://axelarscan.io/logos/accounts/squid.svg"
            alt="Squid Logo"
            style="width:60px; height:60px;"
        >
        <h1 style="margin: 0;">Squid</h1>
    </div>
    """,
    unsafe_allow_html=True
)
