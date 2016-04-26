#!/usr/bin/python
import xml.sax
import glob
from xml.etree import ElementTree
import os


debug = 0
currentPath = os.path.dirname(os.path.abspath(__file__))

def printl(string):
    if debug:
        print "[xml_parser:Debug] "+ str(string)

def main ():
    p = getProviders()
    print p[2].getIncomingServers()

def getProviderFromFilenames():
    provs = []
    printl("Current Path "+currentPath)
    provs = os.listdir(currentPath+"/xml")
    printl (provs)

    return provs



class ProviderXMLHandler:

    fullFilePath = None
    domain = None
    dom = None
    services = []

    def __init__(self, xmlfile):
        self.fullFilePath = os.path.join(currentPath ,os.path.join('xml',xmlfile))
        printl ("Getting "+self.fullFilePath)
        self.dom = ElementTree.parse(self.fullFilePath)
        self.domain = xmlfile
        if self.dom != None:
            printl("File geladen: "+str(self.dom))

        self.getDisplayName()
        self.getIncomingServers()
        #self.getDomains()

    def getDomain(self):
        return self.domain

    def getIncomingServers(self):
        server = []
        incomingServers = self.dom.findall('emailProvider/incomingServer')
        printl ("incoming servers "+ str(len(incomingServers)))
        for s in incomingServers:
            type = s.attrib['type']

            if type not in self.services:
                self.services.append(type)

            printl("Hostname: "+str(s.find('hostname').text))
            printl("Hostname: "+str(s.find('port').text))

            service = []
            service.append(type)
            service.append(s.find('hostname').text)
            service.append(int(s.find('port').text))

            if service not in server:
                server.append(service)

        printl("getIncomingServers: "+str(server))
        return server


    def canProviderIMAP(self):
        if "imap" in self.services:
            return True
        return False

    def canProviderPOP3(self):
        if "pop3" in self.services:
            return True
        return False

    def getDisplayName(self):
        displayName = self.dom.findall('emailProvider/displayName')
        if len(displayName) > 0:
            displayName = displayName[0].text
            printl ("Display name: " + displayName)
            return displayName.encode('utf8')
        else:
            printl ("Display name: none")
        return "None";

    def getDomains(self):
        domains = self.dom.findall('emailProvider/domain')

        printl("\nGetting Domains")
        for d in domains:
            printl(d.text)

        return domains

def getProviders():
    providers = []
    names = getProviderFromFilenames()
    printl("files found: "+str(len(names)))
    for p in names:
        printl ("Provider: "+str(p))
        providers.append(ProviderXMLHandler(p))

    return providers

#main()


