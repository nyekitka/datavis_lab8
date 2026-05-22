from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st



st.set_page_config(
    layout="wide",
    page_title="📊 Business Data Story",
    page_icon="📊",
    initial_sidebar_state="expanded",
)


PALETTE = {
    "primary": "#4F8EF7",
    "secondary": "#F7914F",
    "success": "#4FD1A5",
    "danger": "#F74F6E",
    "warning": "#F7D74F",
    "bg": "#0F1117",
    "card": "#1A1D27",
    "text": "#E8EAF0",
    "muted": "#8B8FA8",
}

SEGMENT_COLORS = {
    "Premium": "#4F8EF7",
    "Standard": "#4FD1A5",
    "Budget": "#F7914F",
}

CATEGORY_COLORS = {
    "Electronics": "#F74F6E",
    "Clothing": "#4F8EF7",
    "Home": "#4FD1A5",
    "Books": "#F7D74F",
    "Sports": "#F7914F",
}

REGION_COLORS = {
    "North": "#4F8EF7",
    "South": "#F74F6E",
    "East": "#4FD1A5",
    "West": "#F7914F",
}



PLOTLY_TEMPLATE = "plotly_dark"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=PALETTE["text"]),
    legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor=PALETTE["muted"], borderwidth=1),
    margin=dict(t=50, b=40, l=10, r=10),
)


st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {PALETTE["bg"]};
        color: {PALETTE["text"]};
    }}

    /* Карточки KPI */
    .kpi-card {{
        background: {PALETTE["card"]};
        border: 1px solid #2A2D3E;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {PALETTE["primary"]};
    }}
    .kpi-label {{
        font-size: 0.85rem;
        color: {PALETTE["muted"]};
        margin-top: 4px;
    }}
    .kpi-delta {{
        font-size: 0.8rem;
        margin-top: 6px;
    }}
    .kpi-delta.positive {{ color: {PALETTE["success"]}; }}
    .kpi-delta.negative {{ color: {PALETTE["danger"]}; }}

    /* Информационные блоки */
    .insight-box {{
        background: linear-gradient(135deg, #1A1D27, #1E2235);
        border-left: 4px solid {PALETTE["primary"]};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    .insight-box.warning {{
        border-left-color: {PALETTE["warning"]};
    }}
    .insight-box.danger {{
        border-left-color: {PALETTE["danger"]};
    }}
    .insight-box.success {{
        border-left-color: {PALETTE["success"]};
    }}

    /* Шаг-заголовок */
    .step-header {{
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {PALETTE["primary"]};
        margin-bottom: 4px;
    }}

    /* Прогресс-бар шагов */
    .progress-bar {{
        display: flex;
        gap: 6px;
        margin-bottom: 8px;
    }}
    .progress-step {{
        height: 4px;
        border-radius: 2px;
        flex: 1;
        background: #2A2D3E;
    }}
    .progress-step.active {{
        background: {PALETTE["primary"]};
    }}
    .progress-step.done {{
        background: {PALETTE["success"]};
    }}

    /* Сайдбар */
    section[data-testid="stSidebar"] {{
        background: {PALETTE["card"]};
        border-right: 1px solid #2A2D3E;
    }}

    div[data-testid="stRadio"] label {{
        font-size: 0.9rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



@st.cache_data
def load_data() -> pd.DataFrame:
    """Загружаем CSV, парсим даты, добавляем вспомогательные колонки."""
    df = pd.read_csv("business_data.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["profit_margin"] = (df["profit"] / df["revenue"] * 100).round(2)
    return df



def apply_layout(
    fig: go.Figure,
    title: str = "",
    height: int = 420
) -> go.Figure:
    """Применяем единый стиль макета к любому графику."""
    fig.update_layout(**PLOTLY_LAYOUT, title=title, height=height)
    fig.update_xaxes(gridcolor="#2A2D3E", zerolinecolor="#2A2D3E")
    fig.update_yaxes(gridcolor="#2A2D3E", zerolinecolor="#2A2D3E")
    return fig


def kpi_card(
    value: str,
    label: str,
    delta: str = "",
    positive: bool = True
) -> str:
    """Генерируем HTML-карточку KPI."""
    delta_class = "positive" if positive else "negative"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """


def insight(
    text: str,
    kind: str = ""
) -> None:
    """Выводим цветной блок с инсайтом."""
    st.markdown(f'<div class="insight-box {kind}">{text}</div>', unsafe_allow_html=True)


def fmt_millions(x: float) -> str:
    """Форматируем число как $X.Xм."""
    return f"${x / 1_000_000:.2f}M"


def sidebar_filters(df: pd.DataFrame, step_key: str) -> pd.DataFrame:
    """
    Фильтры по категории и региону в сайдбаре.
    Возвращает отфильтрованный датафрейм.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Фильтры")

    all_cats = sorted(df["category"].unique())
    selected_cats = st.sidebar.multiselect(
        "Категории",
        options=all_cats,
        default=all_cats,
        key=f"cats_{step_key}",
    )

    all_regions = sorted(df["region"].unique())
    selected_regions = st.sidebar.multiselect(
        "Регионы",
        options=all_regions,
        default=all_regions,
        key=f"regions_{step_key}",
    )

    mask = df["category"].isin(selected_cats) & df["region"].isin(selected_regions)
    return df[mask]


STEPS = [
    "Акт 1 - Обзор",
    "Акт 2 - Аномалия",
    "Акт 3 - Сегменты",
    "Акт 4 - Причина",
    "Акт 5 - Решение",
    "Акт 6 - Рекомендации",
]

if "step" not in st.session_state:
    st.session_state.step = 0

# Сайдбар
with st.sidebar:
    st.markdown("## Business Story")
    st.caption("Интерактивная история бизнес-данных за 2023-2024")
    st.markdown("---")
    st.subheader("Навигация")
    step_choice = st.radio("Выберите акт", STEPS, index=st.session_state.step)
    st.session_state.step = STEPS.index(step_choice)

    st.markdown("---")
    # Кнопки назад/вперёд
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("◀ Назад", use_container_width=True):
            if st.session_state.step > 0:
                st.session_state.step -= 1
                st.rerun()
    with col_next:
        if st.button("Вперёд ▶", use_container_width=True):
            if st.session_state.step < len(STEPS) - 1:
                st.session_state.step += 1
                st.rerun()

# Прогресс-бар вверху страницы
steps_html = "".join(
    f'<div class="progress-step {"done" if i < st.session_state.step else "active" if i == st.session_state.step else ""}"></div>'
    for i in range(len(STEPS))
)
st.markdown(f'<div class="progress-bar">{steps_html}</div>', unsafe_allow_html=True)

# Загружаем данные
df = load_data()

if st.session_state.step == 0:
    st.markdown('<div class="step-header">Акт 1 из 6</div>', unsafe_allow_html=True)
    st.title("Общая динамика бизнеса 2023–2024")

    dff = sidebar_filters(df, "act1")

    total_rev = dff["revenue"].sum()
    total_prof = dff["profit"].sum()
    total_units = dff["units_sold"].sum()
    avg_sat = dff["customer_satisfaction"].mean()

    rev_2023 = dff[dff["year"] == 2023]["revenue"].sum()
    rev_2024 = dff[dff["year"] == 2024]["revenue"].sum()
    rev_growth = (rev_2024 - rev_2023) / rev_2023 * 100

    prof_2023 = dff[dff["year"] == 2023]["profit"].sum()
    prof_2024 = dff[dff["year"] == 2024]["profit"].sum()
    prof_growth = (prof_2024 - prof_2023) / prof_2023 * 100

    cols = st.columns(4)
    cards = [
        (fmt_millions(total_rev), "Суммарная выручка", f"▲ {rev_growth:.1f}% г/г", True),
        (fmt_millions(total_prof), "Суммарная прибыль", f"▲ {prof_growth:.1f}% г/г", True),
        (f"{total_units:,}", "Продано единиц", "", True),
        (f"{avg_sat:.2f} / 5", "Средняя удовлетворённость", "", True),
    ]
    for col, (val, lbl, delta, pos) in zip(cols, cards):
        with col:
            st.markdown(kpi_card(val, lbl, delta, pos), unsafe_allow_html=True)

    st.markdown("---")

    monthly = (
        dff.groupby("month")[["revenue", "profit"]]
        .sum()
        .reset_index()
        .rename(columns={"revenue": "Выручка", "profit": "Прибыль"})
    )

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["Выручка"],
        name="Выручка", mode="lines+markers",
        line=dict(color=PALETTE["primary"], width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Выручка: $%{y:,.0f}<extra></extra>",
    ))
    fig_line.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["Прибыль"],
        name="Прибыль", mode="lines+markers",
        line=dict(color=PALETTE["success"], width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Прибыль: $%{y:,.0f}<extra></extra>",
    ))

    nov23_rows = monthly[monthly["month"] == "2023-11"]
    if not nov23_rows.empty:
        nov23_val = nov23_rows["Выручка"].values[0]
    else:
        nov23_val = monthly["Выручка"].max()

    fig_line.add_annotation(
        x="2023-11", y=nov23_val,
        text="📈 Сезонный пик<br>ноябрь–декабрь",
        showarrow=True, arrowhead=2,
        arrowcolor=PALETTE["warning"], font=dict(color=PALETTE["warning"], size=11),
        bgcolor="rgba(0,0,0,0.5)", bordercolor=PALETTE["warning"],
    )
    apply_layout(fig_line, "📈 Динамика выручки и прибыли по месяцам", height=400)
    st.plotly_chart(fig_line, use_container_width=True)

    cat_monthly = (
        dff.groupby(["month", "category"])["revenue"]
        .sum()
        .reset_index()
    )
    fig_bar = px.bar(
        cat_monthly, x="month", y="revenue", color="category",
        color_discrete_map=CATEGORY_COLORS,
        labels={"revenue": "Выручка ($)", "month": "Месяц", "category": "Категория"},
        hover_data={"revenue": ":,.0f"},
        template=PLOTLY_TEMPLATE,
    )
    apply_layout(fig_bar, "📊 Выручка по категориям (ежемесячно)", height=350)
    st.plotly_chart(fig_bar, use_container_width=True)

    insight(
        "💡 <b>Ключевой инсайт:</b> Бизнес показывает устойчивый рост год к году. "
        "Сезонные пики в ноябре–декабре хорошо выражены. "
        f"В 2024 году выручка выросла на <b>{rev_growth:.1f}%</b> по сравнению с 2023."
    )


elif st.session_state.step == 1:
    st.markdown('<div class="step-header">Акт 2 из 6</div>', unsafe_allow_html=True)
    st.title("Обнаружена аномалия: падение прибыли в Electronics")

    dff = sidebar_filters(df, "act2")


    monthly_cat = (
        dff.groupby(["month", "category"])["profit"]
        .sum()
        .reset_index()
    )
    elec = monthly_cat[monthly_cat["category"] == "Electronics"].copy()
    others = monthly_cat[monthly_cat["category"] != "Electronics"].groupby("month")["profit"].sum().reset_index()
    others["category"] = "Остальные"

    fig_anom = go.Figure()
    fig_anom.add_trace(go.Scatter(
        x=others["month"], y=others["profit"],
        name="Остальные категории", mode="lines",
        line=dict(color=PALETTE["muted"], width=2, dash="dot"),
        hovertemplate="<b>%{x}</b><br>Прибыль (прочие): $%{y:,.0f}<extra></extra>",
    ))
    fig_anom.add_trace(go.Scatter(
        x=elec["month"], y=elec["profit"],
        name="Electronics", mode="lines+markers",
        line=dict(color=PALETTE["danger"], width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Прибыль (Electronics): $%{y:,.0f}<extra></extra>",
    ))

    # Зона аномалии: Q2–Q3 2024
    months = elec["month"].tolist()
    anomaly_start = "2024-04"
    anomaly_end = "2024-09"
    if anomaly_start in months and anomaly_end in months:
        idx_s = months.index(anomaly_start)
        idx_e = months.index(anomaly_end)
        fig_anom.add_vrect(
            x0=anomaly_start, x1=anomaly_end,
            fillcolor=PALETTE["danger"], opacity=0.12,
            layer="below", line_width=0,
        )
        mid_idx = (idx_s + idx_e) // 2
        mid_month = months[mid_idx]
        mid_val = elec.iloc[mid_idx]["profit"] if mid_idx < len(elec) else elec["profit"].min()
        fig_anom.add_annotation(
            x=mid_month, y=mid_val,
            text="Зона падения<br>прибыли",
            showarrow=True, arrowhead=3,
            arrowcolor=PALETTE["danger"],
            font=dict(color=PALETTE["danger"], size=12),
            bgcolor="rgba(0,0,0,0.6)", bordercolor=PALETTE["danger"],
            ax=40, ay=-60,
        )

    apply_layout(fig_anom, "Прибыль Electronics vs. Остальные категории", height=420)
    st.plotly_chart(fig_anom, use_container_width=True)

    st.subheader("Тепловая карта прибыли по категориям и месяцам")
    pivot = (
        dff.groupby(["category", "month"])["profit"]
        .sum()
        .unstack(fill_value=0)
    )
    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0, "#F74F6E"],
            [0.5, "#1A1D27"],
            [1.0, "#4FD1A5"],
        ],
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> | <b>%{x}</b><br>Прибыль: $%{z:,.0f}<extra></extra>",
        colorbar=dict(title="Прибыль ($)"),
    ))
    apply_layout(fig_heat, height=300)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Статистика
    elec_full = dff[dff["category"] == "Electronics"]
    elec_24q2 = elec_full[(elec_full["date"] >= "2024-04-01") & (elec_full["date"] <= "2024-09-30")]
    elec_23 = elec_full[elec_full["year"] == 2023]
    base = elec_23["profit"].sum() / 2
    drop_pct = (elec_24q2["profit"].sum() - base) / base * 100 if base != 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        insight(
            f"<b>Аномалия:</b> В апреле–сентябре 2024 прибыль Electronics просела "
            f"относительно исторического среднего на <b>≈{abs(drop_pct):.0f}%</b>.",
            "warning"
        )
    with col2:
        insight(
            "<b>Гипотеза:</b> Остальные категории не показывают подобного падения. "
            "Значит, проблема специфична для Electronics — нужно копать глубже.",
            "danger"
        )


elif st.session_state.step == 2:
    st.markdown('<div class="step-header">Акт 3 из 6</div>', unsafe_allow_html=True)
    st.title("Анализ сегментов: кто несёт бизнес?")

    dff = sidebar_filters(df, "act3")


    seg_q = (
        dff.groupby(["quarter", "segment"])["revenue"]
        .sum()
        .reset_index()
    )
    fig_stack = px.bar(
        seg_q, x="quarter", y="revenue", color="segment",
        color_discrete_map=SEGMENT_COLORS,
        barmode="stack",
        labels={"revenue": "Выручка ($)", "quarter": "Квартал", "segment": "Сегмент"},
        hover_data={"revenue": ":,.0f"},
        template=PLOTLY_TEMPLATE,
    )
    apply_layout(fig_stack, "Структура выручки по сегментам (квартально)", height=380)
    st.plotly_chart(fig_stack, use_container_width=True)


    bubble = (
        dff.groupby(["category", "segment"])
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            units_sold=("units_sold", "sum"),
            satisfaction=("customer_satisfaction", "mean"),
        )
        .reset_index()
    )
    fig_bubble = px.scatter(
        bubble,
        x="revenue", y="profit",
        size="units_sold",
        color="segment",
        symbol="category",
        color_discrete_map=SEGMENT_COLORS,
        labels={
            "revenue": "Выручка ($)", "profit": "Прибыль ($)",
            "units_sold": "Кол-во единиц", "segment": "Сегмент",
            "category": "Категория", "satisfaction": "Удовлетворённость",
        },
        hover_data={"revenue": ":,.0f", "profit": ":,.0f",
                    "units_sold": ":,d", "satisfaction": ":.2f"},
        size_max=60,
        template=PLOTLY_TEMPLATE,
    )
    apply_layout(fig_bubble, "Выручка vs. Прибыль (размер = объём продаж)", height=430)
    st.plotly_chart(fig_bubble, use_container_width=True)


    seg_summary = (
        dff.groupby("segment")
        .agg(
            Выручка=("revenue", "sum"),
            Прибыль=("profit", "sum"),
            Единиц=("units_sold", "sum"),
            Удовл=("customer_satisfaction", "mean"),
        )
        .reset_index()
    )
    seg_summary["Маржа (%)"] = (seg_summary["Прибыль"] / seg_summary["Выручка"] * 100).round(1)
    seg_summary["Выручка"] = seg_summary["Выручка"].map(lambda x: f"${x:,.0f}")
    seg_summary["Прибыль"] = seg_summary["Прибыль"].map(lambda x: f"${x:,.0f}")
    seg_summary["Удовл"] = seg_summary["Удовл"].map(lambda x: f"{x:.2f}")
    st.dataframe(seg_summary.rename(columns={"segment": "Сегмент"}), use_container_width=True)

    insight(
        "<b>Ключевой инсайт:</b> Сегмент <b>Premium</b> генерирует непропорционально высокую маржу. "
        "Потеря даже небольшой доли Premium-клиентов критически бьёт по прибыли."
    )


elif st.session_state.step == 3:
    st.markdown('<div class="step-header">Акт 4 из 6</div>', unsafe_allow_html=True)
    st.title("Причина: падение удовлетворённости в Electronics")

    dff = sidebar_filters(df, "act4")

    col1, col2 = st.columns(2)

    with col1:
        sat_monthly = (
            dff.groupby(["month", "category"])["customer_satisfaction"]
            .mean()
            .reset_index()
        )
        fig_sat = px.line(
            sat_monthly, x="month", y="customer_satisfaction", color="category",
            color_discrete_map=CATEGORY_COLORS,
            labels={"customer_satisfaction": "Удовлетворённость (1–5)", "month": "Месяц"},
            hover_data={"customer_satisfaction": ":.2f"},
            template=PLOTLY_TEMPLATE,
        )
        for trace in fig_sat.data:
            if trace.name == "Electronics":
                trace.line.width = 3.5
                trace.line.color = PALETTE["danger"]
        fig_sat.add_hline(
            y=3.5, line_dash="dot", line_color=PALETTE["warning"],
            annotation_text="Пороговое значение 3.5",
            annotation_position="top left",
        )
        apply_layout(fig_sat, "Динамика удовлетворённости по категориям", height=380)
        st.plotly_chart(fig_sat, use_container_width=True)

    with col2:
        elec_monthly = (
            dff[dff["category"] == "Electronics"]
            .groupby(["month", "segment"])
            .agg(
                satisfaction=("customer_satisfaction", "mean"),
                profit=("profit", "sum"),
                revenue=("revenue", "sum"),
            )
            .reset_index()
        )
        fig_scatter = px.scatter(
            elec_monthly,
            x="satisfaction", y="profit",
            color="segment",
            color_discrete_map=SEGMENT_COLORS,
            trendline="ols",
            labels={"satisfaction": "Удовлетворённость", "profit": "Прибыль ($)", "segment": "Сегмент"},
            hover_data={"satisfaction": ":.2f", "profit": ":,.0f", "revenue": ":,.0f"},
            template=PLOTLY_TEMPLATE,
        )
        apply_layout(fig_scatter, "Удовлетворённость vs. Прибыль (Electronics)", height=380)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Доля Premium в Electronics по кварталам
    prem_share = (
        dff[dff["category"] == "Electronics"]
        .groupby(["quarter", "segment"])["revenue"]
        .sum()
        .reset_index()
    )
    total_q = prem_share.groupby("quarter")["revenue"].transform("sum")
    prem_share["share"] = prem_share["revenue"] / total_q * 100
    prem_only = prem_share[prem_share["segment"] == "Premium"]

    fig_prem = go.Figure(go.Bar(
        x=prem_only["quarter"], y=prem_only["share"],
        marker_color=PALETTE["primary"],
        hovertemplate="<b>%{x}</b><br>Доля Premium: %{y:.1f}%<extra></extra>",
    ))
    if not prem_only.empty:
        fig_prem.add_annotation(
            x=prem_only["quarter"].iloc[-1],
            y=prem_only["share"].iloc[-1],
            text="Отток Premium",
            showarrow=True, arrowhead=2,
            arrowcolor=PALETTE["danger"],
            font=dict(color=PALETTE["danger"], size=12),
        )
    apply_layout(fig_prem, "Доля Premium-сегмента в выручке Electronics (%)", height=300)
    st.plotly_chart(fig_prem, use_container_width=True)

    insight(
        "<b>Причина установлена:</b> Снижение customer_satisfaction в Electronics ниже "
        "порогового значения 3.5 ведёт к оттоку Premium-клиентов — самого маржинального сегмента. "
        "Тренд-линия подтверждает прямую корреляцию между удовлетворённостью и прибылью.",
        "danger"
    )


elif st.session_state.step == 4:
    st.markdown('<div class="step-header">Акт 5 из 6</div>', unsafe_allow_html=True)
    st.title("What-If: что если улучшить удовлетворённость?")

    dff = sidebar_filters(df, "act5")

    st.markdown(
        "Используйте слайдер ниже, чтобы смоделировать рост удовлетворённости "
        "клиентов в категории **Electronics** и увидеть прогнозируемый эффект на прибыль."
    )

    sat_boost = st.slider(
        "Рост customer_satisfaction в Electronics (%)",
        min_value=0, max_value=30, value=10, step=1,
        format="%d%%",
    )

    elec = dff[dff["category"] == "Electronics"].copy()
    monthly_elec = (
        elec.groupby("month")
        .agg(profit=("profit", "sum"), satisfaction=("customer_satisfaction", "mean"))
        .reset_index()
    )

    if len(monthly_elec) > 1:
        coeffs = np.polyfit(monthly_elec["satisfaction"], monthly_elec["profit"], 1)
        alpha = coeffs[0]
    else:
        alpha = 50_000

    base_sat = monthly_elec["satisfaction"].mean()
    new_sat = base_sat * (1 + sat_boost / 100)
    delta_sat = new_sat - base_sat
    predicted_extra_profit_monthly = alpha * delta_sat
    predicted_extra_profit_annual = predicted_extra_profit_monthly * 12

    base_profit = monthly_elec["profit"].copy()
    new_profit = base_profit + predicted_extra_profit_monthly

    fig_whatif = go.Figure()
    fig_whatif.add_trace(go.Scatter(
        x=monthly_elec["month"], y=base_profit,
        name="Фактическая прибыль", mode="lines",
        line=dict(color=PALETTE["danger"], width=2.5),
        hovertemplate="<b>%{x}</b><br>Факт: $%{y:,.0f}<extra></extra>",
    ))
    fig_whatif.add_trace(go.Scatter(
        x=monthly_elec["month"], y=new_profit,
        name=f"Прогноз (+{sat_boost}% удовл.)", mode="lines+markers",
        line=dict(color=PALETTE["success"], width=2.5, dash="dash"),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>Прогноз: $%{y:,.0f}<extra></extra>",
    ))
    fig_whatif.add_trace(go.Scatter(
        x=monthly_elec["month"].tolist() + monthly_elec["month"].tolist()[::-1],
        y=new_profit.tolist() + base_profit.tolist()[::-1],
        fill="toself",
        fillcolor="rgba(79,209,165,0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Дополнительная прибыль",
        hoverinfo="skip",
    ))
    apply_layout(fig_whatif, f"Прогноз прибыли Electronics при +{sat_boost}% удовлетворённости", height=420)
    st.plotly_chart(fig_whatif, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            kpi_card(f"{base_sat:.2f}", "Базовая удовлетворённость", "", True),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            kpi_card(f"{new_sat:.2f}", "Целевая удовлетворённость", f"+{sat_boost}%", True),
            unsafe_allow_html=True,
        )
    with col3:
        extra = max(predicted_extra_profit_annual, 0)
        st.markdown(
            kpi_card(fmt_millions(extra), "Дополнительная прибыль/год", "прогноз", True),
            unsafe_allow_html=True,
        )

    insight(
        f"<b>Вывод:</b> Повышение удовлетворённости в Electronics на <b>{sat_boost}%</b> "
        f"принесёт дополнительно ~<b>{fmt_millions(max(predicted_extra_profit_annual, 0))}</b> прибыли в год. "
        "Даже небольшие инвестиции в качество продукта и сервис окупаются кратно.",
        "success"
    )

elif st.session_state.step == 5:
    st.markdown('<div class="step-header">Акт 6 из 6</div>', unsafe_allow_html=True)
    st.title("Итоги и рекомендации")

    dff = sidebar_filters(df, "act6")

    st.subheader("Итоговая сводка по категориям и сегментам")
    summary = (
        dff.groupby(["category", "segment"])
        .agg(
            Выручка=("revenue", "sum"),
            Прибыль=("profit", "sum"),
            Единиц=("units_sold", "sum"),
            Удовл=("customer_satisfaction", "mean"),
        )
        .reset_index()
    )
    summary["Маржа (%)"] = (summary["Прибыль"] / summary["Выручка"] * 100).round(1)
    summary = summary.sort_values("Прибыль", ascending=False)
    summary["Выручка"] = summary["Выручка"].map(lambda x: f"${x:,.0f}")
    summary["Прибыль"] = summary["Прибыль"].map(lambda x: f"${x:,.0f}")
    summary["Единиц"] = summary["Единиц"].map(lambda x: f"{x:,d}")
    summary["Удовл"] = summary["Удовл"].map(lambda x: f"{x:.2f}")
    st.dataframe(
        summary.rename(columns={"category": "Категория", "segment": "Сегмент"}),
        use_container_width=True,
        hide_index=True,
    )

    # Маржинальность по категориям
    margin_cat = (
        dff.groupby("category")
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )
    margin_cat["margin"] = (margin_cat["profit"] / margin_cat["revenue"] * 100).round(1)
    margin_cat = margin_cat.sort_values("margin")

    colors = [PALETTE["danger"] if c == "Electronics" else PALETTE["primary"] for c in margin_cat["category"]]
    fig_margin = go.Figure(go.Bar(
        x=margin_cat["margin"],
        y=margin_cat["category"],
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>Маржа: %{x:.1f}%<extra></extra>",
        text=margin_cat["margin"].map(lambda x: f"{x:.1f}%"),
        textposition="outside",
    ))
    elec_margin_rows = margin_cat[margin_cat["category"] == "Electronics"]
    if not elec_margin_rows.empty:
        fig_margin.add_annotation(
            x=elec_margin_rows["margin"].values[0],
            y="Electronics",
            text="Требует внимания",
            showarrow=True, arrowhead=2,
            arrowcolor=PALETTE["danger"],
            font=dict(color=PALETTE["danger"], size=12),
            ax=80, ay=0,
        )
    apply_layout(fig_margin, "📊 Маржинальность по категориям (%)", height=300)
    st.plotly_chart(fig_margin, use_container_width=True)

    st.markdown("---")
    st.subheader("Рекомендации")

    rec_cols = st.columns(3)
    recs = [
        (
            "Качество Electronics",
            "Провести аудит возвратов и жалоб. Ввести расширенную гарантию. "
            "Целевые инвестиции в контроль качества поставщиков.",
            "primary",
        ),
        (
            "Удержание Premium",
            "Запустить программу лояльности для Premium-сегмента. "
            "Персональный менеджер + приоритетная поддержка 24/7.",
            "success",
        ),
        (
            "Использовать рост",
            "Направить дополнительный доход от сезонных пиков (Q4) "
            "на маркетинг в слабых кварталах (Q1-Q2) для сглаживания сезонности.",
            "warning",
        ),
    ]
    for col, (title, text, kind) in zip(rec_cols, recs):
        with col:
            st.markdown(
                f'<div class="insight-box {kind}"><b>{title}</b><br><br>{text}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
