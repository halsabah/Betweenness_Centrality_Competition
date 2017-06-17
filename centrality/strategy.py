from random import randint
import networkx as nx
import itertools

# import sys
# sys.path.insert(1, '..')
# print(sys.path)

from enum import Enum


class Strategy(Enum):
    inactive = "inactive"
    random_egoist = "random egoist"
    random = "random"
    follower = "follower"
    greedy = "greedy"


class StrategyBuilder:
    """
    The strategies could be defined as static from a pure code point of view but we don't define them this way to
    ensure that each player instantiate a strategy object so that they don't share the exact same strategy in memory.
    """
    @staticmethod
    def get_random_egoist_edge(nb_nodes, node_id, history, impossible_edges, imposed_edges):
        """
        Helper function that returns an edge between node_id and a node chosen uniformly at random in the set of
        remaining nodes
        :param nb_nodes: Number of players
        :param node_id: Id of the node calling the function
        :return: tuple (node_id, id of another random node)
        """
        impossible_nodes = set([i[0] if i[0] != node_id else i[1] for i in impossible_edges if node_id in i])
        other_nodes = set(range(nb_nodes))
        other_nodes.remove(node_id)
        other_nodes = list(other_nodes - impossible_nodes)

        return node_id, other_nodes[randint(0, len(other_nodes)-1)]

        # other_nodes = list(range(nb_nodes))
        # other_nodes.remove(node_id)
        # return node_id, other_nodes[randint(0, nb_nodes - 2)]

    @staticmethod
    def get_inactive_strategy():
        """
        Define and return the inactive strategy
        :return: function that returns None when being called (player won't do anything)
        """
        def inactive_strategy(nb_nodes, node_id, history, impossible_edges, imposed_edges):
            return None
        return inactive_strategy

    @staticmethod
    def get_random_strategy():
        """
        Define and return the random strategy
        :return: function that returns a random action (random edge) knowing that a looping edge (u == v) is not
        allowed in the game and is therefore replaced by None
        """
        def random_strategy(nb_nodes, node_id, history, impossible_edges, imposed_edges):
            u, v = randint(0, nb_nodes - 1), randint(0, nb_nodes - 1)
            if u == v:
                return None
            else:
                return u, v
        return random_strategy

    def get_random_egoist_strategy(self):
        """
        Define and return the random egoist strategy (modified edge is random but has the current node as one end)
        :return: function that returns a random action (random edge) knowing that a looping edge (u == v) is not
        allowed in the game and is therefore replaced by None
        """
        def random_egoist_strategy(nb_nodes, node_id, history, impossible_edges, imposed_edges):
            return self.get_random_egoist_edge(nb_nodes, node_id, history, impossible_edges, imposed_edges)
        return random_egoist_strategy

    def get_follower_strategy(self):
        """
        Define and return the follower strategy whereby the player connects to best players or does nothing
        when connected to everyone
        :return: function computing the edge of the follower strategy
        """
        def follower_strategy(nb_nodes, node_id, history, impossible_edges, imposed_edges):

            # build graph related to the current state
            graph = nx.Graph()
            graph.add_nodes_from(list(range(nb_nodes)))
            graph.add_edges_from(history[len(history) - 1])

            # find the best players and order them in decreasing order
            inverse = [(value, key) for key, value in nx.betweenness_centrality(graph).items()]
            sorted(inverse, reverse=True)

            for i in range(len(inverse)):
                if not graph.has_edge(node_id, inverse[i][1]):
                    return node_id, inverse[i][1]

            return None

        return follower_strategy

    def get_greedy_strategy(self):
        """
        Define and return the greedy strategy (myopic, only based on the current state and best current action)
        :return: function that returns the best myopic action given the current state
        """
        def greedy_strategy(nb_nodes, node_id, history, impossible_edges, imposed_edges):

            # if graph is empty, return random egoist
            if len(history[len(history) - 1]) == 0:
                return self.get_random_egoist_edge(nb_nodes, node_id, history, impossible_edges, imposed_edges)

            # build graph related to the current state
            graph = nx.Graph()
            graph.add_nodes_from(list(range(nb_nodes)))
            graph.add_edges_from(history[len(history) - 1])

            # initialize the best current action
            best_u, best_v, best_bet = 0, 0, nx.betweenness_centrality(graph)[node_id]

            # create the list of possible edges
            edges_combination = list(itertools.combinations(range(nb_nodes), r=2))
            possible_edges = set(edges_combination) - set(impossible_edges)
            possible_edges -= set(imposed_edges)

            # iterate through all possible action (possible edge) and keep track of the best choice
            for i, j in possible_edges:
                if graph.has_edge(i, j):
                    graph.remove_edge(i, j)

                    new_bet = nx.betweenness_centrality(graph)[node_id]
                    if new_bet > best_bet:
                        best_u, best_v, best_bet = i, j, new_bet

                    graph.add_edge(i, j)

                elif graph.has_edge(j, i):
                    graph.remove_edge(j, i)

                    new_bet = nx.betweenness_centrality(graph)[node_id]
                    if new_bet > best_bet:
                        best_u, best_v, best_bet = j, i, new_bet

                    graph.add_edge(j, i)

                else:
                    graph.add_edge(i, j)

                    new_bet = nx.betweenness_centrality(graph)[node_id]
                    if new_bet > best_bet:
                        best_u, best_v, best_bet = i, j, new_bet

                    graph.remove_edge(i, j)

            if best_u == best_v:
                return None
            else:
                return best_u, best_v

        return greedy_strategy

    def get_approx_greedy_strategy(self, EPSILON=.1, DELTA=.05):
        """
        Define and return the greedy strategy (myopic, only based on the current state and best current action)
        :return: function that returns the best myopic ation given the current state
        """
        def approx_greedy_strategy(nb_nodes, node_id, history, impossible_edges, imposed_edges, EPSILON=EPSILON, DELTA=DELTA):
            # if graph is empty, return random egoist
            EPSILON = EPSILON
            DELTA = DELTA
            if len(history[len(history) - 1]) == 0:
                return self.get_random_egoist_edge(nb_nodes, node_id)

            # build graph related to the current state
            graph = nx.Graph()
            graph.add_nodes_from(list(range(nb_nodes)))
            graph.add_edges_from(history[len(history) - 1])

            # initialize the best current action
            best_u, best_v, best_bet = 0, 0, approximate_betweenness_centrality(graph, eps=EPSILON, delta=DELTA)[node_id]

            # create the list of possible edges
            edges_combination = list(itertools.combinations(range(nb_nodes), r=2))
            possible_edges = set(edges_combination) - set(impossible_edges)
            possible_edges -= set(imposed_edges)

            # iterate through all possible action (possible edge) and keep track of the best choice
            for i, j in possible_edges:
                if graph.has_edge(i, j):
                    graph.remove_edge(i, j)
                    new_bet = approximate_betweenness_centrality(graph, eps=EPSILON, delta=DELTA)[node_id]
                    if new_bet > best_bet:
                        best_u, best_v, best_bet = i, j, new_bet
                    graph.add_edge(i, j)
                elif i == node_id or j == node_id:
                    # a greedy player would only consider adding edges adjacent to itself
                    graph.add_edge(i, j)

                    new_bet = approximate_betweenness_centrality(graph, eps=EPSILON, delta=DELTA)[node_id]
                    if new_bet > best_bet:
                        best_u, best_v, best_bet = i, j, new_bet

                    graph.remove_edge(i, j)

            if best_u == best_v:
                return None
            else:
                return best_u, best_v

        return approx_greedy_strategy
