import sys
import click
import subprocess


def apply(yaml_desc: str, dry_run: bool = False, **kwargs):
    """ Call kubectl apply

    :param yaml_desc:
    :param dry_run:
    :param kwargs:
    :return:
    """
    args = ['kubectl', 'apply', '-f', '-']
    server_dry_run = kwargs.get('server_dry_run', False)
    fallback_to_dry_run = kwargs.get('fallback_to_dry_run', False)

    if server_dry_run:
        args.append('--server-dry-run')
    elif dry_run:
        args.append('--dry-run')

    proc = subprocess.Popen(' '.join(args), shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc.stdin.write(yaml_desc.encode('utf-8'))
    proc.stdin.close()

    while True:
        nextline = proc.stdout.readline().decode('utf-8')
        if nextline == '' and proc.poll() is not None:
            break

        if 'namespaces' in nextline and 'not found' in nextline and server_dry_run:
            if fallback_to_dry_run:
                click.secho('Namespace does not exist. Falling back to client-side dry-run', fg='yellow')
                return apply(yaml_desc, dry_run=True)
            else:
                proc.kill()
                proc.wait()
                sys.stdout.write(nextline)
                return False

        sys.stdout.write(nextline)
        sys.stdout.flush()

    return proc.wait() == 0

