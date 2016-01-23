#!/bin/env python

import os,sys,urllib,urllib2,time,re
from logbook import Logger,FileHandler
import re
from trac.core import *
from trac.ticket.api import ITicketChangeListener
from trac.web import IRequestHandler
from json import dumps, loads


try:
    
    from urllib.parse import urlparse,parse_qs

except ImportError:
    
    from urlparse import urlparse,parse_qs
    
    
class TicketFieldCatcher(Component):

    implements(ITicketChangeListener,IRequestHandler)

    def match_request(self,req):
        pass
        return re.match(r'/get_sku(?:_trac)?(?:/.*)?$',req.path_info)

    def process_request(self,req):
	pass
           
    def ticket_created(self,ticket):
        pass
        ticket_id = ticket.id
        config = self.config
        env = self.env
        sku = None
        brand = None
        sku = ticket.get_value_or_default("sku")
        brand = ticket.get_value_or_default("brand")
        data = (ticket_id,sku,brand)
        #self.log.debug("length#brand: %s, length#sku: %s" % (len(brand),len(sku)))
       # self.log.debug("ticket_created: %s" % ticket.id)

    """
2016-01-23 18:37:30,883 Trac[ticketchangetoinfluxdb] DEBUG: {u'keywords': u'', u'version': u'1.0', u'component': u'component1', u'summary': u'Testing a'}
2016-01-23 18:37:30,883 Trac[ticketchangetoinfluxdb] DEBUG: 
2016-01-23 18:37:30,883 Trac[ticketchangetoinfluxdb] DEBUG: OLD_VALUES: keywords
2016-01-23 18:37:30,883 Trac[ticketchangetoinfluxdb] DEBUG: OLD_VALUES: version
2016-01-23 18:37:30,883 Trac[ticketchangetoinfluxdb] DEBUG: OLD_VALUES: component
2016-01-23 18:37:30,883 Trac[ticketchangetoinfluxdb] DEBUG: OLD_VALUES: summary


Get the keys that changed, then get the new values.
    """
    def ticket_changed(self,ticket,comment,author,old_values):
        ticket_id = ticket.id
        config = self.config
        env = self.env
        #sku = ticket.get_value_or_default("sku")
        #brand = ticket.get_value_or_default("brand")
        row = None
        self.log.debug(old_values)
        self.log.debug(comment)
        for k in old_values:
            v = ticket.get_value_or_default(k)
            self.log.debug("OLD_VALUES: %s, new: %s" % (k,v))
            
              
    def ticket_deleted(self,ticket):
        pass
        ticket_id = ticket.id
        config = self.config
        env = self.env
        
    def ticket_comment_modified(self,ticket,cdate,author,comment,old_comment):
        pass
        #self.log.debug("ticket_comment_modified: %s" % ticket.id)

    def ticket_change_deleted(self,ticket,cdate,changes):
        pass
        #self.log.debug("ticket_change_deleted: %s" % ticket.id)
    

class Client:
    def __init__(self):
        pass
    def test(self):
        print "test print"
    def set_adapter(self,adapter):
        self.adapter = adapter
    def get_adapter(self):
        return self.adapter

class Adapter:
    def __init__(self):
        pass
    def test(self):
        print "adapter reporting"


class RestClient:
    import os, sys, urllib, urllib2, time, re
    from logbook import Logger, FileHandler
    
    def __init__(self):
        pass


if __name__ == "__main__":
    
    logger = Logger("TicketchangeToInfluxdb")
    logfile = "ticketchangetoinfluxdb.log"
    fh = FileHandler(logfile,"a")
    fh.applicationbound()
    fh.push_application()
    
    client = Client()
    client.test()
    adapter = Adapter()
    client.set_adapter(adapter)
    a =client.get_adapter()
    a.test()
    
    print("This is just a test.")
    logger.info("Testing logging.")



    
