import networkx as nx

import datetime

from centrality.rules import Rules
from centrality.strategy import Strategy
from centrality.player import Player
from centrality.entity import EntityType
from centrality.game import Game
from centrality.plot import Plotter, _display_graph
from centrality.plot2 import Plotter2, _display_graph
from centrality.game import Metrics

if __name__ == '__main__':

    """
    Create rules and game
    """

    rules = Rules()
    rules.nb_max_step = 7
    rules.nb_players = 20

    game1 = Game()
    game1.rules = rules

    """
    Create some players and add them to the game
    After having initialized the graph so that
    every player receives an id, add some impossible edges
    """

    player1 = Player(rules=rules, type=EntityType.competitive_player, name="AI1", strategy_type=Strategy.greedy)
    player2 = Player(rules=rules, type=EntityType.competitive_player, name="AI2", strategy_type=Strategy.greedy)
    # player3 = Player(rules=rules, type=EntityType.competitive_player, name="AI3", strategy_type=Strategy.greedy)
    #player4 = Player(rules=rules, type=EntityType.human, name="H1")
    #player5 = Player(rules=rules, type=EntityType.human, name="H2")

    #player4.picture = "img/medici.jpg"
    #player5.picture = "img/medici2.jpg"

    game1.add_player(player1)
    game1.add_player(player2)
    # game1.add_player(player3)
    #game1.add_player(player4)
    #game1.add_player(player5)

    game1.initialize_graph()

    game1.impossible_edges = [
        # (player1.node_id, player2.node_id),
        # (player2.node_id, player1.node_id),
        # (player1.node_id, player3.node_id),
        # (player3.node_id, player1.node_id),
        # (player2.node_id, player3.node_id),
        # (player3.node_id, player2.node_id),
    ]

    """
    Play the game
    """

    game1.play_game(True)

    plotter = Plotter()
    plotter.plot_state(game1)

    """
    Save the game
    """

    # date = datetime.datetime.now()
    # game1.save(filename="games/" + str(date) + ".pkl")

    """
    Load the game
    """

    # game1 = Game()
    # game1.load("games/" + str(date) + ".pkl")

    """
    Replay the game
    """

    plotter2 = Plotter2()

    plotter2.plot_game(game1, interactive=True, leader_board=True, time_step=0.01)

    '''
    Medici example presentation
    '''

    # map = {
    #     5: "Strozzi",
    #     7: "Ridolfi",
    #     8: "Tornabuon",
    #     9: "Castellan",
    #     10: "Barbadori",
    #     11: "Medici",
    #     12: "Albizi",
    #     13: "Acciaiuol",
    #     14: "Salviati",
    #     16: "Pazzi"
    # }
    #
    # adjacency_list = {
    #     5: [7, 9],
    #     7: [5, 8, 11],
    #     8: [7, 11],
    #     9: [5, 10],
    #     10: [9, 11],
    #     11: [13, 14, 12, 8, 10, 7],
    #     12: [11],
    #     13: [11],
    #     14: [11, 16],
    #     16: [14],
    # }
    #
    # map2 = {
    #     0: 5,
    #     1: 7,
    #     2: 8,
    #     3: 9,
    #     4: 10,
    #     5: 12,
    #     6: 13,
    #     7: 14,
    #     8: 16,
    #     9: 11
    # }
    #
    #
    # def adj_list_to_edge_list(adj_list):
    #     """
    #     Convert an adjacency list to a list of edges
    #
    #     Args:
    #         adj_list: Adjacency list
    #
    #     Returns:
    #         List of edges
    #
    #     Raises:
    #         Exceptions not handled
    #
    #     DocTest:
    #         >>> adj_list_to_edge_list({1: [2,3], 2: [4,5]})
    #         [(1, 2), (1, 3), (2, 4), (2, 5)]
    #     """
    #     res = []
    #
    #     for i in adj_list:
    #         for j in adj_list[i]:
    #             res.append((i, j))
    #
    #     return res
    #
    # game = Game()
    # game.rules = rules
    #
    # italian_families_graph = nx.Graph()
    #
    # italian_families_graph.add_nodes_from(map.keys())
    #
    # italian_families_graph.add_edges_from(adj_list_to_edge_list(adjacency_list))
    #
    # colors = None
    # alpha = None
    # sizes = None
    # labels = None
    #
    # import math
    #
    # positions = {}
    # for i in range(9):
    #     positions[map2[i]] = (math.cos(2 * math.pi * i / 9), math.sin(2 * math.pi * i / 9))
    # positions[11] = (0, 0)
    #
    # images = {}
    # for i in range(9):
    #     images[map2[i]] = "img/default.jpg"
    # images[11] = "img/medici.jpg"
    #
    # _display_graph(italian_families_graph, positions, labels, colors, sizes, alpha, leader_board=None,
    #                display_labels=False, game=game, images=images)
    #
    # import matplotlib.pyplot as plt
    #
    # mng = plt.get_current_fig_manager()
    # mng.resize(*mng.window.maxsize())
    # plt.show()
    # # plt.savefig('img/medici_network.png', transparent=True)
    #
    # print(nx.betweenness_centrality(italian_families_graph))


    """
    Shortest path
    """
    # node_list = []
    # for i in range(2,6,1):
    #     node_list.append(map2[i])
    # node_list.append(11)
    #
    # shortest_path_graph = nx.Graph()
    # shortest_path_graph.add_nodes_from(node_list)
    #
    # shortest_path_graph.add_edges_from([edge for edge in italian_families_graph.edges()
    #                               if (edge[0] in node_list and edge[1] in node_list)])
    #
    # _display_graph(shortest_path_graph, positions, labels, colors, sizes, alpha, leader_board=None,
    #                display_labels=False, game=game, images=images)
    #
    #
    # mng = plt.get_current_fig_manager()
    # mng.resize(*mng.window.maxsize())
    # plt.show()



    # shortest_path_graph = nx.Graph()
    # shortest_path_graph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    #
    # shortest_path_graph.add_edges_from([(1,2),(2,3),(3,4),(4,5),(2,6),(1,6),(2,5),(2,4),(4,6),(1,7),(7,3)])
    #
    # print(nx.betweenness_centrality(shortest_path_graph))
    # # print(nx.clustering(shortest_path_graph))
    # print(nx.triangles(shortest_path_graph))
    #
    #
    # nx.draw_networkx(shortest_path_graph)
    # plt.axis([-0.1,1.1,-0.1,1.1])
    # plt.axis('off')
    #
    # plt.savefig('img/shortest_path.png', transparent=True)