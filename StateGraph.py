from graphviz import Digraph
from copy import deepcopy

class StateGraph(object):
	def __init__(self, inflow, cycle):

		self.states = []
		self.connections = []
		self.inflow = inflow
		self.cycle = cycle

	def generate_all_states(self):

		# possible volume and outflow states
		volume = [['0','0'],['0','+'],['+','-'],['+','0'],['+','+'],['max','-'],['max','0']]
		outflow = [['0','0'],['0','+'],['+','-'],['+','0'],['+','+'],['max','-'],['max','0']]

		for i in self.inflow:
			for v in volume:
				for o in outflow:
					# only add states that have value correspondence
					if (v == o):
						self.states.append({'I': i, 'V': v, 'O': o})        

		# remove some illegal states
		for state in deepcopy(self.states):
			if (state["I"][0] == "0") and (state["O"][0] == "0") and (state["V"][1] != "0"):
				self.states.remove(state)
			elif (state["I"][0] != "0") and (state["O"][0] == "0") and (state["V"][1] != "+"):
				self.states.remove(state)
			elif ((state["I"][0] == "0") and (state["O"][0] != "0") and (state["V"][1] != "-")):
				self.states.remove(state)

	def get_next_states(self, x):   
	# Outputs all the possible next legal states Y from a state x

		def remove_duplicate_states(Y):
		# removes redundant states for efficiency

			Y_reduced = []
			for y in Y:
				if y not in Y_reduced:
					Y_reduced.append(y)
			return Y_reduced

		def new_magnitudes(Y):
		# produces new magnitudes for quantities Volume and Outlfow
		# based on their past magnitudes and their derivatives

			# combinations of [M, d] that the derivative does not affect the magnitude
			non_transitional = [["max", "+"], ["max", "0"],	["+", "0"],	["0", "0"],	["0", "-"]]

			for Q, q in zip(["V", "O"], ["Volume", "Output"]):
				if x[Q] not in non_transitional:
					
					# results in +
					if x[Q] == ["max", "-"]:
						for y in Y:
							y[Q][0] = "+"
							y["trace"] += "{}: The negative derivative reduces the magnitude from max to +. \n".format(q)
					
					# might result in 0 or remain +
					elif x[Q] == ["+", "-"]:
						
						# number of states before branching
						n = len(Y)
						
						# create two branches for every possible state
						for y in deepcopy(Y):
							Y.append(deepcopy(y))

						# fill half the branches with 0 and the other half with +
						for y in Y[:n]:
							y[Q][0] = "0"
							y["trace"] += "{}: We asume that the negative derivative is strong enough, the magnitude decreases to 0. \n".format(q)
						for y in Y[n:]:
							y[Q][0] = "+"
							y["trace"] += "{}: We asume that the negative derivative is not strong enough, the magnitude does not change. \n".format(q)
					
					# might result max or remain +
					elif x[Q] == ["+", "+"]:
						
						# number of states before branching
						n = len(Y)                

						# create two branches for every possible state
						for y in deepcopy(Y):
							Y.append(deepcopy(y))

						# fill half the branches with + and the other half with max
						for y in Y[:n]:
							y[Q][0] = "+"
							y["trace"] += "{}: We asume that the positive derivative is not strong enough, the magnitude does not change. \n".format(q)
						for y in Y[n:]:
							y[Q][0] = "max"
							y["trace"] += "{}: We asume that the positive derivative is strong enough, the magnitude increaes to max. \n".format(q)
					
					# results in +
					elif x[Q] == ["0", "+"]:
						for y in Y:
							y[Q][0] = "+"
							y["trace"] += "{}: The positive derivative increaes the magnitude from 0 to +. \n".format(q)
				
				# current derivative does not affect current magnitude
				# just copy the previous magnitude
				else:
					for y in Y:
						y[Q][0] = x[Q][0]  
						y["trace"] += "{}: The magnitude does not change due to the 0 derivative.".format(q)

			return Y

		def apply_value_correspondance(Y):

			Y_new = []

			for y in deepcopy(Y):
				if (y["V"][0] == "max") and (y["O"][0] == "+"):

					y["O"][0] = "max"
					y["trace"] += "VC: Magnitude of Outlfow becomes max. \n"
					Y_new.append(y)

				elif (y["V"][0] == "+") and (y["O"][0] == "max"):

					y["V"][0] = "max"
					y["trace"] += "VC: Magnitude of Volume becomes max. \n"
					Y_new.append(y)

				elif ((y["V"][0] == "0") and (y["O"][0] == "max")) or ((y["V"][0] == "max") and (y["O"][0] == "0")):

					y_copy1 = deepcopy(y)
					y_copy2 = deepcopy(y)

					y_copy1["V"][0] = "0"
					y_copy1["O"][0] = "0"
					y_copy1["trace"] += "VC: 0 and max conflict. We asume that both become 0. \n"

					y_copy2["V"][0] = "max"
					y_copy2["O"][0] = "max"
					y_copy2["trace"] += "VC: 0 and max conflict. We asume that both become max. \n"

					Y_new.append(y_copy1)
					Y_new.append(y_copy2)

				elif y["V"][0] == y["O"][0]:

					Y_new.append(y)

			return Y_new

		def apply_influence(Y):
		# applies the influence rules
		# I+ (Inflow, Volume) and I- (Outflow, Volume)
		# in some cases there is ambiguity that is resolved with branching

			new_Y = []

			# iterate through possible states so far created
			for y in deepcopy(Y):

				# Inflow positive and Outflow positive
				if (y["I"][0] == "+") and (y["O"][0] != "0"):

					# create three branches for every current state
					y_copy1 = deepcopy(y)
					y_copy2 = deepcopy(y)
					y_copy3 = deepcopy(y)
					
					# derivative of Inflow is greater
					y_copy1["V"][1] = "+"
					y_copy1["trace"] += "Volume: Conflict between positive magnitude of Inflow and positive magnitude of Outflow. We asume that the influence of Inflow is stronger. Derivative of Volume becomes +. \n"

					# derivative of Outflow is greater
					y_copy2["V"][1] = "-"
					y_copy1["trace"] += "Volume: Conflict between positive magnitude of Inflow and positive magnitude of Outflow. We asume that the influence of Outflow is stronger. Derivative of Volume becomes -. \n"
					
					# derivatives are equal
					y_copy3["V"][1] = "0"
					
					y_copy1["trace"] += "Volume: Conflict between positive magnitude of Inflow and positive magnitude of Outflow. We asume that the influence of Inflow is equal to that of the Outlfow. Derivative of Volume becomes 0. \n"
					new_Y = new_Y + [y_copy1, y_copy2, y_copy3]
				
				# Inflow positive and Outlfow 0
				# results in Volume +
				elif (y["I"][0] == "+") and (y["O"][0] == "0"):
					y["V"][1] = "+"
					new_Y.append(y)
					y["trace"] += "Volume: Derivative becomes positive due to the magnitude of Inflow being larger than that of the Outflow. \n"
				
				# Inflow 0 and Outflow positive
				# results in Volume -
				elif (y["I"][0] == "0") and (y["O"][0] != "0"):
					y["V"][1] = "-"
					new_Y.append(y)
					y["trace"] += "Volume: Derivative becomes negative due to the magnitude of Outlfow being larger than that of the Inflow. \n"

				# both quantities 0
				# result in Volume 0
				elif (y["I"][0] == "0") and (y["O"][0] == "0"):
					y["V"][1] = "0"  
					new_Y.append(y)
					y["trace"] += "Volume: Derivative becomes zero due to the magnitude of Inflow being equal to that of the Outflow (zero). \n"

			return new_Y

		def apply_reduction(Y):
		# reduce derivatives of Volume and Outflow

			for y in Y:
				for Q, q in zip(["V", "O"], ["Volume", "Outflow"]):

					# [0, -] -> [0, 0]
					if (y[Q][0] == "0") and (y[Q][1] == "-"):
						y[Q][1] = "0"
						y["trace"] += "{}: derivative becomes from negative zero because magnitude is already zero \n".format(q)

					# [max, +] -> [max, 0]
					elif (y[Q][0] == "max") and (y[Q][1] == "+"):
						y[Q][1] = "0"
						y["trace"] += "{}: derivative becomes from positive zero because magnitude is already max \n.".format(q)

			return Y
				   
		# define list of new states Y
		# only one in the begining
		Y = [{"I": ["", ""], "V": ["", ""], "O": ["", ""], "trace": ""}]

		# get next inflow transition
		# if inflow is cyclical, restart process after last index
		# if inflow is not cyclical, last index will remain the same
		next_index = self.inflow.index(x["I"]) + 1
		Y[0]["trace"]= "I: Chaged exogenously, the next state is state {} in the defined transitions. \n".format(next_index)
		if next_index == len(self.inflow):
			if self.cycle:
				next_index = 0
				Y[0]["trace"] = "I: Changed exogenously, the next state is state {} in the defined transitions. \n".format(next_index)
			else:
				next_index -= 1
				Y[0]["trace"] = "I: Remains the same, this is the last state in its defined transitions. \n"
		Y[0]["I"] = self.inflow[next_index]
		
		# produce new magnitudes for previous magnitudes and derivatives
		Y = new_magnitudes(Y)

		# remove possible duplicate states
		Y = remove_duplicate_states(Y)

		# Biderictional Value Correspondance in magnitude of Volume and Outflow
		Y = apply_value_correspondance(Y)
		# for y in Y:
		# 	y["O"][0] = y["V"][0]

		# get new derivative of Volume based on magnitudes of Inflow and Outflow
		Y = apply_influence(Y)
		
		# remove possible duplicate states
		Y = remove_duplicate_states(Y)
			
		# apply proportionality between Outflow and Volume
		for y in Y:
			if y["V"][1] != y["O"][1]:
				y["O"][1] = deepcopy(y["V"][1])
				y["trace"] += "Outflow: derivative becomes {} due to proportionality. \n".format(y["O"][1])

		# apply reduction rules [max, +] -> [max, 0] and [0, -] -> [0, 0]
		Y = apply_reduction(Y)

		# Remove originating state if produced
		if x in Y:
			Y.remove(x)
		
		return Y

	def getConnections(self):
	# iterates through all legal states and produces a list of every possible state from them
	# connections is a dictionary with keys the state_ids and value a list of state_ids that follow it

		self.connections = {}

		# iterate through legal states
		for i, state in enumerate(self.states):

			# produce next_states for state i
			next_states = self.get_next_states(state)

			# initialize connections for state i
			leads_to = {}

			# append the id of every next state in the connections
			for next_state in next_states:

				trace = next_state["trace"]
				del next_state["trace"]

				if self.states.index(next_state) not in leads_to.keys():
					leads_to[self.states.index(next_state)] = trace

			self.connections[i] = leads_to

		self.start_states = []

		# find all the starting states
		# states that none of the other states lead to
		for i in range(len(self.states)):

			start_state = True
			for connection in self.connections.values():
				if i in connection:
					start_state = False
					break

			if start_state:
				self.start_states.append(i)

	def createStateGraph(self):
		# visualize graph from states and connections

		# graph object
		sg = Digraph()

		# add start node
		sg.node("000", "start \n")

		for i,state in enumerate(self.states):
			state_text = str(i)+"\n"
			for quantity,value in state.items():
				state_text += str(quantity)+str(value)+"\n"
			sg.node(str(i),state_text)

		# add connections to start
		for start_state in self.start_states:
			sg.edge("000", str(start_state))

		for key,edges in self.connections.items():
			for edge in edges:
				sg.edge(str(key),str(edge))

		sg.render(filename="state_graph", view=True)


	def find_shortest_path(self, start_state, end_state, path = []):
	# returns a list containinig state transitions (path) from start to end state specified

		# initialize path
		path = path + [start_state]

		# end process if there is a match
		if start_state == end_state:
			return path

		# return none if there is no possible path
		if not start_state in self.connections.keys():
			return None

		shortest = None

		# call recursively the function to find the shortest path each time
		for current_state in self.connections[start_state].keys():
			if current_state not in path:
				newpath = self.find_shortest_path(current_state, end_state, path)
				if newpath:
					if not shortest or len(newpath) < len(shortest):
						shortest = newpath

		return shortest


	def generate_trace(self, start_state, end_state):

		# find shortest path between the two states
		path = self.find_shortest_path(start_state, end_state)

		print("shortest path:", path)
		print("_"*50)

		for i in range(len(path) - 1):
			s1, s2 = path[i:i+2]
			
			trace = self.connections[s1][s2]

			print("from state {} to state {}".format(s1, s2))
			print(trace)


