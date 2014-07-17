# -*- coding: utf-8 -*-
# Extends for PrenotazioniFolderSchema
from Products.Archetypes.atapi import AnnotationStorage, StringField, StringWidget  # noqa
from archetypes.schemaextender.field import ExtensionField
from pd.prenotazioni import prenotazioniMessageFactory as _


class ExtensionStringField(ExtensionField, StringField):
    """derivative of StringField for extending schemas
    """


class PrenotazioniFolderSchemaExtender(object):

    """ extender for cream visore
    """

    fields = [
        ExtensionStringField(
            'same_day_booking_disallowed',
            storage=AnnotationStorage(),
            widget=StringWidget(
                label=_(
                    'label_same_day_booking_disallowed',
                    u"Same day booking disallowed"
                ),
                description=_(
                    'help_same_day_booking_disallowed',
                    u"States if it is not allowed to reserve a booking "
                    u"during the current day"
                ),
                macro="same_day_booking_disallowed",
                helper_js=(),
                helper_css=(),
            ),
            default='',
            required=True,
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def fiddle(self, schema):
        schema.moveField('same_day_booking_disallowed', after='aData')
