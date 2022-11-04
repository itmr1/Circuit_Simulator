import numpy as np
import objects as obj

matrix_test = True # Turn on to check matrix at one freq

sources = [[],[]]   # m , component

def reset ():
	global sources
	del sources
	sources = [[],[]]

def conductance_matrix (rows, omega):
	G_matrix = np.zeros((rows, rows), dtype=complex)
	for m in range(rows):
		has_sources = False
		grounded = False
		multi = False
		multinodes = []
		for component in obj.Nset[m+1].branches: #Must check for any grounded source first
			if (type(component) == type(obj.Voltage())) and (component.get_DC() == None):
				if (component.get_node1().get_num() == 0) or (component.get_node2().get_num() == 0): #grounded source case
					if matrix_test: print("node", m+1, "is ground source")
					has_sources = True
					grounded = True
					sources[0].append(m)
					sources[1].append(component)
					G_matrix[m, m] = complex(1) if (component.get_node2().get_num() == 0) else complex(-1)
		if not grounded:
			m_sources = [source for source in obj.Nset[m+1].branches if type(source) == obj.Voltage]
			if len(m_sources) > 1: # Checks for multiple sources at one node
				multi = True
			for component in obj.Nset[m+1].branches: #Now checks for floating sources
				if not has_sources and (type(component) == type(obj.Voltage())) and (component.get_DC() == None) \
					and (component.get_node1().get_num() != 0) and (component.get_node2().get_num() != 0):
					has_sources = True
					if component not in sources[1] and not multi: #must be KVL row
						if matrix_test: print("node", m+1, "is floating KVL")
						sources[0].append(m)
						sources[1].append(component)
						G_matrix[m, component.get_node1().get_num() - 1] = complex(1)
						G_matrix[m, component.get_node2().get_num() - 1] = -complex(1)
					else: 										#must be KCL row
						if matrix_test and not multi: print("node", m+1, "is floating KCL")
						elif matrix_test and multi: print("node", m+1, "is multi KCL")
						multinodes.append(obj.Nset[m+1]) #nodes in supernode
						for source in m_sources:
							if source.get_node1() not in multinodes:
								multinodes.append(source.get_node1())
							elif source.get_node2() not in multinodes:
								multinodes.append(source.get_node2())
						for n in range(rows):
							sum_G = 0
							for component in obj.Nset[n+1].branches:
								if component.get_node1() in multinodes or component.get_node2() in multinodes: #OR to check if connected to multinode
									if not (component.get_node1() in multinodes and component.get_node2() in multinodes): #NAND to exclude conductances in supernode
										try: sum_G += component.ss_G(omega)
										except: pass
							if obj.Nset[n+1] in multinodes:								
								G_matrix[m, n] = sum_G
							else:
								G_matrix[m, n] = -sum_G
		if not has_sources:
			if matrix_test: print("node", m+1, "has no sources")
			for n in range(rows): # going through cells
				sum_G = 0
				for i, component in enumerate(obj.Nset[m+1].branches):
					if component in obj.Nset[n+1].branches: #common components
						try: sum_G += component.ss_G(omega)
						except: pass
				if m == n:	#Gmm
					G_matrix[m, n] = sum_G
				else:		#Gmn
					G_matrix[m, n] = -sum_G
	return G_matrix

def short_inductor ():
	obj.Ndupes2 = obj.Nset.copy()
	for source in obj.L:
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
			obj.Ndupes2[obj.Nset.index(scrapped_node)] = kept_node #for user input
			obj.Nset[obj.Nset.index(scrapped_node)] = None
			del scrapped_node
	obj.Nset2 = [node for node in obj.N if node != None]	

def diode_matrix (rows):
	G_matrix = np.zeros((rows, rows), dtype=complex)
	for m in range(rows):
		has_sources = False
		grounded = False
		multi = False
		multinodes = []
		for component in obj.Nset2[m+1].branches: #Must check for any grounded source first
			if (type(component) == type(obj.Voltage())) and (component.get_DC() != None):
				if (component.get_node1().get_num() == 0) or (component.get_node2().get_num() == 0): #grounded source case
					has_sources = True
					grounded = True
					sources[0].append(m)
					sources[1].append(component)
					G_matrix[m, m] = complex(1) if (component.get_node2().get_num() == 0) else complex(-1)
		if not grounded:
			m_sources = [source for source in obj.Nset2[m+1].branches if type(source) == obj.Voltage]
			if len(m_sources) > 1: # Checks for multiple sources at one node
				multi = True
			for component in obj.Nset2[m+1].branches: #Now checks for floating sources
				if not has_sources and (type(component) == type(obj.Voltage())) and (component.get_DC() != None) and (component.get_node1().get_num() != 0) and (component.get_node2().get_num() != 0):
					has_sources = True
					if component not in sources[1] and not multi: #must be KVL row
						sources[0].append(m)
						sources[1].append(component)
						G_matrix[m, component.get_node1().get_num() - 1] = complex(1)
						G_matrix[m, component.get_node2().get_num() - 1] = -complex(1)
					else: 										#must be KCL row
						multinodes.append(obj.Nset2[m+1]) #nodes in supernode
						for source in m_sources:
							if source.get_node1() not in multinodes:
								multinodes.append(source.get_node1())
							elif source.get_node2() not in multinodes:
								multinodes.append(source.get_node2())
						for n in range(rows):
							sum_G = 0
							for component in obj.Nset2[n+1].branches:
								if component.get_node1() in multinodes or component.get_node2() in multinodes: #OR to check if connected to multinode
									if not (component.get_node1() in multinodes and component.get_node2() in multinodes): #NAND to exclude conductances in supernode
										if type(component) == obj.Resistor:													
											try:
												sum_G += component.ss_G(1) 
												#any omega value
											except: pass
							if obj.Nset2[n+1] in multinodes:																
								G_matrix[m, n] = sum_G
							else:									
								G_matrix[m, n] = -sum_G
		if not has_sources:
			for n in range(rows): # going through cells
				sum_G = 0
				if m == n: #Gnn
					for component in obj.Nset2[m+1].branches:
						if type(component) == obj.Resistor:
							try: sum_G += component.ss_G(1) #any omega value
							except: pass
					G_matrix[m, n] = sum_G
				else: #Gmn
					for i, component in enumerate(obj.Nset2[m+1].branches):
						if component in obj.Nset2[n+1].branches: #common components
							if type(component) == obj.Resistor:
								try: sum_G += component.ss_G(1) #any omega value
								except: pass
					G_matrix[m, n] = -sum_G
	return G_matrix

def current_matrix (rows):
	I_matrix = np.zeros((rows, 1), dtype=complex)
	for m in range(rows):
		if m in sources[0]:
			index = sources[0].index(m)
			component = sources[1][index]
			if (component.get_node1().get_num() == m+1) or (component.get_node2().get_num() == m+1):
				I_matrix[m] = component.ss_voltage()
	reset()
	return I_matrix

def diode_current_matrix (rows):
	I_matrix = np.zeros((rows, 1), dtype=complex)
	for m in range(rows):
		sum_I = 0
		if m in sources[0]:
			index = sources[0].index(m)
			component = sources[1][index]
			if (component.get_node1().get_num() == m+1) or (component.get_node2().get_num() == m+1):
				I_matrix[m] = component.get_DC()
		else:
			for source in obj.I:
				try:
					if (source.get_node1().get_num() == m+1):
						sum_I += -source.get_current()
					elif (source.get_node2().get_num() == m+1):
						sum_I += source.get_current()
				except:
					pass
			I_matrix[m] = sum_I				
	reset()
	return I_matrix

def inv_multiply (G_matrix, I_matrix):
	inv_G_matrix = np.linalg.inv(G_matrix)
	V_matrix = np.matmul(inv_G_matrix, I_matrix)
	reset()
	return V_matrix