# -*- coding: UTF-8 -*-
import multiprocessing

from fsqaway.config import HTTP_PORT


proc_name = '4sq'
pidfile = '/tmp/4sq.pid'
daemon = True

workers = multiprocessing.cpu_count() * 2 + 1
bind = ':' + str(HTTP_PORT)
worker_class = 'gevent'

access_log_format = '%(t)s "%(r)s" %(s)s %(h)s t=%(D)s'
errorlog = '/var/log/4sq.log'
accesslog = errorlog
