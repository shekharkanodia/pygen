import os
import connexion
import shutil
import traceback
from flask import jsonify
from jinja2 import Template
from python_on_whales import docker
from . import *

def post_library():
    if connexion.request.is_json:
        try:
            payload_data = connexion.request.get_json()
            library_name = payload_data["library_name"]
            library_install_requires = payload_data["library_install_requires"].split(",") if "library_install_requires" in payload_data else []
            library_version = payload_data["library_version"]
            library_description = payload_data["library_description"]
            library_author = payload_data["library_author"]
            template_name = payload_data["template_name"]
            template_parameters = payload_data["template_parameters"]

            new_library_root_folder = os.path.join(library_folder, f'{library_name}_root')
            os.makedirs(new_library_root_folder, exist_ok=True)

            new_library_folder = os.path.join(new_library_root_folder, f'{library_name}')
            os.makedirs(new_library_folder, exist_ok=True)

            init_file = '__init__.py'
            init_file_path = os.path.join(new_library_folder, init_file)
            
            with open(init_file_path, 'w') as file:
                pass

            setup_template = os.path.join(library_folder,'setup.j2')
            with open(setup_template, 'r') as setup_template_file:
                template_content = setup_template_file.read()
                template = Template(template_content)

            rendered_content = template.render(
                project_name=library_name,
                package_name=library_name,
                install_requires = library_install_requires,
                version=library_version,
                description=library_description,
                author=library_author
            )

            library_setup_file = os.path.join(new_library_root_folder,'setup.py')
            with open(library_setup_file, 'w') as setup_file:
                setup_file.write(rendered_content)

            template_path = os.path.join(template_folder,f'{template_name}')
            with open(template_path, 'r') as template_file:
                template_content = template_file.read()
                template = Template(template_content)

            rendered_content = template.render(**template_parameters)

            library_functions_file = f'{library_name}.py'
            library_functions_file_path = os.path.join(new_library_folder, library_functions_file)
            with open(library_functions_file_path, 'w') as output_file:
                output_file.write(rendered_content)

            result = docker.run(
                "python:3.11.7-bookworm",
                [
                            "sh",
                            "-c",
                            "python3.11 setup.py sdist bdist_wheel",     
                ],
                volumes=[(os.path.abspath(new_library_root_folder), "/usr/src/app")],
                workdir="/usr/src/app",
            )
            print(result)
            source_folder = os.path.join(new_library_root_folder, "dist")
            destination_folder = os.path.join(base_path, "dist")
            try:
                files_to_move = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
                for file_name in files_to_move:
                    source_path = os.path.join(source_folder, file_name)
                    destination_path = os.path.join(destination_folder, file_name)
                    shutil.move(source_path, destination_path)
                print(f"All files moved successfully from {source_folder} to {destination_folder}")
            except Exception as e:
                print(f"An error occurred: {e}")
            return jsonify(message=f"Library created successfully, it is available at http://{server}:{library_port}"), 200
        except Exception as e:
            traceback.print_exc()
            return "Failed to accept library request. Error:{}".format(str(e)), 500
    else:
        return "Library request does not have json body.", 500
