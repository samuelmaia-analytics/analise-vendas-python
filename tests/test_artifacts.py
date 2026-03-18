import pandas as pd
import pytest

from src.artifacts import generate_processed_artifacts
from src.data_contract import load_raw_sales, validate_processed_schema


def test_generate_processed_artifacts(tmp_path):
    df = load_raw_sales()
    files = generate_processed_artifacts(df, tmp_path)

    assert len(files) == 4
    assert all(path.exists() for path in files)

    fato = pd.read_csv(tmp_path / "fato_vendas.csv")
    tempo = pd.read_csv(tmp_path / "dim_tempo.csv")
    produtos = pd.read_csv(tmp_path / "dim_produtos.csv")
    clientes = pd.read_csv(tmp_path / "dim_clientes.csv")
    assert not fato.empty
    assert not tempo.empty
    assert not produtos.empty
    assert not clientes.empty
    fato_ok, fato_missing = validate_processed_schema("fato_vendas.csv", fato)
    tempo_ok, tempo_missing = validate_processed_schema("dim_tempo.csv", tempo)
    produtos_ok, produtos_missing = validate_processed_schema("dim_produtos.csv", produtos)
    clientes_ok, clientes_missing = validate_processed_schema("dim_clientes.csv", clientes)
    assert fato_ok, fato_missing
    assert tempo_ok, tempo_missing
    assert produtos_ok, produtos_missing
    assert clientes_ok, clientes_missing


def test_generate_processed_artifacts_rejects_invalid_input(tmp_path):
    df = pd.DataFrame({"ORDERNUMBER": [1]})

    with pytest.raises(ValueError, match="Dados de entrada sem colunas obrigatorias"):
        generate_processed_artifacts(df, tmp_path)
