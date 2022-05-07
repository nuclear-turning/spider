import codecs

def get_journal_name():
    with codecs.open('../input_data/journal.txt',encoding='utf8') as f:
        return f.read().splitlines()

def get_source_id():
    with codecs.open('../input_data/sno.txt',encoding='utf8') as f:
        return f.read().splitlines()