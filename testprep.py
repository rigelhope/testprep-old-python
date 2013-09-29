#!/usr/bin/python2.7

import cherrypy
from lxml import etree
from lxml.builder import E
import os.path
import argparse

class qbank(object):
    
    def __init__(self, xmlfile, xslfile): 
        self._xml = self._load(xmlfile)
        self._xslt = self._load(xslfile)

    def _load(self, f):
        source = etree.parse(open(f, 'rb'))
        root = source.getroot()
        return root

    def transform(self):
        transform = etree.XSLT(self._xslt)
        return transform(self._xml)

    def store(self, params):
        h = E.history(str(params))
        self._xml.append(h)
        self._out = open('testhistory.xml', 'wb')
        self._out.write(etree.tostring(self._xml))
        self._out.close()               

    def subset(self, selector='question/subject/text()'):
        #TODO: implement subset selection using XPATH selectors
        pass

class Root(object):
    def __init__(self, xmlfile='testdata.xml', xslfile='testview.xsl'):
        self.bank = qbank(xmlfile, xslfile)

    @cherrypy.expose
    def index(self):
        return str(self.bank.transform())

    @cherrypy.expose
    def send(self, **params):
        print params
        self.bank.store(params)
        

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

    cherrypy.config.update(
        {'server.socket_host': args.public })

    cherrypy.quickstart(Root(args.testXML, args.testXSLT), '', config=conf)
