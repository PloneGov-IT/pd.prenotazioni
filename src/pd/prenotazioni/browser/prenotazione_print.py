# -*- coding: utf-8 -*-
from plone.memoize.view import memoize
from rg.prenotazioni.browser.prenotazione_print import PrenotazionePrint as BasePrintView


class PrenotazionePrint(BasePrintView):
    '''
    This is a view to proxy autorizzazione
    '''

    @property
    @memoize
    def print_action(self):
        """
        Link to prenotazioni_print_pdf
        """
        return self.context.absolute_url() + '/prenotazione_print_pdf?uid='+ self.request.get("uid")

