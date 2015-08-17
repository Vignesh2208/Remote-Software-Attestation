This file contains instructions on how to build and run the Attestation System.

System Requirements:
--------------------
* Preferred OS : Linux

* Kernel version between 2.6 to 3.0 
  It was not tested on any other kernel version

* python2.6 or later versions must be installed (However, it was tested only with python2.6 and python2.7)

* pyCrypto library must be installed

Installation Requirements:
---------------------------
* The linux kernel source must be installed
 

Description of Folders:
-----------------------

There are two main folders client/  and server/

client/ folder contains all the necessary files to run a verifier process on a system. The client folder and all of its contents should be copied to the system running the verifier. The verifier should also have the contents of the server folder to run a localhost server.

server/ folder contains all the necessary files to load the attestation kernel module and the Application process on a remote test workstation. The server folder and all of its contents should be copied to the test system.

rootkit/ folder contains the kernel module that performs the system call hook on write(). The rootkit works only in Linux kernel 2.x. The rootkit successfully bypasses the remote attestation by emulating Python 2.7 while actually running Python 2.6

Setting up the test system/Application:
--------------------------------------

The test system should have python installed. The purpose of this attestation system is to check whether the test system runs the same python version as the verifier/client. 

The server folder and all of its contents should be copied to the test system. The steps that have to be followed are listed in order. The server has to be started before the client.

-> Building the kernel module:
-----------------------------

1. cd /server/Attestation_kernel_module
2. sudo make

It was compiled and tested on kernel verions from 2.6 to 3.0. It is not guaranteed to compile on other kernel versions.

-> Installing the kernel module:
--------------------------------

sudo insmod Attestation_module.ko

-> Removing the kernel module:
------------------------------

sudo rmmod Attestation_module

-> Starting the Application:
----------------------------

The application can be started by specifying the IP address of the system on which the Application is running

sudo python Application_process.py <Specify IP address of the system here>
eg:
sudo python Application_process.py 172.16.25.124

If the Application has to run as a localhost server, do: 
sudo python Application_process.py localhost


Setting up the client/Verifier:
-------------------------------

Before starting the verifier, a localhost Application server has to be started on the client system as well. The client sends the same attestation routine to the remote application server as well as the localhost application server and compares the resulting two hashes. To start the localhost application server perform all the steps listed in the previous section.

Start the localhost Application server: sudo python Application_process.py localhost

-> Start the client process:
----------------------------

The Client process can be started by specifying the destination system's IP Address as a commandline argument.

sudo python Client_process.py <IP address of the remote application server>

eg:
sudo python Client_process.py 172.16.22.90


Interpreting results:
--------------------

The client process will construct an attestation routine and send it to the remote application server first. It would get a hash value from the remote server first. Then it would send the same attestation routine to the localhost application server and obtain a locally computed hash. Both hash values would be equal if both systems are running the same python. Otherwise Attestation would fail.

Viewing kernel logs:
--------------------

The kernel module would dump some messages about the details of the code section into the kernel logs. It can be viewed by:

sudo tail -f /var/log/kern.log

Killing the server or Application:
---------------------------------

1. Cntrl + Z
2. sudo fuser -k 29015/tcp

-> Building the rootkit module:
-----------------------------
This must be done on the remote machine

1. cd /rootkit
2. make

It was compiled and tested on kernel verions from 2.6 to 3.0. It is not guaranteed to compile on other kernel versions.

-> Installing the kernel module:
--------------------------------

sudo insmod my_module.ko

-> Removing the kernel module:
------------------------------

sudo rmmod my_module






