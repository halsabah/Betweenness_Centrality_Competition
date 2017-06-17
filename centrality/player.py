from .entity import EntityType
from .strategy import Strategy
from .strategy import StrategyBuilder
from .rules import Rules
from .plot import Plotter

# remove import matplotlib, shouldn't be here
import matplotlib.pyplot as plt

import getpass

class Player:
    def __init__(self, **kwargs):
        self._rules = kwargs.get('rules', Rules())
        self._type = kwargs.get('type', EntityType.non_competitive_player)
        self._node_id = -1
        self._name = kwargs.get('name', "John")
        self._picture = kwargs.get('picture', "img/default.jpg")
        self._strategy_type = kwargs.get('strategy_type', Strategy.inactive)
        self._strategy = lambda nb_nodes, node_id, history, impossible_edges, imposed_edges: None

        if self._strategy_type is Strategy.random_egoist:
            strategy_builder = StrategyBuilder()
            self._strategy = strategy_builder.get_random_egoist_strategy()

        elif self._strategy_type is Strategy.random:
            strategy_builder = StrategyBuilder()
            self._strategy = strategy_builder.get_random_strategy()

        elif self._strategy_type is Strategy.follower:
            strategy_builder = StrategyBuilder()
            self._strategy = strategy_builder.get_follower_strategy()

        elif self._strategy_type is Strategy.greedy:
            strategy_builder = StrategyBuilder()
            self._strategy = strategy_builder.get_greedy_strategy()

    """
    API ref, contract of what users should call from the outside
    Mainly allows to change internal attribute names and have more
    encapsulation.
    """
    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, value):
        self._rules = value

    """
    API ref, contract of what users should call from the outside
    Mainly allows to change internal attribute names and have more
    encapsulation.
    """
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, value):
        self._node_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def picture(self):
        return self._picture

    @picture.setter
    def picture(self, value):
        self._picture = value

    @property
    def strategy_type(self):
        return self._strategy_type

    @strategy_type.setter
    def strategy_type(self, value):
        self._strategy_type = value

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, value):
        self._strategy = value

    def __str__(self):
        return "_".join([self.name, self.strategy_type.value, str(self._node_id)])

    def get_action(self, game, node_id):
        """
        Get the action exercised by the player given the current game history by calling his strategy
        :param game: Game, current game
        :param node_id: int, ID of the current node
        :return: edge to be modified given the strategy of the player and the current history of the game
        (wanted to only consider the current state of the game first but the teacher rightfully indicated that players
        would generally remember the previous states. Anyway, keeping track of the history is more general, allow to
        handle the visualization all at once at the end, and includes the current state, thus we could restrict
        ourselves later.)
        """
        if self.type == EntityType.human:
            #print("Here is the current state of the game")
            #plotter = Plotter()
            #plotter.plot_state(game)
            # plotter.plot_game(game, block=False, interactive=True)
            # u = int(input("Enter the first node id of the edge you want to modify: "))
            # v = int(input("Enter the second node id of the edge you want to modify: "))
            # print("You decided to build/destroy (use has_edge to choose between create and destroy) the edge (" + str(u) + ", " + str(v) + ")")

            print("It is player %s's turn to choose" %node_id)
            u = -1  # user's input start value
            while u not in game.graph.nodes():
                # u = int(getpass.getpass("Enter the first node id of the edge you want to modify: "))  # player action
                u = int(input("Enter the first node id of the edge you want to modify: "))

            print("Got the first node!")

            v = -1  # user's input start value
            while v not in game.graph.nodes():
                # v = int(getpass.getpass("Enter the second node id of the edge you want to modify: "))  # player action
                v = int(input("Enter the second node id of the edge you want to modify: "))

            print("Got the second node!")

            # should be handle by method plot, either automatic or pressing a key if you want plot to stay on screen
            plt.close("all")

            return u, v

        return self.strategy(game.rules.nb_players, node_id, game.history, game.impossible_edges, game.imposed_edges)
