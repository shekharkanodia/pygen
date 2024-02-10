import os
import socket
import connexion
import traceback
import threading
from jinja2 import Template
from flask import jsonify
from python_on_whales import docker
from . import *

def post_service():
    if connexion.request.is_json:
        try:
            payload_data = connexion.request.get_json()
            service_name = payload_data["service_name"]
            service_port = payload_data["service_port"]
            template_name = payload_data["template_name"]
            requirements = payload_data["requirements"].split(",") if "requirements" in payload_data else ""
            template_parameters = payload_data["template_parameters"]

            template_path = os.path.join(template_folder,f'{template_name}')
            with open(template_path, 'r') as template_file:
                template_content = template_file.read()
                template = Template(template_content)

            rendered_content = template.render(**template_parameters)
            
            service_base_folder = os.path.join(service_folder,f"{service_name}")
            os.makedirs(service_base_folder, exist_ok=True)

            service_file = os.path.join(service_base_folder, f'{service_name}.py')
            with open(service_file, 'w') as output_file:
                output_file.write("from flask import Flask, request")
                output_file.write("\n\n")
                output_file.write("app = Flask(__name__)")
                output_file.write("\n\n")
                output_file.write(rendered_content)
                output_file.write("\n\n")
                output_file.write("""if __name__ == '__main__':""")
                output_file.write("\n")
                output_file.write(f"""    app.run(host='0.0.0.0',port={service_port})""")
            
            requirements_file = os.path.join(service_base_folder, 'requirements.txt')
            with open(requirements_file, 'w') as output_file:
                for each_requirement in requirements:
                    each_requirement = each_requirement.strip()
                    output_file.write(each_requirement)
                    output_file.write("\n")

            def free_up_port(port):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    s.bind((server, port))
                except OSError as e:
                    if e.errno == 98:  # Error code 98: Address already in use
                        print(f"Port {port} is in use. Trying to release it.")
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.bind((server, port))
                        print(f"Port {port} released.")
                    else:
                        print(f"Error: {e}")
                finally:
                    s.close()    
            free_up_port(int(service_port))

            def run_service():
                try:
                    docker.run(
                        "python:3.11.7-bookworm",
                        [
                            "sh",
                            "-c",
                            "pip install Flask && pip install -r requirements.txt && python3.11 {0}.py".format(service_name),
                        ],
                        volumes=[(os.path.abspath(service_base_folder), "/usr/src/app")],
                        workdir="/usr/src/app",
                        expose=[f"{service_port}"],
                        publish=[(f"{service_port}",f"{service_port}")]
                    )
                except Exception as e:
                    print(f"An error occurred: {e}")

            service_thread = threading.Thread(target=run_service, args=(), daemon=True)
            service_thread.start()
            return jsonify(message=f"Service creation request placed. Service will be available at http://{server}:{service_port}"), 200
        except Exception as e:
            traceback.print_exc()
            return "Failed to accept service request. Error:{}".format(str(e)), 500
    else:
        return "Service request does not have json body.", 500
