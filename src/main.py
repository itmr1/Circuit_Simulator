from datetime import datetime
import numpy as np
import math
import objects as obj
import parse
import matriceshandler as matrices
import userinput
import results

def AC_analysis (input_file_name, input_source, output_node, save_plot): #Can be called from any external file (for automation)
		if input_file_name == None: input_file_name = userinput.input_file()
		points_per_dec, start_freq, stop_freq = parse.parse_netlist(input_file_name)
		parse.short()
		rows = len(obj.Nset) - 1
		if input_source == None:
			input_source = userinput.input_source()
		else:
			for i, v in enumerate(obj.V):
				if v.get_num() == input_source:
					input_source = v #Dynamically changing data type
		if output_node == None: output_node = userinput.output_node()
		if save_plot == None:
			save_plot = userinput.save_graph()
			if save_plot: show_plot = userinput.show_graph()
		else:
			show_plot = False
		start_time = datetime.now()
		frequencies, gains, phases = results.process_results(points_per_dec, start_freq, stop_freq, rows, input_source, output_node)
		elapsed = str(datetime.now() - start_time)
		print("Done in:", elapsed.split(':')[-1][:-3], "seconds.")
		results.csv_writer(frequencies, gains, phases, input_file_name)
		if save_plot: results.plot_graph(frequencies, gains, phases, input_file_name, show_plot, input_source, output_node)
		obj.reset()
		matrices.reset()

def matrixtester (file = "Netlists/diodecurrent.txt", frequency = 1000 / (2*np.pi), input_v = 1, output_node = 2):
		print(file)
		start_time = datetime.now()
		points_per_dec, start_freq, stop_freq = parse.parse_netlist(file)
		
		parse.shortDC()
		matrices.short_inductor()
		
		rows = len(obj.Nset2) -1
		
		print_components = False
		if print_components:
			for o in obj.N:
				if o != None:
					print("Node ", o.get_num())
					for branch in o.branches:
						try:
							print("Comp: ", type(branch), "node1 ", branch.get_node1().get_num(),"node2 ",branch.get_node2().get_num())
						except:
							print("Comp: ", type(branch))

		G_matrix,I_matrix,V_matrix = results.iterate_diode(rows)

		print("G_matrix =")
		print(G_matrix)
		print("I_matrix =")	
		print(I_matrix)
		print("V_matrix =")
		print(V_matrix)
		elapsed = str(datetime.now() - start_time)
		print("Done in:", elapsed.split(':')[-1][:-3], "seconds.")		
	
'''
		new_f = results.AC_after_DC(file)
		print("NOW DOING AC ANALYSIS")
		AC_analysis(new_f,None, None,None)
'''


if __name__ == "__main__": #Will run only when this file is run directly
	if matrices.matrix_test == False:
		AC_analysis(None, None, None, None)
	else:
		matrixtester() #Use kwargs in the parentheses to overwrite default arguments

	
