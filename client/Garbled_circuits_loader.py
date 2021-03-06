import math
import random
import string
import os
from Garbled_circuits import * 
from Crypto.Cipher import AES
import binascii
from Dead_code_pool import *
import sys
import random

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

no_of_rounds = 8
arg_list = sys.argv
if len(arg_list) == 1 :
	print "Atleast the Run ID number has to given as an argument. Exiting"
	exit()
elif len(arg_list) == 2 :
	RunID = arg_list[1]
	no_of_input_bits = 2
	no_of_output_bits = 2
	
elif len(arg_list) == 3 :
	RunID = arg_list[1]
	no_of_input_bits = int(arg_list[2])
	no_of_output_bits = no_of_input_bits
	
elif len(arg_list) == 4 :
	RunID = arg_list[1]
	no_of_input_bits = int(arg_list[2])
	no_of_output_bits = int(arg_list[3])
else :
	print "Too many arguments. Error. Exiting "
	exit()

IV = "1234567890123456"


input_wire_assignments = [[100,200],[300,400]]
output_wire_assignments = [[500,600],[700,800]]
output_wire_mapping_list = [[1,2],[0,2]]
input_array = [200,300]


def generate_random_input_array(input_wire_assignments,no_of_rounds) : # number of rounds determines no of bits in the key
	no_of_input_bits = len(input_wire_assignments)
	current_bit = 0
	input_array = []
	current_round = 0
	while current_round < no_of_rounds :
		current_round_list = []
		current_bit = 0
		while current_bit < no_of_input_bits :
			choice = random.uniform(0,10)
			if choice <= 5 :
				current_round_list.append(input_wire_assignments[current_bit][0])
			else :
				current_round_list.append(input_wire_assignments[current_bit][1])
			current_bit += 1
		input_array.append(current_round_list)
		current_round += 1
	return input_array
	
def init_circuit_wire_assignments(no_of_input_bits,no_of_output_bits,no_of_rounds) :
	input_wire_assignments = []
	output_wire_assignments = []
	output_wire_mapping_list = []
	current_bit = 0
	while current_bit < no_of_input_bits :
		current_bit_assignment = random.sample(range(100,999),2)
		input_wire_assignments.append(current_bit_assignment)
		current_bit += 1

	current_bit = 0
	while current_bit < no_of_output_bits :
		no_of_mapping_selections = random.randint(0,pow(2,no_of_input_bits))
		current_bit_assignment = random.sample(range(100,999),2)
		output_wire_assignments.append(current_bit_assignment)
		current_wire_mapping_list = random.sample(range(0,pow(2,no_of_input_bits)),no_of_mapping_selections)
		output_wire_mapping_list.append(current_wire_mapping_list)
		current_bit += 1
	input_array = generate_random_input_array(input_wire_assignments,no_of_rounds)
	return [input_wire_assignments,output_wire_assignments,output_wire_mapping_list,input_array]



output_list = init_circuit_wire_assignments(no_of_input_bits,no_of_output_bits,no_of_rounds)
input_wire_assignments = output_list[0]
output_wire_assignments = output_list[1]
output_wire_mapping_list = output_list[2]
input_array = output_list[3]


max_offset = 100
no_of_random_selections = 20
random_selection_list = random.sample(range(0,max_offset-1),no_of_random_selections)	

# Save this to a file for each run

with open('Circuit_parameters' + RunID + '.txt','w') as f :
	f.write("Input wire assignments:\n")
	f.write(str(input_wire_assignments) + '\n\n')
	f.write("Output wire assignments:\n")
	f.write(str(output_wire_assignments) + '\n\n')
	f.write("Output bit mappings:\n")
	f.write(str(output_wire_mapping_list) + '\n\n') 

	temp_input_array_list = []
	counter = 0
	while counter < len(input_array) :
		j = 0
		while j < no_of_input_bits :
			temp_input_array_list.append(input_array[counter][j])
			j += 1
		counter += 1
	f.write("Seed input for key generation:\n")
	f.write(str(temp_input_array_list) + '\n\n')
	
	f.write("Random byte position list:\n")
	f.write(str(random_selection_list)+'\n\n')

f.close()



export_circuit = obtain_circuit(no_of_input_bits,no_of_output_bits,input_wire_assignments,output_wire_assignments,output_wire_mapping_list)
current_round = 0
key_string = ""

while current_round < no_of_rounds :
	output_array = export_circuit.evaluate_circuit(input_array[current_round])
	#print "Round no : ", current_round + 1, " Output array : ", output_array

	counter = 0
	
	while counter < len(output_array) :
		key_string = key_string + str(output_array[counter])
		counter += 1
	current_round += 1


key  = int(key_string,2)
#print 'Final Key : ', key

while len(key_string) % 16 != 0 :
	key_string = "0" + key_string

key = key_string
#print "Final key as a string : ", key

orig_code = """
import re
import os
import binascii
import random
import time

maps_file = open("/proc/self/maps", 'r')
mem_file = open("/proc/self/mem", 'r', 0)
import sys 
"""
code_addition = """
no_of_bytes_to_read = """

code_addition += str(max_offset)

orig_code += code_addition

code_addition = """

no_of_random_selections = """

code_addition += str(no_of_random_selections)

orig_code += code_addition

code_addition = """

random_selection_list = """

code_addition += str(random_selection_list)

orig_code += code_addition

code_addition = """

	
for line in maps_file.readlines():  # for each mapped region
	m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
	print "Attestation Routine : Code Section and Info about the executable : ", line
	print "Attestation Routine : Printing first 100 bytes of the code section of the executable to be attested"
	print ""
	if m.group(3) == 'r':  # if this is a readable region
		if 'r-x' in line or 'rwx' in line or '--x' in line or '-wx' in line :			
			start = int(m.group(1), 16)
			end = int(m.group(2), 16)
			mem_file.seek(start)  # seek to region start
			chunk = mem_file.read(start + no_of_bytes_to_read - start)  # read region contents
			chunk = binascii.hexlify(chunk)
			print '' + chunk  # dump contents to standard output
			break
#random_selection_list = random.sample(range(0,no_of_bytes_to_read-1),no_of_random_selections)	
pid = sys.argv[1]
print ""
print 'Attestation Routine : Process ID to Attest : ', pid

write_string = ""
write_string = write_string + "" + str(pid)
write_string = write_string + " " + str(len(random_selection_list))
for entry in random_selection_list :
	write_string += " " + str(entry)
write_string += " "
print "Attestation Routine : Writing the Attestation arguments to proc file /proc/Attest : ",write_string		

with open("/proc/Attest",'w') as f :
	f.write(write_string)

#print "Attestation Routine : Finished writing to /proc/Attest file"
f.close()
maps_file.close()
mem_file.close()

print "Attestation Routine : Just hovering around now for 5 seconds and waiting for the kernel module to finish up"

time.sleep(5) # delays for 5 seconds
"""

orig_code += code_addition

transformed_code  = orig_code
#optional random deadcode insertion
lower_limit = 0 
upper_limit = 10000
break_points = [[13,32],[38,48]] # these would change with the orig code
transformed_code = insert_dead_code(lower_limit,upper_limit,10,orig_code,break_points)


#for character in orig_code :
#	new_code = new_code + chr(ord(character) ^ key)

encryptor = AES.new(str(key),AES.MODE_CBC,IV)
transformed_code = pad(transformed_code)
new_code = encryptor.encrypt(transformed_code)
new_code = binascii.hexlify(new_code)

#print 'Encrypted code : '
#print new_code
#print "END OF ENCRYPTED CODE. Length = ",len(new_code)


old_code = ""
#for character in new_code :
#	old_code = old_code + chr(ord(character) ^ key)

encryptor = AES.new(str(key),AES.MODE_CBC,IV)
old_code = encryptor.decrypt(new_code.decode('hex'))
old_code = unpad(old_code)

#print "Transformed code : "
#print  transformed_code
#print "END OF TRANSFORMED CODE"

list1 = ""
list1 += str(input_wire_assignments)

list2 = ""
list2 += str(output_wire_assignments)

list3 = ""
list3 += str(output_wire_mapping_list)

output_wire = str(export_circuit.output_wire)
table_of_output_wire = str(export_circuit.table_of_output_wire)


code = """# -*- coding: utf-8 -*-
import math
import random
import string
from Garbled_circuits import *
import sys
import re
import os
from Crypto.Cipher import AES
import binascii
import subprocess

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

arg_list = (sys.argv) 
"""



code_addition = """

no_of_rounds = """

code += code_addition + str(no_of_rounds)


code_addition = """

no_of_input_bits = """

code += code_addition + str(no_of_input_bits)

code_addition = """

no_of_output_bits = """

code += code_addition + str(no_of_output_bits)

code_addition = """

output_wire = """

code += code_addition + output_wire

code_addition = """

table_of_output_wire = """

code += code_addition + table_of_output_wire

code_addition = """

IV = \""""

code += code_addition + IV 

code_addition = """\"

export_circuit = circuit(no_of_input_bits,no_of_output_bits)
export_circuit.set_output_wire_assignments(output_wire)
export_circuit.set_table_of_output_wire(table_of_output_wire)


input_array = []

start = 1
if len(arg_list) - 1 != no_of_rounds*no_of_input_bits :
	print "Argument length incorrect. Exiting. Current length ",len(arg_list)
	exit()

current_round = 0
while current_round < no_of_rounds :
	current_round_list = []
	start = 0
	while start < no_of_input_bits :
		current_round_list.append(int(arg_list[current_round*no_of_input_bits + start + 1]))	
		start += 1
	input_array.append(current_round_list)
	current_round += 1


current_round = 0
key_string = ""

while current_round < no_of_rounds :
	output_array = export_circuit.evaluate_circuit(input_array[current_round])
	if output_array == [] :
		print "Something wrong with input. Exiting "
		exit()
	#print "Round no : ", current_round + 1, " Output array : ", output_array

	counter = 0
	
	while counter < len(output_array) :
		key_string = key_string + str(output_array[counter])
		counter += 1
	current_round += 1


key  = int(key_string,2)
#print 'Final Key : ', key

while len(key_string) % 16 != 0 :
	key_string = "0" + key_string

key = key_string
#print "Final key as a string : ", key

Encrypted_code = r\"\"\""""


code += code_addition + new_code


code_addition = """\"\"\""""

code += code_addition

code_addition = """
#print 'Encrypted code length ', len(Encrypted_code)
Decrypted_code = ""
#for character in Encrypted_code :
#	Decrypted_code = Decrypted_code + chr(ord(character) ^ key)
Decryptor = AES.new(str(key),AES.MODE_CBC,IV)
Decrypted_code = unpad(Decryptor.decrypt(Encrypted_code.decode('hex')))
#print Decrypted_code



#print "Evaluating code "
code_to_write = Decrypted_code


filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
filename = filename + ".py"

new_fd = open(filename,'w')
new_fd.write(code_to_write)
new_fd.close()

with open(filename,'rb') as f :
	contents = f.read()
f.close()
ppid = os.getppid()
subprocess_call_list = [sys.executable, filename,str(ppid)]
#cc= compile(contents,filename,'exec')
#exec(cc)
subprocess.call(subprocess_call_list)
os.remove(filename)
"""

code += code_addition

filename = "test.py"

with open(filename,'w') as f :
	f.write(code)
f.close()

	

				
