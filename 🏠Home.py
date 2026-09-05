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
# BUILDER INFO
# =========================================================

st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">

            <img
                src="https://pbs.twimg.com/profile_images/2060406047391559681/sA9zPNKM_400x400.jpg"
                alt="Eman Raz"
                style="
                    width:25px;
                    height:25px;
                    border-radius:50%;
                "
            >

            <span>
                Built by:
                <a
                    href="https://x.com/0xeman_raz"
                    target="_blank"
                >
                    Eman Raz
                </a>
            </span>

        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SQUID WEBSITE
# =========================================================

st.markdown(
    """
    <div style="font-size: 16px;">

        <div style="
            display: flex;
            align-items: center;
            gap: 10px;
        ">

            <img
                src="https://axelarscan.io/logos/accounts/squid.svg"
                alt="Squid"
                style="width:20px; height:20px;"
            >

            <a
                href="https://www.squidrouter.com/"
                target="_blank"
            >
                Squid Website
            </a>

        </div>

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
    # Internal Transfers
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
    # Inflow
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
    # Outflow
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
# CREATE CHART
# =========================================================

fig = go.Figure()


for metric in selected_metrics:

    # Original values
    original_values = (
        chain_metrics[metric]
        .copy()
    )

    # -----------------------------------------------------
    # Plot values
    # -----------------------------------------------------

    if metric == "Outflow Volume":

        # Outflow goes to LEFT
        plot_values = -original_values

    else:

        plot_values = original_values

    # -----------------------------------------------------
    # Labels
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

        autorange="reversed"
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

        l=20,

        r=20,

        t=100,

        b=40
    ),

    hovermode="closest"
)


# =========================================================
# DISPLAY CHART
# =========================================================

st.plotly_chart(

    fig,

    use_container_width=True
)
