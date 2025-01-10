
# from typing import List, Dict
# from langchain_core.tools import Tool

# from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
# from langchain_community.tools.wikipedia.tool import WikipediaQueryRun


# from .self_ask_agent import get_self_ask_agent, search_team_information
# from .football import get_match_details

# def load_tools(tool_names: List[str] = []) -> Dict[str, Tool]:
#     TOOLS = [
#         search_team_information,
#         # get_match_details,
#         # get_specialist_comments,
#         Tool.from_function(
#             name='Self-ask agent',
#             func=get_self_ask_agent().invoke,
#             description=(
#                 "A tool to answer complicated questions. "
#                 "Useful for when you need to answer questions about competition events like matches, "
#                 "or team details. Input should be a question."
#             )
#         ),
#         WikipediaQueryRun(
#             api_wrapper=WikipediaAPIWrapper(),
#             description=(
#                 "A wrapper around Wikipedia. Useful for when you need "
#                 "to answer general questions about people, players, teams, "
#                 "competitions, stadiums (the stadium history and capacity), "
#                 "cities, events, or other subjects. Input should be a search query."
#             )
#         ),
#         Tool.from_function(
#             name="Get Match Events",
#             func=get_match_details,
#             description=(
#                 "A tool to fetch and process players events for a specific match. "
#                 "Useful for retrieving detailed event information, such as passes, goals, and other actions. "
                
#             )
#         ),
#     ]
#     if tool_names == []:
#         return TOOLS
#     return [t for t in TOOLS if t.name in tool_names]

# def load_tools(tool_names: List[str] = []) -> Dict[str, Tool]:
#     TOOLS = [
#         search_team_information,
#         get_match_details,
#         get_specialist_comments,
#         Tool.from_function(
#             name='Self-ask agent',
#             func=get_self_ask_agent().invoke,
#             description=(
#                 "A tool to answer complicated questions. "
#                 "Useful for when you need to answer questions about competition events like matches, "
#                 "or team details. Input should be a question."
#             )
#         ),
#         WikipediaQueryRun(
#             api_wrapper=WikipediaAPIWrapper(),
#             description=(
#                 "A wrapper around Wikipedia. Useful for when you need "
#                 "to answer general questions about people, players, teams, "
#                 "competitions, stadiums (the stadium history and capacity), "
#                 "cities, events, or other subjects. Input should be a search query."
#             )
#         ),
#         get_events_tool,  # Usando a ferramenta atualizada
#     ]
#     if tool_names == []:
#         return TOOLS
#     return [t for t in TOOLS if t.name in tool_names]


