import objects as obj

multiplier_dict = {'p' : 1e-12, 'n' : 1e-9, 'µ' : 1e-6, 'u' : 1e-6, 'Î¼' : 1e-6, 'm' : 1e-3, 'k' : 1e3, 'G' : 1e9}

def value (line, section):
	term = line.split()[section]
	if term[-1].isdigit():
		return float(term)
	elif term[-3:].lower() == 'meg':
		return float(term[0:-3]) * 1e6
	else:
		try:
			return float(term[0:-1]) * multiplier_dict[term[-1]]
		except:
			return float(term[0:-2]) * multiplier_dict[term[-2:]]

def bjt_node_wrangler(line, component , bjt_type):
	component.set_type(bjt_type)
	collector_term = line.split()[1] #node1
	base_term = line.split()[2] #node2
	emitter_term = line.split()[3] #node3
	collector_val = 0 if collector_term == '0' else int(collector_term[1:])
	base_val = 0 if base_term == '0' else int(base_term[1:])
	emitter_val = 0 if emitter_term == '0' else int(emitter_term[1:])
	#ro = obj.Resistor()
	#rbe = obj.Resistor()
	#current_source = obj.Current()
	obj.I.append(component.current_eq)
	obj.R.append(component.ro_eq)
	obj.R.append(component.rbe_eq)
	component.ro_eq.resistance = component.get_ro()
	component.rbe_eq.resistance = component.get_rbe()
	component.current_eq.set_current(component.get_gm() * component.vbe)
	component.current_eq.voltage_controlled = True
	#Collector
	collector_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == collector_val:
				collector_node_exists = True
				component.set_node1(node)
				node.add_branch(component.ro_eq)
				node.add_branch(component.current_eq)
				if bjt_type == "NPN":
					component.ro_eq.set_node1(node)
					component.current_eq.set_node1(node)
				else:   #PNP
					component.ro_eq.set_node2(node)
					component.current_eq.set_node2(node)
				break
		except: pass
	if not collector_node_exists:
		try:
			obj.N[collector_val] = obj.Node()
		except:
			for i in range(len(obj.N), collector_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[collector_val].set_num(collector_val)
		obj.N[collector_val].add_branch(component.ro_eq)
		obj.N[collector_val].add_branch(component.current_eq)
		component.set_node1(obj.N[collector_val])
		if bjt_type == "NPN":
			component.ro_eq.set_node1(obj.N[collector_val])
			component.current_eq.set_node1(obj.N[collector_val])
		else:
			component.ro_eq.set_node2(obj.N[collector_val]) #pnp
			component.current_eq.set_node2(obj.N[collector_val])
	#Emitter
	emitter_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == emitter_val:
				emitter_node_exists = True
				#adding  the SS model here
				component.set_node3(node)
				node.add_branch(component.ro_eq)
				node.add_branch(component.rbe_eq)
				node.add_branch(component.current_eq)
				if bjt_type == "NPN":
					component.ro_eq.set_node2(node)
					component.rbe_eq.set_node2(node)
					component.current_eq.set_node2(node)
				else:   #pnp
					component.ro_eq.set_node1(node)
					component.rbe_eq.set_node1(node)
					component.current_eq.set_node1(node)
				break
		except: pass
	if not emitter_node_exists:
		try:
			obj.N[emitter_val] = obj.Node()
		except:
			for i in range(len(obj.N), emitter_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[emitter_val].set_num(emitter_val)
		obj.N[emitter_val].add_branch(component.ro_eq) # adding ro resitor
		obj.N[emitter_val].add_branch(component.rbe_eq) #adding rbe resistor
		obj.N[emitter_val].add_branch(component.current_eq) #adding current source
		component.set_node3(obj.N[emitter_val])
		if bjt_type == "NPN":
			component.ro_eq.set_node2(obj.N[emitter_val])
			component.rbe_eq.set_node2(obj.N[emitter_val])
			component.current_eq.set_node2(obj.N[emitter_val])
		else:  #pnp
			component.ro_eq.set_node1(obj.N[emitter_val])
			component.rbe_eq.set_node1(obj.N[emitter_val])
			component.current_eq.set_node1(obj.N[emitter_val])
	#Base
	base_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == base_val:
				base_node_exists = True
				node.add_branch(component.rbe_eq)
				component.set_node2(node)
				if bjt_type == "NPN":
					component.rbe_eq.set_node1(node)
				else: #pnp
					component.rbe_eq.set_node2(node)
				break
		except: pass
	if not base_node_exists:
		try:
			obj.N[base_val] = obj.Node()
		except:
			for i in range(len(obj.N), base_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[base_val].set_num(base_val)
		obj.N[base_val].add_branch(component.rbe_eq)
		component.set_node2(obj.N[base_val])
		if bjt_type == "NPN":
			component.rbe_eq.set_node1(obj.N[base_val])
		else:
			component.rbe_eq.set_node2(obj.N[base_val])

def bjt_node_wrangler2(line, component , bjt_type):
	component.set_type(bjt_type)
	collector_term = line.split()[1] #node1
	base_term = line.split()[2] #node2
	emitter_term = line.split()[3] #node3
	collector_val = 0 if collector_term == '0' else int(collector_term[1:])
	base_val = 0 if base_term == '0' else int(base_term[1:])
	emitter_val = 0 if emitter_term == '0' else int(emitter_term[1:])
	obj.I.append(component.current_eq)
	obj.D.append(component.diode_eq)
	component.current_eq.set_current(component.get_gm() * component.vbe)
	component.current_eq.voltage_controlled = True
	#insert diode using diode node wrangler
	line = "D1 " + base_term + " " + emitter_term
	diode_node_wrangler(line,component.diode_eq)
	#Collector
	collector_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == collector_val:
				collector_node_exists = True
				component.set_node1(node)
				node.add_branch(component.current_eq)
				if bjt_type == "NPN":
					component.current_eq.set_node1(node)
				else:   #PNP
					component.current_eq.set_node2(node)
				break
		except: pass
	if not collector_node_exists:
		try:
			obj.N[collector_val] = obj.Node()
		except:
			for i in range(len(obj.N), collector_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[collector_val].set_num(collector_val)
		obj.N[collector_val].add_branch(component.current_eq)
		component.set_node1(obj.N[collector_val])
		if bjt_type == "NPN":
			component.current_eq.set_node1(obj.N[collector_val])
		else:
			 #pnp
			component.current_eq.set_node2(obj.N[collector_val])
	#Emitter
	emitter_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == emitter_val:
				emitter_node_exists = True
				#adding  the SS model here
				component.set_node3(node)
				node.add_branch(component.current_eq)
				if bjt_type == "NPN":
					component.current_eq.set_node2(node)
				else:   #pnp
					component.current_eq.set_node1(node)
				break
		except: pass
	if not emitter_node_exists:
		try:
			obj.N[emitter_val] = obj.Node()
		except:
			for i in range(len(obj.N), emitter_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[emitter_val].set_num(emitter_val)
		obj.N[emitter_val].add_branch(component.current_eq) #adding current source
		component.set_node3(obj.N[emitter_val])
		if bjt_type == "NPN":
			component.current_eq.set_node2(obj.N[emitter_val])
		else:  #pnp
			component.current_eq.set_node1(obj.N[emitter_val])
	#Base
	base_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == base_val:
				base_node_exists = True
				node.add_branch(component.rbe_eq)
				component.set_node2(node)
				if bjt_type == "NPN":
					### component.rbe_eq.set_node1(node)
					pass
				else: #pnp
					### component.rbe_eq.set_node2(node)
					pass
				break
		except: pass
	if not base_node_exists:
		try:
			obj.N[base_val] = obj.Node()
		except:
			for i in range(len(obj.N), base_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[base_val].set_num(base_val)
		#obj.N[base_val].add_branch(component.rbe_eq)
		component.set_node2(obj.N[base_val])
		if bjt_type == "NPN":
			### component.rbe_eq.set_node1(obj.N[base_val])
			pass
		else:
			### component.rbe_eq.set_node2(obj.N[base_val])
			pass

def diode_node_wrangler(line,component):
	anode_term = line.split()[1] #node1
	cathode_term = line.split()[2] #node2
	anode_val = 0 if anode_term == '0' else int(anode_term[1:])
	cathode_val = 0 if cathode_term == '0' else int(cathode_term[1:])
	component.resistor_eq.resistance = component.get_resistor_eq()
	component.current_eq.current = component.get_current_eq()
	obj.I.append(component.current_eq)
	obj.R.append(component.resistor_eq)
	#Anode
	anode_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == anode_val:
				anode_node_exists = True
				node.add_branch(component.resistor_eq)
				node.add_branch(component.current_eq)
				component.set_node1(node)
				component.resistor_eq.set_node1(node)
				component.current_eq.set_node1(node)
				break
		except: pass
	if not anode_node_exists:
		try:
			obj.N[anode_val] = obj.Node()
		except:
			for i in range(len(obj.N), anode_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[anode_val].set_num(anode_val)
		obj.N[anode_val].add_branch(component.resistor_eq)
		obj.N[anode_val].add_branch(component.current_eq)
		component.set_node1(obj.N[anode_val])
		component.resistor_eq.set_node1(obj.N[anode_val])
		component.current_eq.set_node1(obj.N[anode_val])
	#Cathode
	cathode_node_exists = False
	for node in obj.N:
		try:
			if node.get_num() == cathode_val:
				cathode_node_exists = True
				node.add_branch(component.resistor_eq)
				node.add_branch(component.current_eq)
				component.set_node2(node)
				component.resistor_eq.set_node2(node)
				component.current_eq.set_node2(node)
				break
		except: pass
	if not cathode_node_exists:
		try:
			obj.N[cathode_val] = obj.Node()
		except:
			for i in range(len(obj.N), cathode_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[cathode_val].set_num(cathode_val)
		obj.N[cathode_val].add_branch(component.resistor_eq)
		obj.N[cathode_val].add_branch(component.current_eq)
		component.set_node2(obj.N[cathode_val])
		component.resistor_eq.set_node2(obj.N[cathode_val])
		component.current_eq.set_node2(obj.N[cathode_val])
		


def node_wrangler (line, component):
	node1_term = line.split()[1]
	node2_term = line.split()[2]
	node1_val = 0 if node1_term == '0'  else int(node1_term[1:])
	node2_val = 0 if node2_term == '0'  else int(node2_term[1:])
	#Node1
	node1_exists = False
	for node in obj.N:
		try: #seeing if the node already exists
			if node.get_num() == node1_val:
				node1_exists = True
				node.add_branch(component)
				component.set_node1(node)
				break
		except: pass
	if not node1_exists:
		try: #If it doesn't, create it and retry
			obj.N[node1_val] = obj.Node()
		except:
			for i in range(len(obj.N), node1_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[node1_val].set_num(node1_val)
		obj.N[node1_val].add_branch(component)
		component.set_node1(obj.N[node1_val])
	#Node2
	node2_exists = False
	for node in obj.N:
		try: #seeing if the node already exists
			if node.get_num() == node2_val:
				node2_exists = True
				node.add_branch(component)
				component.set_node2(node)
				break
		except: pass
	if not node2_exists:
		try: #If it doesn't, create it and retry
			obj.N[node2_val] = obj.Node()
		except:
			for i in range(len(obj.N), node2_val):
				obj.N.append(None)
			obj.N.append(obj.Node())
		obj.N[node2_val].set_num(node2_val)
		obj.N[node2_val].add_branch(component)
		component.set_node2(obj.N[node2_val])

		
def parse_netlist (netlist):
	if len(obj.N) == 0: #Adding ground node to N
		obj.N.append(obj.Node())
		obj.N[0].set_num(0)
	netlist = open(netlist, 'r')
	lines = netlist.readlines()
	for line in lines: #Starts interpreting lines
		if line[0] == "*":
			pass #Skip comments
		elif line[0] == "V":
			obj.V.append(obj.Voltage())
			index = len(obj.V) - 1
			obj.V[index].set_num(int(line[1]))
			if line[-2] == ")": #First AC format
				AC_term = line.split()[-2:]
				amplitude = AC_term[0].split('(')[1]
				obj.V[index].set_amplitude(value(amplitude, 0))
				obj.V[index].set_phase(float(AC_term[1][:-1]))
			elif " AC " in line: #Second AC format
				try:
					obj.V[index].set_amplitude(value(line.split()[-2], 0))
					obj.V[index].set_phase(float(line.split()[-1]))
				except:
					obj.V[index].set_amplitude(value(line.split()[-1], 0))
					obj.V[index].set_phase(0)
			else: #DC sources
				obj.V[index].set_DC(value(line, -1))
			node_wrangler(line, obj.V[index])
		elif line[0] == "I":
			obj.I.append(obj.Current())
			index = len(obj.I) - 1
			obj.I[index].set_num(int(line[1]))
			obj.I[index].set_current(value(line, -1))
			node_wrangler(line, obj.I[index])
		elif line[0] == "R":
			obj.R.append(obj.Resistor())
			index = len(obj.R) - 1
			obj.R[index].set_num(int(line[1]))
			obj.R[index].set_resistance(value(line, -1))
			node_wrangler(line, obj.R[index])
		elif line[0] == "C":
			obj.C.append(obj.Capacitor())
			index = len(obj.C) - 1
			obj.C[index].set_num(int(line[1]))
			obj.C[index].set_capacitance(value(line, -1))
			node_wrangler(line, obj.C[index])
		elif line[0] == "L":
			obj.L.append(obj.Inductor())
			index = len(obj.L) - 1
			obj.L[index].set_num(int(line[1]))
			obj.L[index].set_inductance(value(line, -1))
			node_wrangler(line, obj.L[index])
		elif line[0] == "D":
			obj.D.append(obj.Diode())
			index = len(obj.D) - 1
			obj.D[index].set_num(int(line[1]))
			diode_node_wrangler(line, obj.D[index])
		elif line[0] == "Q":
			print("Adding BJT")
			obj.BJT.append(obj.bj_transistor())
			index = len(obj.BJT) -1
			obj.BJT[index].set_num(int(line[1]))
			bjt_node_wrangler2(line, obj.BJT[index], "NPN")
		elif line[-3:] == "PNP":
			obj.BJT.append(obj.bj_transistor())
			index = len(obj.BJT) -1
			obj.BJT[index].set_num(int(line[1]))
			bjt_node_wrangler2(line, obj.BJT[index], "PNP")
		elif line[0:3] == ".ac":  #Simulation command
			points_per_dec = value(line, 2)
			start_freq = value(line, 3)
			stop_freq = value(line, 4)
		elif line[0:3] == ".end":
			break 
	netlist.close()
	return points_per_dec, start_freq, stop_freq 

def short ():
	obj.Ndupes = obj.N.copy()
	for source in obj.V:
		if source.get_DC() != None:
			if source.get_node1().get_num() < source.get_node2().get_num():
				kept_node = source.get_node1() #Kept node always smallest
				scrapped_node = source.get_node2()
			else:
				kept_node = source.get_node2()
				scrapped_node = source.get_node1()
			for component in scrapped_node.branches:
				if component.get_node1() == scrapped_node:
					component.set_node1(kept_node)
					kept_node.add_branch(component)
				elif component.get_node2() == scrapped_node:
					component.set_node2(kept_node)
					kept_node.add_branch(component)
			obj.Ndupes[obj.N.index(scrapped_node)] = kept_node
			obj.N[obj.N.index(scrapped_node)] = None
			del scrapped_node
	obj.Nset = [node for node in obj.N if node != None]	

def shortDC ():
	obj.Ndupes = obj.N.copy()
	for source in obj.V:
		if source.get_DC() == None:
			if source.get_node1().get_num() < source.get_node2().get_num():
				kept_node = source.get_node1() #kept node always smallest
				scrapped_node = source.get_node2()
			else:
				kept_node = source.get_node2()
				scrapped_node = source.get_node1()
			for component in scrapped_node.branches:
				if component.get_node1() == scrapped_node:
					component.set_node1(kept_node)
					kept_node.branches.append(component)
				elif component.get_node2() == scrapped_node:
					component.set_node2(kept_node)
					kept_node.branches.append(component)
			obj.Ndupes[obj.N.index(scrapped_node)] = kept_node
			obj.N[obj.N.index(scrapped_node)] = None
			del scrapped_node
	obj.Nset = [node for node in obj.N if node != None]	