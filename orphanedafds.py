#!/usr/bin/env python2.5

# Copyright 2008 bjweeks, MZMcBride

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import MySQLdb
import wikitools
import settings

report_title = 'Wikipedia:Database reports/Orphaned article deletion discussions'

report_template = u'''
Subpages of [[Wikipedia:Articles for deletion]] that have no incoming links; \
data as of <onlyinclude>%s</onlyinclude>.

{| class="wikitable sortable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! Page
|-
%s
|}
'''

wiki = wikitools.Wiki()
wiki.login(settings.username, settings.password)

conn = MySQLdb.connect(host='sql-s1', db='enwiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
cursor.execute('''
/* orphanedafds.py SLOW_OK */
SELECT
  page_title
FROM page
LEFT JOIN pagelinks
ON pl_title = page_title
AND pl_namespace = page_namespace
LEFT JOIN templatelinks
ON tl_title = page_title
AND tl_namespace = page_namespace
WHERE page_namespace = 4
AND page_is_redirect = 0
AND page_title LIKE "Articles_for_deletion/%"
AND ISNULL(pl_namespace)
AND ISNULL(tl_namespace);
''')

i = 1
output = []
for row in cursor.fetchall():
    page_title = u'{{pllh|1=Wikipedia:%s}}' % unicode(row[0], 'utf-8')
    table_row = u'''| %d
| %s
|-''' % (i, page_title)
    output.append(table_row)
    i += 1

cursor.execute('SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp) FROM recentchanges ORDER BY rc_timestamp DESC LIMIT 1;')
rep_lag = cursor.fetchone()[0]
current_of = (datetime.datetime.utcnow() - datetime.timedelta(seconds=rep_lag)).strftime('%H:%M, %d %B %Y (UTC)')

report = wikitools.Page(wiki, report_title)
report_text = report_template % (current_of, '\n'.join(output))
report_text = report_text.encode('utf-8')
report.edit(report_text, summary='[[Wikipedia:Bots/Requests for approval/Basketrabbit|Bot]]: Updated page.')

cursor.close()
conn.close()