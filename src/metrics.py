from __future__ import annotations

import pandas as pd


def compute_main_metrics(
    df: pd.DataFrame,
    date_col: str = "ORDERDATE",
    sales_col: str = "SALES",
) -> dict[str, float | str]:
    tmp = df.copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp[sales_col] = pd.to_numeric(tmp[sales_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col, sales_col])

    monthly = (
        tmp.set_index(date_col)[sales_col]
        .resample("ME")
        .sum()
        .reset_index(name="total_vendas")
    )
    monthly["crescimento_pct"] = monthly["total_vendas"].pct_change() * 100
    growth = monthly["crescimento_pct"].dropna()

    if monthly.empty:
        return {
            "receita_total": 0.0,
            "crescimento_medio_pct": 0.0,
            "melhor_periodo": "N/A",
            "pior_periodo": "N/A",
        }

    melhor_idx = growth.idxmax() if not growth.empty else 0
    pior_idx = growth.idxmin() if not growth.empty else 0
    melhor_raw = pd.to_datetime(str(monthly.loc[melhor_idx, date_col]), errors="coerce")
    pior_raw = pd.to_datetime(str(monthly.loc[pior_idx, date_col]), errors="coerce")
    melhor = melhor_raw.strftime("%Y-%m") if pd.notna(melhor_raw) else "N/A"
    pior = pior_raw.strftime("%Y-%m") if pd.notna(pior_raw) else "N/A"

    return {
        "receita_total": float(monthly["total_vendas"].sum()),
        "crescimento_medio_pct": float(growth.mean() if not growth.empty else 0.0),
        "melhor_periodo": melhor,
        "pior_periodo": pior,
    }
