import pandas as pd

from src.artifacts import generate_processed_artifacts
from src.data_contract import load_raw_sales


def test_generate_processed_artifacts(tmp_path):
    df = load_raw_sales()
    files = generate_processed_artifacts(df, tmp_path)

    assert len(files) == 2
    assert all(path.exists() for path in files)

    fato = pd.read_csv(tmp_path / "fato_vendas.csv")
    tempo = pd.read_csv(tmp_path / "dim_tempo.csv")
    assert not fato.empty
    assert not tempo.empty
