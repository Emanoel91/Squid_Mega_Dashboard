import streamlit as st

# --- Page Config: Tab Title & Icon ---
st.set_page_config(
    page_title="Squid",
    page_icon="https://axelarscan.io/logos/accounts/squid.svg",
    layout="wide"
)

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
            <img src="https://pbs.twimg.com/profile_images/1841479747332608000/bindDGZQ_400x400.jpg" alt="Eman Raz" style="width:25px; height:25px; border-radius: 50%;">
            <span>Built by: <a href="https://x.com/0xeman_raz" target="_blank">Eman Raz</a></span>
        </div>
        
    </div>
    """,
    unsafe_allow_html=True
)

# --- Info Box ---
st.markdown(
    """
    <div style="background-color: #e6fa36; padding: 15px; border-radius: 10px; border: 1px solid #ffd700;">
        Squid Router is a cross-chain liquidity and messaging protocol built on the Axelar Network, designed to facilitate seamless token swaps, 
        transfers, and smart contract interactions across multiple blockchains. 
        Squid enables users to swap any token across over 90 blockchains (e.g., Ethereum, Polygon, Arbitrum, Solana, Bitcoin) in a single click.
    </div>
    """,
    unsafe_allow_html=True
)

# --- Reference and Rebuild Info ---
st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://pbs.twimg.com/profile_images/1841479747332608000/bindDGZQ_400x400.jpg" alt="Eman Raz" style="width:25px; height:25px; border-radius: 50%;">
            <span>Rebuilt by: <a href="https://x.com/0xeman_raz" target="_blank">Eman Raz</a></span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://pbs.twimg.com/profile_images/1856738793325268992/OouKI10c_400x400.jpg" alt="Flipside" style="width:25px; height:25px; border-radius: 50%;">
            <span>Data Powered by: <a href="https://flipsidecrypto.xyz/home/" target="_blank">Flipside</a></span>
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
            <img src="https://axelarscan.io/logos/logo.png" alt="Axelar" style="width:20px; height:20px;">
            <a href="https://www.axelar.network/" target="_blank">https://www.axelar.network/</a>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://axelarscan.io/logos/accounts/squid.svg" alt="Squid" style="width:20px; height:20px;">
            <a href="https://www.squidrouter.com/" target="_blank">https://www.squidrouter.com/</a>
        </div>
        
    </div>
    """,
    unsafe_allow_html=True
)
