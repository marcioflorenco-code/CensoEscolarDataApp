import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
ARQ_ESCOLA = BASE / "data" / "Tabela_Escola_2025_V2.csv"
ARQ_MATRICULA = BASE / "data" / "Tabela_Matricula_2025_V2.csv"
ARQ_JSON = BASE / "ie_paraiba_2025.json"

UF = "PB"
SITUACAO_EM_ATIVIDADE = 1 

RENOMEAR_GEO = {
    "no_regiao_geog_interm": "no_mesorregiao",
    "co_regiao_geog_interm": "co_mesorregiao",
    "no_regiao_geog_imed": "no_microrregiao",
    "co_regiao_geog_imed": "co_microrregiao",
}

COLS_ESCOLA = [
    "no_entidade", "co_entidade", "no_uf", "sg_uf", "co_uf",
    "no_municipio", "co_municipio",
    "no_regiao_geog_interm", "co_regiao_geog_interm",
    "no_regiao_geog_imed", "co_regiao_geog_imed",
    "nu_ano_censo", "no_regiao", "co_regiao",
    "tp_situacao_funcionamento",
]
COLS_MATRICULA = [
    "co_entidade", "qt_mat_bas", "qt_mat_inf", "qt_mat_fund", "qt_mat_med",
    "qt_mat_prof", "qt_mat_eja", "qt_mat_esp",
]
CAMPOS_JSON = [
    "no_entidade", "co_entidade", "no_uf", "sg_uf", "co_uf",
    "no_municipio", "co_municipio", "no_mesorregiao", "co_mesorregiao",
    "no_microrregiao", "co_microrregiao", "nu_ano_censo", "no_regiao", "co_regiao",
    "qt_mat_bas", "qt_mat_inf", "qt_mat_fund", "qt_mat_med",
    "qt_mat_prof", "qt_mat_eja", "qt_mat_esp",
]


def ler_csv(caminho, colunas):
    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin-1",
        usecols=lambda c: c.lower() in colunas,
        low_memory=False,
    )
    df.columns = [c.lower() for c in df.columns]
    return df


def main():
    escolas = ler_csv(ARQ_ESCOLA, COLS_ESCOLA)
    matriculas = ler_csv(ARQ_MATRICULA, COLS_MATRICULA)

    # essa parte vai filtra Paraíba e escolas em atividade
    escolas_pb = escolas[
        (escolas["sg_uf"] == UF)
        & (escolas["tp_situacao_funcionamento"] == SITUACAO_EM_ATIVIDADE)
    ]

    # junta as matrículas pelo código da entidade 
    df = escolas_pb.merge(matriculas, on="co_entidade", how="left")

    # escolas sem registro de matrícula ficam com 0
    colunas_qt = [c for c in COLS_MATRICULA if c.startswith("qt_")]
    df[colunas_qt] = df[colunas_qt].fillna(0).astype(int)

    # vai ajusta nomes e ordem dos campos
    df = df.rename(columns=RENOMEAR_GEO)[CAMPOS_JSON]
    # Códigos geográficos vêm como float no CSV; converte para inteiro
    df[["co_mesorregiao", "co_microrregiao"]] = df[
        ["co_mesorregiao", "co_microrregiao"]
    ].astype(int)
    df = df.sort_values(["no_municipio", "no_entidade"]).reset_index(drop=True)

    # salva o JSON (lista de objetos)
    registros = json.loads(df.to_json(orient="records", force_ascii=False))
    with open(ARQ_JSON, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    print(f"{len(registros)} instituições de ensino da {UF} salvas em {ARQ_JSON.name}")


if __name__ == "__main__":
    main()