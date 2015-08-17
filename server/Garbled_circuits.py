import math
import random
import string
import os
import sys

class circuit :
	def __init__(self,no_of_input_bits,no_of_output_bits) :
		self.no_of_input_bits = no_of_input_bits
		self.no_of_output_bits = no_of_output_bits
		self.table_of_output_wire = {}
		self.output_wire = {}
		
	def set_output_wire_assignments(self,output_wire) :
		
		self.output_wire  =  output_wire
	def set_table_of_output_wire(self,table_of_output_wire) :
		self.table_of_output_wire = table_of_output_wire
	def evaluate_circuit(self,input_array) :
		intermediate_XOR = 0
		output_bit_array = []
		for entry in input_array :
			intermediate_XOR = intermediate_XOR ^ entry
		output_wire_no = 0
		while output_wire_no < self.no_of_output_bits :
			counter = 0
			while counter < pow(2,self.no_of_input_bits)  :
				#print intermediate_XOR ^ self.table_of_output_wire[output_wire_no][counter],self.output_wire[output_wire_no][0],self.output_wire[output_wire_no][1] 
				if intermediate_XOR ^ self.table_of_output_wire[output_wire_no][counter] == self.output_wire[output_wire_no][0] :
					output_bit_array.append(0)
				elif intermediate_XOR ^ self.table_of_output_wire[output_wire_no][counter] == self.output_wire[output_wire_no][1] :
					output_bit_array.append(1)
				#else :
				#	print "something wrong happened. exiting "
				#	return []	
				counter += 1
			output_wire_no += 1

	
		return output_bit_array
	
class garbled_circuit :
	def __init__(self,no_of_input_bits,no_of_output_bits) :
		self.no_of_input_bits = no_of_input_bits
		self.no_of_output_bits = no_of_output_bits
		self.input_wire = {}
		self.output_wire = {}
		self.table_of_output_wire = {}
		self.mapping_of_output_wire = {}
		
		counter = 0
		while counter < self.no_of_input_bits :
			if counter not in self.input_wire.keys() :
				self.input_wire[counter] = [0, 1]
			counter += 1
		counter = 0
		while counter < self.no_of_input_bits :
			if counter not in self.output_wire.keys() :
				self.output_wire[counter] = [0, 1]
				self.table_of_output_wire[counter] = [0]*(pow(2,self.no_of_input_bits))
				self.mapping_of_output_wire[counter] = []
			counter += 1
	def set_input_wire_assignments(self,input_wire_assignments) :
		if len(input_wire_assignments) != self.no_of_input_bits :
			print "Mismatch in lengths. Exiting "
			return
		else :	
			counter = 0
			while counter < self.no_of_input_bits :
				self.input_wire[counter] = input_wire_assignments[counter]
				counter += 1

			return
	def set_output_wire_assignments(self,output_wire_assignments) :
		if len(output_wire_assignments) != self.no_of_output_bits :
			print "Mismatch in lengths. Exiting "
			return
		else :	
			counter = 0
			while counter < self.no_of_output_bits :
				self.output_wire[counter] = output_wire_assignments[counter]
				counter += 1
			return
	def set_output_wire_mapping(self,wire_no,wire_mapping) :
		max_valid_mapping = pow(2,self.no_of_input_bits) - 1
		counter = 0
		if len(wire_mapping) == 0 :
			print "Length of mapping is zero. Not allowed. Exiting "
			return
		while counter < len(wire_mapping) :
			if wire_mapping[counter] > max_valid_mapping :
				print "Invalid mapping argument. Rolling back and Exiting "
				self.mapping_of_output_wire[wire_no] = []
				return
			self.mapping_of_output_wire[wire_no].append(wire_mapping[counter])
			counter += 1
	def construct_output_wire_table(self,wire_no) :
		if len(self.mapping_of_output_wire[wire_no]) == 0 :
			print "No mapping has been done to this wire. Exiting "
			return
		else :
			counter = 0
			while counter < pow(2,self.no_of_input_bits)  :
				table_entry = 0
				if counter in self.mapping_of_output_wire[wire_no] :
					table_entry = table_entry ^ self.output_wire[wire_no][1]				
					binary_conversion = bin(counter)
					
					 
					binary_conversion = binary_conversion[2:]
					
					while len(binary_conversion) < self.no_of_input_bits :
						binary_conversion  = '0' + binary_conversion
					
			
					
					bit_array = []
					internal_counter = 0
					while internal_counter < len(binary_conversion) :
						bit_array.append(int(binary_conversion[internal_counter]))
						current_bit = bit_array[internal_counter]
						table_entry = table_entry ^ self.input_wire[internal_counter][current_bit]
						internal_counter += 1

				else :
					table_entry = table_entry ^ self.output_wire[wire_no][0]
					binary_conversion = bin(counter)
					
					 
					binary_conversion = binary_conversion[2:]
					
					
					#binary_conversion = binary_conversion.strip('0b')
					while len(binary_conversion) < self.no_of_input_bits :
						binary_conversion  = '0' + binary_conversion
					
					bit_array = []
					internal_counter = 0
					while internal_counter < len(binary_conversion) :
						bit_array.append(int(binary_conversion[internal_counter]))
						current_bit = bit_array[internal_counter]
						table_entry = table_entry ^ self.input_wire[internal_counter][current_bit]
						internal_counter += 1
				self.table_of_output_wire[wire_no][counter] = table_entry
				counter += 1
		return

	def evaluate_circuit(self,input_array) :
		intermediate_XOR = 0
		output_bit_array = []
		counter = 0
		for entry in input_array :
			if entry not in self.input_wire[counter] :
				print "Input is in wrong format. exiting "
				return []
			counter += 1
			intermediate_XOR = intermediate_XOR ^ entry
		output_wire_no = 0
		while output_wire_no < self.no_of_output_bits :
			counter = 0
			while counter < pow(2,self.no_of_input_bits)  :
				#print intermediate_XOR ^ self.table_of_output_wire[output_wire_no][counter],self.output_wire[output_wire_no][0],self.output_wire[output_wire_no][1] 
				if intermediate_XOR ^ self.table_of_output_wire[output_wire_no][counter] == self.output_wire[output_wire_no][0] :
					output_bit_array.append(0)
				elif intermediate_XOR ^ self.table_of_output_wire[output_wire_no][counter] == self.output_wire[output_wire_no][1] :
					output_bit_array.append(1)
				else :
					print "Something wrong with input. exiting "
					return []	
				counter += 1
			output_wire_no += 1

	
		return output_bit_array

	def load_circuit(self,input_wire_assignments,output_wire_assignments,output_wire_mapping_list) :
		self.set_input_wire_assignments(input_wire_assignments)
		self.set_output_wire_assignments(output_wire_assignments)
		wire_no = 0
		while wire_no < self.no_of_output_bits :
			self.set_output_wire_mapping(wire_no,output_wire_mapping_list[wire_no])
			self.construct_output_wire_table(wire_no)
			wire_no += 1
		
		

		
	
def obtain_circuit(no_of_input_bits,no_of_output_bits,input_wire_assignments,output_wire_assignments,output_wire_mapping_list) :
	obj = garbled_circuit(no_of_input_bits,no_of_output_bits)
	export_circuit = circuit(obj.no_of_input_bits,obj.no_of_output_bits)
	obj.load_circuit(input_wire_assignments,output_wire_assignments,output_wire_mapping_list)

	export_circuit.set_output_wire_assignments(obj.output_wire)
	export_circuit.set_table_of_output_wire(obj.table_of_output_wire)
	return export_circuit


