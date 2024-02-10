import os

base_path = "/Users/shekharkanodia/Desktop/pramp/intuit_craft/swagger_server"

template_folder = os.path.join(base_path,"templates")
library_folder = os.path.join(base_path,"dist")
service_folder = os.path.join(base_path,"services")

template_folder_port = 7225
library_folder_port = 7226
service_folder_port = 7227

server = '127.0.0.1'
swagger_port = 8080