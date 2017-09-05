# module imports
import sys
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException


def runRemoteCommand(ip, username, password, command):
	###########################################################################
	# function to pass a command to a Cisco IOS device and return the result  #
	#																		  #
	# input parameters:														  #
	#	ip: 		the ip address of the device to target					  #
	#	username:	the username used for authentication to the device		  #
	# 	password:	the password used for authentication to the device		  #
	#				(N.B. this assumes a privilege 15 account, no provision	  #
	#				is made for running the 'enable' command)				  #
	#	command:	the Cisco IOS command to pass to the device				  #
	###########################################################################
	
	# define the ssh connection properties
	try:
		sshConnection = ConnectHandler(
			device_type='cisco_ios', 
			ip=ip, 
			username=username, 
			password=password
		) 
	except (EOFError, SSHException, NetMikoTimeoutException):
		sys.exit("Error connecting to device: " + ip)

	# establish a connection to the device
	sshConnection.enable()
			
	# send command passed as argument to the device
	commandOutput = sshConnection.send_command(command)
	
	# close SSH connection
	sshConnection.disconnect()
	
	return commandOutput
	
	
	
def runRemoteCommandTimed(ip, username, password, command):
	###########################################################################
	# function to pass a command to a Cisco IOS device and return the result  #
	# uses the 'timing' version of the send command, and includes a delay     #
	# factor in order to help a lengthy output complete before returning      #
	# output.																  #
	#																		  #
	# input parameters:														  #
	#	ip: 		the ip address of the device to target					  #
	#	username:	the username used for authentication to the device		  #
	# 	password:	the password used for authentication to the device		  #
	#				(N.B. this assumes a privilege 15 account, no provision	  #
	#				is made for running the 'enable' command)				  #
	#	command:	the Cisco IOS command to pass to the device				  #
	###########################################################################
	
	# define the ssh connection properties
	try:
		sshConnection = ConnectHandler(
			device_type='cisco_ios', 
			ip=ip, 
			username=username, 
			password=password,
			global_delay_factor=5
		) 
	except (EOFError, SSHException, NetMikoTimeoutException):
		sys.exit("Error connecting to device: " + ip)

		
	# send command passed as argument to the device
	output = sshConnection.send_command_timing(command)
	
	# close SSH connection
	sshConnection.disconnect()
	
	return output