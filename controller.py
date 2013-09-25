import cherrypy
from lxml import etree
from lxml.builder import E

class Root(object):

    def __init__(self):
        self._xmlsource = etree.parse(open('testdata.xml', 'rb'))
        self._xmlroot = self._xmlsource.getroot()
        self._transform = etree.XSLT(etree.parse(open('testview.xsl', 'rb')))
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

cherrypy.quickstart(Root())
