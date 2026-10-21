
import json
import folium
import pandas as pd
import streamlit as st

from pathlib import Path
from branca.colormap import linear
from streamlit_folium import st_folium


def exibir_mapa(resultado, ranking):

    caminho_geojson = (
        Path(__file__).resolve().parent
        / "bairros_osasco.geojson"
    )

    with open(caminho_geojson, "r", encoding="utf-8") as arquivo:
        geojson = json.load(arquivo)

    dados = resultado.copy()

    dados["codigo_bairro"] = (
        dados["codigo_bairro"].astype(str).str.strip()
    )

    ranking_por_bairro = ranking.set_index("Bairro")

    dados_por_codigo = dados.set_index("codigo_bairro")

    escala = linear.YlGnBu_09.scale(0, 100)
    escala.caption = "Índice de Potencial de Mercado (IPM)"

    for feature in geojson["features"]:

        codigo = str(
            feature["properties"]["CD_BAIRRO"]
        ).strip()

        if codigo in dados_por_codigo.index:

            linha = dados_por_codigo.loc[codigo]

            ipm = linha["ipm"]

            feature["properties"]["IPM"] = (
                round(float(ipm), 2)
                if pd.notna(ipm)
                else None
            )

            feature["properties"]["Bairro"] = (
                feature["properties"]["NM_BAIRRO"]
            )

    mapa = folium.Map(
        location=[-23.532, -46.792],
        zoom_start=12,
        tiles="OpenStreetMap",
        dragging=False,
        scrollWheelZoom=False,
        doubleClickZoom=False,
        touchZoom=False,
        boxZoom=False,
        keyboard=False,
        zoom_control=True
    )

    def estilo(feature):

        ipm = feature["properties"].get("IPM")

        cor = (
            escala(ipm)
            if ipm is not None
            else "#BDBDBD"
        )

        return {
            "fillColor": cor,
            "color": "#555555",
            "weight": 1,
            "fillOpacity": 0.75
        }

    camada = folium.GeoJson(
        geojson,
        name="Bairros de Osasco",
        style_function=estilo,
        highlight_function=lambda feature: {
            "weight": 3,
            "color": "#222222",
            "fillOpacity": 0.9
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["Bairro", "IPM"],
            aliases=["Bairro:", "IPM:"],
            localize=True
        ),
        popup=folium.GeoJsonPopup(
            fields=["Bairro", "IPM"],
            aliases=["Bairro:", "IPM:"],
            localize=True
        )
    )

    camada.add_to(mapa)
    escala.add_to(mapa)

    mapa.fit_bounds(camada.get_bounds())

    evento = st_folium(
        mapa,
        height=550,
        use_container_width=True,
        returned_objects=["last_active_drawing"]
    )

    bairro_selecionado = None

    if evento and evento.get("last_active_drawing"):

        propriedades = evento[
            "last_active_drawing"
        ].get("properties", {})

        bairro_selecionado = propriedades.get("Bairro")

    return bairro_selecionado
