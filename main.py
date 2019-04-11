from StateGraph import StateGraph
import os

# add graphviz to path
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

# specify inflow transitions
Inflow = [["0", "+"], ["+", "+"], ["+", "0"], ["+", "-"], ["0", "0"]]

# specify whether inflow states are cyclical
cycle = True

state_graph = StateGraph(Inflow, cycle)
state_graph.generate_all_states()
state_graph.getConnections()
state_graph.createStateGraph()