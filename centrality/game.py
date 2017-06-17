from .rules import Rules
from .player import Player
from .plot import Plotter

import pickle
import networkx as nx
import pandas as pd


from enum import Enum


class Metrics(Enum):
    # warning round_number > 0
    macro_degree_assortativity_coefficient = "macro_degree_assortativity_coefficient"
    # macro_rich_club_coefficient = "macro_rich_club_coefficient"

    macro_transitivity = "macro_transitivity"
    macro_average_clustering = "macro_average_clustering"
    macro_is_connected = "macro_is_connected"
    macro_number_connected_components = "macro_number_connected_components"
    macro_is_distance_regular = "macro_is_distance_regular"
    macro_dominating_set = "macro_dominating_set"
    macro_is_eulerian = "macro_is_eulerian"
    macro_isolates = "macro_isolates"

    # warning is_connected
    macro_diameter = "macro_diameter"
    macro_center = "macro_center"
    macro_periphery = "macro_periphery"
    macro_radius = "macro_radius"
    macro_average_shortest_path_length = "macro_average_shortest_path_length"
    micro_eccentricity = "micro_eccentricity"

    micro_average_neighbor_degree = "micro_average_neighbor_degree"
    micro_clustering = "micro_clustering"
    micro_degree_centrality = "micro_degree_centrality"
    micro_closeness_centrality = "micro_closeness_centrality"
    micro_communicability_centrality = "micro_communicability_centrality"
    micro_load_centrality = "micro_load_centrality"
    micro_betweenness_centrality = "micro_betweenness_centrality"
    micro_triangles = "micro_triangles"
    micro_square_clustering = "micro_square_clustering"
    micro_core_number = "micro_core_number"
    micro_closeness_vitality = "micro_closeness_vitality"


def _get_column_names():
    return [metric.value for metric in Metrics]


def _get_metrics(graph):
    res = []

    # macro
    if len(graph.edges()) is not 0:
        res.append(nx.degree_assortativity_coefficient(graph))
        # res.append(nx.rich_club_coefficient(graph))
    else:
        res.append(None)
        res.append(None)

    res.append(nx.transitivity(graph))
    res.append(nx.average_clustering(graph))
    res.append(nx.is_connected(graph))
    res.append(nx.number_connected_components(graph))
    res.append(nx.is_distance_regular(graph))
    res.append(nx.dominating_set(graph))
    res.append(nx.is_eulerian(graph))
    res.append(nx.isolates(graph))

    if nx.is_connected(graph):
        res.append(nx.diameter(graph))
        res.append(nx.center(graph))
        res.append(nx.periphery(graph))
        res.append(nx.radius(graph))
        res.append(nx.average_shortest_path_length(graph))
        res.append(nx.eccentricity(graph))
    else:
        res.append(None)
        res.append(None)
        res.append(None)
        res.append(None)
        res.append(None)
        res.append(None)

    # micro
    res.append(nx.average_neighbor_degree(graph))
    res.append(nx.clustering(graph))
    res.append(nx.degree_centrality(graph))
    res.append(nx.closeness_centrality(graph))
    res.append(nx.communicability_centrality(graph))
    res.append(nx.load_centrality(graph))
    res.append(nx.betweenness_centrality(graph))
    res.append(nx.triangles(graph))
    res.append(nx.square_clustering(graph))
    res.append(nx.core_number(graph))
    res.append(nx.closeness_vitality(graph))

    return res


class Game:
    def __init__(self):
        self.rules = Rules()
        self.graph = nx.Graph()
        self.players = {}
        self.current_step = 0
        self.history = {}
        self.impossible_edges = []
        self.imposed_edges = []
        self.metrics = None

    def initialize_graph(self):
        """
        Initialize the graph by instantiating graph nodes.
        By default, all the remaining nodes are non_competitive players
        :return: void
        """
        self.graph.add_nodes_from(list(range(self.rules.nb_players)))
        self.history[0] = self.graph.edges()

        while len(self.players) < self.rules.nb_players:
            temp_non_competitive_player = Player(name="NC" + str(len(self.players)))
            self.add_player(temp_non_competitive_player)

    def add_player(self, player, node_id=None):
        """
        Add the given player to the list of players and give it a node_id if there is still an available slot
        :param player: Player, player to be added
        :return: void
        """
        if len(self.players) < self.rules.nb_players:
            if not node_id:
                node_id = len(self.players)
            self.players[node_id] = player
            player.node_id = node_id
        else:
            raise Exception("There are already too many players")

    def get_actions(self):
        """
        Returns the actions for each player's embedded strategy
        """
        modified_edges = set()

        for node_id, player in self.players.items():
            modified_edge = player.get_action(self, player.node_id)
            if modified_edge is not None:
                u, v= modified_edge
                if u>v:
                    modified_edge=(v,u)
                    
                modified_edges.add(modified_edge)
            
            

        return modified_edges

    def update_env(self, actions):
        """
        Mutates the state of the environment (i.e. the graph) based on the actions performed by the players
        """
        for edge in actions:
            u, v = edge
            if not self.graph.has_edge(*edge) and edge not in self.impossible_edges:
                self.graph.add_edge(u, v)
            elif self.graph.has_edge(*edge) and edge not in self.imposed_edges:
                self.graph.remove_edge(u, v)

    def play_round(self, actions=False, metrics=False):
        """
        Play one round of the game. For now, if two players are acting on the same edge, the logical OR component
        is adopted (meaning if two players want to destroy the same edge, it will get destroyed).
        No notion of edge strength and cumulative nodes strength yet
        :return: void
        """
        if not actions:
            actions = self.get_actions()

        self.update_env(actions)

        self.current_step += 1

        self.history[self.current_step] = self.graph.edges()
        
        print("The game at state %s:" %self.current_step)
        plotter = Plotter()
        plotter.plot_state(self)

        if metrics:
            self.metrics.loc[len(self.metrics)] = _get_metrics(self.graph)

    def play_game(self, metrics=False):
        """
        Play the entire game according to the given rules (total number of steps in a game)
        :return: void
        """
        print("Here is the initial state of the game")
        plotter = Plotter()
        plotter.plot_state(self)
        
        if metrics:
            self.metrics = pd.DataFrame(columns=_get_column_names())

        while self.current_step < self.rules.nb_max_step:
            self.play_round(metrics=metrics)

    def save(self, filename="history.pickle"):
        # http://stackoverflow.com/questions/11218477/how-can-i-use-pickle-to-save-a-dict
        game_state = {
        "rules": self.rules,
        "players": _to_repr_players(self.players),
        "history": self.history,
        "current_step": self.current_step
        }
        with open(filename, 'wb') as handle:
            pickle.dump(game_state, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        with open(filename, 'rb') as handle:
            game_state = pickle.load(handle)
            self.rules = game_state["rules"]
            self.history = game_state["history"]
            self.current_step = game_state["current_step"]

            players = _to_players(game_state["players"])
            for k, v in players.items():
                self.add_player(v, k)

            self.initialize_graph()

"""
Pickle doesn't save local objects (like strategies in this example)
Helper ReprClass to solve the problem (only dumping the strategy)
"""


def _to_repr_players(players):

    res = {}

    for k, v in players.items():

        player_without_strategy = PlayerRepr(v.rules,
                                             v.type,
                                             v.node_id,
                                             v.name,
                                             v.strategy_type)

        res[player_without_strategy.node_id] = player_without_strategy

    return res


def _to_players(players):

    res = {}

    for k, v in players.items():
        player_with_strategy = Player(rules=v.rules,
                                      type=v.type,
                                      # node_id=v.node_id, # handled by calling add_player in load()
                                      name=v.name,
                                      strategy_type=v.strategy_type)

        res[k] = player_with_strategy

    return res


class PlayerRepr:
    def __init__(self, rules, type, node_id, name, strategy_type):
        self.rules = rules
        self.type = type
        self.node_id = node_id
        self.name = name
        self.strategy_type = strategy_type