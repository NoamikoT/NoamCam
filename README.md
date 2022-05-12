# NoamCam - Security System
A project using popular modules such as CV, WXPython, and more.

The main purpose of the project is a system in which an individual/company/group of people can monitor multiple places at once, a lot like the popular systems you would see in Movies and TV Shows, and it is used in real life as well.

Some more features of the project includes: Face detecting (turning it on and off), Secure log in (Using a username and password), sounding an alert when a face was detected (when Face detection feature is active on it) or manually, recording the live feeds, zooming on a certain live feed, Getting a mail when a face is found and more.

# Installation
Download ffmpeg from here: And place it under the Serverfiles folder with the name ffmpeg. 

Install the requirements file.

Set the server's IP address in the Setting.py file, and add the clients MAC addresses to the database (myDB.db).

# Known Bugs:
When both clients and a server are connected, and the servers goes down and comes back up, the clients will not be able to connect to the server.

Camera sometimes can't be accessed, and needs to be physically disconnected and connected to the computer.