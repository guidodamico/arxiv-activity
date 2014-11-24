#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime as dt
import itertools
import requests
import feedparser
import csv

def get_results(date_start, date_end, category):
    # Get the articles of a category from date_start to date_end.
    # The dates are in datetime format
    base_url = 'http://export.arxiv.org/api/query?'
    # The 21:00 (GMT) deadline is the time that separates publication between different days
    deadline = dt.time(21,0,0)
    # Need to translate datetime format to string
    start = dt.datetime.combine(date_start, deadline).strftime('%Y%m%d%H%M')
    end = dt.datetime.combine(date_end, deadline).strftime('%Y%m%d%H%M')
    query = 'cat:%s+AND+submittedDate:[%s+TO+%s]&max_results=100' % (category, start, end)
    url = base_url+"search_query="+query
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print("Download of {0} failed with code: {1}".format(url, code))
        return None
    return r

def get_number_primary(feed, category):
    # Given an Atom feed, gives the number of articles in the primary category,
    # to exclude crosslists
    return len([1 for entry in feed.entries
        if entry.arxiv_primary_category['term'] == category])

def daterange(start_date, end_date):
    # Little function that generates an iterator over the range of dates (in
    # days)
    for n in xrange(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)

def main():
    # Notice that the date is in GMT. Deadline is at 16 EST, which is 21 GMT
    categories = ['hep-th', 'hep-ph', 'gr-qc', 'astro-ph.CO', 'astro-ph.HE',
        'astro-ph.IM', 'astro-ph.EP']
    step = dt.timedelta(days=1)
    today = dt.date.today() - step
    #feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    #feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
    start = dt.date(2009, 1, 20)
    end = dt.date(2014, 11, 20)
    #numbers = list(itertools.chain(*[['date'], categories]))
    numbers = []
    for date in daterange(start, end+dt.timedelta(1)):
        num_papers = []
        for cat in categories:
            response = get_results(date, date + step, cat)
            feed = feedparser.parse(response.content)
            num_papers.append(get_number_primary(feed, cat))
        # Notice that the date we put is date + 1 day, because the deadline is
        # at 21 GMT
        numbers.append(list(itertools.chain(*[[str(date+dt.timedelta(1))]
            , num_papers])))
    with open('number_of_papers.csv', 'wb') as f:
        wr = csv.writer(f)
        wr.writerow(['date', 'hep-th', 'hep-ph', 'gr-qc', 'astro-ph.CO', 'astro-ph.HE',
            'astro-ph.IM', 'astro-ph.EP'])       
        wr.writerows(numbers)

if __name__=="__main__":
	main()
