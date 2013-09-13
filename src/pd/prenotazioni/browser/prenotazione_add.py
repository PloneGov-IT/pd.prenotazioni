# -*- coding: utf-8 -*-
from pd.prenotazioni import prenotazioniMessageFactory as _
from plone.memoize.view import memoize
from rg.prenotazioni.browser.prenotazione_add import AddForm as BaseForm
from zope.schema import ValidationError
import re

TELEPHONE_PATTERN = re.compile(r'^3([0-9]| )*$')


class InvalidMobile(ValidationError):
    __doc__ = _("invalid_mobile_number", "Mobile phone number not valid")


def check_mobile_number(value):
    '''
    If value exist it should match TELEPHONE_PATTERN
    '''
    if not value:
        return True
    if isinstance(value, basestring):
        value = value.strip()
    if TELEPHONE_PATTERN.match(value) is not None:
        return True
    raise InvalidMobile(value)


class AddForm(BaseForm):
    """
    """
    contact_details = ['phone', 'mobile', 'email']

    @property
    @memoize
    def form_fields(self):
        '''
        This method adds mobile number validation to prenotazioni form
        '''
        ff = super(AddForm, self).form_fields
        ff['email'].field.required = False
        ff['mobile'].field.constraint = check_mobile_number
        return ff

    def validate(self, action, data):
        '''
        Checks if we can book those data
        '''
        errors = super(AddForm, self).validate(action, data)
        if not any([data.get(key, False) for key in self.contact_details]):
            msg = _('contact_details_error',
                    u'You have to provide at least one of these fields: '
                    u'email, phone, mobile')
            self.set_invariant_error(errors, self.contact_details, msg)

        return errors
