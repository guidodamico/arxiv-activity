#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import requests
import feedparser
import numpy as np
import pickle

def get_results(date_start, date_end, subject):
	base_url = 'http://export.arxiv.org/api/query?'
	deadline = datetime.time(21,0,0)
	start = datetime.datetime.combine(date_start, deadline).strftime('%Y%m%d%H%M')
	end = datetime.datetime.combine(date_end, deadline).strftime('%Y%m%d%H%M')
	search_date = '[%s+TO+%s]' % (start, end)
	sort = 'lastUpdatedDate'
	#query = 'cat:%s+AND+submittedDate:[%s+TO+%s]&sortBy=%s&sortOrder=ascending&start=0&max_results=100' % (subject, start, end, sort)
	query = 'cat:%s+AND+submittedDate:[%s+TO+%s]&max_results=100' % (subject, start, end)
	url = base_url+"search_query="+query
	r = requests.get(url)
	if r.status_code != requests.codes.ok:
		print("Download of {0} failed with code: {1}".format(url, code))
		return None
	return r

def get_number_primary(feed, cat):
	#print [entry.title for entry in feed.entries if entry.arxiv_primary_category['term'] == cat]
	return len([1 for entry in feed.entries if entry.arxiv_primary_category['term'] == cat])

def main():
	# Notice that the date is in GMT. Deadline is at 16 EST, which is 21 GMT
	cat = "astro-ph.CO"
	step = datetime.timedelta(days=1)
	today = datetime.date.today() - step
	#feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
	#feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
	tot_days = 120
	series = []
	for i in xrange(tot_days):
		start = today - step*(i+1)
		end = today - step*i
		response = get_results(start, end, cat)
		feed = feedparser.parse(response.content)
		num_papers = get_number_primary(feed, cat)
		#print np.datetime64(end)
		series.append([end, num_papers])
	with open('cosmo_series.csv', 'w') as f:
		f.writelines(',\t'.join(str(j) for j in i) + '\n' for i in series)

if __name__=="__main__":
	main()
