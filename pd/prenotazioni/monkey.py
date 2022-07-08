# -*- coding: utf-8 -*-
from pyinter.interval import Interval
from rg.prenotazioni.adapters.slot import BaseSlot
from rg.prenotazioni.adapters.slot import LowerEndpoint
from rg.prenotazioni.adapters.slot import slots_to_points
from rg.prenotazioni.adapters.slot import UpperEndpoint


def patchSub(self, value):
    """Subtract something from this"""
    if isinstance(value, Interval):
        value = [value]

    # We filter not overlapping intervals
    good_intervals = [x for x in value if x.overlaps(self)]
    points = slots_to_points(good_intervals)

    start = self.lower_value
    intervals = []
    for x in points:
        if isinstance(x, LowerEndpoint) and x > start:
            intervals.append(BaseSlot(start, x))
            # we raise the bar waiting for another stop
            start = self.upper_value
        elif isinstance(x, UpperEndpoint):
            start = x
    # START PATCH
    if start < self._upper_value:
        # Abbiamo start > upper_value quando per esempio è stato cambiato
        # l'orario di chiusura degli sportelli e ci sono prenotazioni che
        # erano state fatte con l'orario vecchio. Per esempio se c'era
        # come orario di chiusura 12:45 e c'era una prenotazione che finiva alle 12:45
        # e poi viene cambiata la chiusura dello sportello alle 12:30.
        # in questo caso verrebbe generato uno slot inconsistente tipo [45900, 45000]
        intervals.append(BaseSlot(start, self.upper_value))
    # END PATCH
    return intervals
