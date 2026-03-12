from __future__ import annotations

import pandas as pd

from app.presentation.components import build_pareto_chart
from app.presentation.i18n import LANG_OPTIONS, tr


def test_tr_uses_selected_language_and_fallbacks():
    assert tr("settings", "en") == "Settings"
    assert tr("settings", "pt-BR").startswith("Config")
    assert tr("missing-key", "en") == "missing-key"
    assert LANG_OPTIONS["English"] == "en"


def test_build_pareto_chart_limits_rows_and_keeps_two_traces():
    pareto_df = pd.DataFrame(
        {
            "CATEGORY": ["A", "B", "C"],
            "total": [100, 80, 20],
            "cum_share_pct": [50, 90, 100],
        }
    )

    fig = build_pareto_chart(pareto_df, "CATEGORY", top_n=2)

    assert len(fig.data) == 2
    assert list(fig.data[0].x) == ["A", "B"]
