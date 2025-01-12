from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from statsbombpy import sb 
import pandas as pd
import numpy as np

app = FastAPI()


# Pydantic Models
class MatchSummaryRequest(BaseModel):
    match_id: int
    style: str

class MatchSummaryResponse(BaseModel):
    summary: str

class PlayerProfileRequest(BaseModel):
    match_id: int
    player_name: str

class PlayerProfileResponse(BaseModel):
    name: str
    passes_completed: int
    finalizations: int
    shots_on_target: int
    disarms: int
    minutes_played: int
    assisted_goals: int
    duels_won: int
    head_cuts: int
    cards: int


# Endpoint para resumir a partida
@app.post("/match_summary", response_model=MatchSummaryResponse)
async def match_summary(request: MatchSummaryRequest):
    match_id = request.match_id
    style = request.style
    
    
    events = get_events(match_id)
    


    # Simulação do uso de modelo de linguagem
    summary = summarize_events(events, style)

    return MatchSummaryResponse(summary=summary.content)

# Endpoint para perfil do jogador
@app.post("/player_profile", response_model=PlayerProfileResponse)
async def player_profile_api(request: PlayerProfileRequest):
    match_id = request.match_id
    player_name = request.player_name

    # Obter eventos da partida
    stats = player_profile(match_id, player_name)
    

    return PlayerProfileResponse(**stats)

def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)


def get_events(match_id: int) -> str:
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return to_json([
        {k: v for k, v in event.items() if v is not np.nan} 
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])

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
        "finalizations": len(player_events[player_events['type'] == 'Shot']),
        "shots_on_target": player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0],
        "disarms": len(player_events[player_events['type'] == 'Duel']),
        "minutes_played": player_events['minute'].max() - player_events['minute'].min(),
        "assisted_goals": player_events['pass_goal_assist'].sum() if 'pass_goal_assist' in player_events else 0,
        "duels_won": len(player_events[player_events['duel_outcome'] == 'Won']) if 'duel_outcome' in player_events else 0,
        "head_cuts": player_events['clearance_head'].sum() if 'clearance_head' in player_events else 0,
        "cards": player_events['foul_committed_card'].count() if 'foul_committed_card' in player_events else 0,
    }
    return stats

from langchain_openai import ChatOpenAI
def summarize_events(events, style):
    """
    Gera uma descrição textual da partida usando um LLM.

    Args:
        events (list): Lista de eventos principais.
        match_details (dict): Detalhes da partida.

    Returns:
        str: Resumo textual da partida.
    """
    reduced_events = events[:100] if len(events) > 100 else events

    # Reformular o prompt para ser mais sucinto
    prompt = (
        f"Resumo dos eventos principais da partida \n"
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
