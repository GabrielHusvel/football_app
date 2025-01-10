from statsbombpy import sb
import json
import json
import pandas as pd
import numpy as np
from copy import copy
from statsbombpy import sb
from typing import List

def get_competitions() -> str:
    return json.dumps(
        sb.competitions().to_dict(orient='records')
    )

def get_matches(competition_id: int, season_id: int) -> str:
    return json.dumps(
        sb.matches(competition_id=competition_id, season_id=season_id).to_dict(orient='records')
    )
    


class PlayerStatsError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message



def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)


def get_lineups(match_id: int) -> str:
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ['cards', 'positions']
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient='records')
    return to_json(data_final)


def get_events(match_id: int) -> str:
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return to_json([
        {k: v for k, v in event.items() if v is not np.nan} 
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])


def get_player_stats(match_id, player_name) -> str:
    """
    Returns the consolidated statistics of a specific player in a match.

    Parameters:
        match_id (int): ID of the match (provided by StatsBomb).
        player_name (str): Full name of the player.

    Returns:
        dict: Consolidated statistics of the player.

    Raises:
        PlayerStatsError: If any issue occurs while fetching or calculating the statistics.
    """
    try:
        # Load match events
        events = sb.events(match_id=match_id)
        
        # Validate if events were loaded
        if events.empty:
            raise PlayerStatsError(f"No events found for the match with ID {match_id}.")

        # Filter events for the specific player
        player_events = events[events['player'] == player_name]
        
        # Check if the player is present in the events
        if player_events.empty:
            raise PlayerStatsError(f"No events found for player '{player_name}' in match {match_id}.")

        # Consolidate statistics
        stats = {
             "nome": player_name,
            "passes_completed": player_events[(player_events['type'] == 'Pass') & (player_events['pass_outcome'].isna())].shape[0],
            "passes": len(player_events[player_events['type'] == 'Pass']),
            "finalizacoes": len(player_events[player_events['type'] == 'Shot']),
            "shots_on_target": player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0],
            "desarmes": len(player_events[player_events['type'] == 'Duel']),
            "minutos_jogados": player_events['minute'].max() - player_events['minute'].min(),
            "gols_assistidos": player_events['pass_goal_assist'].sum() if 'pass_goal_assist' in player_events else 0,
            "chances_criadas": player_events['pass_shot_assist'].sum() if 'pass_shot_assist' in player_events else 0,
            "xG": player_events['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in player_events else 0,
            "duelos_vencidos": len(player_events[player_events['duel_outcome'] == 'Won']) if 'duel_outcome' in player_events else 0,
            "cortes_cabeca": player_events['clearance_head'].sum() if 'clearance_head' in player_events else 0,
            "cortes_pe_esquerdo": player_events['clearance_left_foot'].sum() if 'clearance_left_foot' in player_events else 0,
            "cortes_pe_direito": player_events['clearance_right_foot'].sum() if 'clearance_right_foot' in player_events else 0,
            "cartoes": player_events['foul_committed_card'].count() if 'foul_committed_card' in player_events else 0,
            "dribles_sucesso": len(player_events[player_events['dribble_outcome'] == 'Complete']) if 'dribble_outcome' in player_events else 0,
            "sob_pressao": len(player_events[player_events['under_pressure'] == True]) if 'under_pressure' in player_events else 0,
            "minutos_jogados": player_events['minute'].max() - player_events['minute'].min() if not player_events['minute'].empty else 0,
            "fouls_committed": player_events[player_events['type'] == 'Foul Committed'].shape[0],
            "fouls_won": player_events[player_events['type'] == 'Foul Won'].shape[0],
            "tackles": player_events[player_events['type'] == 'Tackle'].shape[0],
            "interceptions": player_events[player_events['type'] == 'Interception'].shape[0],
            "dribbles_successful": player_events[(player_events['type'] == 'Dribble') & (player_events['dribble_outcome'] == 'Complete')].shape[0],
            "dribbles_attempted": player_events[player_events['type'] == 'Dribble'].shape[0],
            
        
        }
        
    except PlayerStatsError as e:
        # Propagate the error message
        raise PlayerStatsError(e.message)
    except Exception as e:
        # Handle any other unexpected error
        raise PlayerStatsError(f"An unexpected error occurred: {str(e)}")
    
    return to_json(stats)