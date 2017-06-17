# Betweeness_Centality_Competition
Description:
A number of players compete in order to obtain the highest betweenness centrality in a network. There are N players in the game and the game lasts for T periods. The players are either active or passive. Active players have the ability to create or destroy edges while passive players do not. Moreover, active players are further classified as artificial intelligent(AI) or human. AI players are myopic in the sense that they try to maximize their instantaneous betweenness centrality without taking into account future steps. Human players make their choices based on input from users. Depending on the application, specific predefined edges can be prevented from being created.  At each period, players simultaneously choose an edge to be created or destroyed. The player with the highest betweenness centrality at the end of the game wins.


The default settings are:

T=7;
N= 20;
Number of AI players =2;
Number of human players = 2 (only in the human_interaction.py file);
Impossible edges= None.




For customized settings:

T: In line 21, set rules.nb_max_step=T;
N: In line 22, set rules.nb_players=N;
Number of AI players: Add/Remove players using a format similar to lines 33-35;
Number of human players: Add/Remove players using a format similar to lines 36-37;
Impossible edges: Add impossible edges in line 50. (e.g. game1.impossible_edges = [ (2,3), (4,5)] would prevent edges to be formed between nodes 2 and 3 and between nodes 4 and 5).




The human_interaction.py code should be used if human users are included and the AI_interaction.py code should be used if no human interaction is included. 

