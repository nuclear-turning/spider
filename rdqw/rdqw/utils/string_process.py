import json

def escape(subject):
    sub = json.dumps(subject).replace('"', '')
    sublist = ['%u' + s.upper() for s in sub.split('\\u') if s != '']
    return "||||%s||||||" %  ''.join(sublist)

def deescape(escape_str):
    es = escape_str.replace('|', '')
    str_list = ['\\u' + s.lower() for s in es.split('%u') if s != '']
    return ''.join(str_list).decode('unicode-escape')

def url_cat(querystring):
    url = '?'
    url_query = [q + '=' + querystring[q] for q in querystring]
    url += '&'.join(url_query)
    return url

def de_url_cat(url):
    str = url.split('?')[1]
    querystring = {}
    for s in str.split('&'):
        item = s.split('=')
        querystring[item[0]] = item[1]
    return querystring
