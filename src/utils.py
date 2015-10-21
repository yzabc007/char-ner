import os
import copy
from itertools import *
import random

import encoding

__author__ = 'Onur Kuru'
file_abspath = os.path.abspath(__file__)
ROOT_DIR = os.path.abspath(os.path.join(file_abspath, os.pardir, os.pardir))
DATA_DIR = '{}/data'.format(ROOT_DIR)
SRC_DIR = '{}/src'.format(ROOT_DIR)
SCRIPTS_DIR = '{}/scripts'.format(ROOT_DIR)

WSTART = '/w'
WEND = 'w/'

def valid_file_name(s):
    return "".join(i for i in s if i not in "\"\/ &*?<>|[]()'")

def read_sents_eng(file):
    a,b,c,d = [],[],[],[]
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                w, pt, ct, t = l.strip().split('\t')
                a.append(w);b.append(pt);
                c.append(ct);d.append(t);
            else: # emtpy line
                if len(a):
                    sentences.append({'ws':a,'ts':d,'tsg':copy.deepcopy(d),\
                            'pts':b,'cts':c})
                a,b,c,d = [],[],[],[]
    return sentences

def get_sents(lang='eng'):
    readfunc = globals()['read_sents_'+lang]
    if lang in ('spa','ned','arb','cze','tr'):
        return map(readfunc, ['{}/{}/{}.bio'.format(DATA_DIR,lang,dset) for dset in ('train','testa','testb')])
    else:
        return map(readfunc, ['{}/{}/{}.iob'.format(DATA_DIR,lang,dset) for dset in ('train','testa','testb')])

def read_sents_deu(file):
    a,b,c,d,e = [],[],[],[], []
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                w, lem, pt, ct, t = l.strip().split('\t')
                a.append(w);b.append(pt);
                c.append(ct);d.append(t);e.append(lem)
            else: # emtpy line
                if len(a):
                    sentences.append({'ws':a,'ts':d,'tsg':copy.deepcopy(d),\
                            'pts':b,'cts':c,'lems':e})
                a,b,c,d = [],[],[],[]
    return sentences

def read_sents_arb(file):
    a,b,c,d,e = [],[],[],[], []
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                w, t = l.strip().split('\t')
                a.append(w); d.append(t)
            else: # emtpy line
                if len(a):
                    d = encoding.bio2iob(d)
                    sentences.append({'ws':a,'ts':d})
                a,b,c,d = [],[],[],[]
    return sentences

def read_sents_tr(file):
    a,b,c,d,e = [],[],[],[], []
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                w, t = l.strip().split('\t')
                a.append(w); d.append(t)
            else: # emtpy line
                if len(a):
                    d = encoding.bio2iob(d)
                    sentences.append({'ws':a,'ts':d})
                a,b,c,d = [],[],[],[]
    return sentences

def read_sents_dse(file):
    a,b,c,d = [],[],[],[]
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                try:
                    w, pt, t = l.strip().split('\t')
                except:
                    print l
                    assert False
                a.append(w);b.append(pt);d.append(t);
            else: # emtpy line
                if len(a):
                    d = encoding.bio2iob(d)
                    sentences.append({'ws':a,'ts':d,'tsg':copy.deepcopy(d),\
                            'pts':b})
                a,b,c,d = [],[],[],[]
    return sentences

def read_sents_ned(file):
    a,b,c,d = [],[],[],[]
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                try:
                    w, pt, t = l.strip().split('\t')
                except:
                    print l
                    assert False
                a.append(w);b.append(pt);d.append(t);
            else: # emtpy line
                if len(a):
                    d = encoding.bio2iob(d)
                    sentences.append({'ws':a,'ts':d,'tsg':copy.deepcopy(d),\
                            'pts':b})
                a,b,c,d = [],[],[],[]
    return sentences

def read_sents_cze(file):
    a,b,c,d = [],[],[],[]
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                try:
                    w, lem, pt, t = l.strip().split('\t')
                except:
                    print l
                    assert False
                a.append(w);b.append(pt);d.append(t);
            else: # emtpy line
                if len(a):
                    d = encoding.bio2iob(d)
                    sentences.append({'ws':a,'ts':d,'tsg':copy.deepcopy(d),\
                            'pts':b})
                a,b,c,d = [],[],[],[]
    return sentences

def read_sents_spa(file):
    a,b,c,d = [],[],[],[]
    sentences = []
    with open(file) as src:
        for l in src:
            if len(l.strip()):
                w, pt, t = l.strip().split('\t')
                a.append(w);b.append(pt);d.append(t);
            else: # emtpy line
                if len(a):
                    d = encoding.bio2iob(d)
                    sentences.append({'ws':a,'ts':d,'tsg':copy.deepcopy(d),\
                            'pts':b})
                a,b,c,d = [],[],[],[]
    return sentences


def sample_sents(sents, n, min_ws_len=None, max_ws_len=None):
    pp = sents
    if min_ws_len: pp = ifilter(lambda x: len(x['ws']) >= min_ws_len, pp)
    if max_ws_len: pp = ifilter(lambda x: len(x['ws']) <= max_ws_len, pp)
    return random.sample(list(pp), n)

def get_sent_indx(dset):
    start = 0
    indexes = []
    for sent in dset:
        indexes.append((start,start+len(sent['cseq'])))
        start += len(sent['cseq'])
    return indexes

def get_sent_indx_word(dset):
    start = 0
    indexes = []
    for sent in dset:
        indexes.append((start,start+len(sent['ws'])))
        start += len(sent['ws'])
    return indexes

if __name__ == '__main__':
    trn,dev,tst = get_sents('dse')
    print 'total:', sum(any(1 for t in sent['ts'] if t.startswith('B')) for sent in chain(trn,dev,tst))

    print map(len, (trn,dev,tst))

    sents = sample_sents(trn,5,5,10)
    for sent in sents:
        print sent['ws']
        print sent['ts']
