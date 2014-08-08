# -*- coding: utf-8 -*-
from BTrees.OOBTree import OOTreeSet
from Products.Five.browser import BrowserView
from datetime import datetime
from plone.memoize.view import memoize
from plone import api
from pd.prenotazioni import prenotazioniFileLogger
from rg.prenotazioni.browser.base import BaseView as PrenotazioniBaseView
from rg.prenotazioni.interfaces import IPrenotazioniFolder
from zope.annotation.interfaces import IAnnotations
from json import dumps, loads
from cStringIO import StringIO
from csv import writer


class BaseView(BrowserView):
    ''' The base class for this context
    '''
    entry_set = set([])
    # entry indexes:
    _ei_date = 2

    def set_header(self, *args):
        '''
        Shorcut for setting headers in the request
        '''
        return self.request.RESPONSE.setHeader(*args)

    @property
    @memoize
    def csv_url(self):
        ''' The CSV url to get those data
        '''
        return '%s/%s.csv' % (self.context.absolute_url(), self.__name__)

    @property
    @memoize
    def csv_filename(self):
        ''' The CSV filename
        '''
        return '%s-%s.csv' % (
            self.context.getId(),
            datetime.now().strftime('%Y%m%d%H%M')
        )

    @memoize
    def uid_to_url(self, uid):
        ''' Converts a uid to an url
        '''
        pc = api.portal.get_tool('portal_catalog')
        brains = pc(UID=uid)
        if not brains:
            return {
                'title': uid,
                'url': ''
            }
        brain = brains[0]
        return {
            'title': brain.Title,
            'url': brain.getURL()
        }

    @property
    @memoize
    def entry_number(self):
        ''' Number of entries
        '''
        return len(self.entry_set)

    @memoize
    def load_entries(self, resul_type='list'):
        ''' Number of entries
        '''
        return map(loads, self.entry_set)

    @property
    @memoize
    def older_entry(self):
        ''' The entries grouped by date
        '''
        entries = self.load_entries()
        if not entries:
            return ''
        return min(
            self.load_entries(),
            key=lambda x: x[self._ei_date]
        )

    def entries_by_action(self):
        ''' Return the entries grouped by action
        '''
        results = {}
        entries = self.load_entries()
        for entry in entries:
            results.setdefault(entry[0], []).append(entry)
        return results

    @staticmethod
    def csvencode(data):
        '''
        Converts an array of info to a proper cvs string
        '''
        dummy_file = StringIO()
        cw = writer(dummy_file)
        for line in data:
            cw.writerow(line)
        return dummy_file.getvalue().strip('\r\n')

    @property
    @memoize
    def sorted_entries(self):
        ''' Return the entries as a sorted list
        '''
        return sorted(self.entry_set)

    def expand_entry(self, entry):
        ''' Expand an entry
        '''
        data = loads(entry)
        return {
            'action': data[0],
            'note': data[1],
            'date': datetime.fromtimestamp(data[self._ei_date]).strftime('%Y/%m/%d %H:%M'),  # noqa
            'agenda': self.uid_to_url(data[3]),
            'booking': self.uid_to_url(data[4]),
            'fullname': data[5],
            'user': data[6],
        }

    def get_csv(self):
        ''' This method serves a CSV file with the data of the view
        '''
        self.set_header(
            'Content-Type', 'application/csv; charset=utf8'
        )
        self.set_header(
            'Content-Disposition',
            'attachment;filename=%s' % self.csv_filename
        )
        return self.csvencode(self.load_entries())


class ContextView(BaseView, PrenotazioniBaseView):
    '''
    Aggregates data from the booking folders below
    '''
    logstorage_key = 'pd.prenotazioni.logstorage'
    file_logger = prenotazioniFileLogger

    @property
    @memoize
    def logstorage(self):
        ''' This is an annotation OOTreeSet where we can store log entries
        '''
        annotations = IAnnotations(self.context)
        if not self.logstorage_key in annotations:
            annotations[self.logstorage_key] = OOTreeSet()
        return annotations[self.logstorage_key]

    def add_entry(self, entry):
        ''' Add an entry to the logstorage
        '''
        return self.logstorage.add(entry)

    def remove_entry(self, entry):
        ''' Remove an entry from the logstorage
        '''
        try:
            return self.logstorage.remove(entry)
        except KeyError:
            pass

    @property
    @memoize
    def entry_set(self):
        ''' All the entries saved in this object
        '''
        if not self.prenotazioni.user_can_manage:
            return set([])
        return set(self.logstorage)

    def csvlog(self, data):
        ''' Log something, dumping it on a file and storing it in the
        logstorage
        '''
        self.file_logger.info(self.csvencode([data]))
        self.add_entry(dumps(data))


class AggregateView(BaseView):
    ''' The Base View to get the statistics for this site
    '''
    prenotazioni_interfaces = [
        IPrenotazioniFolder
    ]

    @property
    @memoize
    def plone_tools(self):
        ''' Proxy the plone_tools view
        '''
        return api.content.get_view('plone_tools', self.context, self.request)

    @property
    @memoize
    def prenotazioni_brains(self):
        ''' Return the prenotazioni brains under this context
        '''
        pc = self.plone_tools.catalog()
        query = {
            'object_provides': [x.__identifier__ for x in self.prenotazioni_interfaces],  # noqa
            'path': '/'.join(self.context.getPhysicalPath())
        }
        return pc(**query)

    @property
    @memoize
    def stat_views(self):
        ''' Return the views that give the statistic for all the prenotazioni
        objects
        '''
        return [
            api.content.get_view(
                'booking_stats',
                brain.getObject(),
                self.request
            ) for brain in self.prenotazioni_brains
        ]

    @property
    @memoize
    def entry_set(self):
        ''' The entry_set is the union of all the contained entry_sets
        '''
        entries = set([])
        for view in self.stat_views:
            entries = entries.union(view.entry_set)
        return entries
