# module imports
import sys
from netmiko import ConnectHandler
from runRemoteCommand import runRemoteCommand
from runRemoteCommand import runRemoteCommandTimed


# ensure that the correct amounts of arguments are passed when the script is called
if len(sys.argv) != 10:
    sys.exit("Usage: ./routerUpdate.py <username> <password> <image> <size> <md5> <ftpuser> <ftppassword> <ftpserver> <textfile>")

	
# pass script arguments into an array to be referenced later
cliArguments = sys.argv


# variable assignments from arguments passed at the CLI
username = cliArguments[1]
password = cliArguments[2]
imageName = cliArguments[3]
imageSize = cliArguments[4]
imageSize = int(imageSize)
imageMD5 = cliArguments[5]
ftpUsername = cliArguments[6]
ftpPassword = cliArguments[7]
ftpServer = cliArguments[8]
textFile = cliArguments[9]



def executeFTPCommand(ip, username, password, command, image):
	###########################################################################
	# function to pass a command to a Cisco IOS device and return the result  #
	# used exclusively with the FTP command as this requires confirmation of  #
	# the command entered.													  #
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
			global_delay_factor=1
		) 
	except (EOFError, SSHException, NetMikoTimeoutException):
		sys.exit("SSH is not enabled for this device.")

		
	# send command passed as argument to the device
	output = sshConnection.send_command_timing(command)
	if image in output:
		output += sshConnection.send_command_timing(image)
	
	# close SSH connection
	sshConnection.disconnect()
	
	
	

	

# create the FTP command based on the arguments passed at the CLI
ftpCommand = "copy ftp://" + ftpUsername + ":" + ftpPassword + "@" + ftpServer + "/" + imageName + " flash:/" + imageName
	

# open the file for reading
try:
	ipAddressesFile = open(textFile)
except OpenErrors:
	print ("Error opening file containing IP addresses over which to iterate")


# iterate through file of IP addresses
for line in ipAddressesFile:
	
	# if the line begins with a '#' then it is a comment, and we don't want to process it, otherwise go ahead
	if not line.startswith("#"):
		
		# remove the carriage return from the line by splitting it and just taking the first array element. 
		# this gives us the IP address of the router
		ipAddress = line.splitlines()
		ipAddress = ipAddress[0]
		
		# call fuction 'runRemoteCommand' in order to get the router hostname
		routerHostname = runRemoteCommand(ipAddress, username, password,"show run | i hostname")
		# edit the return string to include only interesting data
		# hostname string returns in the format:
		# hostname <hostname>
		# split string into an array on a whitespace delimeter and use the second argument in the array
		routerHostname = routerHostname.split(' ')
		routerHostname = routerHostname[1]
				
		# check that there is enought free space on the target router to take the new image
		# runRemoteCommand returns a string in the form: 
		#
		# <x> bytes available (<x> bytes used)
		freeSpace = runRemoteCommand(ipAddress, username, password, "sh flash: | i available")

		# we require just the free space value as an integer, so split the string on a space and then take
		# the first element of the array which will be the value in string form.  This is then converted to 
		# an integer so that value comparisons can be made.
		freeSpace = freeSpace.split(' ')
		freeSpace = freeSpace[0]
		try:
			freeSpace = int(freeSpace)
		except ValueError:
			print ("Error coverting free space value to integer for router" + routerHostname)
			break

		# build the command required to identify if the IOS image is already present on the router, taking the
		# image name that was passed as an argument when the script was invoked.  This string is then passed
		# to the router and executed.
		imageCommand = "sh flash | i " + imageName
		imagePresent = runRemoteCommand(ipAddress, username, password, imageCommand)
		
		# check that the image isn't already present in the router flash
		if imagePresent == "":
			# check to see if there is enough free space on the router flash to load the new image
			if freeSpace > imageSize:
				# if both conditions are passed (the image isn't present, and the flash has enough free space)
				# then run the command that instructs the router to grab the image from the FTP server
				print ("Image not present. Transferring image to router: " + routerHostname)
				executeFTPCommand(ipAddress, username, password, ftpCommand, imageName)
			else:
				print ("Image not present, but there is not enough free space on flash on: " + routerHostname)
		else:
			print ("Image already present on: " + routerHostname)
				
		
		# before the image is deemed to be successfully transferred to flash and ready to execute, we need to 
		# ensure that it passes the validation checks.  The verify command is run against the router in order
		# to grab the MD5 hash of the compiled image.  This can then be compared against the expected MD5 hash
		# value to determine validity of the image.
		# The string returned is needs to be split on a space in order to grab the 8th element in the array.  
		# This element is the MD5 hash that results from the verify command.  Some work is done to the string
		# in order to strip the carriage returns at the end of the string.  This means a direct string comparison
		# can be made with the MD5 hash value passed at the command line.
		print ("Beginning image MD5 hash verification")
		verifyImage = runRemoteCommandTimed(ipAddress, username, password, "verify /md5 flash:" + imageName)
		verifyImage = verifyImage.split(' ')
		verifyImage = verifyImage[7]
		verifyImage = verifyImage.replace('\n','').replace('\r','')
		
		
		if imageMD5 == verifyImage:
			# the MD5 hashes match, image is good to go
			print ("Successful MD5 verify completed on router: " + routerHostname)
		else:
			# the MD5 hashes don't match, there is an issue with the image
			print ("MD5 verify failed. Please investigate image on router: " + routerHostname)