import subprocess
from bootstrap.container_config import *


def install_docker():
    """
    Build the portainer container
    :return:
    """
    print('Installing docker')

    install_docker_command = subprocess.Popen(['sh', './build/install_docker_linux.sh'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
    stdout, stderr = install_docker_command.communicate()

    print(f'Docker install stage output: {stdout}, {stderr}')


def build_portainer():
    """
    Build the portainer container
    :return:
    """
    print('Building portainer')

    build_portainer_command = subprocess.Popen(['sh', './build/portainer_build_linux.sh'],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
    stdout, stderr = build_portainer_command.communicate()

    print(f'Portainer build stage output: {stdout}, {stderr}')


def update_portainer():
    """
    Update the portainer container
    :return:
    """
    print('Updating portainer')

    update_portainer_command = subprocess.Popen(['sh', './build/portainer_update_linux.sh'],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
    stdout, stderr = update_portainer_command.communicate()

    print(f'Portainer update stage output: {stdout}, {stderr}')


def run_portainer():
    """
    Run the portainer container
    :return:
    """
    print('Running portainer')

    run_portainer_command = subprocess.Popen(['sh', './build/portainer_run_linux.sh'],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
    stdout, stderr = run_portainer_command.communicate()

    print(f'Portainer run stage output {stdout}, {stderr}')


def build_chatbot():
    """
    Build the chatbot container
    :return:
    """
    print('Building chatbot')

    build_chatbot_command = subprocess.Popen(['sh', './build/build_chatbot_linux.sh', chatbot_name, chatbot_password],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
    stdout, stderr = build_chatbot_command.communicate()

    print(f'Chatbot build stage output {stdout}, {stderr}')


def run_chatbot():
    """
    Build the chatbot container
    :return:
    """
    print('Running chatbot')

    run_chatbot_command = subprocess.Popen(['sh', './build/run_chatbot_linux.sh', chatbot_name],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
    stdout, stderr = run_chatbot_command.communicate()

    print(f'Chatbot run stage output {stdout}, {stderr}')