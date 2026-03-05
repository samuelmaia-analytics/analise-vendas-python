# scripts/analise_crescimento.py
import pandas as pd
import os
import glob


def encontrar_arquivo_vendas():
    """
    Procura especificamente por arquivos de vendas/fatos, não dimensões.
    """
    # Padrões de nomes que indicam tabelas de vendas/fatos
    padroes_vendas = [
        "fato_vendas*.csv",
        "vendas*.csv",
        "sales*.csv",
        "orders*.csv",
        "pedidos*.csv",
        "*venda*.csv",
        "*sales*.csv",
    ]

    # Primeiro, procurar na pasta data/processed
    for padrao in padroes_vendas:
        caminho_completo = os.path.join("data", "processed", padrao)
        arquivos = glob.glob(caminho_completo)
        if arquivos:
            print(f"📁 Arquivo de vendas encontrado: {arquivos[0]}")
            return arquivos[0]

    # Fallback: legacy/dados_processados
    for padrao in padroes_vendas:
        caminho_completo = os.path.join("legacy", "dados_processados", padrao)
        arquivos = glob.glob(caminho_completo)
        if arquivos:
            print(f"📁 Arquivo de vendas encontrado: {arquivos[0]}")
            return arquivos[0]

    # Se não encontrar, procurar na pasta data/raw
    for padrao in padroes_vendas:
        caminho_completo = os.path.join("data", "raw", padrao)
        arquivos = glob.glob(caminho_completo)
        if arquivos:
            print(f"📁 Arquivo de vendas encontrado: {arquivos[0]}")
            return arquivos[0]

    # Fallback: legacy/dados
    for padrao in padroes_vendas:
        caminho_completo = os.path.join("legacy", "dados", padrao)
        arquivos = glob.glob(caminho_completo)
        if arquivos:
            print(f"📁 Arquivo de vendas encontrado: {arquivos[0]}")
            return arquivos[0]

    return None


def calcular_crescimento(dados, coluna_data=None, coluna_valor=None, periodo="M"):
    """
    Calcula o crescimento percentual das vendas entre períodos consecutivos.
    Suporta Pandas versão 2.0+ com nova sintaxe de frequências.
    """
    # Se as colunas não foram especificadas, tentar identificar automaticamente
    if coluna_data is None:
        # Procurar colunas de data - especificamente DATE_ID no seu caso
        colunas_data = [
            col
            for col in dados.columns
            if any(
                termo in col.lower()
                for termo in ["date", "data", "id"]  # Incluindo 'id' para DATE_ID
            )
        ]

        # Priorizar colunas que parecem ser de data
        for col in colunas_data:
            if "date" in col.lower() or "data" in col.lower():
                coluna_data = col
                break

        if coluna_data is None and colunas_data:
            coluna_data = colunas_data[0]

        if coluna_data:
            print(f"📅 Coluna de data identificada: {coluna_data}")
        else:
            raise ValueError("Não foi possível identificar uma coluna de data")

    if coluna_valor is None:
        # Procurar colunas de valor - especificamente SALES no seu caso
        colunas_valor = [
            col
            for col in dados.columns
            if any(
                termo in col.lower()
                for termo in [
                    "sales",
                    "venda",
                    "price",
                    "preço",
                    "total",
                    "amount",
                    "valor",
                ]
            )
        ]

        if colunas_valor:
            coluna_valor = colunas_valor[0]
            print(f"💰 Coluna de valor identificada: {coluna_valor}")
        else:
            # Se não encontrar, pode ser uma coluna numérica
            colunas_numericas = dados.select_dtypes(
                include=["float64", "int64"]
            ).columns
            if len(colunas_numericas) > 0:
                coluna_valor = colunas_numericas[0]
                print(f"💰 Usando coluna numérica: {coluna_valor}")
            else:
                raise ValueError("Não foi possível identificar uma coluna de valor")

    # Converter data - para seu caso específico, DATE_ID parece ser numérico
    print("\n🔄 Processando dados...")

    # Verificar o tipo da coluna de data
    if dados[coluna_data].dtype in ["int64", "float64"]:
        # Se for numérico, pode ser um ID - precisamos de uma data real
        print(
            f"⚠️ A coluna {coluna_data} é numérica. Precisamos de uma coluna de data real."
        )
        print("📋 Colunas disponíveis para data:")
        colunas_reais = [
            col
            for col in dados.columns
            if "date" in col.lower() or "data" in col.lower()
        ]
        if colunas_reais:
            coluna_data = colunas_reais[0]
            print(f"✅ Usando coluna: {coluna_data}")
        else:
            # Se não houver coluna de data, criar uma sequência de datas baseada no índice
            print("⚠️ Nenhuma coluna de data encontrada. Criando datas sequenciais...")
            dados["DATA_ANALISE"] = pd.date_range(
                start="2003-01-01", periods=len(dados), freq="D"
            )
            coluna_data = "DATA_ANALISE"

    # Garantir que a coluna de data seja datetime
    dados[coluna_data] = pd.to_datetime(dados[coluna_data], errors="coerce")

    # Remover linhas com data inválida
    dados_limpos = dados.dropna(subset=[coluna_data])
    if len(dados_limpos) < len(dados):
        print(
            f"⚠️ {len(dados) - len(dados_limpos)} linhas com data inválida foram removidas"
        )

    # Mapeamento de períodos para nova sintaxe do Pandas (versão 2.0+)
    freq_map = {
        "M": "ME",  # Month End (antes era 'M')
        "MS": "MS",  # Month Start (mantém)
        "T": "QE",  # Quarter End (antes era 'Q')
        "QS": "QS",  # Quarter Start (mantém)
        "A": "YE",  # Year End (antes era 'A')
        "AS": "YS",  # Year Start (antes era 'AS')
    }

    # Agrupar por período com a nova sintaxe
    if periodo.upper() == "M":
        freq = freq_map["M"]
        vendas_periodo = (
            dados_limpos.resample(freq, on=coluna_data)[coluna_valor]
            .sum()
            .reset_index()
        )
        vendas_periodo.columns = [coluna_data, "total_vendas"]
        periodo_nome = "Mensal"
    elif periodo.upper() == "T":
        freq = freq_map["T"]
        vendas_periodo = (
            dados_limpos.resample(freq, on=coluna_data)[coluna_valor]
            .sum()
            .reset_index()
        )
        vendas_periodo.columns = [coluna_data, "total_vendas"]
        periodo_nome = "Trimestral"
    elif periodo.upper() == "A":
        freq = freq_map["A"]
        vendas_periodo = (
            dados_limpos.resample(freq, on=coluna_data)[coluna_valor]
            .sum()
            .reset_index()
        )
        vendas_periodo.columns = [coluna_data, "total_vendas"]
        periodo_nome = "Anual"
    else:
        raise ValueError(
            "Período deve ser 'M' (mensal), 'T' (trimestral) ou 'A' (anual)"
        )

    # Calcular crescimento
    vendas_periodo["crescimento_%"] = vendas_periodo["total_vendas"].pct_change() * 100
    vendas_periodo["crescimento_%"] = vendas_periodo["crescimento_%"].round(2)

    # Formatar data para exibição
    vendas_periodo[coluna_data] = vendas_periodo[coluna_data].dt.strftime("%Y-%m-%d")

    print(f"\n📊 Análise de Crescimento {periodo_nome}")
    print("-" * 60)
    print(vendas_periodo.to_string(index=False))

    # Estatísticas (ignorando NaN do primeiro período)
    crescimento_valido = vendas_periodo["crescimento_%"].dropna()
    if len(crescimento_valido) > 0:
        crescimento_medio = crescimento_valido.mean()
        crescimento_min = crescimento_valido.min()
        crescimento_max = crescimento_valido.max()

        print(f"\n📈 Crescimento médio: {crescimento_medio:.2f}%")
        print(f"📉 Menor crescimento: {crescimento_min:.2f}%")
        print(f"📊 Maior crescimento: {crescimento_max:.2f}%")

        # Períodos com melhor e pior desempenho
        melhor_periodo = vendas_periodo.loc[crescimento_valido.idxmax(), coluna_data]
        pior_periodo = vendas_periodo.loc[crescimento_valido.idxmin(), coluna_data]

        print(f"🏆 Melhor período: {melhor_periodo} ({crescimento_max:.2f}%)")
        print(f"📉 Pior período: {pior_periodo} ({crescimento_min:.2f}%)")

    return vendas_periodo


def analisar_estrutura_dados(df):
    """Analisa a estrutura dos dados para ajudar na configuração"""
    print("\n🔍 Análise da estrutura dos dados:")
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Colunas: {list(df.columns)}")

    print("\n📊 Tipos de dados:")
    for col in df.columns:
        print(f"   {col}: {df[col].dtype}")

    # Verificar colunas de data potenciais
    print("\n📅 Possíveis colunas de data:")
    for col in df.columns:
        if any(termo in col.lower() for termo in ["date", "data", "id"]):
            amostra = df[col].iloc[0] if len(df) > 0 else "N/A"
            print(f"   • {col} (ex: {amostra})")

    # Verificar colunas de valor potenciais
    print("\n💰 Possíveis colunas de valor:")
    for col in df.columns:
        if any(termo in col.lower() for termo in ["sales", "price", "total", "quant"]):
            if df[col].dtype in ["float64", "int64"]:
                amostra = df[col].iloc[0] if len(df) > 0 else "N/A"
                print(f"   • {col} (ex: {amostra})")


def main():
    print("🚀 Iniciando análise de crescimento de vendas...")

    # Carregar dados de vendas
    caminho_vendas = encontrar_arquivo_vendas()

    if not caminho_vendas:
        print("\n❌ Não foi possível encontrar dados de vendas.")
        print("Por favor, verifique se existe um arquivo de vendas nas pastas:")
        print("  - data/processed/")
        print("  - data/raw/")
        print("  - legacy/dados_processados/ (legado)")
        print("  - legacy/dados/ (legado)")
        return

    print(f"📥 Carregando dados de: {caminho_vendas}")
    df = pd.read_csv(caminho_vendas)

    # Analisar estrutura dos dados
    analisar_estrutura_dados(df)

    print("\n" + "=" * 60)
    print("Opções de análise:")
    print("1. Crescimento Mensal")
    print("2. Crescimento Trimestral")
    print("3. Crescimento Anual")
    print("4. Todas as análises")
    print("5. Análise customizada (especificar colunas)")

    opcao = input("\nEscolha uma opção (1-5): ").strip()

    if opcao == "5":
        print("\n📝 Configuração customizada:")
        print(f"Colunas disponíveis: {list(df.columns)}")
        col_data = input("Nome da coluna de data: ").strip()
        col_valor = input("Nome da coluna de valor: ").strip()

        print("\n" + "=" * 60)
        calcular_crescimento(
            df, coluna_data=col_data, coluna_valor=col_valor, periodo="M"
        )
        print("\n" + "=" * 60)
        calcular_crescimento(
            df, coluna_data=col_data, coluna_valor=col_valor, periodo="T"
        )
        print("\n" + "=" * 60)
        calcular_crescimento(
            df, coluna_data=col_data, coluna_valor=col_valor, periodo="A"
        )
    elif opcao == "4":
        calcular_crescimento(df, periodo="M")
        print("\n" + "=" * 60)
        calcular_crescimento(df, periodo="T")
        print("\n" + "=" * 60)
        calcular_crescimento(df, periodo="A")
    elif opcao == "1":
        calcular_crescimento(df, periodo="M")
    elif opcao == "2":
        calcular_crescimento(df, periodo="T")
    elif opcao == "3":
        calcular_crescimento(df, periodo="A")
    else:
        print("Opção inválida. Executando análise mensal...")
        calcular_crescimento(df, periodo="M")


if __name__ == "__main__":
    main()
