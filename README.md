# Router Configuration Update

## Description 
Using Netmiko, SSH to a list of routers taken from a given text file and load an image onto the router via FTP, checking first for the requisite amount of free space, and the the image doesn't already exist in the router flash.  								

Python 2.7


## Prerequisites

Netmiko, Paramiko


## Usage

./routerUpdate.py <username> <password> <image> <size>  <ftpuser> <ftppasswprd> <ftpserver> <textfile>	
where:
- <username> the username used for authentication to the devices
- <password> the password used for authentication to the devices
- <image> 	 the name of the IOS image to load onto the router (N.B. this image must exist of the FTP server)
- <size> 	 the size of the IOS image in bytes
- <md5> 	 the MD5 hash of the image
- <ftpuser>  the username used for authentication to the FTP server
- <ftppassword>  the password used for authentication to the FTP server
- <ftpuser>  the IP address of the FTP server
- <textfile> a list of router IP addresses to connect to.  Any lines that start with a '#' are igorned as comments.


## Author

Andrew Burridge
