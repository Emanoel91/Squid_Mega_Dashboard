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

# The route-level field that holds the number of transactions for
# that source/destination pair. The API's exact field name isn't
# guaranteed, so we auto-detect it from this candidate list (first
# match wins). If your API uses a different field name, just add
# it here.
TRANSACTION_COUNT_FIELD_CANDIDATES = [
    "txCount",
    "tx_count",
    "numTxs",
    "num_txs",
    "numTransactions",
    "num_transactions",
    "transactionCount",
    "transaction_count",
    "transactions",
    "txs",
    "count"
]

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


def detect_transaction_field(df):
    """
    Returns the first column name (from TRANSACTION_COUNT_FIELD_CANDIDATES)
    that actually exists in the API response, or None if none of them do.
    """

    for candidate in TRANSACTION_COUNT_FIELD_CANDIDATES:

        if candidate in df.columns:
            return candidate

    return None


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

# Logos supplied directly by the user for chains that neither
# CoinGecko nor LI.FI had. These always win over anything fetched
# from those sources — they're checked first in find_chain_logo.
# Keys are matched loosely (spaces/dashes/underscores ignored,
# case-insensitive), so "Unknown Zone" and "unknownzone" both work.
MANUAL_CHAIN_LOGO_OVERRIDES = {
    "lava": "https://s2.coinmarketcap.com/static/img/coins/64x64/32722.png",
    "xion": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/xion.webp",
    "c4e": "https://s2.coinmarketcap.com/static/img/coins/64x64/22633.png",
    "umee": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/umee.webp",
    "agoric": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/agoric.webp",
    "nolus": "https://s2.coinmarketcap.com/static/img/coins/64x64/28485.png",
    "jackal": "https://s2.coinmarketcap.com/static/img/coins/64x64/25261.png",
    "unknown zone": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "carbon": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/carbon.webp",
    "acre": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/acre.webp",
    "fetch": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/fetch.webp",
    "sentinel": "https://s2.coinmarketcap.com/static/img/coins/64x64/2643.png",
    "humanai": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/humans.webp",
    "decentr": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/decentr.webp",
    "bitsong": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/bitsong.webp",
    "ngmi": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "quicksilver": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/quicksilver.webp",
    "cheqd": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/cheqd.webp",
    "flippandomainnet": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "quasar": "https://s2.coinmarketcap.com/static/img/coins/64x64/27607.png",
    "dchain": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "dig": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "747": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "98866": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "hub": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "maria": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
    "digchain": "https://s2.coinmarketcap.com/static/img/coins/64x64/17748.png",
    "impacthub": "https://raw.githubusercontent.com/0xsquid/assets/main/images/webp128/chains/impacthub.webp",
    "nirvana": "https://s2.coinmarketcap.com/static/img/coins/64x64/27561.png",
}


def _normalize_lookup_key(value):
    """Lowercase + strip spaces/dashes/underscores, for loose matching."""

    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


# Pre-normalized version of the manual overrides, built once.
_NORMALIZED_MANUAL_OVERRIDES = {
    _normalize_lookup_key(name): url
    for name, url in MANUAL_CHAIN_LOGO_OVERRIDES.items()
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

    # 1) manual overrides always win (user-supplied, highest confidence)
    normalized_key = _normalize_lookup_key(chain_name)

    if normalized_key in _NORMALIZED_MANUAL_OVERRIDES:
        return _NORMALIZED_MANUAL_OVERRIDES[normalized_key]

    # 2) exact match
    if key in logo_map:
        return logo_map[key]

    # 3) known alias match
    alias = CHAIN_NAME_ALIASES.get(key)

    if alias and alias in logo_map:
        return logo_map[alias]

    # 4) loose match (handles minor naming differences,
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
# CALCULATE CHAIN METRICS (shared core for volume & transactions)
# =========================================================

def _aggregate_chain_metrics(df, value_col, names):
    """
    Generic inflow/outflow/internal/total/net aggregation over any
    numeric column (volume, transaction count, etc). `names` maps
    the logical roles to the output column names to use.
    """

    working = df.copy()

    working[value_col] = pd.to_numeric(
        working[value_col],
        errors="coerce"
    ).fillna(0)

    working["source"] = (
        working["source"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    working["destination"] = (
        working["destination"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # -----------------------------------------------------
    # Internal: source == destination
    # -----------------------------------------------------

    internal = (
        working[
            working["source"] == working["destination"]
        ]
        .groupby("source")[value_col]
        .sum()
        .rename(names["internal"])
    )

    # -----------------------------------------------------
    # Inflow: other chain -> chain
    # -----------------------------------------------------

    inflow = (
        working[
            working["source"] != working["destination"]
        ]
        .groupby("destination")[value_col]
        .sum()
        .rename(names["inflow"])
    )

    # -----------------------------------------------------
    # Outflow: chain -> other chain
    # -----------------------------------------------------

    outflow = (
        working[
            working["source"] != working["destination"]
        ]
        .groupby("source")[value_col]
        .sum()
        .rename(names["outflow"])
    )

    chains = sorted(
        set(working["source"])
        |
        set(working["destination"])
    )

    metrics = pd.DataFrame(
        index=chains
    )

    metrics = metrics.join(inflow)
    metrics = metrics.join(outflow)
    metrics = metrics.join(internal)

    metrics = metrics.fillna(0)

    metrics[names["total"]] = (
        metrics[names["inflow"]]
        +
        metrics[names["outflow"]]
        +
        metrics[names["internal"]]
    )

    metrics[names["net"]] = (
        metrics[names["inflow"]]
        -
        metrics[names["outflow"]]
    )

    metrics.index.name = "Chain"

    return metrics.reset_index()


VOLUME_NAMES = {
    "inflow": "Inflow Volume",
    "outflow": "Outflow Volume",
    "internal": "Internal Transfer Volume",
    "total": "Total Transfer Volume",
    "net": "Net Flow",
}

TRANSACTION_NAMES = {
    "inflow": "Inflow Transaction",
    "outflow": "Outflow Transaction",
    "internal": "Internal Transaction",
    "total": "Total Transaction",
    "net": "Net Flow Transaction",
}


def calculate_chain_metrics(df):

    return _aggregate_chain_metrics(
        df,
        "volume",
        VOLUME_NAMES
    )


def calculate_chain_transaction_metrics(df, tx_field):

    return _aggregate_chain_metrics(
        df,
        tx_field,
        TRANSACTION_NAMES
    )


# =========================================================
# NUMBER FORMATTERS
# =========================================================

def format_volume(value, show_sign=False):
    """Formats a dollar amount, e.g. $1.23M."""

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


def format_count(value, show_sign=False):
    """Formats a plain (non-currency) count, e.g. 1.23M, 842."""

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
            f"{value / 1_000_000_000:.2f}B"
        )

    elif value >= 1_000_000:

        formatted = (
            f"{value / 1_000_000:.2f}M"
        )

    elif value >= 1_000:

        formatted = (
            f"{value / 1_000:.2f}K"
        )

    else:

        formatted = (
            f"{value:,.0f}"
        )

    return sign + formatted


# =========================================================
# METRIC / CHART DISPLAY CONFIG
# =========================================================

POSITIVE_COLOR = "#16A34A"
NEGATIVE_COLOR = "#DC2626"
NEUTRAL_TEXT_COLOR = "#111111"

# Bar color per volume metric (Net Flow is colored by sign instead).
VOLUME_METRIC_COLORS = {
    "Inflow Volume": "#16A34A",
    "Outflow Volume": "#DC2626",
    "Internal Transfer Volume": "#EAB308",
    "Total Transfer Volume": "#2563EB",
}

# Bar color per transaction metric (Net Flow Transaction is colored
# by sign instead).
TRANSACTION_METRIC_COLORS = {
    "Inflow Transaction": "#16A34A",
    "Outflow Transaction": "#DC2626",
    "Internal Transaction": "#EAB308",
    "Total Transaction": "#2563EB",
}

# Each row below pairs a volume metric with its transaction-count
# counterpart: left chart = top 10 by volume metric,
# right chart = top 10 by the matching transaction metric.
ROW_METRIC_PAIRS = [
    ("Inflow Volume", "Inflow Transaction"),
    ("Outflow Volume", "Outflow Transaction"),
    ("Net Flow", "Net Flow Transaction"),
    ("Total Transfer Volume", "Total Transaction"),
    ("Internal Transfer Volume", "Internal Transaction"),
]


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
        "ytd",
        "1y",
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

transaction_field = detect_transaction_field(
    route_df
)

if transaction_field is None:

    st.warning(
        "ستون شمارش تراکنش در پاسخ API پیدا نشد "
        "(نام‌های بررسی‌شده: "
        f"{', '.join(TRANSACTION_COUNT_FIELD_CANDIDATES)}). "
        "فعلاً هر ردیف از داده به‌عنوان ۱ تراکنش شمرده شده؛ "
        "برای دقت کامل، نام واقعی این ستون را به "
        "TRANSACTION_COUNT_FIELD_CANDIDATES در بالای کد اضافه کنید."
    )

    route_df_for_tx = route_df.copy()

    route_df_for_tx["_tx_count_fallback"] = 1

    transaction_field = "_tx_count_fallback"

else:

    route_df_for_tx = route_df


chain_tx_metrics = calculate_chain_transaction_metrics(
    route_df_for_tx,
    transaction_field
)

chain_logo_map = get_chain_logo_map()


# =========================================================
# SHARED TABLE-STYLING HELPERS
# =========================================================

def _style_net_flow(value):

    if value > 0:
        return f"color: {POSITIVE_COLOR}; font-weight: 600;"

    elif value < 0:
        return f"color: {NEGATIVE_COLOR}; font-weight: 600;"

    return f"color: {NEUTRAL_TEXT_COLOR};"


def _style_neutral(value):

    return f"color: {NEUTRAL_TEXT_COLOR};"


def _apply_cell_style(styler, style_fn, subset):
    """
    pandas >= 2.1 renamed Styler.applymap to Styler.map (and pandas 3.x
    removed applymap entirely), so pick whichever this environment has.
    """

    style_method = getattr(styler, "map", None) or styler.applymap

    return style_method(
        style_fn,
        subset=subset
    )


def render_metrics_table(
    metrics_df,
    logo_map,
    value_columns,
    net_flow_column,
    sort_column,
    value_formatter
):

    table_df = metrics_df.copy()

    # Look up logos BEFORE re-casing the chain name for display,
    # since the logo lookup expects the original (lowercase) name.
    table_df["Logo"] = table_df["Chain"].apply(
        lambda c: find_chain_logo(c, logo_map)
    )

    table_df["Chain"] = table_df["Chain"].str.title()

    ordered_columns = ["Logo", "Chain"] + value_columns

    table_df = table_df[ordered_columns]

    table_df = table_df.sort_values(
        by=sort_column,
        ascending=False
    ).reset_index(drop=True)

    format_map = {
        col: (
            (lambda v: value_formatter(v, show_sign=True))
            if col == net_flow_column
            else (lambda v: value_formatter(v))
        )
        for col in value_columns
    }

    styler = table_df.style.format(format_map)

    styler = _apply_cell_style(
        styler,
        _style_net_flow,
        subset=[net_flow_column]
    )

    other_columns = [
        col for col in value_columns
        if col != net_flow_column
    ]

    styler = _apply_cell_style(
        styler,
        _style_neutral,
        subset=other_columns
    )

    st.dataframe(
        styler,
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
# TABLE 1 — FULL METRICS (VOLUME)
# =========================================================

st.markdown(
    "### 💸 All Chains — Full Metrics (Volume)"
)

render_metrics_table(
    chain_metrics,
    chain_logo_map,
    value_columns=[
        "Inflow Volume",
        "Outflow Volume",
        "Internal Transfer Volume",
        "Total Transfer Volume",
        "Net Flow"
    ],
    net_flow_column="Net Flow",
    sort_column="Total Transfer Volume",
    value_formatter=format_volume
)


# =========================================================
# TABLE 2 — FULL METRICS (TRANSACTIONS)
# =========================================================

st.markdown(
    "### 🚀 All Chains — Full Metrics (Transactions)"
)

render_metrics_table(
    chain_tx_metrics,
    chain_logo_map,
    value_columns=[
        "Inflow Transaction",
        "Outflow Transaction",
        "Internal Transaction",
        "Total Transaction",
        "Net Flow Transaction"
    ],
    net_flow_column="Net Flow Transaction",
    sort_column="Total Transaction",
    value_formatter=format_count
)


# =========================================================
# TOP 10 BAR CHART BUILDER
# =========================================================

def build_ranked_bar_chart(
    sub_df,
    metric,
    chart_title,
    logo_map,
    bar_color,
    value_formatter
):
    """
    Vertical bar chart for a small set of chains (e.g. top 10).
    Each x-axis position shows either the chain's logo (if found)
    or its name as text — never both.
    """

    chains = sub_df["Chain"].tolist()

    values = sub_df[metric].tolist()

    logos = [
        find_chain_logo(chain, logo_map)
        for chain in chains
    ]

    show_sign = metric.startswith("Net Flow")

    value_labels = [
        value_formatter(v, show_sign=show_sign)
        for v in values
    ]

    hover_labels = [
        f"{chain.title()}<br>{metric}: {value_formatter(v, show_sign=show_sign)}"
        for chain, v in zip(chains, values)
    ]

    if show_sign:

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


def render_top_pair_row(
    volume_metric,
    transaction_metric,
    volume_df,
    transaction_df,
    logo_map,
    n=10
):

    vol_color = VOLUME_METRIC_COLORS.get(volume_metric)

    tx_color = TRANSACTION_METRIC_COLORS.get(transaction_metric)

    top_volume_df = volume_df.nlargest(
        n,
        volume_metric
    ).reset_index(drop=True)

    top_tx_df = transaction_df.nlargest(
        n,
        transaction_metric
    ).reset_index(drop=True)

    col_left, col_right = st.columns(2)

    with col_left:

        fig_volume = build_ranked_bar_chart(
            top_volume_df,
            volume_metric,
            f"Top 10 — {volume_metric}",
            logo_map,
            bar_color=vol_color,
            value_formatter=format_volume
        )

        st.plotly_chart(
            fig_volume,
            use_container_width=True
        )

    with col_right:

        fig_tx = build_ranked_bar_chart(
            top_tx_df,
            transaction_metric,
            f"Top 10 — {transaction_metric}",
            logo_map,
            bar_color=tx_color,
            value_formatter=format_count
        )

        st.plotly_chart(
            fig_tx,
            use_container_width=True
        )


# =========================================================
# TOP 10 ROWS — VOLUME METRIC PAIRED WITH ITS TRANSACTION METRIC
# =========================================================

st.markdown("---")

st.markdown(
    "### 🏆 Top 10 Chains by Metric"
)

for volume_metric, transaction_metric in ROW_METRIC_PAIRS:

    render_top_pair_row(
        volume_metric,
        transaction_metric,
        chain_metrics,
        chain_tx_metrics,
        chain_logo_map,
        n=10
    )
