#1 - Configuração do Ambiente e Integração com a API StatsBombPy:
# Configure o ambiente de desenvolvimento (Python 3.8+).
# Instale a biblioteca StatsBombPy e outras dependências necessárias.
# Produza um arquivo requirements.txt com todas as bibliotecas utilizadas no projeto.
# Crie uma função simples que receba uma ID de partida e retorne os dados brutos dessa partida utilizando a API.
import requests
import streamlit as st
from statsbombpy import sb


def get_matches_info(match_id):
    """
    Obtém informações das partidas de uma competição em uma temporada específica.
    
    Args:
        match_id (int): ID da competição.
       
    
    Returns:
        DataFrame: Informações das partidas.
    """
    events = sb.events(match_id=match_id)
    
   
    return events


    
#2 - Organização do Projeto e Publicação no GitHub:
# Estruture o projeto em pastas organizadas (e.g., app, docs).
# Inclua um arquivo README.md com as seguintes informações:
# Descrição do projeto e objetivo.
# Instruções para configurar o ambiente e executar o código.
# Exemplos de entrada e saída das funcionalidades.
# Use commits claros e bem descxztos ao longo do desenvolvimento.


#3 - Sumarização de Partidas com LLM:
# Desenvolva uma função que:
# Identifique os eventos principais da partida (gols, assistências, cartões, etc.).
# Utilize um modelo LLM para transformar esses eventos em uma sumarização textual descritiva.
# Certifique-se de que a saída seja clara e amigável, como:
# "O time A venceu o time B por 3 a 1. Os destaques foram os gols de João e Lucas, além de uma assistência de Ana."
import os
import numpy as np
import pandas as pd
import json
from langchain_openai import ChatOpenAI
def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)
def get_events(match_id: int) -> str:
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return to_json([
        {k: v for k, v in event.items() if v is not np.nan} 
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])



def summarize_events(events, match_details, style):
    """
    Gera uma descrição textual da partida usando um LLM.

    Args:
        events (list): Lista de eventos principais.
        match_details (dict): Detalhes da partida.

    Returns:
        str: Resumo textual da partida.
    """
    # Reduzir a quantidade de eventos para no máximo 5 eventos mais importantes
    reduced_events = events[:5] if len(events) > 5 else events

    # Reformular o prompt para ser mais sucinto
    prompt = (
        f"Resumo dos eventos principais da partida entre {match_details['home_team']} e {match_details['away_team']}:\n"
        f"Eventos: {reduced_events}.\n"
        "Descreva o resultado em um texto claro e amigável. usando o estilo de narrativa {style}"
    )
    
    # Configurar o modelo para limitar tokens
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=500,  # Definir limite de tokens
        timeout=None,
        max_retries=2,
        api_key=(os.getenv('OPENAI_API_KEY'))
    )
    ai_msg = llm.invoke(prompt)
    return ai_msg



# 4 - Criação de Perfil de Jogador:
# Desenvolva uma funcionalidade que permita criar um perfil detalhado de um jogador específico da partida, contendo:
# Nome do jogador.
# Estatísticas como número de passes, finalizações, desarmes e minutos jogados.
# Retorne os dados de forma clara e organizada (e.g., JSON ou tabela).



from statsbombpy import sb
import pandas as pd

def player_profile(match_id, player_name):
    # Obter eventos da partida
    events = sb.events(match_id=match_id)
    
    # Filtrar eventos relacionados ao jogador
    player_events = events[events['player'] == player_name]
    
    # Estatísticas do jogador
    stats = {
        "name": player_name,
        "passes_completed": player_events[(player_events['type'] == 'Pass') & (player_events['pass_outcome'].isna())].shape[0],
        # "passes": len(player_events[player_events['type'] == 'Pass']),
        "finalizations": len(player_events[player_events['type'] == 'Shot']),
        "shots_on_target": player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0],
        "disarms": len(player_events[player_events['type'] == 'Duel']),
        "minutes_played": player_events['minute'].max() - player_events['minute'].min(),
        "assisted_goals": player_events['pass_goal_assist'].sum() if 'pass_goal_assist' in player_events else 0,
        # "chances_created": player_events['pass_shot_assist'].sum() if 'pass_shot_assist' in player_events else 0,
        # "xG": player_events['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in player_events else 0,
        "duels_won": len(player_events[player_events['duel_outcome'] == 'Won']) if 'duel_outcome' in player_events else 0,
        "head_cuts": player_events['clearance_head'].sum() if 'clearance_head' in player_events else 0,
        # "left_foot_cuts": player_events['clearance_left_foot'].sum() if 'clearance_left_foot' in player_events else 0,
        # "courts_foot_right": player_events['clearance_right_foot'].sum() if 'clearance_right_foot' in player_events else 0,
        "cards": player_events['foul_committed_card'].count() if 'foul_committed_card' in player_events else 0,
        # "dribbling_success": len(player_events[player_events['dribble_outcome'] == 'Complete']) if 'dribble_outcome' in player_events else 0,
        # "under_pressure": len(player_events[player_events['under_pressure'] == True]) if 'under_pressure' in player_events else 0,
        # "fouls_committed": player_events[player_events['type'] == 'Foul Committed'].shape[0],
        # "fouls_won": player_events[player_events['type'] == 'Foul Won'].shape[0],
        # "tackles": player_events[player_events['type'] == 'Tackle'].shape[0],
        # "interceptions": player_events[player_events['type'] == 'Interception'].shape[0],
        # "dribbles_successful": player_events[(player_events['type'] == 'Dribble') & (player_events['dribble_outcome'] == 'Complete')].shape[0],
        # "dribbles_attempted": player_events[player_events['type'] == 'Dribble'].shape[0],
        
}
    return stats



# 5 - Desenvolvimento de uma API com FastAPI:
# Crie os seguintes endpoints:
# /match_summary: Retorna a sumarização de uma partida.
# /player_profile: Retorna o perfil detalhado de um jogador.
# Utilize Pydantic para validar as entradas e saídas.


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd

app = FastAPI()

# Modelos para entrada e saída
class MatchSummaryRequest(BaseModel):
    match_id: int
    style: str

class PlayerProfileRequest(BaseModel):
    match_id: int
    player_name: str


# Endpoints
@app.post("/match_summary")
def match_summary(request: MatchSummaryRequest):
    try:
        # Obter dados do StatsBomb
        events = sb.events(match_id=request.match_id)
        goals = events[events['type'] == 'Shot'][events['shot_outcome'] == 'Goal']
        summary = {
            "total_gols": len(goals),
            "equipes": events['team'].unique().tolist(),
        }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/player_profile", response_model=PlayerProfileResponse)
def get_player_profile(request: PlayerProfileRequest):
    try:
        stats = player_profile(request.match_id, request.player_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 6 - Narração Personalizada de Partidas
# Desenvolva uma funcionalidade para criar narrativas baseadas nos eventos da partida.
# Permita ao usuário escolher entre estilos de narração, como:
# Formal (técnico e objetivo).
# Humorístico (descontraído e criativo).
# Técnico (análise detalhada dos eventos).

def narrate_match(match_id, match_details):

    # Extrair eventos principais
    key_events = get_events(match_id)

    # Verificar se há eventos disponíveis
    if not key_events:
        st.warning("Nenhum evento encontrado para esta partida.")
    else:
        # Seleção de estilo de narração
        st.subheader("Selecione o Estilo de Narração")
        style = st.radio(
            "Escolha um estilo:",
            options=["Formal", "Humorístico", "Técnico"],
            index=0
        )

    # Resumir eventos
    summary = summarize_events(key_events, match_details, style)
    return summary
    

# 7 - Interface Inicial com Streamlit
# Desenvolva uma interface simples que permita ao usuário:
# Selecionar uma partida por ID.
# Exibir os eventos principais e o perfil de um jogador.
# Mostrar os resultados de forma visual e amigável.
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from data_footbal.macth_competition import get_competitions, get_matches, get_lineups, get_events

st.set_page_config(layout="wide",
                   page_title="Football Match Resumed App",
                   page_icon="⚽️")

msgs = StreamlitChatMessageHistory()


if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(messages=msgs, memory_key="chat_history", return_messages=True)

memory = st.session_state.memory

def memorize_message():
    user_input = st.session_state["user_input"]
    st.session_state["memory"].chat_memory.add_message(HumanMessage(content=user_input))
    
def load_competitions():
    """
    Simulates loading competitions from your function.
    Replace this with the actual call to fetch competitions.
    """
    return json.loads(get_competitions())

def load_matches(competition_id, season_id):
    """
    Simulates loading matches for a specific competition.
    Replace this with the actual call to fetch matches for a competition.
    """
    return  json.loads(get_matches(competition_id, season_id))


# Streamlit Sidebar
st.sidebar.title("Football Match Selector")
# Step 1: Select a Competition
selected_competition = None
selected_season = None
selected_match = None
match_id = None
match_details = None
specialist_comments = None

st.sidebar.header("Step 1: Select a Competition")
competitions = load_competitions()
competition_names = sorted(set([comp['competition_name'] for comp in competitions]))
selected_competition = st.sidebar.selectbox("Choose a Competition",
                                            competition_names)
if selected_competition:
    # Step 2: Select a Season
    st.sidebar.header("Step 2: Select a Season")
    seasons = set(comp['season_name'] for comp in competitions
                  if comp['competition_name'] == selected_competition)
    selected_season = st.sidebar.selectbox("Choose a Season", sorted(seasons))
    
    
if selected_season:
    # Get the selected competition ID
    competition_id = next(
        (comp['competition_id'] for comp in competitions 
         if comp['competition_name'] == selected_competition),
        None
    )
    season_id = next(
        (comp['season_id'] for comp in competitions 
                               if comp['season_name'] == selected_season 
                               and comp['competition_name'] == selected_competition),
        None
    )
    # Step 2: Select a Match
    st.sidebar.header("Step 3: Select a Match")
    matches = load_matches(competition_id, season_id)
    match_names = sorted([f"{match['home_team']} vs {match['away_team']}" for match in matches])
    
    if selected_match:=st.sidebar.selectbox("Choose a Match", match_names):
        import	config
        # Get the selected match ID
        match_details = next(
            (match for match in matches if f"{match['home_team']} vs {match['away_team']}" == selected_match),
            None
        ) 
        match_id = match_details['match_id']
        config.MATCH_ID = match_id
        
# Eventos e Resumo
with st.container():
    # st.header("Eventos da Partida")

   
    # Extrair eventos principais
    key_events = get_events(match_id)


    # Resumir eventos
    summary = narrate_match(match_id, match_details)
    st.subheader("Resumo da Partida")
    st.write(summary.content)

    

        # Extrair times
    home_team = match_details.get("home_team", "Time da Casa")
    away_team = match_details.get("away_team", "Time Visitante")

    # Criar opções para o selectbox
    team_options = [home_team, away_team]

    # Exibir o selectbox
    player_team = st.sidebar.selectbox("Selecione um time:", team_options)
    config.PLAYER_TEAM = player_team
    team = sb.lineups(match_id=match_id)[player_team]
    player1= st.sidebar.selectbox("Selecione o primeiro jogador:", team['player_name'])
    player2= st.sidebar.selectbox("Selecione o segundo jogador:", team['player_name'])
    
    player1_stats = player_profile(match_id, player1)
    player2_stats = player_profile(match_id, player2)
    
    
    def plot_stats(stats1, stats2, player1, player2):
        df = pd.DataFrame([stats1, stats2], index=[player1, player2]).T
        st.bar_chart(df)
    st.subheader("Comparação de Estatísticas")
    plot_stats(player1_stats, player2_stats, player1, player2)
    

    data_match = []
    for player in team['player_name']:
        data_match.append(player_profile(match_id, player))
    df_events = pd.DataFrame(data_match)
    df_events.to_csv('src/tools/data_football.csv', index=False)        
    # st.write(data_match)
    

# 8 - Criação de um Agente ReAct com LangChain:
# Configure um agente utilizando LangChain para interagir com os dados da partida.
# Implemente ferramentas para realizar:
# Consulta de eventos específicos da partida.
# Geração de comparações entre dois jogadores.
# Habilite o agente a responder perguntas como:
# "Quem deu mais passes na partida?"
# "Qual jogador teve mais finalizações no primeiro tempo?"

from langchain.schema import AIMessage, HumanMessage
from tools.football import get_match_details, get_specialist_comments, match_lineup_events
import json
from agent import load_agent

# Main Page
if not match_id:
    st.title("Football Match Conversation")
    st.write("Use the sidebar to select a competition, then a match, and start a conversation.")
else:
    st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True)
    st.markdown(f'<h1 class="title">{selected_match}</h1><h3 class="title">{selected_competition} - Season {selected_season}</h3>', unsafe_allow_html=True)
    with st.container(border=False):
        st.chat_input(key="user_input", on_submit=memorize_message) 
        if user_input := st.session_state.user_input:
            chat_history = st.session_state["memory"].chat_memory.messages
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    with st.chat_message("user"):
                        st.write(f"{msg.content}")
                elif isinstance(msg, AIMessage):
                    with st.chat_message("assistant"):
                        st.write(f"{msg.content}")
                        
            with st.spinner("Agent is responding..."):
                # tools = load_tools()
                # st.write(tools)
                # tool_names = [tool.name for tool in tools]
                # st.write(tool_names)
                # tool_descriptions = [tool.description for tool in tools]
                # st.write(tool_descriptions)
                try:
                    # Load agent
                    agent = load_agent()
                    print('agent')
                    
                    # Cache tools to avoid redundant calls
                    tools = [           
                    get_match_details,
                    get_specialist_comments,
                    match_lineup_events,
                    ]
                    
                    tool_names = [tool.name for tool in tools]
                    tool_descriptions = [tool.description for tool in tools]
                    
                    print(match_id, season_id, competition_id)
                    # Prepare input for the agent
                    input_data = {
                        "match_id": match_id,
                        "df_events": df_events,
                        "match_name": selected_match,
                        "key_events": key_events,
                        "match_detail": match_details,
                        "input": user_input,
                        "agent_scratchpad": "",
                        "competition_id": competition_id,
                        "season_id": season_id,
                        "tool_names": tool_names,
                        "tools": tool_descriptions,

                        
                    }

                    # # Debug: Print input to verify structure (optional)
                    # st.write(f"Input to agent: {input_data}")

                    # Invoke agent
                    response = agent.invoke(input=input_data, handle_parsing_errors=True)

                    # Validate response
                    if isinstance(response, dict) and "output" in response:
                        output = response.get("output")
                    else:
                        output = "Sorry, I couldn't understand your request. Please try again."

                    # Add response to chat memory
                    st.session_state["memory"].chat_memory.add_message(AIMessage(content=output))

                    # Display response in chat
                    with st.chat_message("assistant"):
                        st.write(output)

                except Exception as e:
                    # Handle and display errors gracefully
                    st.error(f"Error during agent execution: {str(e)}")
                    st.write("Ensure that your inputs and agent configuration are correct.")




# # 9 - Aprimoramento da Interface com Funcionalidades Avançadas:
# # Melhore a interface Streamlit, adicionando:
# # Filtros para explorar eventos específicos (e.g., apenas gols ou cartões).
# # Visualizações gráficas para estatísticas dos jogadores (e.g., gráficos de barras, tabelas interativas).
# # Comparação direta entre dois jogadores selecionados.

import streamlit as st
import pandas as pd
import plotly.express as px  
import seaborn as sns


# Carregar os dados da partida (simulação de dados para exemplo)

st.write(df_events)
# Seleção de evento
eventos_selecionados = st.sidebar.multiselect(
    "Selecione os eventos para exibir:",
    options=["assisted_goals", "cards", "finalizations", "passes" "shots_on_target","disarms","minutes_played","chances_created","xG","duels_won","head_cuts","left_foot_cuts","courts_foot_right","dribbling_success","under_pressure","fouls_committed","fouls_won","tackles","interceptions","dribbles_successful","dribbles_attempted"   ],
    default=["assisted_goals", "cards", "finalizations", ]
)
# Mapeando os eventos selecionados para colunas correspondentes

colunas_selecionadas = [evento for evento in eventos_selecionados]


# Filtrar os eventos baseados na seleção
df_filtrado = df_events[["name"] + colunas_selecionadas]


# Gráfico de barras para estatísticas selecionadas
fig = px.bar(df_filtrado.melt(id_vars="name"), x="name", y="value", color="variable", barmode="group")
st.plotly_chart(fig)


# Seleção de jogadores para comparação

jogador1 = player1
jogador2 = player2
# Comparação de jogadores
jogador1_stats = df_events[df_events['name'] == jogador1].to_dict('records')[0]
jogador2_stats = df_events[df_events['name'] == jogador2].to_dict('records')[0]

col1, col2 = st.columns(2)
with col1:
    st.write(f"**{jogador1}**")
    st.json(jogador1_stats)

with col2:
    st.write(f"**{jogador2}**")
    st.json(jogador2_stats)

# Função para converter dados filtrados em CSV
def convert_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

# Baixar os dados filtrados
csv = convert_to_csv(df_filtrado)
st.download_button("Baixar CSV", csv, "dados_filtrados.csv")


# # 10 - Integração Completa das Funcionalidades:
# # Garanta que o fluxo completo esteja funcional:
# # Seleção da partida.
# # Geração da sumarização e narrativas.
# # Criação de perfis detalhados de jogadores.
# # Certifique-se de que as versões em FastAPI e Streamlit sejam independentes, mas cubram as mesmas funcionalidades.

