"""
In settings.py:

DEBUG=True
DEBUG_SQL=True
SQL_LOG='/path/to/file'

and MIDDLEWARE_CLASSES += ('debug_middleware.SQLMiddleWare',)

If LOCAL_DEV is True, we print to the console in any case.

"""


import os
import time
import datetime
from django.conf import settings
from django.db import connection
from pprint import pprint

def print_output( string ):
    print string



class SQLMiddleWare:

    start=None

    def process_request(self, request):
        self.start=time.time()

    def process_response (self, request, response):

        div="==============================\n"
        debug_sql = getattr(settings, "DEBUG_SQL", False)
        sql_log = settings.SQL_LOG
        if (not self.start) or not (settings.DEBUG and debug_sql):
            return response

        if settings.DEBUG and settings.DEBUG_SQL and not settings.LOCAL_DEV:
            self.sql_log_file = open(settings.SQL_LOG, 'a+')
            print_output=self.sql_log_file.write

        timesql=0.0
        for q in connection.queries:
            timesql+=float(q['time'])
        seen={}
        duplicate=0
        for q in connection.queries:
            sql=q["sql"]
            c=seen.get(sql, 0)
            if c:
                duplicate+=1
            q["seen"]=c
            seen[sql]=c+1
            
        timerequest=round(time.time()-self.start, 3)
        queries=connection.queries
        print_output( div )
        print_output( "%s\n" % request.path )
        print_output( div )
        print_output( "%s\n" % str(request) )
        print_output( div )
        for i in queries:
            print_output( "Seen: %s\n" % i['seen'] )
            print_output( "Time: %s\n" % i['time'] )
            print_output( "SQL: %s\n" % i['sql'] )
            print_output( div )
            print_output( "\n" )
        print_output( div )
        print_output( div )
        print_output( "Execution time for %s: %f\n" % (request.path, timerequest) )            
        self.sql_log_file.close()
        return response
