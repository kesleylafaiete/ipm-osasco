
import pandas as pd


def classificar_indicador(valor):
    if pd.isna(valor):
        return "Não disponível"
    if valor >= 70:
        return "Favorável"
    if valor >= 40:
        return "Intermediária"
    return "Desfavorável"


def gerar_interpretacao(detalhe):
    ad = detalhe["Aderência Demográfica"]
    ae = detalhe["Compatibilidade Econômica"]
    oc = detalhe["Oportunidade Competitiva"]

    textos = []

    if pd.isna(ad):
        textos.append("A aderência demográfica não pôde ser avaliada.")
    elif ad >= 70:
        textos.append(
            "A aderência demográfica é favorável, indicando boa "
            "presença do público-alvo em relação aos demais bairros."
        )
    elif ad >= 40:
        textos.append(
            "A aderência demográfica é intermediária, indicando "
            "presença moderada do público-alvo."
        )
    else:
        textos.append(
            "A aderência demográfica é desfavorável, indicando "
            "menor presença do público-alvo."
        )

    if pd.isna(ae):
        textos.append("A compatibilidade econômica não pôde ser avaliada.")
    elif ae >= 70:
        textos.append(
            "A compatibilidade econômica é favorável, considerando "
            "a renda média do bairro e a faixa selecionada."
        )
    elif ae >= 40:
        textos.append(
            "A compatibilidade econômica é intermediária, pois "
            "a renda média apresenta afastamento da faixa selecionada."
        )
    else:
        textos.append(
            "A compatibilidade econômica é desfavorável, pois "
            "a renda média está distante da faixa selecionada."
        )

    if pd.isna(oc):
        textos.append("A oportunidade competitiva não pôde ser avaliada.")
    elif oc >= 70:
        textos.append(
            "A oportunidade competitiva é favorável, indicando "
            "menor pressão concorrencial relativa ao público-alvo."
        )
    elif oc >= 40:
        textos.append(
            "A oportunidade competitiva é intermediária, indicando "
            "pressão concorrencial moderada."
        )
    else:
        textos.append(
            "A oportunidade competitiva é desfavorável, indicando "
            "maior pressão concorrencial relativa ao público-alvo."
        )

    return textos
