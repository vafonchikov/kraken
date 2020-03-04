import os
import getpass
from docker import APIClient
from os.path import isdir
from .check import Check
from .process import img_build, ImageBuildArgs
from .colorize import colorize

def img_build_docker(data, part, filename, base_dir, context, local, no_cache, docker_socket, build_args):
    """
    """
    docker_dir = f"{base_dir}/docker"

    if not isdir(docker_dir):
        print(f"{docker_dir} is not defined")
        exit(1)

    builder = APIClient(base_url=docker_socket)

    docker_registry_url = os.getenv("DOCKER_REGISTRY")
    docker_registry_user_name = os.getenv("DOCKER_REGISTRY_USER_NAME")
    docker_registry_user_password = os.getenv("DOCKER_REGISTRY_USER_PASSWORD")
    docker_registry_user_email = os.getenv("DOCKER_REGISTRY_USER_EMAIL")

    if not local:
        if not docker_registry_url:
            colorize("'DOCKER_REGISTRY' is not defined", "yellow")
            docker_registry_url = input("Docker registry url: ")

        if not docker_registry_user_name:
            colorize("'DOCKER_REGISTRY_USER_NAME' is not defined", "yellow")
            docker_registry_user_name = input("User name: ")

        if not docker_registry_user_email:
            colorize("'DOCKER_REGISTRY_USER_EMAIL' is not defined", "yellow")
            docker_registry_user_email = input("User email: ")

        if not docker_registry_user_password:
            colorize("'DOCKER_REGISTRY_USER_PASSWORD' is not defined'", "yellow")
            docker_registry_user_password = getpass.getpass(prompt='Password: ')

        c = Check(docker_registry_url,
                  docker_registry_user_name,
                  docker_registry_user_email,
                  docker_registry_user_password)
        c.registry_available(builder)

    img_build(ImageBuildArgs(data,
              part,
              filename,
              context,
              local,
              docker_dir,
              builder,
              docker_registry_url,
              docker_registry_user_name,
              docker_registry_user_email,
              docker_registry_user_password,
              no_cache,
              build_args))
