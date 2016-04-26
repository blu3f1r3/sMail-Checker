class Provider:


    def setService(self, service):
        self.services.append(service)

    def __init__(self, displayName, domain):
        self.displayName = displayName
        self.domain = domain
        self.services = []

    def getServices(self):
        return self.services

    def getDomain(self):
        return self.domain



class Service:
    type = None
    host = None
    port = None

    def __init__(self, type, host, port):
        self.type = type
        self.host = host
        self.port = port

    def getType(self):
        return self.type
    def getHost(self):
        return self.host
    def getPort(self):
        return self.port
