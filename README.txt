.. contents::

Introduction
============

PD Prenotazioni::

  zope-conf-additional +=
    <product-config pd.prenotazioni>
        logfile ${buildout:directory}/var/log/prenotazioni.log
    </product-config>

Searchable text for Prenotazione objects is customized.
In particular it adds the comments to the index.
