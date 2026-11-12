
import streamlit as st
import pandas as pd

from pathlib import Path
from motor_ipm import calcular_ipm, preparar_ranking
from mapa_ipm import exibir_mapa
from interpretacao_ipm import gerar_interpretacao

st.set_page_config(
    page_title="IPM - Potencial de Mercado",
    page_icon="📊",
    layout="wide"
)

PASTA = Path(__file__).resolve().parent

@st.cache_data
def carregar_dados():
    return pd.read_csv(PASTA / "base_tratada.csv")


df = carregar_dados()

st.title("📊 Índice de Potencial de Mercado")
st.write(
    "Sistema experimental de análise do potencial "
    "de mercado dos bairros de Osasco - SP."
)

st.sidebar.header("Perfil do público-alvo")

sexo = st.sidebar.selectbox(
    "Sexo",
    ["ambos", "mulheres", "homens"],
    format_func=lambda x: {
        "ambos": "Ambos",
        "mulheres": "Mulheres",
        "homens": "Homens"
    }[x]
)

opcoes_idade = {
    "0 a 9 anos": "0_9",
    "10 a 19 anos": "10_19",
    "20 a 29 anos": "20_29",
    "30 a 39 anos": "30_39",
    "40 a 49 anos": "40_49",
    "50 a 59 anos": "50_59",
    "60 a 69 anos": "60_69",
    "70 anos ou mais": "70_mais"
}

idades = st.sidebar.multiselect(
    "Faixas etárias",
    options=list(opcoes_idade.keys()),
    default=["20 a 29 anos", "30 a 39 anos"]
)

renda_min = st.sidebar.number_input(
    "Renda mínima (R$)",
    min_value=0.0,
    value=3000.0,
    step=500.0
)

renda_max = st.sidebar.number_input(
    "Renda máxima (R$)",
    min_value=0.0,
    value=6000.0,
    step=500.0
)

if not idades:
    st.warning("Selecione pelo menos uma faixa etária.")
    st.stop()

if renda_min >= renda_max:
    st.warning("A renda máxima deve ser maior que a mínima.")
    st.stop()

faixas = [opcoes_idade[idade] for idade in idades]

resultado = calcular_ipm(
    df=df,
    sexo=sexo,
    faixas_etarias=faixas,
    renda_min=renda_min,
    renda_max=renda_max
)

ranking = preparar_ranking(resultado)

avaliados = ranking["IPM"].notna().sum()
sem_publico = (ranking["Público-alvo"] == 0).sum()
melhor_bairro = ranking.loc[
    ranking["IPM"].notna(), "Bairro"
].iloc[0]

st.subheader("Resumo da análise")

col1, col2, col3 = st.columns(3)

col1.metric("Bairros avaliados", int(avaliados))
col2.metric("Sem público-alvo", int(sem_publico))
col3.metric("Primeiro colocado", melhor_bairro)

st.subheader("🏆 Top 5 - Potencial de Mercado")

top5 = ranking.dropna(subset=["IPM"]).head(5).copy()

st.bar_chart(
    top5.set_index("Bairro")["IPM"],
    horizontal=True,
    sort=False,
    x_label="Pontuação IPM",
    y_label="Bairro"
)

st.subheader("Ranking completo de potencial de mercado")

ranking_exibicao = ranking.copy()

st.dataframe(
    ranking_exibicao,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "Baixar ranking em CSV",
    data=ranking.to_csv(index=False).encode("utf-8-sig"),
    file_name="ranking_ipm_osasco.csv",
    mime="text/csv"
)

st.caption(
    "O IPM é um índice exploratório baseado em "
    "aderência demográfica (40%), compatibilidade "
    "econômica (30%) e oportunidade competitiva (30%). "
    "Não representa uma previsão garantida de sucesso comercial."
)

st.subheader("Detalhes de um bairro")

st.write("Clique em um bairro no mapa para visualizar seus indicadores.")

bairro_selecionado = exibir_mapa(resultado, ranking)

if bairro_selecionado:
    st.markdown(
        f"### 📍 Bairro selecionado: {bairro_selecionado}"
    )

if not bairro_selecionado:
    st.info("Selecione um bairro no mapa para visualizar os detalhes.")
    st.stop()


detalhe = ranking[
    ranking["Bairro"] == bairro_selecionado
].iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.metric("IPM", f'{detalhe["IPM"]:.2f}' if pd.notna(detalhe["IPM"]) else "N/D")
c2.metric("Público-alvo", f'{int(detalhe["Público-alvo"]):,}'.replace(",", "."))
c3.metric("Aderência demográfica", f'{detalhe["Aderência Demográfica"]:.2f}')
c4.metric("Compatibilidade econômica", f'{detalhe["Compatibilidade Econômica"]:.2f}')

st.write("**Oportunidade competitiva:**",
         round(detalhe["Oportunidade Competitiva"], 2)
         if pd.notna(detalhe["Oportunidade Competitiva"]) else "N/D")


st.subheader("Análise do potencial de mercado")

st.caption("Interpretação automática dos indicadores do bairro selecionado.")

interpretacoes = gerar_interpretacao(detalhe)

st.markdown("**👥 Aderência demográfica**")
st.write(interpretacoes[0])

st.markdown("**💰 Compatibilidade econômica**")
st.write(interpretacoes[1])

st.markdown("**🏪 Oportunidade competitiva**")
st.write(interpretacoes[2])

st.caption("Classificações descritivas, não validadas estatisticamente. A análise econômica utiliza a renda média do bairro; a análise competitiva considera os concorrentes ativos do segmento de artigos esportivos.")



