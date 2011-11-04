###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2010, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
from zope.component import adapts
from zope.interface import implements
from Products.AdvancedQuery import MatchGlob, And, Or, Eq, In, RankByQueries_Max
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.Zuul.tree import PermissionedCatalogTool
from Products.ZenModel.DataRoot import DataRoot
from Products.Zuul.utils import allowedRolesAndGroups
from Products.Zuul.search import ISearchProvider
from Products.Zuul.search import ISearchResult

class DeviceSearchProvider(object):
    """
    Provider which searches Zenoss's global catalog for matching devices
    """
    implements(ISearchProvider)
    adapts(DataRoot)

    def __init__(self, dmd):
        self._dmd = dmd


    def getCategoryCounts(self, parsedQuery, filterFn=None):
        return self.getSearchResults(parsedQuery, countOnly=True, filterFn=filterFn)

    def getSearchResults(self, parsedQuery, sorter=None, category=None, countOnly=False,
                         unrestricted=False, filterFn=None):
        """
        Queries the catalog.  Searches the searchKeywords index
        using *keyword1* AND *keyword2* AND so on.
        If there are preferred categories, find maxResults # of instances
        before searching other categories.

        @rtype generator of BrainSearchResult objects
        """
        operators = parsedQuery.operators
        keywords = parsedQuery.keywords

        if not keywords:
            return

        def listMatchGlob(op, index, list):
            return op(*[ MatchGlob(index, '*%s*' % i ) for i in list ])
        dmd = self._dmd
        kw_query = Or(listMatchGlob(And, 'titleOrId', keywords),
                      listMatchGlob(And, 'getDeviceIp', keywords))
        full_query = kw_query
        cat = PermissionedCatalogTool(dmd, dmd.Devices.deviceSearch)

        querySet = full_query
        if not unrestricted:
            # take permissions into account
            roles = In('allowedRolesAndUsers', allowedRolesAndGroups(self._dmd))
            querySet = [full_query, roles]
            querySet = And(*querySet)

        catalogItems = cat.catalog.evalAdvancedQuery(querySet)
        brainResults = [DeviceSearchResult(catalogItem)
                        for catalogItem in catalogItems]
        if filterFn:
            brainResults = filter(filterFn, brainResults)

        if countOnly:
            return dict(Device=len(brainResults))
        results = brainResults

        if sorter is not None:
            results = sorter.limitSort(results)

        return results

    def getQuickSearchResults(self, parsedQuery, maxResults=None):
        """
        Currently just calls getSearchResults
        """
        return self.getSearchResults( parsedQuery, maxResults )


class DeviceSearchResult(object):
    """
    Wraps a brain from the search catalog for inclusion in search results.
    """

    implements(ISearchResult)

    def __init__(self, brain):
        self._brain = brain

    @property
    def url(self):
        return self._brain.getPath()

    @property
    def category(self):
        return self._brain.meta_type

    @property
    def excerpt(self):
        return self._brain.id

    iconTemplate = '<img src="/zport/dmd/img/icons/noicon.png"/>'

    @property
    def icon(self):
        # show no icon so we don't have to wake up the object
        return self.iconTemplate

    @property
    def popout(self):
        return False

