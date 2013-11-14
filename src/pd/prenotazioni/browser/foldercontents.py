# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.app.content.browser.foldercontents import (FolderContentsTable
                                                      , FolderContentsBrowserView
                                                      , FolderContentsView)


class PrenotazioniFolderContentsTable(FolderContentsTable):
    """
    The foldercontents table WITH NO BUTTONS
    """
    buttons = []


class PrenotazioniFolderContentsView(FolderContentsView):
    '''
    The foldercontents CUSTOMIZED
    '''
    def contents_table(self):
        ''' Hide folfer action if the user doesn't have Manager role
        '''
        roles = api.user.get_roles()
        if 'Manager' in roles:
            table = FolderContentsTable(aq_inner(self.context), self.request)
            return table.render()
        else:
            table = PrenotazioniFolderContentsTable(aq_inner(self.context), self.request)
            return table.render()


class PrenotazioniFolderContentsBrowserView(FolderContentsBrowserView):
    table = PrenotazioniFolderContentsTable
