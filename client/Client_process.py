import socket
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
import subprocess
import select
import time
import os

key = open("Public_key.pem", "r").read()
rsapubkey = RSA.importKey(key)
key = open("Private_key.pem", "r").read()
rsaprivatekey = RSA.importKey(key)

server_IP_address_dict = {}
server_IP_address_dict[1] = 'localhost'
server_IP_address_dict[2] = '130.126.245.43'


# Possible message types : 01 - > Attestation routine, 02 -> Input argument, 03 -> others
def get_file_content(file_path,line_number = -1) :
	if line_number == -1 :
		with open(file_path,'r') as f :
			content = f.read()
		f.close()
		return content
	else :
		f=open(file_path)
		lines=f.readlines()
		content = lines[line_number]
		f.close()
		return content

def send_message(message,sock,message_type) :
	# Send data
	len_of_message = 0
	len_of_message = str(len(message))
	
	while len(len_of_message) < 32 :
		len_of_message = '0' + len_of_message

	h = SHA256.new()
	h.update(message)
	message_digest = str(h.hexdigest())

	output = rsaprivatekey.sign(message_digest,0)
	message_digest_signature = str(output[0])
	message_digest_signature_len = str(len(message_digest_signature))

	while len(message_digest_signature_len) < 32 :
		message_digest_signature_len = '0' + message_digest_signature_len

	message_len = str(len(message) + len(message_digest_signature) + 64 + len(message_type))

	while len(message_len) < 32 :
		message_len = '0' + message_len


	transmit_message = len_of_message + message_digest_signature_len + message_type + message + message_digest_signature


	#print >>sys.stderr, 'sending "%s"' % transmit_message
	sock.sendall(message_len)
	sock.sendall(transmit_message)



	# Look for the response

	if message_type == '01' :
		response_messages = ["ACK_SUCCESS","ACK_FAILURE"]
		amount_received = 0
		amount_expected = len("ACK_SUCCESS")
		sock.setblocking(0)
   		data = ""
		received_message = ""
		time_out_in_seconds = 15
		#print "Client : Waiting for an ACK from the remote meter"
		ready = select.select([sock], [], [], time_out_in_seconds)
		start_time = time.time()
		if ready[0]:
			data = sock.recv(4096)		
		end_time  = time.time()

		if end_time - start_time >= time_out_in_seconds :
			print "Timed out expired. Remote system is not reachable Attestation failed"
			received_message = "ACK_FAILURE"
			return received_message

		
		received_message += str(data)
		
		print >>sys.stderr, 'Client : Received response to Attestation Request is "%s"' % received_message
		return received_message	

	elif message_type == '02':
	
		sock.setblocking(0)	
   		data = ""
		received_message = ""
		time_out_in_seconds = 15
		print "Client : Waiting for an ACK with computed hash"
		ready = select.select([sock], [], [], time_out_in_seconds)
		start_time = time.time()
		if ready[0]:
			data = sock.recv(4096)		
		end_time  = time.time()

		if end_time - start_time >= time_out_in_seconds :
			print "Client : Timed out. Attestation failed"
			received_message = "ACK_FAILURE"
			return received_message

		
		received_message += str(data)
		
		# Received message is of the form : ACK_SUCCESS::Hash  or ACK_FAILURE::0
		ACK_Components = received_message.split('::')
		if ACK_Components[0] == "ACK_FAILURE" :
			print "Client : Did not time out but received an ACK_FAILURE. Attestation failed"
			return ACK_Components[0]

		elif ACK_Components[0] == "ACK_SUCCESS" :
			print "Client : Received an ACK_SUCCESS with the computed hash"
			Computed_Hash = ACK_Components[1]
			return Computed_Hash

		
arg_list = sys.argv
if len(arg_list) < 2:
	print "Not enough arguments. Must provide Destination Nodeid as argument"
	exit()
else :
	server_IP_address = arg_list[1]



#if NodeID not in server_IP_address_dict.keys() :
#	print "Dont have a record of the destination. Exiting "
#	exit()
#server_IP_address = server_IP_address_dict[NodeID]

h = SHA256.new()
h.update(server_IP_address)
NodeID = str(h.hexdigest())[1:10]

port = 29015


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

# Connect the socket to the port where the server is listening
server_address = (server_IP_address, port)


try:
    

	subprocess.call([sys.executable, 'Garbled_circuits_loader.py', str(NodeID)]) # launch the garbled_circuits_loader
	attestation_routine = get_file_content('test.py',-1) # The attestation routine to be transmitted
	input_argument_string = get_file_content('Circuit_parameters'+str(NodeID) + '.txt',10) # the command line argument needed for the attestation routine
	os.remove('Circuit_parameters'+str(NodeID) + '.txt')
	os.remove('test.py')
	input_argument_string = input_argument_string.replace('[',"")
	input_argument_string = input_argument_string.replace(']',"")
	input_argument_string = input_argument_string.replace(',',"")
	input_argument_string = input_argument_string.replace('\n',"")
	
	print "Input argument (For Key generation to run Encrypted Payload) ="
	print  input_argument_string
	print ""
	print ""
	
	#------------------------------ SEND ATTESTATION ROUTINE TO REMOTE SYSTEM -------------------------------------------------------------------#
	
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)
	print "Client : Sending Attestation Routine to remote workstation"
	print "Client : Waiting for an ACK to Attestation Request from the remote workstation"
	received_response = send_message(attestation_routine,sock,message_type = '01')
	sock.close()

	if received_response == "ACK_SUCCESS" :
		#print >>sys.stderr, 'connecting to %s port %s' % server_address
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
		sock.connect(server_address)
		
		received_response = send_message(input_argument_string,sock,message_type = '02')
		sock.close()

		if received_response == "ACK_FAILURE" :
			print "Client : Attestation Failed"
			exit()
		else :
	
			if received_response != "" :
				received_hash = ':'.join(x.encode('hex') for x in received_response)
				print "Client : Received Hash : "
				print received_hash
			else :
				print "Client : Received Hash is None. Something is wrong"
		
	else :
		print "Attestation routine send failed, exiting "
		exit()
		
	#----------------------------------------- LOCAL COMPUTATION OF THE HASH FOR VERIFICATION --------------------------------------------------#
	

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
	server_address = ('localhost',port)

	sock.connect(server_address)
	print ""
	print ""
	print "Client : Sending Attestation Routine to localhost"
	print "Client : Waiting for an ACK to Attestation Request from localhost"
	received_response = send_message(attestation_routine,sock,message_type = '01')
	sock.close()

	if received_response == "ACK_SUCCESS" :
		#print >>sys.stderr, 'connecting to %s port %s' % server_address
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
		sock.connect(server_address)
		
		received_response = send_message(input_argument_string,sock,message_type = '02')
		sock.close()

		if received_response == "ACK_FAILURE" :
			print "Client : could not contact local host Attestation Failed"
			exit()
		else :
			if received_response != "" :
				locally_computed_hash = ':'.join(x.encode('hex') for x in received_response)
				print "Client : Locally computed Hash : "
				print locally_computed_hash
			else :
				locally_computed_hash = ""
				print "Client : Locally computed Hash is None. Something is wrong"
		
	else :
		print "Attestation routine send to local host failed, exiting "
		exit()
finally:
	print ""
	print >>sys.stderr, 'Finishing up'

	

if received_hash == locally_computed_hash :
	print ""
	print "Remote Attestation succeeded. Both hash values are equal"
	print ""
elif received_hash == None :
	print ""
	print "Attestation Failed. Did not get back any hash from the remote workstation"
else :
	print ""
	print "Attestation Failed. Received Hash is incorrect "



