import numpy as np
import math
import csv
import matriceshandler as matrices
import matplotlib
import objects as obj
from matplotlib import pyplot as plt

def process_results(points_per_dec, start_freq, stop_freq, rows, input_source, output_node):
	Vs = []
	frequencies = []
	G_matrix = matrices.conductance_matrix(rows, 1) #Needs to be done to obtain sources for I matrix
	I_matrix = matrices.current_matrix(rows) #I matrix only made once as it doesn't use omega
	step = 1
	frequency_step = start_freq
	while frequency_step < stop_freq:  #Frequency step simulation
		frequencies.append(frequency_step)
		omega = frequency_step * 2 * np.pi
		G_matrix = matrices.conductance_matrix(rows, omega)
		V_matrix = matrices.inv_multiply(G_matrix, I_matrix)
		Vs.append(V_matrix[output_node - 1])
		frequency_step = 10**(step / points_per_dec) * start_freq
		step += 1
	gains = []
	phases = []
	for v in range(len(Vs)):  #Calculating gains and phases
		output_mag = float(np.absolute(Vs[v]))
		try:
			gain = 20*math.log10(output_mag/input_source.get_amplitude())
		except:
			gain = -9999999		#-infinity in case 0 voltage
		gains.append(gain)
		output_phase = float((np.angle(Vs[v], deg=True)))
		phases.append(output_phase - input_source.get_phase())
	return frequencies, gains, phases

def iterate_diode(rows):
	convergence = False
	while not convergence:
		obj.operating_points[0].clear()
		obj.operating_points[1].clear()
		G_Dmatrix = matrices.diode_matrix(rows)
		I_Dmatrix = matrices.diode_current_matrix(rows)
		V_Dmatrix = matrices.inv_multiply(G_Dmatrix, I_Dmatrix)
		count = 0
		for d in obj.D:
			if d.get_node1().get_num() == 0:
				Node1 = 0
			else:
				Node1 = (V_Dmatrix[d.get_node1().get_num()-1]).real
			if d.get_node2().get_num() == 0:
				Node2 = 0
			else:
				Node2 = (V_Dmatrix[d.get_node2().get_num()-1]).real
			oppoint = Node1 - Node2
			if not math.isclose(oppoint, d.guess, rel_tol = 1e-5, abs_tol = 0.0005):
				count += 1
				print("New Oppoint for Diode",d.get_num(), oppoint)
				d.set_oppoint(oppoint)
				d.resistor_eq.resistance = d.get_resistor_eq()
				d.current_eq.current = d.get_current_eq()
			else:
				obj.operating_points[0].append(d.get_num())
				obj.operating_points[1].append(d.resistor_eq.resistance)
		if count == 0:
			convergence = True
	return G_Dmatrix, I_Dmatrix, V_Dmatrix

def AC_after_DC(input_file):
	num_resistors = len(obj.R)
	lines_to_add = []
	file = open(input_file,"r")
	input_netlist = file.readlines()
	for i,d in enumerate(obj.D):
		num_resistors+= 1
		diode_number = d.get_num()
		index = obj.operating_points[0].index(diode_number)
		node1 = d.get_node1().get_num()
		node2 = d.get_node2().get_num()
		line = "R" +str(num_resistors) + " " + "N00" +str(node1) + " " + "N00" +str(node2) + " " + str(obj.operating_points[1][index]) + "\n"
		print("LINE ADDED: ", line)
		lines_to_add.append(line)		
	for i,net_line in enumerate(input_netlist):
		if net_line[0] != "D":
			lines_to_add.append(net_line)
	new_file = open("Netlists/NEW.txt","w")
	new_file.writelines(lines_to_add)
	new_file.close()
	new_file = open("Netlists/NEW.txt","r")
	lines = new_file.readlines()				
	obj.reset()
	matrices.sources[0].clear()
	matrices.sources[1].clear()
	return "Netlists/NEW.txt"

def iterate_bjt2(rows): # DC LSM
	convergence = False
	while not convergence:
		G_Dmatrix = matrices.diode_matrix(rows)
		I_Dmatrix = matrices.diode_current_matrix(rows)
		V_Dmatrix = matrices.inv_multiply(G_Dmatrix, I_Dmatrix)
		count = 0
		for b in obj.BJT:
			if b.diode_eq.get_node1().get_num() == 0:
				Node1 = 0
			else:
				Node1 = (V_Dmatrix[b.diode_eq.get_node1().get_num()-1]).real
			if b.diode_eq.get_node2().get_num() == 0:
				Node2 = 0
			else:
				Node2 = (V_Dmatrix[b.diode_eq.get_node2().get_num()-1]).real
			oppoint = Node1 - Node2
			icnew = b.get_ic(oppoint)
			if not (math.isclose(oppoint, b.diode_eq.guess, rel_tol = 1e-5,abs_tol = 0) or math.isclose(icnew, b.Ic,rel_tol = 1e-5, abs_tol = 5e-5)):
				count += 1
				b.diode_eq.set_oppoint(oppoint)
				b.set_ic(icnew)
				b.set_vbe(oppoint)
				print("NEW Ic:", b.Ic)
				print("NEW Vbe:", b.diode_eq.guess)
				b.diode_eq.resistor_eq.resistance = b.diode_eq.get_resistor_eq()
				b.diode_eq.current_eq.current = b.diode_eq.get_current_eq()
				b.current_eq.set_current(b.get_gm() * b.vbe)
		if count == 0:
			convergence = True
	return G_Dmatrix, I_Dmatrix, V_Dmatrix

def iterate_bjt(rows): # AC SSM
	convergence = False
	iteration = 0
	while not convergence and (iteration != 2):
		G_Dmatrix = matrices.diode_matrix(rows)
		I_Dmatrix = matrices.diode_current_matrix(rows)
		V_Dmatrix = matrices.inv_multiply(G_Dmatrix, I_Dmatrix)
		iteration+=1
		count = 0
		for b in obj.BJT:
		
			if b.get_type() == "NPN":
				
				if b.rbe_eq.get_node1().get_num() == 0:
					BaseNode = 0
				else:
					BaseNode = (V_Dmatrix[b.rbe_eq.get_node1().get_num()-1]).real
				if b.rbe_eq.get_node2().get_num() == 0:
					EmitterNode = 0
				else:
					EmitterNode = (V_Dmatrix[b.rbe_eq.get_node2().get_num()-1]).real
				vbenew = BaseNode - EmitterNode
				print("BASE node" , BaseNode)
				print("EMitter Node" , EmitterNode)

				if b.ro_eq.get_node1().get_num() == 0:
					CollectorNode = 0
				else:
					CollectorNode = (V_Dmatrix[b.ro_eq.get_node1().get_num()-1]).real
				vce = CollectorNode - EmitterNode
				icnew = b.get_ic(b.ro_eq.get_impedance(1),vce, b.current_eq.get_current())
				if not (math.isclose(vbenew, b.vbe, rel_tol = 1e-5) and math.isclose(icnew, b.Ic, rel_tol = 1e-5)):
					count+=1
					b.set_ic(icnew)
					b.set_vbe(vbenew)
					b.ro_eq.resistance = b.get_ro()
					b.rbe_eq.resistance = b.get_rbe()
					b.current_eq.set_current(b.get_gm() * b.vbe)
					print("VBE ", vbenew )
					print("IC " , icnew)
			
			elif b.get_type() == "PNP":

				if b.rbe_eq.get_node2().get_num() == 0:
					BaseNode = 0
				else:
					BaseNode = (V_Dmatrix[b.rbe_eq.get_node2().get_num()-1]).real
				if b.rbe_eq.get_node1().get_num() == 0:
					EmitterNode = 0
				else:
					EmitterNode = (V_Dmatrix[b.rbe_eq.get_node1().get_num()-1]).real
				vbenew = BaseNode - EmitterNode
				

				if b.ro_eq.get_node2().get_num() == 0:
					CollectorNode = 0
				else:
					CollectorNode = (V_Dmatrix[b.ro_eq.get_node2().get_num()-1]).real
				vce = CollectorNode - EmitterNode
				icnew = b.get_ic(b.ro_eq.get_impedance(1),vce, b.current_eq.get_current())
				if not (math.isclose(vbenew, b.vbe, rel_tol = 1e-5) and math.isclose(icnew, b.Ic, rel_tol = 1e-5)):
					count+=1
					b.set_ic(icnew)
					b.set_vbe(vbenew)
					b.ro_eq.resistance = b.get_ro()
					b.rbe_eq.resistance = b.get_rbe()
					b.current_eq.set_current(b.get_gm() * b.vbe)
		if count == 0:
			convergence = True
	return G_Dmatrix, I_Dmatrix, V_Dmatrix

def csv_writer (frequencies, gains, phases, input_file_name):
	output_name = input_file_name[:-4].split('/')[-1] + '.csv'
	output_file = open(str("Results/" + output_name) , "w+")
	writer = csv.writer(output_file, delimiter = ",")
	for i, freq in enumerate(frequencies):
		writer.writerow([freq, gains[i], phases[i]])
	output_file.close()
	print("Saved " + "Results/" + output_name)

def plot_graph (frequencies, gains, phases, input_file_name, show_plot, input_source, output_node):
	matplotlib.interactive(False) #True makes graph close on creation
	fig, (ax1, ax2) = plt.subplots(2, 1)
	output_name = input_file_name[:-4].split('/')[-1]
	title = "Transfer Function for " + output_name + f" V(n00{output_node})/V{input_source.get_num()}"
	fig.suptitle(title)
	ax1.set_xscale("log")
	ax1.set_xlabel("Frequency (Hz)")
	ax1.plot(frequencies, gains, color="blue")
	ax1.set_ylabel("Magnitude (dB)")
	ax2.plot(frequencies, phases, color="red")
	ax2.set_xscale("log")
	ax2.set_xlabel("Frequency (Hz)")
	ax2.set_ylabel("Phase (°)")
	plt.savefig("../Results/" + output_name + '.png')
	print("Saved " + "Results/" + output_name + '.png')
	if show_plot: plt.show()