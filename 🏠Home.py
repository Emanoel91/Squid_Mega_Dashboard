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


# =========================================================
# API CONFIGURATION
# =========================================================

BASE_API_URL = (
    "https://www.squidrouter.com/api/analytics/routes"
)

# Public chain-logo sources (no API key required). CoinGecko is
# tried first since it covers the widest range of chains;
# LI.FI is used only to fill in anything CoinGecko is missing.
COINGECKO_PLATFORMS_URL = (
    "https://api.coingecko.com/api/v3/asset_platforms"
)

LIFI_CHAINS_URL = "https://li.quest/v1/chains"


# =========================================================
# LOAD DATA FROM API
# =========================================================

@st.cache_data(ttl=300)
def get_route_data(time_range):

    response = requests.get(
        BASE_API_URL,
        params={
            "range": time_range
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if "data" not in result:
        raise ValueError(
            "API response does not contain 'data'."
        )

    df = pd.DataFrame(result["data"])

    return df


# =========================================================
# LOAD CHAIN LOGOS
# =========================================================

# Manual aliases for chain names that are spelled/abbreviated
# differently between the Squid data and the logo sources below.
# Add more entries here any time a chain doesn't get a logo.
# Values should match a CoinGecko asset-platform id when possible
# (see https://api.coingecko.com/api/v3/asset_platforms).
CHAIN_NAME_ALIASES = {
    "bsc": "binance-smart-chain",
    "binance": "binance-smart-chain",
    "bnb": "binance-smart-chain",
    "bnb chain": "binance-smart-chain",
    "avax": "avalanche",
    "eth": "ethereum",
    "op": "optimistic-ethereum",
    "optimism": "optimistic-ethereum",
    "arb": "arbitrum-one",
    "arbitrum": "arbitrum-one",
    "poly": "polygon-pos",
    "matic": "polygon-pos",
    "polygon": "polygon-pos",
    "ftm": "fantom",
    "gnosis": "xdai",
    "xdai": "xdai",
}


def _fetch_coingecko_logo_map():

    logos = {}

    try:

        response = requests.get(
            COINGECKO_PLATFORMS_URL,
            timeout=15
        )

        response.raise_for_status()

        platforms = response.json()

        for platform in platforms:

            platform_id = str(
                platform.get("id", "")
            ).strip().lower()

            name = str(
                platform.get("name", "")
            ).strip().lower()

            shortname = str(
                platform.get("shortname", "")
            ).strip().lower()

            image = platform.get("image") or {}

            logo = (
                image.get("small")
                or image.get("thumb")
                or image.get("large")
                or ""
            )

            if not logo:
                continue

            if platform_id:
                logos[platform_id] = logo

            if name:
                logos[name] = logo

            if shortname:
                logos[shortname] = logo

    except Exception:

        # Silently fall back — the chart still works without logos.
        pass

    return logos


def _fetch_lifi_logo_map():

    logos = {}

    try:

        response = requests.get(
            LIFI_CHAINS_URL,
            timeout=15
        )

        response.raise_for_status()

        chains_data = response.json().get("chains", [])

        for chain in chains_data:

            name = str(
                chain.get("name", "")
            ).strip().lower()

            key = str(
                chain.get("key", "")
            ).strip().lower()

            logo = chain.get("logoURI", "")

            if not logo:
                continue

            if name:
                logos[name] = logo

            if key:
                logos[key] = logo

    except Exception:

        pass

    return logos


@st.cache_data(ttl=86400)
def get_chain_logo_map():
    """
    Builds a {chain_name_or_id_lowercase: logo_url} lookup table,
    combining CoinGecko (primary) with LI.FI (fallback for any
    chain CoinGecko doesn't have). Never raises — an unreachable
    source just means fewer/no logos, not a broken chart.
    """

    combined = _fetch_lifi_logo_map()

    # CoinGecko entries take priority over LI.FI on overlapping keys.
    combined.update(
        _fetch_coingecko_logo_map()
    )

    return combined


def find_chain_logo(chain_name, logo_map):
    """
    Looks up a logo URL for a given chain name.
    Returns "" (empty) when no confident match is found.
    """

    key = str(chain_name).strip().lower()

    if not key:
        return ""

    # 1) exact match
    if key in logo_map:
        return logo_map[key]

    # 2) known alias match
    alias = CHAIN_NAME_ALIASES.get(key)

    if alias and alias in logo_map:
        return logo_map[alias]

    # 3) loose match (handles minor naming differences,
    #    e.g. "polygon" vs "polygon-pos")
    for name_key, url in logo_map.items():

        if (
            name_key.startswith(key)
            or key.startswith(name_key)
        ):
            return url

    # Not found -> leave empty on purpose
    return ""


# =========================================================
# CALCULATE CHAIN METRICS
# =========================================================

def calculate_chain_metrics(df):

    df = df.copy()

    # -----------------------------------------------------
    # Clean data
    # -----------------------------------------------------

    df["volume"] = pd.to_numeric(
        df["volume"],
        errors="coerce"
    ).fillna(0)

    df["source"] = (
        df["source"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df["destination"] = (
        df["destination"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # -----------------------------------------------------
    # Internal Transfer Volume
    # source == destination
    # -----------------------------------------------------

    internal = (
        df[
            df["source"] == df["destination"]
        ]
        .groupby("source")["volume"]
        .sum()
        .rename("Internal Transfer Volume")
    )

    # -----------------------------------------------------
    # Inflow Volume
    # other chain -> chain
    # -----------------------------------------------------

    inflow = (
        df[
            df["source"] != df["destination"]
        ]
        .groupby("destination")["volume"]
        .sum()
        .rename("Inflow Volume")
    )

    # -----------------------------------------------------
    # Outflow Volume
    # chain -> other chain
    # -----------------------------------------------------

    outflow = (
        df[
            df["source"] != df["destination"]
        ]
        .groupby("source")["volume"]
        .sum()
        .rename("Outflow Volume")
    )

    # -----------------------------------------------------
    # Get all chains
    # -----------------------------------------------------

    chains = sorted(
        set(df["source"])
        |
        set(df["destination"])
    )

    metrics = pd.DataFrame(
        index=chains
    )

    metrics = metrics.join(inflow)
    metrics = metrics.join(outflow)
    metrics = metrics.join(internal)

    metrics = metrics.fillna(0)

    # -----------------------------------------------------
    # Total Transfer Volume
    # -----------------------------------------------------

    metrics["Total Transfer Volume"] = (
        metrics["Inflow Volume"]
        +
        metrics["Outflow Volume"]
        +
        metrics["Internal Transfer Volume"]
    )

    # -----------------------------------------------------
    # Net Flow
    # -----------------------------------------------------

    metrics["Net Flow"] = (
        metrics["Inflow Volume"]
        -
        metrics["Outflow Volume"]
    )

    metrics.index.name = "Chain"

    metrics = metrics.reset_index()

    return metrics


# =========================================================
# NUMBER FORMATTER
# =========================================================

def format_volume(value, show_sign=False):

    if pd.isna(value):
        value = 0

    sign = ""

    if show_sign:

        if value > 0:
            sign = "+"

        elif value < 0:
            sign = "-"

    value = abs(value)

    if value >= 1_000_000_000:

        formatted = (
            f"${value / 1_000_000_000:.2f}B"
        )

    elif value >= 1_000_000:

        formatted = (
            f"${value / 1_000_000:.2f}M"
        )

    elif value >= 1_000:

        formatted = (
            f"${value / 1_000:.2f}K"
        )

    else:

        formatted = (
            f"${value:,.0f}"
        )

    return sign + formatted


# =========================================================
# TIME RANGE FILTER
# =========================================================

st.markdown("---")

st.markdown(
    "### 📅 Time Range"
)

time_range = st.selectbox(
    "Select time range",
    options=[
        "7d",
        "30d",
        "90d",
        "all"
    ],
    index=1,
    label_visibility="collapsed"
)


# =========================================================
# LOAD API DATA
# =========================================================

try:

    route_df = get_route_data(
        time_range
    )

except requests.exceptions.RequestException as e:

    st.error(
        f"Unable to connect to Squid API: {e}"
    )

    st.stop()

except Exception as e:

    st.error(
        f"Unable to process API data: {e}"
    )

    st.stop()


# =========================================================
# CALCULATE METRICS
# =========================================================

chain_metrics = calculate_chain_metrics(
    route_df
)

chain_logo_map = get_chain_logo_map()


# =========================================================
# METRIC SELECTION
# =========================================================

st.markdown(
    "### 📊 Chain Transfer Analytics"
)

available_metrics = [

    "Inflow Volume",

    "Outflow Volume",

    "Internal Transfer Volume",

    "Total Transfer Volume",

    "Net Flow"
]


selected_metrics = st.multiselect(

    "Select metrics to display",

    options=available_metrics,

    default=[
        "Inflow Volume",
        "Outflow Volume"
    ],

    label_visibility="collapsed"
)


if not selected_metrics:

    st.info(
        "Please select at least one metric."
    )

    st.stop()


# =========================================================
# SORTING
# =========================================================

sort_metric = st.selectbox(

    "Sort chains by",

    options=available_metrics,

    index=3
)


chain_metrics = chain_metrics.sort_values(

    by=sort_metric,

    ascending=False
)


# =========================================================
# COLORS
# =========================================================

metric_colors = {

    "Inflow Volume":
        "#16A34A",

    "Outflow Volume":
        "#DC2626",

    "Internal Transfer Volume":
        "#EAB308",

    "Total Transfer Volume":
        "#2563EB",

    "Net Flow":
        "#111111"
}


# =========================================================
# CREATE HORIZONTAL BAR CHART
# =========================================================

fig = go.Figure()


for metric in selected_metrics:

    # Original values
    original_values = (
        chain_metrics[metric]
        .copy()
    )

    # -----------------------------------------------------
    # Outflow displayed on the negative side
    # -----------------------------------------------------

    if metric == "Outflow Volume":

        plot_values = -original_values

    else:

        plot_values = original_values

    # -----------------------------------------------------
    # Labels displayed on bars
    # -----------------------------------------------------

    if metric == "Net Flow":

        labels = [

            format_volume(
                value,
                show_sign=True
            )

            for value in original_values

        ]

    else:

        labels = [

            format_volume(
                value
            )

            for value in original_values

        ]

    # -----------------------------------------------------
    # Add trace
    # -----------------------------------------------------

    fig.add_trace(

        go.Bar(

            y=chain_metrics["Chain"],

            x=plot_values,

            name=metric,

            orientation="h",

            marker=dict(

                color=metric_colors[
                    metric
                ]

            ),

            text=labels,

            textposition="auto",

            textfont=dict(
                size=11
            ),

            customdata=original_values,

            hovertemplate=(

                "<b>%{y}</b><br>"

                + metric

                + ": $%{customdata:,.2f}"

                + "<extra></extra>"
            )
        )
    )


# =========================================================
# CHART LAYOUT
# =========================================================

# Extra left margin to make room for the chain logos that get
# drawn to the left of the y-axis tick labels below.
LEFT_MARGIN_PX = 170

fig.update_layout(

    barmode="group",

    height=max(
        600,
        len(chain_metrics) * 32
    ),

    title=dict(

        text=(
            f"Chain Transfer Volume — "
            f"{time_range.upper()}"
        ),

        x=0.5,

        xanchor="center"
    ),

    xaxis=dict(

        title="Volume",

        zeroline=True,

        zerolinewidth=2,

        zerolinecolor="#333333",

        tickformat="~s",

        showgrid=True,

        gridcolor="rgba(0,0,0,0.08)"
    ),

    yaxis=dict(

        title="",

        categoryorder="array",

        categoryarray=(
            chain_metrics[
                "Chain"
            ].tolist()
        ),

        autorange="reversed",

        # Push tick labels away from the axis line so the
        # logo images (placed further left) don't overlap them.
        ticksuffix="   "
    ),

    legend=dict(

        orientation="h",

        yanchor="bottom",

        y=1.02,

        xanchor="center",

        x=0.5
    ),

    plot_bgcolor="rgba(0,0,0,0)",

    paper_bgcolor="rgba(0,0,0,0)",

    margin=dict(

        l=LEFT_MARGIN_PX,

        r=20,

        t=100,

        b=40
    ),

    hovermode="closest"
)


# =========================================================
# ADD CHAIN LOGOS NEXT TO CHAIN NAMES
# =========================================================

# Plotly can't embed images directly inside axis tick labels,
# so each logo is drawn as a small floating image anchored to
# its chain's row on the y-axis (yref="y") and positioned in
# the left margin using paper coordinates (xref="paper").

LOGO_SIZE_FRACTION = 0.035   # width, as a fraction of plot width
LOGO_X_POSITION = -0.02      # just left of the plot area (paper coords)

for chain_name in chain_metrics["Chain"]:

    logo_url = find_chain_logo(
        chain_name,
        chain_logo_map
    )

    if not logo_url:
        # No matching logo found -> leave it empty, as requested
        continue

    fig.add_layout_image(

        dict(

            source=logo_url,

            xref="paper",

            yref="y",

            x=LOGO_X_POSITION,

            y=chain_name,

            sizex=LOGO_SIZE_FRACTION,

            sizey=0.8,

            xanchor="right",

            yanchor="middle",

            layer="above"
        )
    )


# =========================================================
# DISPLAY CHART
# =========================================================

st.plotly_chart(

    fig,

    use_container_width=True
)
