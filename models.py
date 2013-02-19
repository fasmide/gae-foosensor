#!/usr/bin/env python
# -*- coding: utf8 -*-

from google.appengine.ext import db
from google.appengine.api import memcache


class Client(db.Model):
    #Den kan ingen ting
    a = True #wtf