from __future__ import annotations

import pandas as pd
import pytest

from app.ui.analytics import (
    build_executive_insights,
    classify_concentration_signal,
    classify_growth_signal,
    compute_pareto,
    compute_yoy,
    format_period_label,
)
from app.ui.i18n import tr


def test_compute_pareto_sorts_and_accumulates_share():
    df = pd.DataFrame(
        {
            "CATEGORY": ["A", "B", "A", "C"],
            "SALES": [100, 50, 50, 25],
        }
    )

    pareto = compute_pareto(df, "CATEGORY", "SALES")

    assert pareto.iloc[0]["CATEGORY"] == "A"
    assert pareto.iloc[0]["share_pct"] == pytest.approx(150 / 225 * 100)
    assert pareto.iloc[-1]["cum_share_pct"] == 100


def test_compute_yoy_generates_yoy_columns():
    dates = pd.date_range("2023-01-31", periods=14, freq="ME")
    df = pd.DataFrame({"ORDERDATE": dates, "SALES": range(100, 114)})

    yoy = compute_yoy(df, "ORDERDATE", "SALES")

    assert list(yoy.columns) == ["ORDERDATE", "total", "yoy_abs", "yoy_pct"]
    assert yoy["yoy_abs"].notna().sum() >= 1


def test_build_insights_and_signals_return_localized_outputs():
    insights = build_executive_insights(
        receita_total=1000,
        crescimento_medio=10,
        mes_pico="Jan (1)",
        top3_share=55.0,
        melhor_periodo="2024-01",
        pior_periodo="2024-02",
        lang="en",
        tr=tr,
    )

    growth_label, growth_class = classify_growth_signal(9.0, "en", tr)
    concentration_label, concentration_class = classify_concentration_signal(75.0, "en", tr)

    assert len(insights) >= 4
    assert growth_label == "Strong traction"
    assert growth_class == "signal-good"
    assert concentration_label == "High risk"
    assert concentration_class == "signal-risk"


def test_format_period_label_formats_dates_and_falls_back_for_unknown_values():
    assert format_period_label("2024-03-31") == "2024-03"
    assert format_period_label("not-a-date") == "not-a-date"
