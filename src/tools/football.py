from langchain.tools import tool
from langchain.chains import LLMChain
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, List
import json
import pandas as pd
import numpy as np
from statsbombpy import sb
import os
import yaml
from data_football.macth_competition import get_lineups, get_matches, get_events, get_player_stats
import json
import yaml
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
        "minutes_played": player_events['minute'].max() - player_events['minute'].min(),
        "assisted_goals": player_events['pass_goal_assist'].sum() if 'pass_goal_assist' in player_events else 0,
        "head_cuts": player_events['clearance_head'].sum() if 'clearance_head' in player_events else 0,
        "cards": player_events['foul_committed_card'].count() if 'foul_committed_card' in player_events else 0,
 
        # "disarms": len(player_events[player_events['type'] == 'Duel']),
        # "duels_won": len(player_events[player_events['duel_outcome'] == 'Won']) if 'duel_outcome' in player_events else 0,
        # "passes": len(player_events[player_events['type'] == 'Pass']),       
        # "chances_created": player_events['pass_shot_assist'].sum() if 'pass_shot_assist' in player_events else 0,
        # "xG": player_events['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in player_events else 0,
        # "left_foot_cuts": player_events['clearance_left_foot'].sum() if 'clearance_left_foot' in player_events else 0,
        # "courts_foot_right": player_events['clearance_right_foot'].sum() if 'clearance_right_foot' in player_events else 0,
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

    

def filter_starting_xi(line_ups: str) -> dict:
    """
    Filter the starting XI players from the provided lineups.
    
    Args:
        line_ups (str): The JSON string containing the lineups of the teams.
        
    Returns:
    
    """
    line_ups_dict = json.loads(line_ups)
    filter_starting_xi =  {}
    for team, team_line_up in line_ups_dict.items():
        filter_starting_xi[team] = []
        for player in sorted(team_line_up, key= lambda x: x["jersey_number"]):
            try:
                positions = player["positions"]["positions"]
                if positions[0].get("start_reason") == "Starting XI":
                    filter_starting_xi[team].append({
                        "player": player["player_name"],
                        "position": positions[0].get('position'),
                        "jersey_number": player["jersey_number"]
                    })
            except (KeyError, IndexError):
                continue
    return filter_starting_xi


def get_sport_specialist_comments_about_match(match_details: str, line_ups: str) -> str:
    """
    Returns the comments of a sports specialist about a specific match.
    The comments are generated based on match details and lineups.
    """
    
    line_ups = filter_starting_xi(line_ups)
    
    agent_prompt = """
    You are a sports commentator with expertise in football (soccer). Respond as
    if you are delivering an engaging analysis for a TV audience. Here is the
    information to include:

    Instructions:
    1. Game Overview:
        - Describe the importance of the game (league match, knockout, rivalry, etc.).
        - Specify when and where the game took place.
        - Provide the final result.
    3. Analysis of the Starting XI:
        - Evaluate the starting lineups for both teams.
        - Highlight key players and their roles.
        - Mention any surprising decisions or notable absences.
    3.  Contextual Insights:
        - Explain the broader implications of the match (rivalry, league standings, or storylines).
    4. Engaging Delivery:
        - Use a lively, professional, and insightful tone, making the commentary
        appealing to fans of all knowledge levels.
    
    The match details are provided by the provided as follow: 
    {match_details}
    You have acces to dataframe with player events in de match: {df_events}
    The team lineups are provided here:
    {lineups}
    
    Provide the expert commentary on the match as you are in a sports broadcast.
    Start your analysis now and engage the audience with your insights.
    
    Say: "Hello everyone, I've watched to the match between [Home Team] and [Away Team]..."
    """
    llm = GoogleGenerativeAI(model="gemini-pro")
    input_variables={"match_details": yaml.dump(match_details),
                     "lineups": yaml.dump(line_ups)}
    prompt = PromptTemplate.from_template(agent_prompt)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    return chain.run(
        **input_variables
    )


def retrieve_match_details(competition_id, season_id, match_id):
    match_details = sb.matches(competition_id=competition_id, season_id=season_id)
    return match_details[match_details['match_id']==int(match_id)]

def match_details_retrieve(action_input:str) -> str:
    """
    Get the details of a specific match 
    
    Args:
        - action_input(str): The input data containing the match_id.
          format: {
              "match_id": 12345
              "competition_id": 123,
                "season_id": 02
            }
    """
    match_id = json.loads(action_input)["match_id"]
    competition_id = json.loads(action_input)["competition_id"]
    season_id = json.loads(action_input)["season_id"]
    matches = json.loads(get_matches(competition_id, season_id))
    match_details= next(
        (match for match in matches if match["match_id"] == int(match_id)),
        None
    )
    return match_details


def details_match(action_input:str) -> str:
    """
    Get the details of a specific match 
    
    Args:
        - action_input(str): The input data containing the match_id.
          format: {
              "match_id": 12345
              "competition_id": 123,
                "season_id": 02
            }
    """
    return yaml.dump(match_details_retrieve(action_input))

@tool
def get_specialist_comments(action_input:str) -> str:
    """
    Provide an overview of the match and the match details.
    Provide comments of a sports specialist about a specific match.
    The specialist knows match details and lineups.
    
    Args:
        - action_input(str): The input data containing the competition_id, season_id and match_id.
          format: {
              "competition_id": 123,
              "season_id": 02,
              "match_id": 12345
            }
    """
    match_details = match_details_retrieve(action_input)
    line_ups = get_lineups(match_details["match_id"])
    return get_sport_specialist_comments_about_match(match_details, line_ups)
    
@tool
def get_match_details(action_input:str) -> str:
    """
    Get the details of a specific match 
    
     Args:
         - action_input(str): The input data containing the match_id.
           format: {
               "match_id": 12345
               "competition_id": 123,
               "season_id": 02
             }
    """
    data_input = json.loads(action_input)
    competition_id = data_input["competition_id"]
    season_id = data_input["season_id"]
    match_id = data_input["match_id"]

    match_details = retrieve_match_details(competition_id, season_id, match_id)
    match_text = match_details.apply(lambda row: ', '.join([f"{col}: {row[col]}" for col in match_details.columns]),
              axis=1).tolist()
    

    
    return match_text[0]




@tool 
def match_lineup_events():
    """
    Gets match data in pandas dataframe format.
    Query the event data in the dataframe to respond correctly.
    """
    df = pd.read_csv('src/tools/football_data.csv', sep=',')

    
    return df

