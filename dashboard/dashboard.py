"""Bike Sharing Interactive Dashboard.

Cara menjalankan:
    pip install -r requirements.txt
    streamlit run dashboard/dashboard.py
"""

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
RAW_DIR = BASE_DIR.parent / "Bike-sharing-dataset"

# URL publik dataset Capital Bikeshare (beberapa mirror)
BIKE_DAY_URLS = [
    "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/biking/day.csv",
    "https://raw.githubusercontent.com/PraxisML/Bike-Sharing-Dataset/master/day.csv",
]
BIKE_HOUR_URLS = [
    "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/biking/hour.csv",
    "https://raw.githubusercontent.com/PraxisML/Bike-Sharing-Dataset/master/hour.csv",
]

SEASON_MAP = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
WEATHER_MAP = {
    1: "Cerah / Berawan",
    2: "Mendung / Berkabut",
    3: "Hujan / Salju Ringan",
    4: "Hujan Lebat / Badai",
}
WEATHER_GROUP_MAP = {1: "Cerah", 2: "Mendung", 3: "Buruk", 4: "Buruk"}
WEEKDAY_MAP = {
    0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu",
    4: "Kamis", 5: "Jumat", 6: "Sabtu",
}
WORKINGDAY_MAP = {1: "Hari Kerja", 0: "Akhir Pekan / Libur"}

COLOR_BASE = "#4C72B0"
COLOR_HIGHLIGHT = "#C44E52"
COLOR_ALT = "#DD8452"
COLOR_MUTED = "#A3A3A3"
PLOTLY_CONFIG = {"displayModeBar": "interactive", "displaylogo": False}


# ---------------------------------------------------------------------------
# Data loading & preprocessing
# ---------------------------------------------------------------------------
def _denormalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dteday"] = pd.to_datetime(df["dteday"])
    df["temp_c"] = (df["temp"] * 41).round(1)
    df["atemp_c"] = (df["atemp"] * 50).round(1)
    df["hum_pct"] = (df["hum"] * 100).round(1)
    df["windspeed_kph"] = (df["windspeed"] * 67).round(1)
    df["season_name"] = df["season"].map(SEASON_MAP)
    df["weather_name"] = df["weathersit"].map(WEATHER_MAP)
    df["weather_group"] = df["weathersit"].map(WEATHER_GROUP_MAP)
    df["weekday_name"] = df["weekday"].map(WEEKDAY_MAP)
    df["day_type"] = df["workingday"].map(WORKINGDAY_MAP)
    df["year"] = df["yr"].map({0: "2011", 1: "2012"}).astype(str)
    if "cnt" in df.columns:
        df["demand_group"] = pd.qcut(
            df["cnt"], q=3, labels=["Rendah", "Sedang", "Tinggi"]
        )
    return df


def _try_read_local() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    day_path = BASE_DIR / "main_data.csv"
    if not day_path.exists():
        for p in (DATA_DIR / "day.csv", RAW_DIR / "day.csv", BASE_DIR / "day.csv"):
            if p.exists():
                day_path = p
                break
    hour_path = DATA_DIR / "hour.csv"
    if not hour_path.exists():
        for p in (RAW_DIR / "hour.csv", BASE_DIR / "hour.csv"):
            if p.exists():
                hour_path = p
                break
    day_df = pd.read_csv(day_path, parse_dates=["dteday"]) if day_path.exists() else None
    hour_df = pd.read_csv(hour_path, parse_dates=["dteday"]) if hour_path.exists() else None
    return day_df, hour_df


def _try_read_urls() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    day_df = hour_df = None
    for url in BIKE_DAY_URLS:
        try:
            day_df = pd.read_csv(url, parse_dates=["dteday"])
            break
        except Exception:
            continue
    for url in BIKE_HOUR_URLS:
        try:
            hour_df = pd.read_csv(url, parse_dates=["dteday"])
            break
        except Exception:
            continue
    return day_df, hour_df


def _dummy_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(42)
    dates = pd.date_range("2011-01-01", "2012-12-31", freq="D")
    n = len(dates)
    season = ((dates.month % 12) // 3 + 1).astype(int)
    yr = (dates.year - 2011).astype(int)
    weekday = dates.weekday.to_numpy()
    workingday = ((weekday < 5)).astype(int)
    temp_norm = rng.uniform(0.1, 0.9, n)
    base = 1500 + temp_norm * 4000 + yr * 500 + workingday * 300
    cnt = np.clip(base + rng.normal(0, 500, n), 20, 9000).astype(int)
    registered = (cnt * rng.uniform(0.75, 0.9, n)).astype(int)
    casual = cnt - registered
    day = pd.DataFrame({
        "instant": np.arange(1, n + 1), "dteday": dates, "season": season,
        "yr": yr, "mnth": dates.month, "holiday": 0, "weekday": weekday,
        "workingday": workingday, "weathersit": rng.choice([1, 2, 3], n, p=[0.6, 0.3, 0.1]),
        "temp": temp_norm, "atemp": temp_norm, "hum": rng.uniform(0.3, 0.9, n),
        "windspeed": rng.uniform(0.05, 0.4, n), "casual": casual,
        "registered": registered, "cnt": cnt,
    })
    rows = []
    for _, r in day.iterrows():
        for h in range(24):
            peak = 1.8 if (r["workingday"] and h in (8, 17, 18)) or (
                not r["workingday"] and 11 <= h <= 15
            ) else (0.3 if 0 <= h <= 5 else 1.0)
            c = max(int(r["cnt"] / 24 * peak + rng.normal(0, 5)), 0)
            reg = int(c * 0.8) if r["workingday"] else int(c * 0.5)
            rows.append({
                "instant": len(rows) + 1, "dteday": r["dteday"], "season": r["season"],
                "yr": r["yr"], "mnth": r["mnth"], "hr": h, "holiday": r["holiday"],
                "weekday": r["weekday"], "workingday": r["workingday"],
                "weathersit": r["weathersit"], "temp": r["temp"], "atemp": r["atemp"],
                "hum": r["hum"], "windspeed": r["windspeed"], "casual": c - reg,
                "registered": reg, "cnt": c,
            })
    hour = pd.DataFrame(rows)
    return day, hour


@st.cache_data(show_spinner="Memuat dataset…")
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    day_df, hour_df = _try_read_local()
    if day_df is None or hour_df is None:
        day_url, hour_url = _try_read_urls()
        if day_url is not None:
            day_df = day_url
        if hour_url is not None:
            hour_df = hour_url
    if day_df is None or hour_df is None:
        day_df, hour_df = _dummy_data()
        st.session_state["_data_source"] = "dummy"
    else:
        st.session_state["_data_source"] = "lokal/url"
    return _denormalize(day_df), _denormalize(hour_df)


# ---------------------------------------------------------------------------
# Filter helpers
# ---------------------------------------------------------------------------
def init_session() -> None:
    defaults = {
        "flt_start": date(2011, 1, 1),
        "flt_end": date(2012, 12, 31),
        "flt_date_input": (date(2011, 1, 1), date(2012, 12, 31)),
        "flt_years": ["2011", "2012"],
        "flt_seasons": list(SEASON_MAP.values()),
        "flt_weathers": list(WEATHER_MAP.values()),
        "flt_daytype": "Semua",
        "trend_mode": "Harian",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_filters() -> None:
    st.session_state["flt_start"] = date(2011, 1, 1)
    st.session_state["flt_end"] = date(2012, 12, 31)
    st.session_state["flt_date_input"] = (date(2011, 1, 1), date(2012, 12, 31))
    st.session_state["flt_years"] = ["2011", "2012"]
    st.session_state["flt_seasons"] = list(SEASON_MAP.values())
    st.session_state["flt_weathers"] = list(WEATHER_MAP.values())
    st.session_state["flt_daytype"] = "Semua"
    st.session_state["trend_mode"] = "Harian"


def apply_filters(
    day_df: pd.DataFrame,
    hour_df: pd.DataFrame,
    start: date,
    end: date,
    years: list[str],
    seasons: list[str],
    weathers: list[str],
    daytype: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end) + pd.Timedelta(1, unit="D")
    day_sel = day_df[
        day_df["dteday"].between(start_ts, end_ts, inclusive="left")
        & day_df["year"].isin(years)
        & day_df["season_name"].isin(seasons)
        & day_df["weather_name"].isin(weathers)
    ].copy()
    if daytype != "Semua":
        day_sel = day_sel[day_sel["day_type"] == daytype]
    hour_sel = hour_df[
        hour_df["dteday"].between(start_ts, end_ts, inclusive="left")
        & hour_df["year"].isin(years)
        & hour_df["season_name"].isin(seasons)
        & hour_df["weather_name"].isin(weathers)
    ].copy()
    if daytype != "Semua":
        hour_sel = hour_sel[hour_sel["day_type"] == daytype]
    return day_sel, hour_sel


# ---------------------------------------------------------------------------
# Render: KPI
# ---------------------------------------------------------------------------
def render_kpis(day_sel: pd.DataFrame) -> None:
    st.subheader("Ringkasan Metrik")
    total = int(day_sel["cnt"].sum())
    n_days = len(day_sel)
    avg_day = day_sel["cnt"].mean() if n_days else 0.0
    reg = int(day_sel["registered"].sum())
    cas = int(day_sel["casual"].sum())
    reg_pct = reg / total * 100 if total > 0 else 0.0
    cas_pct = cas / total * 100 if total > 0 else 0.0
    if n_days:
        peak_row = day_sel.loc[day_sel["cnt"].idxmax()]
        peak_label = peak_row["dteday"].strftime("%d %b %Y")
        peak_val = int(peak_row["cnt"])
    else:
        peak_label, peak_val = "—", 0
    avg_atemp = day_sel["atemp_c"].mean() if n_days else 0.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Penyewaan", f"{total:,}")
    c2.metric("Rata-rata Harian", f"{avg_day:,.0f}", help="unit/hari")
    c3.metric("Pengguna Terdaftar", f"{reg:,}", delta=f"{reg_pct:.1f}% dari total")
    c4.metric("Pengguna Kasual", f"{cas:,}", delta=f"{cas_pct:.1f}% dari total")
    c5.metric("Hari Puncak", peak_label, delta=f"{peak_val:,} sepeda")
    c6.metric("Rata-rata Suhu Terasa", f"{avg_atemp:.1f} °C")


# ---------------------------------------------------------------------------
# Render: charts
# ---------------------------------------------------------------------------
def render_trend_chart(day_sel: pd.DataFrame) -> None:
    st.markdown("#### Tren Penyewaan")
    mode = st.radio(
        "Agregasi", ["Harian", "Bulanan"], horizontal=True, key="trend_mode",
        label_visibility="collapsed",
    )
    if mode == "Bulanan":
        plot_df = (
            day_sel.set_index("dteday")[["cnt", "registered", "casual"]]
            .resample("ME")
            .sum()
            .reset_index()
        )
        x_title, y_title = "Bulan", "Total penyewaan (sepeda/bulan)"
    else:
        plot_df = day_sel[["dteday", "cnt", "registered", "casual"]].copy()
        x_title, y_title = "Tanggal", "Jumlah penyewaan (sepeda/hari)"

    fig = go.Figure()
    for col, color, name in [
        ("cnt", COLOR_BASE, "Total (cnt)"),
        ("registered", COLOR_HIGHLIGHT, "Terdaftar"),
        ("casual", COLOR_ALT, "Kasual"),
    ]:
        fig.add_trace(go.Scatter(
            x=plot_df["dteday"], y=plot_df[col], name=name,
            mode="lines", line=dict(color=color, width=1.8),
            hovertemplate="%{x|%d %b %Y}<br>%{y:,.0f} sepeda<extra>" + name + "</extra>",
        ))
    fig.update_layout(
        title="Perkembangan Penyewaan Total, Terdaftar & Kasual",
        xaxis_title=x_title, yaxis_title=y_title,
        yaxis=dict(rangemode="tozero"),
        legend=dict(orientation="h", y=1.12), margin=dict(t=60, b=40),
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


def render_donut(day_sel: pd.DataFrame) -> None:
    st.markdown("#### Komposisi Pengguna")
    reg = int(day_sel["registered"].sum())
    cas = int(day_sel["casual"].sum())
    fig = go.Figure(go.Pie(
        labels=["Terdaftar", "Kasual"], values=[reg, cas],
        hole=0.55,
        marker=dict(colors=[COLOR_BASE, COLOR_ALT]),
        hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>",
        textinfo="label+percent",
    ))
    fig.update_layout(
        title="Rasio Pengguna Terdaftar vs Kasual",
        margin=dict(t=50, b=20), annotations=[dict(
            text=f"{reg + cas:,}<br>total", x=0.5, y=0.5,
            font_size=14, showarrow=False,
        )],
    )
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


def render_hourly_pattern(hour_sel: pd.DataFrame) -> None:
    st.markdown(
        "**Pertanyaan 1:** Bagaimana pola rata-rata jumlah penyewaan per jam "
        "pada hari kerja vs akhir pekan sepanjang periode terpilih?"
    )
    if hour_sel.empty:
        st.info("Tidak ada data jam untuk filter ini.")
        return
    pattern = (
        hour_sel.groupby(["hr", "day_type"])["cnt"]
        .mean()
        .reset_index()
        .rename(columns={"cnt": "rata2_cnt"})
    )
    fig = px.line(
        pattern, x="hr", y="rata2_cnt", color="day_type",
        markers=True,
        color_discrete_map={"Hari Kerja": COLOR_BASE, "Akhir Pekan / Libur": COLOR_ALT},
        labels={"hr": "Jam dalam sehari", "rata2_cnt": "Rata-rata penyewaan (sepeda/jam)",
                "day_type": "Tipe Hari"},
        title="Rata-rata Penyewaan per Jam: Hari Kerja vs Akhir Pekan",
    )
    fig.update_layout(yaxis_rangemode="tozero", xaxis_dtick=1, hovermode="x unified",
                      legend=dict(orientation="h", y=1.12), margin=dict(t=60, b=40))
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    peak = (
        pattern.sort_values("rata2_cnt", ascending=False)
        .groupby("day_type", as_index=False)
        .head(3)
        .sort_values(["day_type", "hr"])
    )
    peak["rata2_cnt"] = peak["rata2_cnt"].round(0).astype(int)
    st.markdown("**Jam sibuk (top 3):**")
    st.dataframe(
        peak.rename(columns={"hr": "Jam", "day_type": "Tipe Hari",
                             "rata2_cnt": "Rata-rata cnt"}),
        width="stretch", hide_index=True,
    )


def render_weather_impact(day_sel: pd.DataFrame) -> None:
    st.markdown(
        "**Pertanyaan 2:** Berapa persen penurunan rata-rata penyewaan "
        "pada cuaca buruk dibanding cuaca cerah?"
    )
    stats = (
        day_sel.groupby("weather_group")["cnt"]
        .agg(["mean", "count"])
        .reindex(["Cerah", "Mendung", "Buruk"])
        .round(1)
    )
    mean_cerah, mean_buruk = stats.loc["Cerah", "mean"], stats.loc["Buruk", "mean"]
    if pd.notna(mean_cerah) and pd.notna(mean_buruk) and mean_cerah > 0:
        drop = (mean_cerah - mean_buruk) / mean_cerah * 100
        st.info(f"Cuaca buruk menurunkan rata-rata penyewaan sebesar **{drop:.1f}%** dibanding cuaca cerah.")
    else:
        drop = None
        st.warning("Data tidak mencukupi untuk membandingkan cuaca cerah & buruk pada filter ini.")

    plot_df = day_sel.groupby("weather_group", as_index=False)["cnt"].agg(
        mean="mean", std="std", count="count"
    )
    order = ["Cerah", "Mendung", "Buruk"]
    plot_df["weather_group"] = pd.Categorical(plot_df["weather_group"], order, ordered=True)
    plot_df = plot_df.sort_values("weather_group")
    colors = [COLOR_BASE if g != "Buruk" else COLOR_HIGHLIGHT for g in plot_df["weather_group"]]
    fig = go.Figure(go.Bar(
        x=plot_df["weather_group"].astype(str), y=plot_df["mean"],
        marker_color=colors,
        error_y=dict(type="data", array=plot_df["std"].fillna(0), visible=True),
        customdata=plot_df[["count"]].to_numpy(),
        hovertemplate="%{x}<br>Rata-rata: %{y:,.0f} sepeda/hari<br>Jumlah hari: %{customdata[0]}<extra></extra>",
    ))
    fig.update_layout(
        title="Rata-rata Penyewaan Harian per Kondisi Cuaca",
        xaxis_title="Kondisi cuaca", yaxis_title="Rata-rata penyewaan (sepeda/hari)",
        yaxis=dict(rangemode="tozero"), margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    sw = (
        day_sel.groupby(["season_name", "weather_group"], as_index=False)["cnt"]
        .mean()
        .rename(columns={"cnt": "rata2_cnt"})
    )
    fig2 = px.bar(
        sw, x="season_name", y="rata2_cnt", color="weather_group",
        barmode="group",
        category_orders={
            "season_name": list(SEASON_MAP.values()),
            "weather_group": order,
        },
        color_discrete_map={"Cerah": COLOR_BASE, "Mendung": COLOR_MUTED, "Buruk": COLOR_HIGHLIGHT},
        labels={"season_name": "Musim", "rata2_cnt": "Rata-rata penyewaan (sepeda/hari)",
                "weather_group": "Cuaca"},
        title="Rata-rata Penyewaan per Musim dan Kondisi Cuaca",
    )
    fig2.update_layout(yaxis_rangemode="tozero", legend=dict(orientation="h", y=1.12),
                       margin=dict(t=60, b=40))
    st.plotly_chart(fig2, width="stretch", config=PLOTLY_CONFIG)


def render_demand_groups(day_sel: pd.DataFrame) -> None:
    st.markdown(
        "**Pertanyaan 3 (Analisis Lanjutan):** Bagaimana pengelompokan hari ke dalam "
        "kategori permintaan Rendah/Sedang/Tinggi (binning persentil) dan "
        "karakteristik musim/cuacanya?"
    )
    dist = (
        day_sel["demand_group"]
        .value_counts()
        .reindex(["Rendah", "Sedang", "Tinggi"])
        .fillna(0)
        .astype(int)
    )
    cols = st.columns(3)
    for c, label in zip(cols, ["Rendah", "Sedang", "Tinggi"]):
        c.metric(f"Hari Permintaan {label}", int(dist[label]))

    season_ct = (
        day_sel.groupby(["demand_group", "season_name"], as_index=False, observed=True)
        .size()
        .rename(columns={"size": "jumlah_hari"})
    )
    fig = px.bar(
        season_ct, x="demand_group", y="jumlah_hari", color="season_name",
        barmode="group",
        category_orders={"demand_group": ["Rendah", "Sedang", "Tinggi"],
                         "season_name": list(SEASON_MAP.values())},
        labels={"demand_group": "Kelompok permintaan", "jumlah_hari": "Jumlah hari",
                "season_name": "Musim"},
        title="Distribusi Musim pada Tiap Kelompok Permintaan Harian",
    )
    fig.update_layout(legend=dict(orientation="h", y=1.12), margin=dict(t=60, b=40))
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    weather_ct = (
        day_sel.groupby(["demand_group", "weather_group"], as_index=False, observed=True)
        .size()
        .rename(columns={"size": "jumlah_hari"})
    )
    fig2 = px.bar(
        weather_ct, x="demand_group", y="jumlah_hari", color="weather_group",
        barmode="group",
        category_orders={"demand_group": ["Rendah", "Sedang", "Tinggi"],
                         "weather_group": ["Cerah", "Mendung", "Buruk"]},
        color_discrete_map={"Cerah": COLOR_BASE, "Mendung": COLOR_MUTED, "Buruk": COLOR_HIGHLIGHT},
        labels={"demand_group": "Kelompok permintaan", "jumlah_hari": "Jumlah hari",
                "weather_group": "Cuaca"},
        title="Distribusi Kondisi Cuaca pada Tiap Kelompok Permintaan Harian",
    )
    fig2.update_layout(legend=dict(orientation="h", y=1.12), margin=dict(t=60, b=40))
    st.plotly_chart(fig2, width="stretch", config=PLOTLY_CONFIG)

    profile = (
        day_sel.groupby("demand_group", observed=True)
        .agg(
            hari=("cnt", "count"),
            rata2_suhu_c=("temp_c", "mean"),
            rata2_kelembapan=("hum_pct", "mean"),
        )
        .round(1)
        .reindex(["Rendah", "Sedang", "Tinggi"])
        .reset_index()
        .rename(columns={
            "demand_group": "Kelompok", "hari": "Jumlah Hari",
            "rata2_suhu_c": "Rata-rata Suhu (°C)",
            "rata2_kelembapan": "Rata-rata Kelembapan (%)",
        })
    )
    st.markdown("**Profil kelompok permintaan:**")
    st.dataframe(profile, width="stretch", hide_index=True)


def render_temp_sensitivity(day_sel: pd.DataFrame) -> None:
    st.markdown("#### Sensitivitas Suhu & Kelembaban")
    bins = [-np.inf, 10, 20, 30, np.inf]
    labels = ["< 10 °C", "10–20 °C", "20–30 °C", "> 30 °C"]
    tmp = day_sel.copy()
    tmp["suhu_bin"] = pd.cut(tmp["temp_c"], bins=bins, labels=labels)
    agg = (
        tmp.groupby("suhu_bin", observed=True)
        .agg(rata2_cnt=("cnt", "mean"), rata2_hum=("hum_pct", "mean"), hari=("cnt", "count"))
        .reindex(labels)
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg["suhu_bin"].astype(str), y=agg["rata2_cnt"],
        name="Rata-rata penyewaan",
        marker_color=[COLOR_MUTED, COLOR_BASE, COLOR_BASE, COLOR_HIGHLIGHT],
        customdata=agg[["hari", "rata2_hum"]].to_numpy(),
        hovertemplate=(
            "%{x}<br>Rata-rata: %{y:,.0f} sepeda/hari"
            "<br>Jumlah hari: %{customdata[0]}"
            "<br>Kelembapan: %{customdata[1]:.0f}%<extra></extra>"
        ),
    ))
    fig.update_layout(
        title="Rata-rata Penyewaan Harian per Rentang Suhu Terasa",
        xaxis_title="Rentang suhu terasa", yaxis_title="Rata-rata penyewaan (sepeda/hari)",
        yaxis=dict(rangemode="tozero"), showlegend=False, margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    scatter_df = tmp.sample(min(len(tmp), 400), random_state=42)
    fig2 = px.scatter(
        scatter_df, x="temp_c", y="cnt", color="day_type",
        color_discrete_map={"Hari Kerja": COLOR_BASE, "Akhir Pekan / Libur": COLOR_ALT},
        labels={"temp_c": "Suhu terasa (°C)", "cnt": "Penyewaan (sepeda/hari)",
                "day_type": "Tipe Hari"},
        title="Sebaran Penyewaan Harian vs Suhu (sampel ≤400 titik)",
        opacity=0.65,
        hover_data=["dteday", "weather_group"],
    )
    fig2.update_layout(yaxis_rangemode="tozero", legend=dict(orientation="h", y=1.12),
                       margin=dict(t=60, b=40))
    st.plotly_chart(fig2, width="stretch", config=PLOTLY_CONFIG)


# ---------------------------------------------------------------------------
# Render: insights & data explorer
# ---------------------------------------------------------------------------
def render_insights(day_sel: pd.DataFrame, hour_sel: pd.DataFrame) -> None:
    with st.expander("💡 Insight Bisnis (ringkasan naratif)", expanded=False):
        if len(day_sel) < 2:
            st.info("Data terlalu sedikit untuk merangkum insight.")
            return
        by_year = day_sel.groupby("year")["cnt"].sum()
        if "2011" in by_year.index and "2012" in by_year.index and by_year["2011"] > 0:
            yoy = (by_year["2012"] - by_year["2011"]) / by_year["2011"] * 100
            st.markdown(
                f"- **Pertumbuhan tahunan (YoY):** Total penyewaan 2012 "
                f"{'naik' if yoy >= 0 else 'turun'} **{abs(yoy):.1f}%** dibanding 2011 "
                f"({by_year['2011']:,.0f} → {by_year['2012']:,.0f} sepeda)."
            )
        if not hour_sel.empty:
            work = hour_sel[hour_sel["day_type"] == "Hari Kerja"]
            weekend = hour_sel[hour_sel["day_type"] != "Hari Kerja"]
            if not work.empty:
                pk = work.groupby("hr")["cnt"].mean().nlargest(2).index.tolist()
                st.markdown(
                    f"- **Komuter vs rekreasi:** Hari kerja memuncak pada jam "
                    f"{', '.join(f'{h:02d}.00' for h in sorted(pk))}, "
                    f"sedangkan akhir pekan lebih landai dengan puncak siang hari."
                )
        w = day_sel.groupby("weather_group")["cnt"].mean()
        if {"Cerah", "Buruk"} <= set(w.index) and w["Cerah"] > 0:
            drop = (w["Cerah"] - w["Buruk"]) / w["Cerah"] * 100
            st.markdown(
                f"- **Cuaca buruk:** Rata-rata penyewaan turun **{drop:.1f}%** "
                f"pada kondisi buruk dibanding cerah ({w['Cerah']:,.0f} → {w['Buruk']:,.0f} sepeda/hari)."
            )
        hot = day_sel[day_sel["temp_c"] > 30]
        cold = day_sel[day_sel["temp_c"] < 10]
        if len(hot) and len(cold):
            st.markdown(
                f"- **Suhu ekstrem:** Hari dengan suhu terasa > 30 °C rata-rata "
                f"{hot['cnt'].mean():,.0f} sepeda/hari vs < 10 °C {cold['cnt'].mean():,.0f} sepeda/hari."
            )


def render_data_explorer(day_sel: pd.DataFrame) -> None:
    st.subheader("Eksplorasi Data & Unduh")
    show_cols = [
        "dteday", "season_name", "year", "weekday_name", "day_type",
        "weather_name", "temp_c", "atemp_c", "hum_pct", "windspeed_kph",
        "casual", "registered", "cnt", "demand_group",
    ]
    rename = {
        "dteday": "Tanggal", "season_name": "Musim", "year": "Tahun",
        "weekday_name": "Hari", "day_type": "Tipe Hari", "weather_name": "Cuaca",
        "temp_c": "Suhu (°C)", "atemp_c": "Suhu Terasa (°C)",
        "hum_pct": "Kelembapan (%)", "windspeed_kph": "Angin (km/jam)",
        "casual": "Kasual", "registered": "Terdaftar", "cnt": "Total",
        "demand_group": "Kelompok",
    }
    table = day_sel[show_cols].rename(columns=rename)
    st.dataframe(table, width="stretch", hide_index=True)
    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Unduh data tersaring (CSV)",
        data=csv,
        file_name="bike_sharing_filtered.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    init_session()
    day_df, hour_df = load_data()

    st.title("🚲 Bike Sharing Interactive Dashboard")
    st.caption(
        "Capital Bikeshare, Washington D.C. · 2011–2012 · "
        f"sumber data: {st.session_state.get('_data_source', 'lokal')}"
    )

    with st.sidebar:
        st.header("🎛️ Filter")
        if st.button("🔄 Reset Filter", width="stretch"):
            reset_filters()
            st.rerun()

        date_range = st.date_input(
            "Rentang Tanggal",
            key="flt_date_input",
        )
        st.multiselect(
            "Tahun", options=["2011", "2012"],
            key="flt_years",
        )
        st.multiselect(
            "Musim", options=list(SEASON_MAP.values()),
            key="flt_seasons",
        )
        st.multiselect(
            "Kondisi Cuaca", options=list(WEATHER_MAP.values()),
            key="flt_weathers",
        )
        st.selectbox(
            "Tipe Hari", options=["Semua", "Hari Kerja", "Akhir Pekan / Libur"],
            key="flt_daytype",
        )

    start, end = st.session_state["flt_start"], st.session_state["flt_end"]
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = date_range
        st.session_state["flt_start"], st.session_state["flt_end"] = start, end

    day_sel, hour_sel = apply_filters(
        day_df, hour_df, start, end,
        st.session_state["flt_years"],
        st.session_state["flt_seasons"],
        st.session_state["flt_weathers"],
        st.session_state["flt_daytype"],
    )

    if day_sel.empty or hour_sel.empty:
        st.warning(
            "Data tidak tersedia untuk kombinasi filter ini. "
            "Longgarkan filter tahun/musim/cuaca/tanggal, atau tekan Reset Filter."
        )
        st.stop()

    render_kpis(day_sel)
    st.markdown("---")

    tab_trend, tab1, tab2, tab3, tab_suhu = st.tabs([
        "📈 Tren & Komposisi",
        "🕒 Pertanyaan 1: Jam Sibuk",
        "🌦️ Pertanyaan 2: Pengaruh Cuaca",
        "📦 Pertanyaan 3: Kelompok Permintaan",
        "🌡️ Sensitivitas Suhu",
    ])
    with tab_trend:
        render_trend_chart(day_sel)
        render_donut(day_sel)
    with tab1:
        render_hourly_pattern(hour_sel)
    with tab2:
        render_weather_impact(day_sel)
    with tab3:
        render_demand_groups(day_sel)
    with tab_suhu:
        render_temp_sensitivity(day_sel)

    st.markdown("---")
    render_insights(day_sel, hour_sel)
    render_data_explorer(day_sel)
    st.caption(
        "Sumber data: Bike Sharing Dataset (Capital Bikeshare, Washington D.C., 2011–2012)."
    )


if __name__ == "__main__":
    main()
