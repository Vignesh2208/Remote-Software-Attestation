import random
import string

lower_limit = 0
upper_limit = 10000
variable_init_values = []


default_orig_code = """
import re	
import os	
import binascii	
import random	
import time	

maps_file = open("/proc/self/maps", 'r')	
mem_file = open("/proc/self/mem", 'r', 0)	
import sys	
no_of_bytes_to_read = 100	
no_of_random_selections = 20	

	
for line in maps_file.readlines():  # for each mapped region	
	m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
	#print 'Orig line', line
	#print m.group(1),m.group(2),m.group(3)
	if m.group(3) == 'r':  # if this is a readable region
		if 'r-x' in line or 'rwx' in line or '--x' in line or '-wx' in line :
			print line
			start = int(m.group(1), 16)
			end = int(m.group(2), 16)
			mem_file.seek(start)  # seek to region start
			chunk = mem_file.read(start + no_of_bytes_to_read - start)  # read region contents
			chunk = binascii.hexlify(chunk)
			print '' + chunk  # dump contents to standard output
			break
random_selection_list = random.sample(range(0,no_of_bytes_to_read-1),no_of_random_selections)	

pid = os.getpid()	
print 'Process ID : ', pid	

write_string = ""	
write_string = write_string + "" + str(pid)	
write_string = write_string + " " + str(len(random_selection_list))	
for entry in random_selection_list :	
	write_string += " " + str(entry)
write_string += " "
print "Writing the string to proc file. String : ",write_string		

with open("/proc/Attest",'w') as f :	
	f.write(write_string)

print "Finished writing to proc file"	
f.close()	
maps_file.close()	
mem_file.close()	

print "Just hovering around now for 5 seconds"	

time.sleep(5) # delays for 10 seconds	
"""
def generate_random_function(lower_limit,upper_limit,max_no_of_lines) :
	x_init = random.uniform(lower_limit,upper_limit)
	y_init = random.uniform(lower_limit,upper_limit)
	function_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
	function_name = 'func' + function_name
	operator = ['+','-','*']
	number_of_lines = random.uniform(1,max_no_of_lines)
	line_count = 1
	function_code = """
def """ + function_name + "() :" + """ 
	x = """ + str(x_init) +	"""
	y = """ + str(y_init)

	function_body_code = ""
	while line_count <= number_of_lines :
		selected_operator = random.choice(operator)
		choice = random.uniform(0,10)
		if choice <= 5 :
			code_addition = """
	x = x""" + selected_operator + "y"
		else :
			code_addition = """
	y = x""" + selected_operator + "y"
		function_body_code += code_addition
		line_count += 1
	code_addition = """
	#print x,y
	"""
	function_body_code += code_addition
	function_code += function_body_code
	code_addition = """
""" + function_name + "()"
	function_code += code_addition
	return function_code	

	
def generate_random_code_snippet(lower_limit,upper_limit,max_no_of_lines) :

	x_init = random.uniform(lower_limit,upper_limit)
	y_init = random.uniform(lower_limit,upper_limit)
	
	operator = ['+','-','*']
	number_of_lines = random.uniform(1,max_no_of_lines)
	line_count = 1
	snippet_code = """
x = """ + str(x_init) +	"""
y = """ + str(y_init)

	snippet_body_code = ""
	while line_count <= number_of_lines :
		selected_operator = random.choice(operator)
		choice = random.uniform(0,10)
		if choice <= 5 :
			code_addition = """
x = x""" + selected_operator + "y"
		else :
			code_addition = """
y = x""" + selected_operator + "y"
		snippet_body_code += code_addition
		line_count += 1
	code_addition = """
#print x,y
"""
	snippet_body_code += code_addition
	snippet_code += snippet_body_code
	return snippet_code	

def insert_dead_code(lower_limit,upper_limit,max_no_of_lines,orig_code,break_points) :
	transformed_code = ""
	code_snippet_list = orig_code.split('\n')
	current_block = 0
	current_code_statement_index = 0
	while current_code_statement_index < len(code_snippet_list) :
		if current_block <= len(break_points) - 1 and current_code_statement_index == break_points[current_block][0] :
			while current_code_statement_index <= break_points[current_block][1] :
				transformed_code += code_snippet_list[current_code_statement_index] + '\n'
				current_code_statement_index += 1
			current_block += 1
		else :
			choice = random.uniform(0,10) 
			if choice <= 2 : # insert dead code
				if choice <= 1 :				
					code_to_add = generate_random_function(lower_limit,upper_limit,max_no_of_lines) + '\n'
				else :
					code_to_add = generate_random_code_snippet(lower_limit,upper_limit,max_no_of_lines) + '\n'
				transformed_code += code_to_add
			transformed_code += code_snippet_list[current_code_statement_index] + '\n'
			current_code_statement_index += 1

	return transformed_code
	





