from StateGraph import StateGraph
import os

# add graphviz to path
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

# specify inflow transitions
Inflow = [["0", "+"], ["+", "+"], ["+", "0"], ["+", "-"], ["0", "0"]]

# specify whether inflow states are cyclical
cycle = True

# specify whether to output graph visualization
output = True

# specify start and end states for generating the trace
start_state, end_state = 2, 23

# Create connections dictionary
state_graph = StateGraph(Inflow, cycle)
state_graph.generate_all_states()
state_graph.getConnections()

# output graph visualization in pdf form
if output:
	state_graph.createStateGraph()

# get trace for specified state tuple
state_graph.generate_trace(start_state, end_state)