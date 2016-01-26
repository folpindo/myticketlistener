#!/bin/env python


"""

If there is changes on the following fields, the changes along with some details will be pushed to influxdb.

    Custom Fields
        1. dev_loe
        1. qa_loe
        1. consumed_hours
        1. qa_assigned
        1. dev_assigned
        1. ticket_progress
        1. hours
        
    Ticket:
        1. status
        

On trac.ini, just insert the following lines:

[ticketchangetoinfluxdb]
ticket_fields = dev_loe, qa_loe, consumed_hours, qa_assigned, dev_assigned, ticket_progress, hours, status

 
"""

import os,sys,urllib,urllib2,time,re
from influxdb import InfluxDBClient
from logbook import Logger,FileHandler
from trac.core import *
from trac.ticket.api import ITicketChangeListener
from trac.web import IRequestHandler
from json import dumps, loads


try:
    
    from urllib.parse import urlparse,parse_qs

except ImportError:
    
    from urlparse import urlparse,parse_qs
    
    
class TicketchangeToInfluxdb(Component):

    implements(ITicketChangeListener,IRequestHandler)

    def match_request(self,req):
        pass
        #return re.match(r'/get_sku(?:_trac)?(?:/.*)?$',req.path_info)

    def process_request(self,req):
	pass
           
    def ticket_created(self,ticket):
        pass
        ticket_id = ticket.id
        config = self.config
        env = self.env
        sku = None
        brand = None
        #sku = ticket.get_value_or_default("sku")
        #brand = ticket.get_value_or_default("brand")
        #data = (ticket_id,sku,brand)

    def ticket_changed(self,ticket,comment,author,old_values):

        ticket_id = ticket.id
        config = self.config

        infdb_item = InfluxdbItem()
        infdb_item.set_config(config)
        infdb_item.set_ticket(ticket)
        infdb_item.set_comment(comment)
        infdb_item.set_author(author)
        
        infdb_item.set_old_values(old_values)
        infdb_item.set_log(self.log)
        self.log.debug("old_values:")
        self.log.debug(old_values)

        self.log.debug("Checking if the change is monitored or not (valid or invalid)")
        monitored_fields_changed = False
        monitored_fields_changed = infdb_item.is_change_valid()

        if monitored_fields_changed:
            json_body = [
                {
                    "measurement": "DevLOE",
                    "tags": {
                        "ticket_number":12346,
                        "ticket_status":"assigned",
                        "ticket_owner":"folpindo",
                        "ticket_milestone":"milestone1"
                    },
                    "time": "2009-12-10T23:03:00Z",
                    "fields": {
                        "value": 15
                    }
                }
            ]
            client = InfluxDBClient('localhost', 8086, '', '', 'trac_sample')
            #client.create_database('trac_sample')
            client.write_points(json_body)

        env = self.env
        #sku = ticket.get_value_or_default("sku")
        #brand = ticket.get_value_or_default("brand")
        
        row = None
        self.log.debug(type(config))
        self.log.debug(old_values)
        self.log.debug(comment)
        
        for k in old_values:
            v = ticket.get_value_or_default(k) #the values to be pushed to influxdb
            self.log.debug("OLD_VALUES: %s, new: %s" % (k,v))
            
              
    def ticket_deleted(self,ticket):
        pass
        #ticket_id = ticket.id
        #config = self.config
        #env = self.env
        
    def ticket_comment_modified(self,ticket,cdate,author,comment,old_comment):
        pass
        #self.log.debug("ticket_comment_modified: %s" % ticket.id)

    def ticket_change_deleted(self,ticket,cdate,changes):
        pass
        #self.log.debug("ticket_change_deleted: %s" % ticket.id)

    
class InfluxdbItem:
    
    def __init__(self):
        pass

    def set_config(self,config):
        self.config = config

    def set_ticket(self,ticket):
        self.ticket = ticket
        
    def set_comment(self,comment):
        self.comment = comment
        
    def set_author(self,author):
        self.author = author

    def set_log(self,log):
        self.log = log

    def set_old_values(self,old_values):
        self.old_values = old_values

    def get_monitored_fields(self):
        config = self.config
        parser = config.parser
        ticket_fields = []
        monitored_change = False
        
        if parser.has_section('ticketchangetoinfluxdb'):
            self.log.debug("Found Ticket Change To Influxdb Section")
            if config.has_option('ticketchangetoinfluxdb','ticket_fields'):
                ticket_fields_str = config.get('ticketchangetoinfluxdb','ticket_fields')
                ticket_fields = [field.strip() for field in ticket_fields_str.split(',')]
        else:
            self.log.debug("Unable to find Ticket Change to Influxdb Section")

        return ticket_fields

    def get_url(self):
        config = self.config
        parser = config.parser
        url = None

        if parser.has_section('ticketchangetoinfluxdb'):
            if config.has_option('ticketchangetoinfluxdb','influxdb_api_url'):
                self.influxdb_api_url = config.get('ticketchangetoinfluxdb','influxdb_api_url')
                url = self.influxdb_api_url

        return url
    
    def is_change_valid(self):
        
        ticket_fields = self.get_monitored_fields()
        monitored_change = False
        
        for field_key in self.old_values.keys():
            if field_key in ticket_fields:
                monitored_change = True
                self.log.debug("Found changed on monitored field.")
                break
            
        return monitored_change
    
    def get_operation(self):
        return 'write'
    def get_db(self):
        return 'trac_ecom'
    
    
    def get_data(self):
        pass

    def set_params(self):
        pass
    

class Client:
    
    def __init__(self):
        pass
    
    def test(self):
        print "test print"
        
    def set_adapter(self,adapter):
        self.adapter = adapter
        
    def get_adapter(self):
        return self.adapter

    def set_url(self,url):
        self.url = url

    def get_url(self):
        return self.url

    def call_api(self):
        return self.adapter.call_api()
    
    def set_client(self,client):
        self.client(client)
    

class Adapter:
    
    def __init__(self):
        pass

    def set_url(self, url):
        pass

    def set_client(self,client):
        self.client = client

    def set_client_url(self, url):
        self.client.set_url(url)

    def call_api(self):
        return self.client.send()

    def get_client(self):
        return self.client
    
    def test(self):
        print "adapter reporting"


class RestClient:
    
    import os, sys, urllib, urllib2, time, re
    from logbook import Logger, FileHandler
    
    def __init__(self):
        pass
    
    def set_data(self,data):
        
        self.data = data
        
    def set_url(self,url):
        self.url = url

    def set_headers(self):
        #headers = {'Content-Type':'application/octet-stream'}
        headers = {'Content-Length':'%d' % len(self.data),'Content-Type':'application/octet-stream'}
        self.set_req()
        for k,v in headers.iteritems():
            self.req.add_header(k,v)

    def set_req(self):
        self.req = urllib2.Request(self.url, urllib.urlencode(self.data))
        #self.req = urllib2.Request(self.url)
        
    def send(self):
        self.set_req()
        return urllib2.urlopen(self.req)
        


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



    
