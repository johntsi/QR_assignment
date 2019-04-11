from graphviz import Digraph
from copy import copy, deepcopy

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
		for state in self.states:
			if ((state["I"][0] == "0") and (state["O"][0] == "0") and (state["V"][1] != "0")):
				self.states.remove(state)
			elif ((state["I"][0] != "0") and (state["O"][0] == "0") and (state["V"][1] != "+")):
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

			for Q in ["V", "O"]:
				if x[Q] not in non_transitional:
					
					# results in +
					if x[Q] == ["max", "-"]:
						for y in Y:
							y[Q][0] = "+"
					
					# might result in 0 or remain +
					elif x[Q] == ["+", "-"]:
						
						# number of states before branching
						n = len(Y)
						
						# create two branches for every possible state
						for y in deepcopy(Y):
							Y.append(copy(y))

						# fill half the branches with 0 and the other half with +
						for y in Y[:n]:
							y[Q][0] = "0"
						for y in Y[n:]:
							y[Q][0] = "+"
					
					# might result max or remain +
					elif x[Q] == ["+", "+"]:
						
						# number of states before branching
						n = len(Y)                

						# create two branches for every possible state
						for y in deepcopy(Y):
							Y.append(copy(y))

						# fill half the branches with + and the other half with max
						for y in Y[:n]:
							y[Q][0] = "+"
						for y in Y[n:]:
							y[Q][0] = "max"
					
					# results in +
					elif x[Q] == ["0", "+"]:
						for y in Y:
							y[Q][0] = "+"
				
				# current derivative does not affect current magnitude
				# just copy the previous magnitude
				else:
					for y in Y:
						y[Q][0] = x[Q][0]  

			return Y

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
					y_copy1 = copy(y)
					y_copy2 = copy(y)
					y_copy3 = copy(y)
					
					# derivative of Inflow is greater
					y_copy1["V"][1] = "+"

					# derivative of Outflow is greater
					y_copy2["V"][1] = "-"

					# derivatives are equal
					y_copy3["V"][1] = "0"
					
					new_Y += [y_copy1, y_copy2, y_copy3]
				
				# Inflow positive and Outlfow 0
				# results in Volume +
				elif (y["I"][0] == "+") and (y["O"][0] == "0"):
					y["V"][1] = "+"
					new_Y.append(y)
				
				# Inflow 0 and Outflow positive
				# results in Volume -
				elif (y["I"][0] == "0") and (y["O"][0] != "0"):
					y["V"][1] = "-"
					new_Y.append(y)
					
				# both quantities 0
				# result in Volume 0
				elif (y["I"][0] == "0") and (y["O"][0] == "0"):
					y["V"][1] = "0"  
					new_Y.append(y)
					
			return new_Y

		def apply_reduction(Y):
		# reduce derivatives of Volume and Outflow

			for y in Y:
				for Q in ["V", "O"]:

					# [0, -] -> [0, 0]
					if (y[Q][0] == "0") and (y[Q][1] == "-"):
						y[Q][1] = "0"

					# [max, +] -> [max, 0]
					elif (y[Q][0] == "max") and (y[Q][1] == "+"):
						y[Q][1] = "0"

			return Y
				   
		# define list of new states Y
		# only one in the begining
		Y = [{"I": ["", ""], "V": ["", ""], "O": ["", ""]}]

		# get next inflow transition
		# if inflow is cyclical, restart process after last index
		# if inflow is not cyclical, last index will remain the same
		next_index = self.inflow.index(x["I"]) + 1
		if next_index == len(self.inflow):
			if self.cycle:
				next_index = 0
			else:
				next_index -= 1
		Y[0]["I"] = self.inflow[next_index]
		
		# produce new magnitudes for previous magnitudes and derivatives
		Y = new_magnitudes(Y)

		# remove possible duplicate states
		Y = remove_duplicate_states(Y)

		# Biderictional Value Correspondance in magnitude of Volume and Outflow
		for y in Y:
			y["O"][0] = y["V"][0]

		# get new derivative of Volume based on magnitudes of Inflow and Outflow
		Y = apply_influence(Y)
		
		# remove possible duplicate states
		Y = remove_duplicate_states(Y)
			
		# apply proportionality between Outflow and Volume
		for y in Y:
			y["O"][1] = y["V"][1]

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
			leads_to = []

			# append the id of every next state in the connections
			for next_state in next_states:
				if self.states.index(next_state) not in leads_to:
					leads_to.append(self.states.index(next_state))

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