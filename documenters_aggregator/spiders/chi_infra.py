# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import re
import datetime as dt
import pytz

from documenters_aggregator.spider import Spider


class Chi_infraSpider(Spider):
    name = 'chi_infra'
    long_name = 'Chicago Infrastructure Trust'
    allowed_domains = ['chicagoinfrastructure.org']
    start_urls = ['http://chicagoinfrastructure.org/public-records/scheduled-meetings/']

    year = dt.date.today().year

    def parse(self, response):
        """
        Currently, the meeting page just gives dates, so there's limited info to report.
        The dates have no years, but the list has a year at the top. I pull this
        to add to the datetimes.
        """

        year_item = response.css('div.entry')[1].css('div.entry p')[0].extract()
        year_match = re.search(r'([0-9]{4})', year_item)
        self.year = int(year_match.group(1))

        for item in response.css('div.entry')[1].css('div.entry p')[1:]:
            start_time = self._parse_start(item)
            data = {
                '_type': 'event',
                'name': 'Board Meeting',
                'description': None,
                'classification': 'Board Meeting',
                'start_time': start_time.isoformat(),
                'end_time': None,
                'all_day': False,
                'status': 'tentative',
                'location': self._parse_location(item),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(item, data, start_time)
            yield data

    def _parse_start(self, item):
        """
        No times given; set to Midnight
        """
        extracted = item.extract()
        match = re.search(r'([a-zA-Z]*),\s{1}([a-zA-Z]+)\s([0-9]{1,2})', extracted)
        date_string = '{0} {1}'.format(match.group(0), str(dt.datetime.now().year))

        start_date_obj = dt.datetime.strptime(date_string, "%A, %B %d %Y")
        tz = pytz.timezone('America/Chicago')
        return tz.localize(start_date_obj)

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]

    def _parse_location(self, item):
        """
        No location provided
        """
        return {
            'url': None,
            'name': None,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            }
        }
