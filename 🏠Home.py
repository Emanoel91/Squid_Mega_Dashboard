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

        # Silently fall back — the dashboard still works without logos.
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
    source just means fewer/no logos, not a broken dashboard.
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
# METRIC DISPLAY CONFIG (shared by table + charts)
# =========================================================

METRIC_COLUMNS = [
    "Inflow Volume",
    "Outflow Volume",
    "Internal Transfer Volume",
    "Total Transfer Volume",
    "Net Flow"
]

# Single bar color per metric. Net Flow is handled separately
# (colored per-bar by sign), so it has no fixed color here.
METRIC_COLORS = {
    "Inflow Volume": "#16A34A",
    "Outflow Volume": "#DC2626",
    "Internal Transfer Volume": "#EAB308",
    "Total Transfer Volume": "#2563EB",
}

POSITIVE_COLOR = "#16A34A"
NEGATIVE_COLOR = "#DC2626"
NEUTRAL_TEXT_COLOR = "#111111"


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
# CALCULATE METRICS + LOGOS
# =========================================================

chain_metrics = calculate_chain_metrics(
    route_df
)

chain_logo_map = get_chain_logo_map()


# =========================================================
# FULL METRICS TABLE
# =========================================================

st.markdown(
    "### 📋 All Chains — Full Metrics"
)

table_df = chain_metrics.copy()

# Look up logos BEFORE re-casing the chain name for display,
# since the logo lookup expects the original (lowercase) name.
table_df["Logo"] = table_df["Chain"].apply(
    lambda c: find_chain_logo(c, chain_logo_map)
)

table_df["Chain"] = table_df["Chain"].str.title()

table_df = table_df[
    [
        "Logo",
        "Chain",
        "Inflow Volume",
        "Outflow Volume",
        "Internal Transfer Volume",
        "Total Transfer Volume",
        "Net Flow"
    ]
]

table_df = table_df.sort_values(
    by="Total Transfer Volume",
    ascending=False
).reset_index(drop=True)


def _style_net_flow(value):

    if value > 0:
        return f"color: {POSITIVE_COLOR}; font-weight: 600;"

    elif value < 0:
        return f"color: {NEGATIVE_COLOR}; font-weight: 600;"

    return f"color: {NEUTRAL_TEXT_COLOR};"


def _style_neutral(value):

    return f"color: {NEUTRAL_TEXT_COLOR};"


table_styler = table_df.style.format(
    {
        "Inflow Volume": lambda v: format_volume(v),
        "Outflow Volume": lambda v: format_volume(v),
        "Internal Transfer Volume": lambda v: format_volume(v),
        "Total Transfer Volume": lambda v: format_volume(v),
        "Net Flow": lambda v: format_volume(v, show_sign=True),
    }
)

# pandas >= 2.1 renamed Styler.applymap to Styler.map (and pandas 3.x
# removed applymap entirely), so pick whichever this environment has.
_style_cell = getattr(
    table_styler,
    "map",
    None
) or table_styler.applymap

table_styler = _style_cell(
    _style_net_flow,
    subset=["Net Flow"]
)

_style_cell = getattr(
    table_styler,
    "map",
    None
) or table_styler.applymap

table_styler = _style_cell(
    _style_neutral,
    subset=[
        "Inflow Volume",
        "Outflow Volume",
        "Internal Transfer Volume",
        "Total Transfer Volume"
    ]
)

st.dataframe(
    table_styler,
    column_config={
        "Logo": st.column_config.ImageColumn(
            "Logo",
            width="small"
        ),
        "Chain": st.column_config.TextColumn(
            "Chain"
        )
    },
    hide_index=True,
    use_container_width=True
)


# =========================================================
# TOP 10 / BOTTOM 10 BAR CHART BUILDER
# =========================================================

def build_ranked_bar_chart(sub_df, metric, chart_title, logo_map, bar_color=None):
    """
    Vertical bar chart for a small set of chains (top or bottom N).
    Each x-axis position shows either the chain's logo (if found)
    or its name as text — never both.
    """

    chains = sub_df["Chain"].tolist()

    values = sub_df[metric].tolist()

    logos = [
        find_chain_logo(chain, logo_map)
        for chain in chains
    ]

    show_sign = (metric == "Net Flow")

    value_labels = [
        format_volume(v, show_sign=show_sign)
        for v in values
    ]

    hover_labels = [
        f"{chain.title()}<br>{metric}: {format_volume(v, show_sign=show_sign)}"
        for chain, v in zip(chains, values)
    ]

    if metric == "Net Flow":

        bar_colors = [
            POSITIVE_COLOR if v >= 0 else NEGATIVE_COLOR
            for v in values
        ]

    else:

        bar_colors = bar_color

    x_positions = list(
        range(len(chains))
    )

    fig = go.Figure(

        go.Bar(

            x=x_positions,

            y=values,

            marker=dict(
                color=bar_colors
            ),

            text=value_labels,

            textposition="outside",

            textfont=dict(
                size=11
            ),

            hovertext=hover_labels,

            hoverinfo="text"
        )
    )

    # Tick text is empty wherever a logo will be drawn instead.
    tick_text = [
        "" if logo else chain.title()
        for logo, chain in zip(logos, chains)
    ]

    fig.update_layout(

        title=dict(
            text=chart_title,
            x=0.5,
            xanchor="center",
            font=dict(size=13)
        ),

        xaxis=dict(
            tickmode="array",
            tickvals=x_positions,
            ticktext=tick_text,
            tickangle=0
        ),

        yaxis=dict(
            title=metric,
            tickformat="~s",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="#999999"
        ),

        height=380,

        margin=dict(
            l=40,
            r=20,
            t=50,
            b=90
        ),

        showlegend=False,

        plot_bgcolor="rgba(0,0,0,0)",

        paper_bgcolor="rgba(0,0,0,0)"
    )

    # Draw a logo image under each x position that has one.
    for x_pos, logo_url in zip(x_positions, logos):

        if not logo_url:
            continue

        fig.add_layout_image(

            dict(

                source=logo_url,

                xref="x",

                yref="paper",

                x=x_pos,

                y=-0.10,

                sizex=0.7,

                sizey=0.22,

                xanchor="center",

                yanchor="top",

                layer="above"
            )
        )

    return fig


def render_top_bottom_row(metric, chain_metrics_df, logo_map, n=10):

    bar_color = METRIC_COLORS.get(metric)

    top_df = chain_metrics_df.nlargest(
        n,
        metric
    ).reset_index(drop=True)

    bottom_df = chain_metrics_df.nsmallest(
        n,
        metric
    ).sort_values(
        metric,
        ascending=True
    ).reset_index(drop=True)

    col_top, col_bottom = st.columns(2)

    with col_top:

        fig_top = build_ranked_bar_chart(
            top_df,
            metric,
            f"Top 10 — {metric}",
            logo_map,
            bar_color=bar_color
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    with col_bottom:

        fig_bottom = build_ranked_bar_chart(
            bottom_df,
            metric,
            f"Bottom 10 — {metric}",
            logo_map,
            bar_color=bar_color
        )

        st.plotly_chart(
            fig_bottom,
            use_container_width=True
        )


# =========================================================
# TOP 10 / BOTTOM 10 ROWS — ONE ROW PER METRIC
# =========================================================

st.markdown("---")

st.markdown(
    "### 🏆 Top & Bottom Chains by Metric"
)

for metric in METRIC_COLUMNS:

    render_top_bottom_row(
        metric,
        chain_metrics,
        chain_logo_map,
        n=10
    )
