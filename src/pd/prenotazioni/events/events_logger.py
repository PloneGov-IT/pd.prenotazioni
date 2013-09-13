# -*- coding: utf-8 -*-
from pd.prenotazioni import prenotazioniFileLogger as logger
from plone import api
import StringIO
import csv


def csv2string(data):
    '''
    Converts an array of info to a proper cvs string
    '''
    dummy_file = StringIO.StringIO()
    cw = csv.writer(dummy_file)
    cw.writerow(data)
    return dummy_file.getvalue().strip('\r\n')


def on_workflow_change(obj, event):
    '''
    This handler logs a cvs string for
    each IPrenotazione workflow changes
    '''
    user = api.user.get_current()
    data = [obj.UID(), obj.Title(), user.getId(), event.action]
    logger.info(csv2string(data))


def on_move(obj, event):
    '''
    This handler logs a cvs string for
    every IPrenotazione document moved
    '''
    user = api.user.get_current()
    data = [obj.UID(), obj.Title(), user.getId(), 'moved']
    logger.info(csv2string(data))


def on_modify(obj, event):
    '''
    This handler logs a cvs string for
    every IPrenotazione document modified
    '''
    user = api.user.get_current()
    data = [obj.UID(), obj.Title(), user.getId(), 'changed']
    logger.info(csv2string(data))
