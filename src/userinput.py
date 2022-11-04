import objects as obj
import os

def input_file ():
	entry = input("Enter input file name: ").strip()
	if entry[-4:] != ".txt":
		entry = entry + ".txt"
	filename = "Netlists/" + entry
	if os.path.isfile(filename):
		print("input file:", filename[3:])
	else:
		print ("File does not exist!")
		return input_file()
	return filename

def input_source ():
	entry = input("Enter input source: ").strip()
	if (entry[0].lower() == 'v'):
		entry = entry[1:]
	try: 
		v_num = int(entry)
		for i, v in enumerate(obj.V):
			if v.get_num() == v_num:
				return v
	except: pass
	print("Invalid, try again.")
	return input_source()

def output_node ():
	entry = input("Enter output node: ").strip()
	if (entry[0].lower() == 'n'):
		entry = entry[1:]
	try: 
		node_num = int(entry)
		short_node_num = obj.Nset.index(obj.Ndupes[node_num])
		return short_node_num
	except:
		print("Invalid, try again.")
		return output_node()

def save_graph ():
	entry = input("Create graph? [y/n] (Enter to skip): ").strip()
	if entry.lower() == "y":
		return True
	else:
		return False

def show_graph ():
	entry = input("Show graph? [y/n] (Enter to skip): ").strip()
	if entry.lower() == "y":
		return True
	else:
		return False
