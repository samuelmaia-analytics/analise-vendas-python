from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from typing import Callable

from src.sales_analytics.metrics import compute_growth_over_period

from app.ui.data import format_currency, safe_to_datetime, safe_to_numeric


def compute_yoy(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    freq: str = "ME",
) -> pd.DataFrame:
    tmp = df[[date_col, value_col]].copy()
    tmp[date_col] = safe_to_datetime(tmp[date_col])
    tmp[value_col] = safe_to_numeric(tmp[value_col])
    tmp = tmp.dropna(subset=[date_col, value_col])

    agg = (
        tmp.set_index(date_col)
        .resample(freq)[value_col]
        .sum()
        .reset_index()
        .rename(columns={value_col: "total"})
    )
    agg["yoy_abs"] = agg["total"] - agg["total"].shift(12)
    agg["yoy_pct"] = (agg["total"] / agg["total"].shift(12) - 1) * 100
    return agg


def compute_pareto(df: pd.DataFrame, dim_col: str, value_col: str) -> pd.DataFrame:
    tmp = df[[dim_col, value_col]].copy()
    tmp[value_col] = safe_to_numeric(tmp[value_col])
    tmp = tmp.dropna(subset=[dim_col, value_col])

    pareto = (
        tmp.groupby(dim_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={value_col: "total"})
    )
    total_all = pareto["total"].sum()
    pareto["share_pct"] = (pareto["total"] / total_all) * 100 if total_all else 0
    pareto["cum_share_pct"] = pareto["share_pct"].cumsum()
    pareto["rank"] = np.arange(1, len(pareto) + 1)
    return pareto


@st.cache_data(show_spinner=False)
def calcular_crescimento_cached(
    df: pd.DataFrame,
    coluna_data: str,
    coluna_valor: str,
    periodo: str,
) -> pd.DataFrame:
    return compute_growth_over_period(
        df=df.copy(),
        date_col=coluna_data,
        sales_col=coluna_valor,
        period=periodo,
    )


def format_period_label(value: object) -> str:
    try:
        parsed = pd.to_datetime(str(value), errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%Y-%m")
    except Exception:
        pass
    return str(value)


def build_executive_insights(
    receita_total: float,
    crescimento_medio: float,
    mes_pico: str,
    top3_share: float | None,
    melhor_periodo: str,
    pior_periodo: str,
    lang: str,
    tr: Callable[..., str],
) -> list[str]:
    insights = [
        tr("insight_revenue", lang, value=format_currency(receita_total, "$")),
        tr("insight_peak", lang, value=mes_pico),
    ]

    if pd.notna(crescimento_medio):
        direcao = tr("expansion", lang) if crescimento_medio >= 0 else tr("retraction", lang)
        insights.append(tr("insight_growth", lang, direction=direcao, value=crescimento_medio))

    if top3_share is not None:
        insights.append(tr("insight_top3", lang, value=top3_share))

    insights.append(tr("insight_range", lang, best=melhor_periodo, worst=pior_periodo))
    return insights


def classify_growth_signal(value: float, lang: str, tr: Callable[..., str]) -> tuple[str, str]:
    if pd.isna(value):
        return tr("na", lang), "signal-warn"
    if value >= 8:
        return tr("growth_strong", lang), "signal-good"
    if value >= 2:
        return tr("growth_moderate", lang), "signal-warn"
    return tr("growth_weak", lang), "signal-risk"


def classify_concentration_signal(value: float | None, lang: str, tr: Callable[..., str]) -> tuple[str, str]:
    if value is None or pd.isna(value):
        return tr("na", lang), "signal-warn"
    if value <= 50:
        return tr("risk_low", lang), "signal-good"
    if value <= 70:
        return tr("risk_moderate", lang), "signal-warn"
    return tr("risk_high", lang), "signal-risk"
