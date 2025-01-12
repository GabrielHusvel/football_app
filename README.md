# Análise de Partidas de Futebol

Este projeto utiliza FastAPI, LLMs, Streamlit e LangChain para analisar dados de partidas de futebol do StatsBombpy, disponiveis gratuitamente em https://github.com/statsbomb/statsbombpy?tab=readme-ov-file#statsbombpy-

## Instalação

pip install -r requirements.txt
após isso todas as funções irão funcionar normalmente

## Execusção

Digite no terminal: streamlit run src/main.py;
o apicativo irá abrir em uma aba no navegador ou pegue o link no terminal;
escolha competição, temporada, e time;
faça perguntas ao llm;

## Análise

Analise a resposta do llm e as análises disposta pelo aplicativo.

## Uso api

inicie com a requisiçao para receber o resumo personalizado(style) da partida selecionada(match_id):
HTTP POST http://127.0.0.1:8000/match_summary match_id=3890477 style="friendly"

inicie com a requisiçao para receber os dados do player selecionado(player_name) na partida selecionada(match_id):
HTTP POST http://127.0.0.1:8000/player_profile match_id=3890477 player_name="Ja-Cheol Koo"