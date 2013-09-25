#!/usr/bin/python2.7

import cherrypy
from lxml import etree
from lxml.builder import E
import os.path

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

    conf = {'/static': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': os.path.join(current_dir, 'static')
                        }}

    cherrypy.quickstart(Root(), '', config=conf)
