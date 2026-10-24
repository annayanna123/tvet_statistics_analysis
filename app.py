import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError
from sqlalchemy import create_engine, text


st.set_page_config(
    page_title = "Philippine TVET Statistics",
    page_icon = ":material/monitoring:",
    layout = "wide",
)


st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            max-width: 1500px;
        }

        [data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.18);
            padding: 18px 20px;
            border-radius: 12px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.88rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }

        div[data-testid="stPlotlyChart"] {
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            padding: 8px;
        }

        .section-description {
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.9rem;
            margin-top: -8px;
            margin-bottom: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


app_dir = Path(__file__).resolve().parent
load_dotenv(app_dir / ".env.local")
load_dotenv(app_dir / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
    except (KeyError, StreamlitSecretNotFoundError):
        DATABASE_URL = None


st.title("Philippine TVET Statistics")
st.subheader("National Accomplishment on Assessment and Certification of TVET Graduates by Region")
st.caption("Reporting period: January 2021")


#connection to the database

@st.cache_data(ttl=300)
def load_data(database_url):
    engine = create_engine(
        database_url,
        pool_pre_ping=True
    )

    query = text("""
        SELECT 
        r.region_id,
        r.region_name,
        p.province_name,
        p.reporting_period,
        p.assessed_female,
        p.assessed_male,
        p.assessed_total,
        p.certified_female,
        p.certified_male,
        p.certified_total,
        p.certification_rate
        FROM province_stats AS p
        JOIN regions AS r ON p.region_id = r.region_id
        WHERE p.reporting_period = :period
        ORDER BY r.region_name, p.province_name
    """)

    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(query, connection, params={"period": "2021-01-01"},)
    finally:
        engine.dispose()

    if df.empty:
        st.warning("No data available for the selected reporting period.")
        return df

    df["reporting_period"] = pd.to_datetime(df["reporting_period"])


    return df

if not DATABASE_URL:
    st.error(
        "Database URL is not configured. Set DATABASE_URL in your environment, "
        ".env file, or .streamlit/secrets.toml."
    )
    st.stop()

try:
    df = load_data(DATABASE_URL)
except Exception as e:
    st.error("Could not connect to the database. Please check your database configuration.")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("No data available for the selected reporting period.")
    st.stop()


# Filters



# --- Checkbox dropdown filters ---
all_regions = sorted(df["region_name"].dropna().unique().tolist())

def get_provinces(regions):
    return sorted(
        df.loc[df["region_name"].isin(regions), "province_name"]
        .dropna().unique().tolist()
    )

# Initialize filters with all available regions and provinces
if "region_filter" not in st.session_state:
    st.session_state["region_filter"] = all_regions.copy()

if "province_filter" not in st.session_state:
    st.session_state["province_filter"] = get_provinces(
        st.session_state["region_filter"]
    )

def update_regions():
    selected = [
        r for r in all_regions
        if st.session_state.get(f"region_cb_{r}", False)
    ]
    st.session_state["region_filter"] = selected

    # Selecting regions automatically selects all their provinces
    provinces = get_provinces(selected)
    st.session_state["province_filter"] = provinces

    for p in df["province_name"].dropna().unique():
        st.session_state[f"province_cb_{p}"] = p in provinces

def update_provinces():
    available = get_provinces(st.session_state["region_filter"])
    st.session_state["province_filter"] = [
        p for p in available
        if st.session_state.get(f"province_cb_{p}", False)
    ]

def select_all_regions():
    st.session_state["region_filter"] = all_regions.copy()
    for r in all_regions:
        st.session_state[f"region_cb_{r}"] = True

    provinces = get_provinces(all_regions)
    st.session_state["province_filter"] = provinces
    for p in df["province_name"].dropna().unique():
        st.session_state[f"province_cb_{p}"] = p in provinces

def clear_regions():
    st.session_state["region_filter"] = []
    st.session_state["province_filter"] = []

    for r in all_regions:
        st.session_state[f"region_cb_{r}"] = False
    for p in df["province_name"].dropna().unique():
        st.session_state[f"province_cb_{p}"] = False

def select_all_provinces():
    provinces = get_provinces(st.session_state["region_filter"])
    st.session_state["province_filter"] = provinces.copy()

    for p in df["province_name"].dropna().unique():
        st.session_state[f"province_cb_{p}"] = p in provinces

def clear_provinces():
    st.session_state["province_filter"] = []
    for p in df["province_name"].dropna().unique():
        st.session_state[f"province_cb_{p}"] = False

# Initialize checkbox states before displaying widgets
for r in all_regions:
    st.session_state.setdefault(
        f"region_cb_{r}", r in st.session_state["region_filter"]
    )

for p in df["province_name"].dropna().unique():
    st.session_state.setdefault(
        f"province_cb_{p}", p in st.session_state["province_filter"]
    )

header_col, region_col, province_col = st.columns([2.2, 1.1, 1.3])

with header_col:
    st.title("Philippine TVET Statistics")
    st.caption("National Accomplishment on Assessment and Certification · January 2021")

with region_col:
    with st.popover(
        f"Region ({len(st.session_state['region_filter'])})",
        use_container_width=True
    ):
        st.button("Select all", key="select_all_regions",
                  on_click=select_all_regions)
        st.button("Clear all", key="clear_regions",
                  on_click=clear_regions)

        for r in all_regions:
            st.checkbox(
                r,
                key=f"region_cb_{r}",
                on_change=update_regions
            )

with province_col:
    available_provinces = get_provinces(
        st.session_state["region_filter"]
    )
    selected_province_count = sum(
        p in st.session_state["province_filter"]
        for p in available_provinces
    )

    with st.popover(
        f"Province ({selected_province_count}/{len(available_provinces)})",
        use_container_width=True
    ):
        st.button("Select all", key="select_all_provinces",
                  on_click=select_all_provinces)
        st.button("Clear all", key="clear_provinces",
                  on_click=clear_provinces)

        if not available_provinces:
            st.caption("Select a region first.")
        else:
            for p in available_provinces:
                st.checkbox(
                    p,
                    key=f"province_cb_{p}",
                    on_change=update_provinces
                )

filtered_df = df[
    df["region_name"].isin(st.session_state["region_filter"])
    & df["province_name"].isin(st.session_state["province_filter"])
].copy()



# metrics for the dashboard

total_assessed = int(filtered_df["assessed_total"].sum())
total_certified = int(filtered_df["certified_total"].sum())

overall_rate = (
    total_certified / total_assessed * 100
    if total_assessed > 0
    else None
)

province_count = filtered_df["province_name"].nunique()
region_count = filtered_df["region_name"].nunique()

# cards

total_assessed = int(filtered_df["assessed_total"].sum())
total_certified = int(filtered_df["certified_total"].sum())

overall_rate = (
    total_certified / total_assessed * 100
    if total_assessed > 0
    else None
)

province_count = filtered_df["province_name"].nunique()
region_count = filtered_df["region_name"].nunique()

st.subheader("Overview")
st.markdown(
    '<div class="section-description">'
    'Summary of the selected geographic areas.'
    '</div>',
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Persons Assessed", f"{total_assessed:,}")
kpi2.metric("Persons Certified", f"{total_certified:,}")
kpi3.metric(
    "Derived Certification Rate",
    f"{overall_rate:.2f}%" if overall_rate is not None else "N/A",
)
kpi4.metric("Provinces Included", f"{province_count:,}")

st.caption(
    f"{region_count} region(s) and {province_count} province(s) "
    "included in the current selection."
)

st.divider()


# Data for the charts

regional = (
    filtered_df.groupby("region_name", as_index=False)
    .agg(
        assessed=("assessed_total", "sum"),
        certified=("certified_total", "sum"),
    )
)

regional_long = regional.melt(
    id_vars="region_name",
    value_vars=["assessed", "certified"],
    var_name="Metric",
    value_name="Persons",
)

regional_long["Metric"] = regional_long["Metric"].map({
    "assessed": "Assessed",
    "certified": "Certified",
})


province_summary = (
    filtered_df.groupby(
        ["region_name", "province_name"], as_index=False
    )
    .agg(
        assessed=("assessed_total", "sum"),
        certified=("certified_total", "sum"),
    )
    .sort_values("assessed", ascending=False)
    .head(10)
    .sort_values("assessed", ascending=True)
)

province_long = province_summary.melt(
    id_vars=["province_name", "region_name"],
    value_vars=["assessed", "certified"],
    var_name="Metric",
    value_name="Persons",
)

province_long["Metric"] = province_long["Metric"].map({
    "assessed": "Assessed",
    "certified": "Certified",
})



rate_data = (
    filtered_df.dropna(subset=["certification_rate"])
    .sort_values("certification_rate", ascending=False)
    .head(10)
    .sort_values("certification_rate", ascending=True)
)


gender_data = pd.DataFrame({
    "Sex": ["Female", "Male"],
    "Assessed": [
        filtered_df["assessed_female"].sum(),
        filtered_df["assessed_male"].sum(),
    ],
    "Certified": [
        filtered_df["certified_female"].sum(),
        filtered_df["certified_male"].sum(),
    ],
})

gender_long = gender_data.melt(
    id_vars="Sex",
    var_name="Metric",
    value_name="Persons",
)


# charts

st.subheader("Geographic Comparison")
st.markdown(
    '<div class="section-description">'
    'Compare the volume of assessment and certification across '
    'regions and provinces.'
    '</div>',
    unsafe_allow_html=True,
)

left_chart, right_chart = st.columns(2, gap="large")

with left_chart:
    st.markdown("**Assessment and Certification by Region**")

    fig_region = px.bar(
        regional_long,
        x="region_name",
        y="Persons",
        color="Metric",
        barmode="group",
        labels={
            "region_name": "Region",
            "Persons": "Number of persons",
        },
        color_discrete_sequence=["#647B91", "#8DA399"],
    )

    fig_region.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=25, b=10),
        legend_title_text="",
        xaxis_tickangle=-35,
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
    )

with right_chart:
    st.markdown("**Assessment and Certification by Province**")

    fig_province = px.bar(
        province_long,
        x="Persons",
        y="province_name",
        color="Metric",
        barmode="group",
        orientation="h",
        hover_data=["region_name"],
        labels={
            "province_name": "Province",
            "Persons": "Number of persons",
        },
        color_discrete_sequence=["#647B91", "#8DA399"],
    )

    fig_province.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
        legend_title_text="",
    )

    st.plotly_chart(
        fig_province,
        use_container_width=True,
    )


# Secondary charts

st.divider()
st.subheader("Certification and Gender Analysis")
st.markdown(
    '<div class="section-description">'
    'Explore reported certification rates and differences in '
    'assessment and certification counts by sex.'
    '</div>',
    unsafe_allow_html=True,
)

left_chart, right_chart = st.columns(2, gap="large")

with left_chart:
    st.markdown("**Reported Certification Rate by Province**")

    fig_rate = px.bar(
        rate_data,
        x="certification_rate",
        y="province_name",
        color="certification_rate",
        orientation="h",
        hover_data=[
            "region_name",
            "assessed_total",
            "certified_total",
        ],
        labels={
            "certification_rate": "Reported rate (%)",
            "province_name": "Province",
        },
        color_discrete_sequence=["#647B91"],
    )

    fig_rate.update_layout(
        height=max(420, len(rate_data) * 27),
        margin=dict(l=10, r=10, t=25, b=10),
        coloraxis_colorbar_title="Rate (%)",
    )

    st.plotly_chart(
        fig_rate,
        use_container_width=True,
    )

with right_chart:
    st.markdown("**Assessment and Certification by Sex**")

    fig_gender = px.bar(
        gender_long,
        x="Sex",
        y="Persons",
        color="Metric",
        barmode="group",
        labels={
            "Sex": "Sex",
            "Persons": "Number of persons",
        },
        color_discrete_sequence=["#647B91", "#8DA399"],
    )

    fig_gender.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=25, b=10),
        legend_title_text="",
    )

    st.plotly_chart(
        fig_gender,
        use_container_width=True,
    )

# Findings

st.divider()
st.subheader("Key Findings")

finding1, finding2 = st.columns(2, gap="large")

top_certified = filtered_df.loc[
    filtered_df["certified_total"].idxmax()
]

top_assessed = filtered_df.loc[
    filtered_df["assessed_total"].idxmax()
]

with finding1:
    st.markdown("**Highest certification count**")
    st.markdown(f"### {top_certified['province_name']}")
    st.write(
        f"{int(top_certified['certified_total']):,} certified persons "
        f"in {top_certified['region_name']}."
    )

with finding2:
    st.markdown("**Highest assessment count**")
    st.markdown(f"### {top_assessed['province_name']}")
    st.write(
        f"{int(top_assessed['assessed_total']):,} assessed persons "
        f"in {top_assessed['region_name']}."
    )

valid_rates = rate_data[rate_data["assessed_total"] > 0]

if not valid_rates.empty:
    lowest_rate = valid_rates.iloc[0]
    highest_rate = valid_rates.iloc[-1]

    rate_col1, rate_col2 = st.columns(2, gap="large")

    with rate_col1:
        st.markdown("**Lowest reported rate among provinces with assessments**")
        st.write(
            f"{lowest_rate['province_name']}: "
            f"{lowest_rate['certification_rate']:.2f}%"
        )

    with rate_col2:
        st.markdown("**Highest reported rate among provinces with assessments**")
        st.write(
            f"{highest_rate['province_name']}: "
            f"{highest_rate['certification_rate']:.2f}%"
        )

st.caption(
    "Findings update according to the selected regions and provinces. "
    "The derived overall rate is total certified divided by total assessed; "
    "the provincial chart displays the source-reported rate."
)

# data

st.divider()

with st.expander("View underlying data"):
    display_columns = [
        "region_name",
        "province_name",
        "assessed_female",
        "assessed_male",
        "assessed_total",
        "certified_female",
        "certified_male",
        "certified_total",
        "certification_rate",
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download filtered data as CSV",
        data=filtered_df[display_columns].to_csv(
            index=False
        ).encode("utf-8"),
        file_name="tvet_statistics_filtered.csv",
        mime="text/csv",
    )

st.caption(
    "Source: TESDA. Reporting period: January 1–31, 2021."
)

