
import math

N = []
Nset = []
Ndupes = []
V = []
I = []
R = []
C = []
L = []
D = []
BJT = []
MOS = []
operating_points = [[],[]]

def reset (): #Clears objects for memory management in case of automation
	global N, Nset, Ndupes, V, I, R, C, L , operating_points
	del N, Nset, Ndupes, V, I, R, C, L , operating_points
	N = []
	Nset = []
	Ndupes = []
	V = []
	I = []
	R = []
	C = []
	L = []
	operating_points = [[],[]]

def components_amount():
	return len(V) + len(I) + len(R) + len(C) + len(L) + len(D) + len(BJT) + len(MOS)

def OP_components_amount():
	return len(D) + len(BJT) + len(MOS)


class Node:
	def __init__ (self):
		self.num = None
		self.branches = []
	
	def get_num (self):
		return self.num

	def set_num (self, num):
		self.num = num

	def get_branches (self):
		return self.branches
	
	def add_branch (self, branch):
		self.branches.append(branch)


class Component:
	def __init__ (self):
		self.num = None
		self.node1 = 0
		self.node2 = 0
		self.node3 = None

	def get_num (self):
		return self.num

	def set_num (self, num):
		self.num = num

	def get_node1 (self):
		return self.node1

	def set_node1 (self, node):
		self.node1 = node

	def get_node2 (self):
		return self.node2

	def set_node2 (self, node):
		self.node2 = node

	def set_node3 (self, node):
		self.node3 = node
	
	def ss_G (self, omega):
		return (complex(1)/self.get_impedance(omega))
	

class Voltage (Component):
	def __init__ (self):
		super().__init__()
		self.DC = None
		self.amplitude = None
		self.phase = None

	def get_voltage (self):
		if self.DC == None:
			voltage = complex(self.amplitude * math.cos(math.radians(self.phase)), self.amplitude * math.sin(math.radians(self.phase)))
		else:
			voltage = complex(self.DC, 0)
		return voltage
	
	def get_DC (self):
		return self.DC

	def set_DC (self, DC):
		self.DC = DC
	
	def get_amplitude (self):
		return self.amplitude

	def set_amplitude (self, a):
		self.amplitude = a
	
	def get_phase (self):
		return self.phase
	
	def set_phase (self, p):
		self.phase = p
	
	def ss_voltage (self):
		if self.DC == None:
			ss_voltage = complex(self.amplitude * math.cos(math.radians(self.phase)), self.amplitude * math.sin(math.radians(self.phase)))
		return ss_voltage


class Current (Component):
	def __init__ (self):
		super().__init__()
		self.current = None
		self.voltage_controlled = False

	def get_current (self):
		current = complex(self.current, 0)
		return current
	
	def set_current (self, current):
		self.current = current
	
	def ss_current (self):
		return complex(0, 0)


class Resistor (Component):
	def __init__ (self):
		super().__init__()
		self.resistance = None

	def get_impedance (self, omega):
		impedance = complex(self.resistance, 0)
		return impedance
	
	def set_resistance (self, r):
		self.resistance = r


class Capacitor (Component):
	def __init__ (self):
		super().__init__()
		self.capacitance = None

	def get_impedance (self, omega):
		impedance = complex(0, -1/(omega * self.capacitance))
		return impedance
	
	def set_capacitance (self, c):
		self.capacitance = c


class Inductor (Component):
	def __init__ (self):
		super().__init__()
		self.inductance = None

	def get_impedance (self, omega):
		impedance = complex(0, omega * self.inductance)
		return impedance
	
	def set_inductance (self, l):
		self.inductance = l


class Diode (Component):
	
	def __init__(self):
		super().__init__()
		self.IS = 1e-14
		self.guess = 0.7
		self.VT = 0.02585
		self.resistor_eq = Resistor()
		self.current_eq = Current()

	def set_satcurrent (self, Is):
		self.IS = Is

	def set_oppoint (self, point):
		self.guess = point
	def get_resistor_eq(self):
		conductance = (self.IS / self.VT)*math.exp(self.guess/self.VT)
		impedance = 1/conductance
		return impedance

	def get_current_eq(self):
		dcurrent = self.IS*(math.exp(self.guess/self.VT)-1)
		current = (dcurrent - ((1/self.get_resistor_eq()*self.guess)))
		return current
	

class bj_transistor(Component):
	def __init__(self):
		super().__init__()
		self.Ic = 0.001
		self.vT = 0.02585
		self.vbe = 0.7
		self.VA = 100
		self.beta = 200
		self.Is = 1e-14
		self.current_eq = Current()
		self.diode_eq = Diode()
		self.bjt_type = ""
		
		
	def set_type(self, bjt):
		self.bjt_type = bjt

	def get_type(self):
		return self.bjt_type

	def get_gm (self):
		return self.Ic / self.vT
	
	def get_ro (self):
		return self.VA / self.Ic

	def get_rbe (self):
		return self.beta / self.get_gm()

	def set_vbe(self,vbe_guess):
		self.vbe = vbe_guess
	
	def set_ic(self,ic_guess):
		self.Ic = ic_guess

	def get_ic(self, vbe):
		icnew = self.Is*math.exp(vbe/self.vT)
		return icnew

	def get_vbe(self):
		return self.vbe