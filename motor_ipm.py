
import numpy as np
import pandas as pd


def normalizar_0_100(serie):
    minimo = serie.min()
    maximo = serie.max()

    if maximo > minimo:
        return (serie - minimo) / (maximo - minimo) * 100

    return pd.Series(0.0, index=serie.index)


def calcular_publico_alvo(df, sexo, faixas_etarias):
    resultado = df.copy()

    faixas_validas = [
        "0_9", "10_19", "20_29", "30_39",
        "40_49", "50_59", "60_69", "70_mais"
    ]

    if sexo not in ["homens", "mulheres", "ambos"]:
        raise ValueError("Sexo inválido.")

    if not faixas_etarias:
        raise ValueError("Selecione pelo menos uma faixa etária.")

    if any(f not in faixas_validas for f in faixas_etarias):
        raise ValueError("Faixa etária inválida.")

    prefixo = {
        "homens": "homens",
        "mulheres": "mulheres",
        "ambos": "pop"
    }[sexo]

    colunas = [
        f"{prefixo}_{faixa}" for faixa in faixas_etarias
    ]

    resultado["publico_alvo"] = resultado[colunas].sum(axis=1)

    resultado["percentual_publico"] = (
        resultado["publico_alvo"]
        .div(resultado["populacao_total"].replace(0, np.nan))
        * 100
    )

    return resultado


def calcular_aderencia_demografica(df):
    resultado = df.copy()

    resultado["publico_normalizado"] = normalizar_0_100(
        resultado["publico_alvo"]
    )

    resultado["percentual_normalizado"] = normalizar_0_100(
        resultado["percentual_publico"]
    )

    resultado["aderencia_demografica"] = (
        0.60 * resultado["publico_normalizado"]
        + 0.40 * resultado["percentual_normalizado"]
    )

    return resultado


def calcular_ae(df, renda_min, renda_max):
    resultado = df.copy()

    if renda_min >= renda_max:
        raise ValueError(
            "A renda mínima deve ser menor que a máxima."
        )

    def calcular_score(renda):
        if renda_min <= renda <= renda_max:
            return 100.0

        distancia = (
            renda_min - renda
            if renda < renda_min
            else renda - renda_max
        )

        amplitude = renda_max - renda_min

        return max(
            0.0,
            100 * (1 - distancia / amplitude)
        )

    resultado["compatibilidade_economica"] = (
        resultado["renda_media"].apply(calcular_score)
    )

    return resultado


def calcular_oc(df):
    resultado = df.copy()

    resultado["pressao_competitiva"] = np.where(
        resultado["publico_alvo"] > 0,
        (
            resultado["concorrentes"]
            / resultado["publico_alvo"].replace(0, np.nan)
        ) * 10000,
        np.nan
    )

    p95 = resultado["pressao_competitiva"].quantile(0.95)

    resultado["pressao_ajustada"] = (
        resultado["pressao_competitiva"].clip(upper=p95)
    )

    minimo = resultado["pressao_ajustada"].min()
    maximo = resultado["pressao_ajustada"].max()

    if maximo > minimo:
        resultado["oportunidade_competitiva"] = (
            100
            - (
                (resultado["pressao_ajustada"] - minimo)
                / (maximo - minimo)
            ) * 100
        )
    else:
        resultado["oportunidade_competitiva"] = 50.0

    resultado.loc[
        resultado["publico_alvo"] == 0,
        "oportunidade_competitiva"
    ] = np.nan

    return resultado


def calcular_ipm(
    df,
    sexo,
    faixas_etarias,
    renda_min,
    renda_max
):
    resultado = calcular_publico_alvo(
        df, sexo, faixas_etarias
    )

    resultado = calcular_aderencia_demografica(resultado)

    resultado = calcular_ae(
        resultado, renda_min, renda_max
    )

    resultado = calcular_oc(resultado)

    resultado["ipm"] = (
        0.40 * resultado["aderencia_demografica"]
        + 0.30 * resultado["compatibilidade_economica"]
        + 0.30 * resultado["oportunidade_competitiva"]
    )

    resultado["alerta_base_demografica"] = np.select(
        [
            resultado["publico_alvo"] == 0,
            resultado["publico_alvo"] < 500
        ],
        [
            "Sem público-alvo",
            "Base demográfica pequena"
        ],
        default="Base demográfica adequada ao teste"
    )

    resultado.loc[
        resultado["publico_alvo"] == 0,
        "ipm"
    ] = np.nan

    resultado = resultado.sort_values(
        "ipm",
        ascending=False,
        na_position="last"
    ).copy()

    resultado["posicao"] = range(1, len(resultado) + 1)

    resultado.loc[
        resultado["ipm"].isna(),
        "posicao"
    ] = np.nan

    return resultado


def preparar_ranking(df_resultado):
    colunas = [
        "posicao",
        "bairro",
        "publico_alvo",
        "percentual_publico",
        "aderencia_demografica",
        "compatibilidade_economica",
        "oportunidade_competitiva",
        "ipm",
        "alerta_base_demografica"
    ]

    ranking = df_resultado[colunas].copy()

    ranking = ranking.rename(columns={
        "posicao": "Posição",
        "bairro": "Bairro",
        "publico_alvo": "Público-alvo",
        "percentual_publico": "% Público-alvo",
        "aderencia_demografica": "Aderência Demográfica",
        "compatibilidade_economica": "Compatibilidade Econômica",
        "oportunidade_competitiva": "Oportunidade Competitiva",
        "ipm": "IPM",
        "alerta_base_demografica": "Observação"
    })

    ranking = ranking.sort_values(
        "IPM",
        ascending=False,
        na_position="last"
    ).reset_index(drop=True)

    colunas_numericas = [
        "% Público-alvo",
        "Aderência Demográfica",
        "Compatibilidade Econômica",
        "Oportunidade Competitiva",
        "IPM"
    ]

    ranking[colunas_numericas] = (
        ranking[colunas_numericas].round(2)
    )

    return ranking
