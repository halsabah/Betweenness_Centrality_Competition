from .entity import EntityType

import networkx as nx

import math
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn')
# print(plt.style.available)

class Plotter2:
    def __init__(self):
        self.node_transparency = 0.3
        self.significant_digits = 4
        self.color_competitive_player = "r"
        self.color_non_competitive_player = "b"
        self.color_human = "g"
        self.color_other_entity = "k"
        self.current_interactive_graph = 0  # Allow to navigate through the graphs in interactive mode
        self.labels_interactive_graph = False  # Allow to display the labels in interactive mode
        self.leader_board_size = 3

    """
    Helper functions to build components later used to plot networks
    """
    @staticmethod
    def get_positions(nb_players):
        """
        Compute the positions of the players so that they are fixed when visualizing the evolution of the game
        :param nb_players: int, number of players in the game
        :return: dictionary of (x,y) coordinate tuple
        """
        positions = {}
        for i in range(nb_players):
            positions[i] = (math.cos(2 * math.pi * i / nb_players), math.sin(2 * math.pi * i / nb_players))
        return positions

    def get_colors(self, game):
        """
        Compute the colors of the players according to their entity type to be able to easily differentiate them
        :param game: Game, played game
        :return: string of color initials
        """
        colors = ""
        for i in range(game.rules.nb_players):
            player = game.players[i]
            if player.type is EntityType.competitive_player:
                colors += self.color_competitive_player
            elif player.type is EntityType.non_competitive_player:
                colors += self.color_non_competitive_player
            elif player.type is EntityType.human:
                colors += self.color_human
            else:
                colors += self.color_other_entity
        return colors

    def get_graph_labels_sizes(self, game, round_number, node_list=None):
        """
        Compute the labels and sizes of the players according to a given graph state (game + round number)
        :param game: Game, played game
        :param round_number: int, time step/round number of the game
        :param node_list: [int], nodes to be plotted
        :return: tuple containing a dictionary for the labels and an array for the sizes
        """

        current_graph = nx.Graph()
        current_graph.add_nodes_from(game.graph.nodes())
        current_graph.add_edges_from(game.history[round_number])

        labels = {}
        betweenness = nx.betweenness_centrality(current_graph)

        for i in range(game.rules.nb_players):
            player = game.players[i]
            if player.type is EntityType.competitive_player or player.type is EntityType.human:
                labels[i] = "player #" + str(player.node_id) + "\n" +\
                            player.name + "\n" +\
                            str(round(betweenness[i], self.significant_digits))
            elif player.type is EntityType.non_competitive_player:
                labels[i] = "player #" + str(player.node_id) + "\n" + \
                            player.name + "\n" +\
                            str(round(betweenness[i], self.significant_digits))
            else:
                labels[i] = "other_entity"

        sizes = [(10 * c + 1) * 300 for c in list(betweenness.values())]

        if node_list is not None:
            current_graph = nx.Graph()
            current_graph.add_nodes_from(node_list)
            current_graph.add_edges_from([edge for edge in game.history[round_number]
                                          if (edge[0] in node_list and edge[1] in node_list)])

            labels = {key: value for (key, value) in labels.items() if key in node_list}

        return current_graph, labels, sizes

    """
    Helper functions to build artists to plot metrics given axes ref
    """
    def build_plot_macro(self, game, round_number, metric, ax):
        df = game.metrics.iloc[:round_number+1, :]
        pl = ax.plot(df.index.values, df[metric.value])
        plt.title(" ".join(metric.value.split("_")[1:]))
        plt.axis([-1, len(game.history)+1, df[metric.value].min()-1, df[metric.value].max()+1])
        return pl

    def build_plot_micro(self, game, round_number, node_ids, metric, ax):
        df = game.metrics.iloc[:round_number+1, :]
        for i in node_ids:
            val = df[metric.value].apply(lambda x: x[i])
            pl = ax.plot(df.index.values, val)
            plt.title(" ".join(metric.value.split("_")[1:]))
            # plt.axis([-1, len(game.history)+1, min(df[metric.value].apply(min)) -1, max(df[metric.value].apply(max)) +1])
        return pl
    # ill coded, return pl? / could also apply and create new col instead of slicing every time

    def build_plot_micro_distrib(self, game, round_number, metric, ax):
        # Superpose hist only if you can find colors shade that make the intent obvious

        # df = game.metrics.iloc[:round_number+1, :]
        # val = df[metric.value].apply(lambda x: list(x.values()))
        # for i in range(round_number+1):
        #     hi = ax.hist(val[i], alpha=(i*0.05+0.2), color='b')
        # return hi
        df = game.metrics.iloc[:round_number+1, :]
        val = df[metric.value].apply(lambda x: list(x.values()))
        hi = ax.hist(val[round_number], alpha=0.5, color='b')
        plt.title((" ".join(metric.value.split("_")[1:]) + " distribution"))
        return hi


    """
    Plot multiple views
    """

    def multi_plot(self, game, round_number, node_ids, metrics, fig):
        plt.clf()

        for metric in metrics:
            if "macro" == metric[0]:
                ax = fig.add_subplot(*metric[2])
                self.build_plot_macro(game, round_number, metric[1], ax)
            elif "micro" == metric[0]:
                ax = fig.add_subplot(*metric[2])
                self.build_plot_micro(game, round_number, node_ids, metric[1], ax)
            elif "micro_distrib" == metric[0]:
                ax = fig.add_subplot(*metric[2])
                self.build_plot_micro_distrib(game, round_number, metric[1], ax)

        plt.show()

    """
    Plot the overall game
    """

    def multi_plot_dynamic(self, game, node_ids, metrics, interactive=False, time_step=0.05):

        if interactive:

            # keyboard event handler
            def key_event(e):

                if e.key == "right":
                    self.current_interactive_graph += 1
                elif e.key == "left":
                    self.current_interactive_graph -= 1
                else:
                    return

                self.current_interactive_graph %= len(game.history)

                curr_pos = self.current_interactive_graph

                self.multi_plot(game, curr_pos, node_ids, metrics, fig)

                fig.canvas.draw()

            fig = plt.figure()
            fig.canvas.mpl_connect('key_press_event', key_event)

            self.multi_plot(game, 0, node_ids, metrics, fig)

            plt.show()

        else:

            fig = plt.figure()

            plt.ion()

            for round_number in range(len(game.history)-1):

                self.multi_plot(game, round_number, node_ids, metrics, fig)
                plt.pause(time_step)

            while True:
                plt.pause(0.05)

    def plot_state(self, game, node_list=None, block=True):
        """
        Plot the current state of a game. Extensive use of NetworkX library, main method used is draw_networkx() and it
        is given various parameters like positions, labels, colors, sizes. The majority of the code here only computes
        those values.
        :param game: Game, current game object
        :param node_list: [int], List of nodes to be plotted
        :param block: boolean, graph stop or not computations
        :return: void
        """
        positions = self.get_positions(game.rules.nb_players)
        colors = self.get_colors(game)
        current_graph, labels, sizes = self.get_graph_labels_sizes(game, len(game.history) - 1, node_list)

        plt.axis([-2, 2, -2, 2])
        plt.axis('off')

        nx.draw_networkx(current_graph, positions, labels=labels,
                         node_color=colors, node_size=sizes, alpha=self.node_transparency)

        plt.show(block=block)

    def plot_game(self, game, interactive=False, time_step=0.05, node_list=None, leader_board=False):
        """
        Plot a whole game.
        :param game: Game, current game object
        :param interactive: Boolean, if false plot the history of the game, if true allow the user to navigate through
        the state
        :param time_step: int, time step for the non interactive mode
        :param node_list: [int], node to be plotted
        :return: void
        """
        positions = self.get_positions(game.rules.nb_players)
        colors = self.get_colors(game)
        alpha = self.node_transparency
        graphs = [self.get_graph_labels_sizes(game, round_number, node_list)
                  for round_number in range(len(game.history))]

        if interactive:

            # keyboard event handler
            def key_event(e):

                if e.key == "right":
                    self.current_interactive_graph += 1
                elif e.key == "left":
                    self.current_interactive_graph -= 1
                elif e.key == "up":
                    self.labels_interactive_graph = True
                elif e.key == "down":
                    self.labels_interactive_graph = False
                else:
                    return
                self.current_interactive_graph %= len(graphs)

                curr_pos = self.current_interactive_graph

                ax.cla()

                graph = graphs[curr_pos][0]
                labels = graphs[curr_pos][1]
                sizes = graphs[curr_pos][2]
                leader_board_str = ''
                if leader_board:
                    leader_board_str = _get_leader_board(game, curr_pos, self.leader_board_size, self.significant_digits)

                _display_graph(graph, positions, labels, colors, sizes, alpha, leader_board=leader_board_str,
                               display_labels=self.labels_interactive_graph, game=game)

                mng = plt.get_current_fig_manager()
                mng.resize(*mng.window.maxsize())

                fig.canvas.draw()

            fig = plt.figure()

            fig.canvas.mpl_connect('key_press_event', key_event)
            ax = fig.add_subplot(111)

            graph = graphs[0][0]
            labels = graphs[0][1]
            sizes = graphs[0][2]
            leader_board_str = ''
            if leader_board:
                leader_board_str = _get_leader_board(game, 0, self.leader_board_size, self.significant_digits)

            _display_graph(graph, positions, labels, colors, sizes, alpha, leader_board=leader_board_str,
                           display_labels=self.labels_interactive_graph, game=game)

            mng = plt.get_current_fig_manager()
            #mng.resize(*mng.window.maxsize())

            plt.show()

        else:

            plt.ion()

            for round_number in range(len(game.history)):

                plt.clf()

                graph = graphs[round_number][0]

                labels = graphs[round_number][1]
                sizes = graphs[round_number][2]
                leader_board_str = ''
                if leader_board:
                    leader_board_str = _get_leader_board(game, round_number, self.leader_board_size,
                                                         self.significant_digits)

                _display_graph(graph, positions, labels, colors, sizes, alpha, leader_board=leader_board_str,
                               display_labels=True, game=game)

                mng = plt.get_current_fig_manager()
                mng.resize(*mng.window.maxsize())

                # Pause to record video for presentations
                # if round_number == 0:
                #     plt.pause(10)

                plt.pause(time_step)

            while True:
                plt.pause(0.05)


def _display_graph(graph, positions, labels, colors, sizes, alpha, leader_board=None, display_labels=False, **kwargs):

    if leader_board:
        plt.axis([-1.5, 2, -2, 2])
        plt.axis('off')
        plt.text(1.5, 2, leader_board)
    else:
        plt.axis([-2, 2, -2, 2])
        plt.axis('off')

    if display_labels:
        nx.draw_networkx(graph, positions, labels=labels, node_color=colors,
                         node_size=sizes, alpha=alpha, **kwargs)
    else:
        nx.draw_networkx(graph, positions, node_color=colors, alpha=alpha, **kwargs)


def _get_leader_board(game, round_number, leader_board_size, significant_digits):
    g = nx.Graph()
    g.add_nodes_from(game.graph.nodes())
    g.add_edges_from(game.graph.edges())

    inverse_table = [(value, key) for key, value in nx.betweenness_centrality(g).items()]
    inverse_table = sorted(inverse_table, reverse=True)
    return "Leader board:\n" + "\n".join(
        map(
            lambda x: str(x[0]+1) + ". " +
                      str(game.players[x[1][1]].name) + ": " +
                      str(round(x[1][0], significant_digits)),
            enumerate(inverse_table[:leader_board_size])
        )
    )


"""
Rewrite draw_networkx to attach mlp canvas and handle user events
"""

def draw_networkx(G, pos=None, arrows=True, with_labels=True, **kwds):
    """Draw the graph G using Matplotlib.

    Draw the graph with Matplotlib with options for node positions,
    labeling, titles, and many other drawing features.
    See draw() for simple drawing without labels or axes.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.

    with_labels :  bool, optional (default=True)
       Set to True to draw labels on the nodes.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    nodelist : list, optional (default G.nodes())
       Draw only specified nodes

    edgelist : list, optional (default=G.edges())
       Draw only specified edges

    node_size : scalar or array, optional (default=300)
       Size of nodes.  If an array is specified it must be the
       same length as nodelist.

    node_color : color string, or array of floats, (default='r')
       Node color. Can be a single color format string,
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string, optional (default='o')
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8'.

    alpha : float, optional (default=1.0)
       The node and edge transparency

    cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of nodes

    vmin,vmax : float, optional (default=None)
       Minimum and maximum for node colormap scaling

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)

    width : float, optional (default=1.0)
       Line width of edges

    edge_color : color string, or array of floats (default='r')
       Edge color. Can be a single color format string,
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    edge_cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of edges

    edge_vmin,edge_vmax : floats, optional (default=None)
       Minimum and maximum for edge colormap scaling

    style : string, optional (default='solid')
       Edge line style (solid|dashed|dotted,dashdot)

    labels : dictionary, optional (default=None)
       Node labels in a dictionary keyed by node of text labels

    font_size : int, optional (default=12)
       Font size for text labels

    font_color : string, optional (default='k' black)
       Font color string

    font_weight : string, optional (default='normal')
       Font weight

    font_family : string, optional (default='sans-serif')
       Font family

    label : string, optional
        Label for graph legend

    Notes
    -----
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.
    Yes, it is ugly but drawing proper arrows with Matplotlib this
    way is tricky.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G)) # use spring layout

    >>> import matplotlib.pyplot as plt
    >>> limits=plt.axis('off') # turn of axis

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if pos is None:
        pos = nx.drawing.spring_layout(G)  # default to spring layout

    node_collection = draw_networkx_nodes(G, pos, **kwds)
    edge_collection = nx.draw_networkx_edges(G, pos, arrows=arrows, **kwds)
    if with_labels:
        nx.draw_networkx_labels(G, pos, **kwds)
    plt.draw_if_interactive()


def draw_networkx_nodes(G, pos,
                        nodelist=None,
                        node_size=300,
                        node_color='r',
                        node_shape='o',
                        alpha=1.0,
                        cmap=None,
                        vmin=None,
                        vmax=None,
                        ax=None,
                        linewidths=None,
                        label=None,
                        **kwds):
    """Draw the nodes of the graph G.

    This draws only the nodes of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    nodelist : list, optional
       Draw only specified nodes (default G.nodes())

    node_size : scalar or array
       Size of nodes (default=300).  If an array is specified it must be the
       same length as nodelist.

    node_color : color string, or array of floats
       Node color. Can be a single color format string (default='r'),
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8' (default='o').

    alpha : float
       The node transparency (default=1.0)

    cmap : Matplotlib colormap
       Colormap for mapping intensities of nodes (default=None)

    vmin,vmax : floats
       Minimum and maximum for node colormap scaling (default=None)

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)

    label : [None| string]
       Label for legend

    Returns
    -------
    matplotlib.collections.PathCollection
        `PathCollection` of the nodes.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nodes=nx.draw_networkx_nodes(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    fig = plt.figure()
    ax = fig.add_subplot(111)

    if ax is None:
        ax = plt.gca()

    if nodelist is None:
        nodelist = G.nodes()

    if not nodelist or len(nodelist) == 0:  # empty nodelist, no drawing
        return None

    try:
        xy = numpy.asarray([pos[v] for v in nodelist])
    except KeyError as e:
        raise nx.NetworkXError('Node %s has no position.'%e)
    except ValueError:
        raise nx.NetworkXError('Bad value in node positions.')

    node_collection = ax.scatter(xy[:, 0], xy[:, 1],
                                 s=node_size,
                                 c=node_color,
                                 marker=node_shape,
                                 cmap=cmap,
                                 vmin=vmin,
                                 vmax=vmax,
                                 alpha=alpha,
                                 linewidths=linewidths,
                                 label=label,
                                 picker=True)

    def on_pick(event):
        ind = event.ind
        artist = event.artist
        print(ind, numpy.take(xy, ind))
        print(artist)
        print(kwds.get('game').players[ind[0]].name)

    fig.canvas.mpl_connect('pick_event', on_pick)

    node_collection.set_zorder(2)
    return node_collection
