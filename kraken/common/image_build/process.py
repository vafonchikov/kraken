from os.path import basename
from os.path import isfile
import sys
from .colorize import colorize
from collections import namedtuple

ImageBuildArgs = namedtuple("ImageBuildArgs", "data, part, filename, context, local, "
                            "docker_dir, builder, url, user, email, password, no_cache, build_args")

def img_build(args: ImageBuildArgs):
    discribes_containers = []

    for key,value in args.data['kind'].items():
        if key in ('Deployment', 'CronJob', 'Job'):

            for container in value['containers']:
                discribes_containers.append(container['name'])
                if not args.part or container['name'] in args.part:

                    img = container['docker_img']
                    tag = container['build_tag']
                    dockerfile = f"{args.docker_dir}/Dockerfile-{basename(container['docker_img'])}"

                    if not isfile(dockerfile):
                        colorize(f"Dockerfile {dockerfile} not found", "yellow")
                        colorize(f"Trying pull {img}:{tag} from docker hub", "yellow")
                        try:
                            args.builder.pull(img, tag=tag, stream=True, decode = True)
                        except:
                            colorize(f"Docker image {img}:{tag} not found on docker hub", "red")
                            exit(1)
                        colorize(f"Pull {img}:{tag} from docker hub successfully\n", "green")
                        continue


                    if args.url and args.url not in img and not args.local:
                        colorize(f"Image {img} not for registry {args.url}.\n"\
                                 f"You can't push this image in this registry\n"\
                                 f"Fix image name or build with flag '--local'", "red")
                        exit(1)

                    info = f"Building docker image from {dockerfile}.\n"\
                           f"Image tag: {img}:{tag}"

                    colorize(info, "green")

                    for response in args.builder.build(path=args.context, tag=f"{img}:{tag}", dockerfile=dockerfile, decode=True, nocache=args.no_cache, buildargs=args.build_args):

                        if "stream" in response:
                            sys.stdout.write(response['stream'])
                        elif 'error' in response:
                            info = f"{response['error']}\n"\
                                   f"IMAGE {img}:{tag} BUILD FAILED"
                            colorize(info, "red")
                            exit(1)

                    if not args.local:
                        login = args.builder.login(args.user,
                                              args.password,
                                              args.email,
                                              args.url)
                        if "Status" in login:
                            colorize(f"{login['Status']} for registry {args.url}", "green")

                        status = []

                        colorize(f"Pushing image {img}:{tag} to registry {args.url}", "yellow")
                        for response in args.builder.push(img, tag, stream=True, decode=True):
                            if 'status' in response and 'id' in response:
                                info = f"{response['id']}: {response['status']}"
                                if info not in status:
                                    status.append(info)
                                    print(info)
                            elif 'errorDetail' in response:
                                info = f"{response['error']}"
                                colorize(info, "red")
                                exit(1)
                        colorize(f"Successfully pushed image {img}:{tag}", "green")

    check_container_exist = list(set(args.part) - set(discribes_containers))

    if check_container_exist:
        warning = f"The following containers not found in config '{args.filename}':"
        colorize(warning, "red")
        for i in check_container_exist:
            colorize(i, "red")
