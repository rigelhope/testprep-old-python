#!/usr/bin/python2.7

import cherrypy
from lxml import etree
from lxml.builder import E
import os.path
import argparse
import random
import json

class qbank(object):

    max_qs = 200
    
    def __init__(self, xmlfile, xslfile): 
        self._xml = self._load(xmlfile)
        # store the original qbank here

        self._xslt = self._load(xslfile)
        # the xsl for the presentation layer

        self._qids = self._get_list()
        #the initial list of question ids from the qbank

        self._test = self.make_test()
        #init by random generation of a 50q test.
        #this is what will be presented, if nothing else is changed

        self._subject_index = self.counts(self.subset())
        #creates a dict with subject strings as keys and list of question ids as value

    def make_test(self):
        '''
        generate a random test from the _qids list
        _qids list is alterable to select questions fitting specific criteria, esp subject
        this method may be called again to generate a new test
        returns an etree Element, with a root of "qbank" and questions as sub-elements
        '''
#        q = []
#        if len(self._qids) > self.max_qs:
#            q = E.qbank()
#            for i in self.get_qs_from_ids(self.select_qids()):
#                q.append(i)
#        else:
#            q = self._xml
        q = E.qbank()
        for i in self.get_qs_from_ids(self.select_qids()):
            q.append(i)
        return q

    def _load(self, f):
        source = etree.parse(open(f, 'rb'))
        root = source.getroot()
        return root

    def _flatten(self, l):
        '''flattens a list of lists l'''
        return [i for sublist in l for i in sublist]

    def transform(self):
        '''
        does the final xslt transformation to presentation format.
        '''
        transform = etree.XSLT(self._xslt)
        return transform(self._test)

    def store(self, params):
        '''
        writes accumulated selection/review data in raw JSON format. needs work.
        '''
        h = E.history(self._clean_JSON(params))
        self._xml.append(h)
        self._out = open('testhistory.xml', 'wb')
        self._out.write(etree.tostring(self._xml))
        self._out.close()               

    def subset(self, value='subject/text()', key='@id', root='//question', source=None):
        '''
        returns a dict using xpath selectors.
        default values for key and value are id and selector , respectively
        '''
        subset = {}
        if source == None:
            source = self._xml
        try:
            for i in self._xml.xpath(root):
                subset[i.xpath(key)[0]] = i.xpath(value)[0]
        except IndexError:
            subset = self._xml.xpath(root)
        return subset

    def _get_list(self, contents='@id', root='//question', source=None):
        l=[]
        if source == None:
            source = self._xml
        for i in source.xpath(root):
            l.append(i.xpath(contents))
        l = self._flatten(l)
        return l

    def select_qids(self, qty=None, qlist=None):
        '''
        returns a random subset of list elements, presumably question ids
        '''
        l = []
        if qty == None:
            qty = self.max_qs
            if qty > len(self._qids):
                qty = len(self._qids)
        if qlist == None:
            qlist = self._qids
        random.shuffle(qlist)
        for i in range(qty):
            l.append(qlist[i])
        return l            

    def get_qs_from_ids(self, qlist=None, selector='@id', root='//question', source=None):
        '''
        returns list of questions as etree Elements based on the list of id's given
        '''
        l = []
        if qlist == None:
            qlist = self._qids
        if source == None:
            source = self._xml
        for i in qlist:
            l.append(source.xpath(root+'['+selector+'='+str(i)+']'))
        l = self._flatten(l)
        return l

    def counts(self, c):
        '''
        c is the dict to be counted
        inverts a dict, value is a list of keys that had that value
        used for finding subsets for e.g. subject selection
        '''
        counts = {}
        valueset = set(c.values())
        for i in valueset:
            counts[i] = [id for id, subject in c.items() if subject == i]
        return counts

    def get_subject_counts(self):
        subj_counts = {}
        subj = self.counts(self.subset())
        for i in subj.keys():
            subj_counts[i] = len(subj[i])
        return subj_counts

    def subject_HTML(self, counts):
        '''
        convenience function for rendering index page with checkbox selectors for each subject.
        '''
        HTML = ''
        for i in counts.viewitems():
            HTML += '''<input type="checkbox" name="select" value="%s" />%20s : %10s<br />
            ''' % (i[0], i[0], i[1])
        return HTML

    def select_subjects(self, selections):
        try:
            s = selections['select']
            print s
        except KeyError:
            print "No selections"
            return
        l = []
        if isinstance(s, list):
            for i in s:
                l.append(self._subject_index[i])
        else: 
            l.append(self._subject_index[s])
        l = self._flatten(l)
        print len(l)
        self._qids = l
        print "self._qids is length "+str(len(self._qids))
        self._test = self.make_test()

    def _clean_JSON(self, data):
        #jquery sends the JSON data as a dict.
        #the key is the actual list of events, that's all we want
        #the value is null, so this can be discarded
        #overbuilt, in case there are multiple strings that need concatenation
        j = json.JSONDecoder()
        d = data.keys()
        r = d.pop()
        if d:
        #if there is more than one element, concatenate it
            print "there were additional elements not handled"
        r = j.decode(r)
        return r

class Root(object):
    def __init__(self, xmlfile='testdata.xml', xslfile='testview.xsl'):
        self.bank = qbank(xmlfile, xslfile)


    @cherrypy.expose
    def index(self, *data):
        print data
        return '''
            <html>
            <head>
            <link rel="stylesheet" href="static/jquery-ui.css" />
            <link rel="stylesheet" href="static/testprep.css" />
            </head>
            <body>
            <table width="400" border="1">
            <tr>
            <form action="select_subjects" method="post">
            <td>%s</td>
            <td><input type="submit" value="Save"></td>
            </form>
            </tr>
            </table>
            </body>
            </html>
            ''' % self.bank.subject_HTML(self.bank.get_subject_counts())

    @cherrypy.expose
    def test(self):
        return str(self.bank.transform())

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def select_subjects(self, **selections):
        print selections
        self.bank.select_subjects(selections)
        raise cherrypy.HTTPRedirect("/test")


    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
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
                        'tools.staticdir.dir': os.path.join(current_dir, 'static')},
            '/media': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': os.path.join(current_dir, 'media')}
            }

    cherrypy.config.update(
        {'server.socket_host': args.public })

    cherrypy.quickstart(Root(args.testXML, args.testXSLT), '', config=conf)
