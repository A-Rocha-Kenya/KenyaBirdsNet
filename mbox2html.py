#!/usr/bin/env python3
#
# Raphaël Nussbaumer
#
# Convert the KenyaBirdNet MBOX file to html file for the Archive (https://github.com/A-Rocha-Kenya/KenyaBirdsNet)
# 
# Script adapted from https://gist.github.com/frafra/43a50162d2f0ecce741379c940e40ec6

# External dependency
import jinja2 # Jinja2 syntax: http://jinja.pocoo.org/docs/dev/
import email.parser, email.policy
import mailbox
import os.path
import codecs
from dateutil.parser import parse
from slugify import slugify


# Html template for message page
template_page = jinja2.Template("""
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="icon" href="../arocha_old_logo_small.png" >
    <title>{{ Subject }}</title>
  </head>
  <body>
  <div><strong>From</strong>: {{ From }}</div>
  <div><strong>Date</strong>: {{ Date }}</div>
  <div><strong>Subject</strong>: {{ Subject }}</div>
  <hr/>
  {% if is_html %}
  {{ body|safe }}
  {% else %}
  <pre>{{ body }}</pre>
  {% endif %}
  {% if attachments %}
  <hr/>
  {% for att in attachments %}
  <img src="{{ att }}">
  {% endfor %}
  {% endif %}
</body>
</html>
""".strip(), trim_blocks=True, lstrip_blocks=True, autoescape=True)

# Html template for index page
template_index = jinja2.Template("""
<!DOCTYPE html>
<html>
<head>
<meta name="google-site-verification" content="RvJWoyJm1mDTIWs_SAiTSE4fEUcgCakVmAnuvtaisZ8" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<title>Kenya Birds Net Archive</title>
<link rel="icon" href="arocha_old_logo_small.png" >

<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
<script async src="https://cse.google.com/cse.js?cx=013832855720512177257:nug0eupgurc"></script>
<style>
    body                   { padding: 1.5rem; }
    .tableFixHead          { overflow-y: auto; height: 100px; }
    .tableFixHead thead th { position: sticky; top: 0; background: white;}
</style> 
</head>
<body>
<h2>Kenya Birds Net Archive</h2>
<div class="gcse-search"></div>
<table class="table table-bordered table-striped table-hover table-sm tableFixHead">
<thead>
    <tr><th scope="col">Subject</th><th scope="col">From</th><th scope="col">Date</th><th scope="col">Attachment</th></tr>
</thead>
<tbody> 
{{table}}
{% for i in index %}
  <tr>
  <td><a href="{{i.outfile}}">{{i.Subject}}</a></td>
  <td>{{i.From}}</td>
  <td nowrap>{{i.Date}}</td>
  <td align="center">{{i.attachments_str}}</td>
  </tr>
{% endfor %}
</tbody>
</table>
</body>
</html>
""".strip(), trim_blocks=True, lstrip_blocks=True, autoescape=True)

# Mailbox parser
inbox = mailbox.mbox("KenyaBirdsNet2002-2019.mbox")

# Test with attachment
# message = inbox.items()[555][1]

# Create the index structure
index = []

for u, message in inbox.items():
    info = {
        'attachments': []
        }
    # message_info = collections.defaultdict(dict)
    
    # Message parser
    msg_parser = email.parser.BytesFeedParser(policy=email.policy.default)
    msg_parser.feed(message.as_bytes())
    msg = msg_parser.close()
    if not [x[1] for x in msg.items() if x[0]=='Subject']:
        continue
    
    # Title
    info['From'] =  [x[1] for x in msg.items() if x[0]=='From'][0]
    d = parse([x[1] for x in msg.items() if x[0]=='Date'][0])
    info['Date'] =   d.strftime('%Y-%m-%d %H:%M')
    info['Subject'] =  [x[1] for x in msg.items() if x[0]=='Subject'][0]
    info['title'] =  info['Subject']
    
    # Header
    # info['header'] = msg.items()
    
    # Body
    simplest = msg.get_body(preferencelist=('html', 'plain'))
    info['is_html'] = simplest.get_content_type() == 'text/html'
    # soup = BeautifulSoup(simplest.get_content(), 'html.parser')
    info['body'] = simplest.get_content()
    
    # Do not include messages with less than 10 character
    if len(info['body'])<10:
        continue
    
    # Attachements
    for i in msg.iter_attachments(): 
        if (i.is_attachment()):
            # Only include if the attachement file is there
            if (os.path.isfile("Attachments/"+i.get_filename())):
                info['attachments'].append("../Attachments/"+i.get_filename())
            else:
                print("Attachments/"+i.get_filename())
    # Create attachement string for index
    info['attachments_str'] = '*' if len(info['attachments'])>0 else ''
    
    # filename
    info['outfile'] = 'Messages/' + slugify( d.strftime('%Y%m%d') + '-' + info['title'] ) + '.html'
    
    # Add to index 
    index.append(info)
    
    # Write file
    with codecs.open(info['outfile'], 'w', encoding='utf8') as f:
        f.write(template_page.render(info))

with codecs.open("index.html", 'w', encoding='utf8') as f:
    f.write(template_index.render({'index':index}))

# Write to file

# inbox.items()[555][1].as_string()

t = []
with codecs.open("sitemap.txt", 'w', encoding='utf8') as f:
    for u in index:
        f.write(u['outfile']+'\n')
