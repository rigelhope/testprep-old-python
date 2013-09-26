#!/usr/bin/python2.7

import cherrypy
from lxml import etree
from lxml.builder import E
import os.path
import argparse

class Root(object):

    def __init__(self, 
                    xmlfile='testdata.xml',
                    xslfile='testview.xsl' ):
        self._xmlsource = etree.parse(open(xmlfile, 'rb'))
        self._xmlroot = self._xmlsource.getroot()
        self._transform = etree.XSLT(etree.parse(open(xslfile, 'rb')))
        self.html = self._transform(self._xmlsource)
        

    @cherrypy.expose
    def index(self):
        return str(self.html)

    @cherrypy.expose
    def send(self, **params):
        print params
        h = E.history(str(params))
        self._xmlroot.append(h)
        self._out = open('testhistory.xml', 'wb')
        self._out.write(etree.tostring(self._xmlroot))
        self._out.close()               

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))

    p = argparse.ArgumentParser(description='Start a webserver (CherryPy) to present an XML question bank as a webpage')
    p.add_argument('testXML', nargs='?', default='testdata.xml', help='XML test file')
    p.add_argument('testXSLT', nargs='?', default='testview.xsl', help='XSLT presentation file')
    p.add_argument('--public', default='127.0.0.1', action='store_const', const='0.0.0.0', help='make publicly accessible on this IP')
    args = p.parse_args()

    conf = {'/static': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': os.path.join(current_dir, 'static')
                        }}

#uncomment to serve publicly
    cherrypy.config.update(
        {'server.socket_host': args.public })

    cherrypy.quickstart(Root(args.testXML, args.testXSLT), '', config=conf)
