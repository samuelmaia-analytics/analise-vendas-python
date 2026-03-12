from __future__ import annotations

from datetime import datetime
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_TITLE = "Revenue Intelligence - Samuel Maia"
APP_ICON = ":bar_chart:"
LAYOUT = "wide"

COLOR_REVENUE = "#0b3c5d"
COLOR_GROWTH = "#c2410c"
COLOR_PARETO_BAR = "#0f766e"
COLOR_PARETO_LINE = "#b45309"
COLOR_YOY = "#1d4ed8"
PLOT_FONT = "Segoe UI, Segoe UI Variable, Helvetica Neue, Arial, sans-serif"


def build_pareto_chart(pareto_df: pd.DataFrame, dim_col: str, top_n: int = 15) -> go.Figure:
    plot_df = pareto_df.head(top_n).copy()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=plot_df[dim_col].astype(str),
            y=plot_df["total"],
            name="Total",
            marker_color=COLOR_PARETO_BAR,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=plot_df[dim_col].astype(str),
            y=plot_df["cum_share_pct"],
            name="% acumulado",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=COLOR_PARETO_LINE, width=2.5),
        )
    )
    fig.update_layout(
        template="plotly_white",
        height=420,
        xaxis_title=dim_col,
        yaxis=dict(title="Total", showgrid=True),
        yaxis2=dict(title="% acumulado", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family=PLOT_FONT),
        margin=dict(l=30, r=30, t=30, b=30),
    )
    return fig


def inject_css() -> None:
    css = """
<style>
    :root { --ink-900: #0f172a; --ink-700: #334155; --surface: #ffffff; --line: #dbe4ef; --brand-1: #0f766e; --brand-2: #0b3c5d; --brand-3: #c2410c; }
    .stApp { background: radial-gradient(circle at 2% 2%, #e0f2fe 0, transparent 36%), radial-gradient(circle at 94% 7%, #ffedd5 0, transparent 35%), #f1f5f9; font-family: "Segoe UI", "Segoe UI Variable", "Helvetica Neue", Arial, sans-serif; color: var(--ink-900); }
    .block-container { padding-top: 1rem; padding-bottom: 1.8rem; max-width: 1380px; }
    .hero-wrap { background: linear-gradient(120deg, var(--brand-2) 0%, var(--brand-1) 52%, #0ea5e9 100%); border-radius: 20px; padding: 1.25rem 1.35rem; margin-bottom: 0.85rem; color: #f8fafc; box-shadow: 0 14px 30px rgba(11, 60, 93, 0.24); }
    .hero-title { margin: 0; font-size: 2.05rem; line-height: 1.2; font-weight: 760; letter-spacing: -0.02em; }
    .hero-subtitle { margin: 0.45rem 0 0 0; font-size: 0.96rem; color: #e2e8f0; }
    .hero-badges { margin-top: 0.65rem; display: flex; gap: 0.45rem; flex-wrap: wrap; }
    .hero-badge { border: 1px solid rgba(255, 255, 255, 0.32); border-radius: 999px; padding: 0.2rem 0.58rem; font-size: 0.74rem; color: #ecfeff; background: rgba(255, 255, 255, 0.1); }
    [data-testid="stSidebar"] { border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }
    [data-testid="stSidebar"] * { color: var(--ink-900) !important; }
    [data-testid="stSidebar"] .stFileUploader *, [data-testid="stSidebar"] div[data-baseweb="select"] * { color: #f8fafc !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] { background-color: #0f172a !important; border-radius: 8px; }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea { color: #f8fafc !important; background-color: #0f172a !important; }
    [data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 0.48rem 0.75rem; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06); }
    [data-testid="stMetricLabel"] { text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.72rem; font-weight: 700; color: #64748b !important; }
    [data-testid="stMetricValue"] { color: var(--ink-900) !important; font-weight: 760 !important; }
    [data-testid="stMetricDelta"] { color: #0f766e !important; }
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] span { color: var(--ink-900); }
    .section-card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 0.78rem 0.94rem; margin-bottom: 0.8rem; }
    .proof-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.6rem; margin: 0.1rem 0 0.8rem 0; }
    .proof-card { background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border: 1px solid var(--line); border-radius: 12px; padding: 0.55rem 0.7rem; }
    .proof-k { font-size: 0.74rem; color: var(--ink-700); margin: 0; }
    .proof-v { font-size: 1.04rem; margin: 0.1rem 0 0 0; color: var(--ink-900); font-weight: 760; }
    .snapshot-list { margin: 0; padding-left: 1.1rem; color: var(--ink-900); }
    .snapshot-list li { margin-bottom: 0.25rem; }
    .signal-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.7rem; margin-top: 0.4rem; }
    .signal-card { border-radius: 10px; padding: 0.72rem 0.8rem; border: 1px solid transparent; }
    .signal-title { font-size: 0.78rem; color: var(--ink-700); margin-bottom: 0.2rem; }
    .signal-value { font-size: 1rem; font-weight: 700; color: var(--ink-900); }
    .signal-good { background: #ecfdf5; border-color: #86efac; } .signal-warn { background: #fffbeb; border-color: #fde68a; } .signal-risk { background: #fef2f2; border-color: #fca5a5; }
    .lead-strip { background: linear-gradient(90deg, #0b3c5d 0%, #0f766e 50%, #c2410c 100%); border-radius: 14px; padding: 0.8rem 0.95rem; margin: 0.85rem 0; color: #f8fafc; display: grid; grid-template-columns: 1.6fr 1fr 1fr; gap: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.2); }
    .lead-title { margin: 0; font-weight: 780; font-size: 1.02rem; } .lead-txt { margin: 0.2rem 0 0 0; font-size: 0.84rem; color: #e2e8f0; }
    .lead-k { margin: 0; font-size: 0.72rem; color: #dbeafe; text-transform: uppercase; letter-spacing: 0.05em; } .lead-v { margin: 0.1rem 0 0 0; font-size: 1.08rem; font-weight: 760; }
    [data-baseweb="tab-list"] { gap: 0.35rem; } [data-baseweb="tab"] { border-radius: 10px; background: #e2e8f0; border: 1px solid #d1d9e6; color: var(--ink-700); font-weight: 650; padding: 0.4rem 0.65rem; }
    [aria-selected="true"][data-baseweb="tab"] { background: #0b3c5d; border-color: #0b3c5d; color: #f8fafc; }
    @media (max-width: 980px) { .signal-grid, .proof-grid, .lead-strip { grid-template-columns: 1fr; } }
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


def render_header(origem: str | None, dados_reais: bool, lang: str, tr: Callable[..., str]) -> None:
    fonte = origem if origem else tr("simulated_data", lang)
    tipo = tr("real_data", lang) if dados_reais else tr("demo_data", lang)
    st.markdown(
        f"""
<div class='hero-wrap'>
    <h1 class='hero-title'>{tr('hero_title', lang)}</h1>
    <p class='hero-subtitle'>{tr('hero_subtitle', lang)}</p>
    <p class='hero-subtitle'><strong>{tr('source', lang)}:</strong> {fonte} | <strong>{tr('type', lang)}:</strong> {tipo} | <strong>{tr('updated', lang)}:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    <div class='hero-badges'>
        <span class='hero-badge'>{tr('badge_1', lang)}</span>
        <span class='hero-badge'>{tr('badge_2', lang)}</span>
        <span class='hero-badge'>{tr('badge_3', lang)}</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_proof_strip(periodos: int, dimensoes: int, top3_share: float | None, crescimento_medio: float, lang: str, tr: Callable[..., str]) -> None:
    concentracao = f"{top3_share:.1f}%" if top3_share is not None else tr("na", lang)
    crescimento = f"{crescimento_medio:.1f}%" if pd.notna(crescimento_medio) else tr("na", lang)
    st.markdown(
        f"""
<div class='proof-grid'>
    <div class='proof-card'><p class='proof-k'>{tr('proof_scale', lang)}</p><p class='proof-v'>{periodos} {tr('periods', lang)}</p></div>
    <div class='proof-card'><p class='proof-k'>{tr('proof_dims', lang)}</p><p class='proof-v'>{dimensoes}</p></div>
    <div class='proof-card'><p class='proof-k'>{tr('proof_top3', lang)}</p><p class='proof-v'>{concentracao}</p></div>
    <div class='proof-card'><p class='proof-k'>{tr('proof_growth', lang)}</p><p class='proof-v'>{crescimento}</p></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_lead_strip(
    receita_total: float,
    crescimento_medio: float,
    top3_share: float | None,
    dados_reais: bool,
    lang: str,
    tr: Callable[..., str],
    format_currency: Callable[[float, str], str],
) -> None:
    crescimento = f"{crescimento_medio:.1f}%" if pd.notna(crescimento_medio) else tr("na", lang)
    concentracao = f"{top3_share:.1f}%" if top3_share is not None else tr("na", lang)
    origem_label = tr("dataset_real", lang) if dados_reais else tr("dataset_demo", lang)
    st.markdown(
        f"""
<div class='lead-strip'>
    <div>
        <p class='lead-title'>{tr('lead_title', lang)}</p>
        <p class='lead-txt'>{tr('lead_text', lang)}</p>
    </div>
    <div>
        <p class='lead-k'>{tr('lead_revenue', lang)}</p>
        <p class='lead-v'>{format_currency(receita_total, '$')}</p>
        <p class='lead-txt'>{origem_label}</p>
    </div>
    <div>
        <p class='lead-k'>{tr('lead_headline', lang)}</p>
        <p class='lead-v'>Growth {crescimento}</p>
        <p class='lead-txt'>Top 3 share {concentracao}</p>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
