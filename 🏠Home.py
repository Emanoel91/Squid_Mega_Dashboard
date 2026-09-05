import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go


# =========================================================
# API
# =========================================================

BASE_API_URL = "https://www.squidrouter.com/api/analytics/routes"


# =========================================================
# GET ROUTE DATA
# =========================================================

@st.cache_data(ttl=300)
def get_route_data(time_range):

    url = BASE_API_URL

    params = {
        "range": time_range
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return pd.DataFrame(result["data"])


# =========================================================
# AGGREGATE CHAIN METRICS
# =========================================================

def calculate_chain_metrics(df):

    # Make sure volume is numeric
    df["volume"] = pd.to_numeric(
        df["volume"],
        errors="coerce"
    ).fillna(0)

    # Normalize chain names
    df["source"] = df["source"].astype(str).str.lower()
    df["destination"] = df["destination"].astype(str).str.lower()

    # -----------------------------------------------------
    # Internal transfers
    # source == destination
    # -----------------------------------------------------

    internal = (
        df[df["source"] == df["destination"]]
        .groupby("source")["volume"]
        .sum()
        .rename("Internal Transfer Volume")
    )

    # -----------------------------------------------------
    # Inflow
    # destination receives funds from another chain
    # -----------------------------------------------------

    inflow = (
        df[df["source"] != df["destination"]]
        .groupby("destination")["volume"]
        .sum()
        .rename("Inflow Volume")
    )

    # -----------------------------------------------------
    # Outflow
    # source sends funds to another chain
    # -----------------------------------------------------

    outflow = (
        df[df["source"] != df["destination"]]
        .groupby("source")["volume"]
        .sum()
        .rename("Outflow Volume")
    )

    # -----------------------------------------------------
    # All chains
    # -----------------------------------------------------

    chains = sorted(
        set(df["source"]).union(
            set(df["destination"])
        )
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
        + metrics["Outflow Volume"]
        + metrics["Internal Transfer Volume"]
    )

    # -----------------------------------------------------
    # Net Flow
    # -----------------------------------------------------

    metrics["Net Flow"] = (
        metrics["Inflow Volume"]
        - metrics["Outflow Volume"]
    )

    metrics.index.name = "Chain"

    metrics = metrics.reset_index()

    return metrics


# =========================================================
# TIME FILTER
# =========================================================

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
# LOAD DATA
# =========================================================

try:

    route_df = get_route_data(time_range)

except Exception as e:

    st.error(
        f"Unable to load Squid Analytics API: {e}"
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
    ]
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
        "#16A34A",      # Green

    "Outflow Volume":
        "#DC2626",      # Red

    "Internal Transfer Volume":
        "#EAB308",      # Strong Yellow

    "Total Transfer Volume":
        "#2563EB",      # Blue

    "Net Flow":
        "#111111"       # Black
}


# =========================================================
# CREATE HORIZONTAL BAR CHART
# =========================================================

fig = go.Figure()


for metric in selected_metrics:

    values = chain_metrics[metric].copy()

    # -----------------------------------------------------
    # Outflow is displayed as negative
    # This creates the left/right symmetry
    # -----------------------------------------------------

    if metric == "Outflow Volume":

        values = -values

    fig.add_trace(
        go.Bar(

            y=chain_metrics["Chain"],

            x=values,

            name=metric,

            orientation="h",

            marker=dict(
                color=metric_colors[metric]
            ),

            hovertemplate=(
                "<b>%{y}</b><br>"
                + metric
                + ": %{x:,.2f}"
                + "<extra></extra>"
            )
        )
    )


# =========================================================
# LAYOUT
# =========================================================

fig.update_layout(

    barmode="group",

    height=max(
        600,
        len(chain_metrics) * 32
    ),

    title=dict(
        text=f"Chain Transfer Volume — {time_range.upper()}",
        x=0.5,
        xanchor="center"
    ),

    xaxis=dict(

        title="Volume",

        zeroline=True,

        zerolinewidth=2,

        zerolinecolor="#333333",

        tickformat=",.0f",

        showgrid=True,

        gridcolor="rgba(0,0,0,0.08)"
    ),

    yaxis=dict(

        title="",

        categoryorder="array",

        categoryarray=chain_metrics[
            "Chain"
        ].tolist(),

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
# DISPLAY
# =========================================================

st.plotly_chart(
    fig,
    use_container_width=True
)
