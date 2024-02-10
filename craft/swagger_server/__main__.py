#!/usr/bin/env python3

import os
import socket
import warnings
import connexion
import threading
from python_on_whales import docker
from . import *
from swagger_server import encoder
warnings.filterwarnings("ignore", category=DeprecationWarning)

def run_service(port_number, directory):
    try:
        docker.pull("python:3.11.7-bookworm")
        docker.run("python:3.11.7-bookworm", ["mkdir", "-p", "/usr/src/app"])
        result = docker.run(
            "python:3.11.7-bookworm",
            [
                "sh",
                "-c",
                "python3 -m http.server {0}".format(port_number),
            ],
            volumes=[(os.path.abspath(directory), "/usr/src/app")],
            workdir="/usr/src/app",
            expose=[f"{port_number}"],
            publish=[(f"{port_number}",f"{port_number}")]
        )
    except Exception as e:
        print(f"An error occurred: {e}")

def free_up_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((server, port))
    except OSError as e:
        if e.errno == 98:  # Error code 98: Address already in use
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((server, port))
    finally:
        s.close()

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Python Paved Road REST APIs'}, pythonic_params=True)
    app.run(port=swagger_port)

if __name__ == '__main__':
    load_containers = os.getenv('LOAD_CONTAINERS')
    if load_containers == "True":
        running_containers = [container.id for container in docker.ps(all=True)]
        for container_id in running_containers:
            print(f"Stopping container:{container_id}")
            docker.stop(container_id)

        free_up_port(template_folder_port)
        template_thread = threading.Thread(target=run_service, args=(template_folder_port, template_folder), daemon=True)
        template_thread.start()
        print(f"Templates are being displayed on port {template_folder_port} from directory {template_folder}")
        
        free_up_port(library_folder_port)
        library_thread = threading.Thread(target=run_service, args=(library_folder_port, library_folder), daemon=True)
        library_thread.start()
        print(f"Libraries are being displayed on port {library_folder_port} from directory {library_folder}")

        free_up_port(service_folder_port)
        service_thread = threading.Thread(target=run_service, args=(service_folder_port, service_folder), daemon=True)
        service_thread.start()
        print(f"Services are being displayed on port {service_folder_port} from directory {service_folder}")
    
    main()
