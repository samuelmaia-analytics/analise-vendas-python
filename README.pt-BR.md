# Pipeline de Analytics de Vendas

[README em inglês](README.md)

Este repositório foi estruturado para parecer e se comportar como um pequeno sistema analítico real. Ele lê um CSV bruto de vendas, valida qualidade de dados, materializa saídas curadas, gera um resumo executivo e reaproveita o mesmo core analítico em uma aplicação Streamlit.

## Valor de negócio

O pipeline responde a perguntas centrais de gestão comercial:

- quanto de receita foi gerado
- se a receita está acelerando ou desacelerando
- quais períodos performaram melhor e pior
- quão concentrada está a receita por linha de produto
- se a base é confiável o suficiente para consumo analítico

## Arquitetura

```text
.
|-- .github/workflows/      pipelines de CI
|-- app/                    camada de apresentação Streamlit
|   |-- presentation/       componentes, i18n e adapters de UI
|   `-- streamlit_app.py    entrypoint do dashboard
|-- assets/                 imagens estáticas para documentação e portfólio
|-- data/
|   |-- raw/                dataset versionado de entrada
|   `-- processed/          saídas curadas geradas pelo pipeline
|-- docs/                   notas de arquitetura e engenharia
|-- legacy/                 fallback compatível com a estrutura antiga
|-- notebooks/              exploração isolada do fluxo principal
|-- reports/                saídas executivas e analíticas geradas
|-- scripts/                scripts de manutenção do repositório
|-- src/sales_analytics/
|   |-- cli.py              interface oficial de linha de comando
|   |-- ingestion.py        resolução da origem e fingerprint do dataset
|   |-- data_contract.py    contratos de schema da entrada e das saídas
|   |-- quality.py          validações de qualidade de dados
|   |-- transformations.py  normalização da base analítica
|   |-- metrics.py          KPI, crescimento, YoY e Pareto
|   |-- artifacts.py        materialização dos artefatos curados
|   |-- batch_pipeline.py   orquestração batch e manifesto de execução
|   |-- reporting.py        publicação das saídas executivas
|   |-- config.py           paths e runtime por ambiente
|   |-- logging_utils.py    logging centralizado
|   `-- settings.py         limites de runtime do Streamlit
|-- tests/                  regressão funcional, contratos, CLI e app
|-- .env.example            template de configuração local
|-- app.py                  entrypoint raiz do Streamlit
|-- pyproject.toml          configuração de pacote e ferramentas
`-- README.pt-BR.md
```

Gerado em runtime, não versionado por padrão:

- `data/state/` para manifestos e estado de execução
- arquivos dentro de `data/processed/` e `reports/` são sobrescritos a cada reprocessamento

Fluxo oficial:

1. Resolver a origem da base e calcular fingerprint SHA-256.
2. Validar schema e qualidade.
3. Normalizar a base analítica.
4. Calcular KPI, crescimento, YoY e Pareto.
5. Materializar artefatos:
   - `fato_vendas.csv`
   - `dim_tempo.csv`
   - `dim_produtos.csv`
   - `dim_clientes.csv`
6. Persistir saídas operacionais:
   - `executive_summary.csv`
   - `cleaned_sales.csv`
   - `periodic_sales.csv`
   - `yoy_sales.csv`
   - `pareto_sales.csv`
   - `pipeline_manifest.json`
   - `quality_report.json`
   - `kpis.json`
   - `latest_success.json`
   - `latest_failure.json` em caso de erro
7. Opcionalmente manter snapshots por execução em:
   - `data/processed/history/<run_id>/`
   - `reports/history/<run_id>/`
   - `data/state/runs/<run_id>/`
8. Gerar dicionário de dados orientado a contrato:
   - `reports/data_dictionary.md`

## Confiabilidade

- Escrita idempotente: reprocessamentos sobrescrevem os mesmos destinos.
- Escrita atômica: evita arquivos parciais em caso de falha no meio da execução.
- Reprocessável: o pipeline pode ser executado novamente a partir da mesma base bruta.
- Rastreável: cada execução registra fingerprint, parâmetros, qualidade e KPI.
- Auditável historicamente: snapshots por `run_id` preservam o que cada execução gerou.
- Retenção configurável: snapshots antigos podem ser removidos automaticamente conforme a política do ambiente.
- Retenção por idade: snapshots também podem ser limpos por janela temporal, não apenas por quantidade de execuções.
- Freshness configurável: o pipeline pode sinalizar base defasada com referência e limite definidos por ambiente.

## Como rodar

Instalação:

```bash
pip install -e ".[dev]"
```

Configuração opcional copiando `.env.example` para `.env`:

```bash
# exemplo
# copie .env.example para .env
```

Executar o pipeline batch completo:

```bash
sales-analytics run-pipeline
```

Exportar apenas o resumo executivo:

```bash
sales-analytics export-summary
```

Gerar o dicionário de dados:

```bash
sales-analytics generate-data-dictionary
```

Abrir a aplicação:

```bash
streamlit run app.py
```

## Qualidade

```bash
ruff check .
black --check .
isort . --check-only
mypy src
pytest
```

O projeto também possui `pre-commit` e CI no GitHub Actions com lint, tipagem, testes e validação de build.

## Decisões técnicas

- `pandas` foi mantido como motor principal porque o escopo não justifica computação distribuída.
- A modelagem curada segue um formato star-schema enxuto, suficiente para mostrar disciplina de dados sem overengineering.
- A camada Streamlit consome o mesmo core do pipeline batch, evitando duplicação de regra de negócio.
- O dicionário de dados é gerado a partir dos contratos em código, reduzindo drift entre implementação e documentação.

## Trade-offs

- Ainda não há scheduler, orquestrador externo ou armazenamento em nuvem.
- Os contratos são intencionais e leves; não substituem uma plataforma formal de data quality.
- O pipeline é orientado a arquivo local, então retry fica limitado ao contexto atual.

## Container

Build:

```bash
docker build -t sales-analytics-portfolio .
```

Executar o pipeline batch no container:

```bash
docker run --rm -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" sales-analytics-portfolio
```

Smoke test da CLI no container:

```bash
docker run --rm sales-analytics-portfolio sales-analytics summary
```

Executar o dashboard no container:

```bash
docker run --rm -p 8501:8501 -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" sales-analytics-portfolio streamlit run app.py --server.address 0.0.0.0
```

## Roadmap

- snapshots históricos por execução
- assertions de freshness
- containerização
- modelagem warehouse/dbt-like para consumo downstream
