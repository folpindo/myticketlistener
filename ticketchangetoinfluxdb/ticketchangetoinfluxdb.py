#!/bin/env python


"""

If there is changes on the following fields, the changes along with some details will be pushed to influxdb.

    Custom Fields (This should be set as monitored_fields in the trac configuration.)
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

;Rest API settings

direct= 0
api = 1

url = http://bteves.lion.perfectfitgroup.local
service_version = v1
service_name = Ordermetrics
method = getMethod


;Connection parameters for influxdb

host = localhost
port = 8086
user =
user_pwd =
database = trac_ecom


ticket_fields = dev_loe, qa_loe, consumed_hours, qa_assigned, dev_assigned, ticket_progress, hours, status
monitored_fields = dev_loe, qa_loe, consumed_hours, qa_assigned, dev_assigned, ticket_progress, hours, status
database = sample
dev_loe = DevLOE
qa_loe = QALOE
universal_tags = ticket_id|id,ticket_status|status,dev_assigned|owner,ticket_qa_assigned|qa_asigned

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
        #return re.match(r'/handler(?:_trac)?(?:/.*)?$',req.path_info)

    def process_request(self,req):
	pass

    def ticket_created(self,ticket):
        pass
           
    """
    Build the data to be pushed to influxdb.
    """
    def get_data(self,ticket,author):
        
        config = self.config
        parser = config.parser
        
        measurement = None
        influxdata = []
        tags = {}
        fields_key_values = {}
        
        monitored_fields = self.get_monitored_fields() # get the list of monitored fields
        fields = self.get_fields() # get the list of fields to be pushed to influxdb
        universal_tags = self.get_tags() # get the list of field that are to be tagged

        """
        Extract trac field value with key to be used in influxdb for the fields.
        """
        for field in fields:
            k,v = field.split("|")
            if v == 'author':
                fields_key_values['author'] = author
            else:
                fields_key_values[k.strip()] = ticket.get_value_or_default(v.strip())
               
        """
        Extract trac field value with key to be used in influxdb for the tags.
        """
        for tags_kv in universal_tags:
            k,v = tags_kv.split("|")
            tags[k.strip()] = ticket.get_value_or_default(v.strip())
            
        """
        We have now set the measurement name.
        The field=measurement in configuration will not work with this version.
        """
        if parser.has_section('ticketchangetoinfluxdb'):
            if config.has_option('ticketchangetoinfluxdb','measurement'):
                measurement_str = config.get('ticketchangetoinfluxdb','measurement')
                measurement = measurement_str.strip()
                
        influxdata =  {
            "measurement": measurement,
            "tags": tags,
            "time": ticket.get_value_or_default("changetime"),
            "fields": fields_key_values  
        }
        
        return [influxdata]
    
    
    def get_tags(self):
        
        config = self.config
        parser = config.parser
        tags = []
        
        if parser.has_section('ticketchangetoinfluxdb'):
            if config.has_option('ticketchangetoinfluxdb',"universal_tags"):
                tags_str = config.get('ticketchangetoinfluxdb',"universal_tags")
                tags = [field.strip() for field in tags_str.split(',')]
                
        return tags
    
    """
    Get the list of monitored fields
    
    """
    def get_monitored_fields(self):
        config = self.config
        parser = config.parser
        ticket_fields = []
        monitored_change = False

        if parser.has_section('ticketchangetoinfluxdb'):
            self.log.debug("Found Ticket Change To Influxdb Section")
            if config.has_option('ticketchangetoinfluxdb','monitored_fields'):
                ticket_fields_str = config.get('ticketchangetoinfluxdb','monitored_fields')
                ticket_fields = [field.strip() for field in ticket_fields_str.split(',')]
        else:
            self.log.debug("Unable to find Ticket Change to Influxdb Section")

        return ticket_fields
    
    """
    Get the list to be set on the fields on influxdb.
    """
    def get_fields(self):
        config = self.config
        parser = config.parser
        fields = []

        if parser.has_section('ticketchangetoinfluxdb'):
            if config.has_option('ticketchangetoinfluxdb','fields'):
                fields_str = config.get('ticketchangetoinfluxdb','fields')
                fields = [field.strip() for field in fields_str.split(',')]

        return fields
    
    def check_database(self):
        pass
    
    def create_database(self,database):
        pass
    
    def get_mode(self):
        pass
    
    def call_api(self):
        pass

    def ticket_changed(self,ticket,comment,author,old_values):
        
        ticket_id = ticket.id
        config = self.config
        parser = config.parser
        
        infdb_item = InfluxdbItem()
        infdb_item.set_config(config)
        infdb_item.set_ticket(ticket)
        infdb_item.set_comment(comment)
        infdb_item.set_author(author)
        infdb_item.set_old_values(old_values)
        infdb_item.set_log(self.log)
        
        monitored_fields_changed = False
        monitored_fields_changed = infdb_item.is_change_valid()
        self.log.debug("Chage valid:")
        self.log.debug(monitored_fields_changed)
        data = []
        database = None
        
        if monitored_fields_changed:
            
            data = self.get_data(ticket,author)
            
            self.log.debug("Influxdb data:")
            self.log.debug(data)
            
            # Default influxdb connection parameters below
            host = "localhost"
            port = 8086
            database = "trac_sample"
            influxdb_user = ""
            influxdb_user_pwd = ""
                       
            # Override default configurations
            if parser.has_section('ticketchangetoinfluxdb'):        
                if config.has_option('ticketchangetoinfluxdb','host'):
                    host = config.get('ticketchangetoinfluxdb','host')
            
            if parser.has_section('ticketchangetoinfluxdb'):        
                if config.has_option('ticketchangetoinfluxdb','port'):
                    port = config.get('ticketchangetoinfluxdb','port')
                    
            if parser.has_section('ticketchangetoinfluxdb'):        
                if config.has_option('ticketchangetoinfluxdb','database'):
                    database = config.get('ticketchangetoinfluxdb','database')
                    
            if parser.has_section('ticketchangetoinfluxdb'):        
                if config.has_option('ticketchangetoinfluxdb','user'):
                    influxdb_user = config.get('ticketchangetoinfluxdb','user')
                    
            if parser.has_section('ticketchangetoinfluxdb'):        
                if config.has_option('ticketchangetoinfluxdb','user_pwd'):
                    influxdb_user_pwd = config.get('ticketchangetoinfluxdb','user_pwd')                    
                    
            if database is not None:
                client = InfluxDBClient(host, port, influxdb_user, influxdb_user_pwd, database)
                client.write_points(data)
                
              
    def ticket_deleted(self,ticket):
        pass

    def ticket_comment_modified(self,ticket,cdate,author,comment,old_comment):
        pass

    def ticket_change_deleted(self,ticket,cdate,changes):
        pass


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
