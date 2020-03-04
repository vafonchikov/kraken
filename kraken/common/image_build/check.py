from .colorize import colorize

class Check:

        def __init__(self, host, user, email, password):
                self.host = host
                self.user = user
                self.email = email
                self.password = password
                self.port = 443

        def registry_available(self, docker):
            try:
                docker.login(self.user,
                             self.password,
                             self.email,
                             self.host)
                return True
            except Exception as error:
                colorize(str(error), "red")
                exit(1)
