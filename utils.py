import copy
from itertools import *
import random, numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder

def read_sents(file):
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

def get_sents():
    return read_sents('data/train.bilou'), read_sents('data/testa.bilou'), read_sents('data/testb.bilou')

def get_cfeatures(wi, ci, sent):
    return {'c':sent['cseq'][ci]}

def sent2mat(sents, dvec, le):
    XL, yL = [],[]
    for sent in sents:
        # Xsent = dvec.transform(get_features(i,sent,c) for i in range(len(sent['ws'])))
        Xsent = dvec.transform(get_features(i, sent, c) for (i,w) in enumerate(sent['ws']) for c in w)
        ysent = le.transform([sent['ts'][i] for (i,w) in enumerate(sent['ws']) for c in w])
        XL.append(Xsent)
        yL.append(ysent)
    return XL, yL

def dset2mat(sents, dvec, le):
    XL, yL = [],[]
    for sent in sents:
        # Xsent = dvec.transform(get_features(i,sent,c) for i in range(len(sent['ws'])))
        Xsent = dvec.transform(get_features(i, sent, c) for (i,w) in enumerate(sent['ws']) for c in w)
        ysent = le.transform([sent['ts'][i] for (i,w) in enumerate(sent['ws']) for c in w])
        XL.append(Xsent)
        yL.append(ysent)
    return XL, yL
    pass

def extend_sent2(sent):
    cseq, tseq, wiseq = [], [], []
    wi = 0
    for w, t in zip(sent['ws'], sent['ts']):
        if t == 'O': tp, ttype = 'O', 'O'
        else: tp, ttype = t.split('-')
        if ttype == 'ORG': ttype = 'G' + ttype
        ttype = ttype[0].lower()

        cseq.extend([c for c in w+' '])
        wiseq.extend([wi for c in w+' '])
        wi+=1
        if tp == 'U':
            for c in w:
                tseq.append(ttype)
            tseq.append(ttype+'-l')
        elif tp == 'B':
            for c in w:
                tseq.append(ttype)
            tseq.append(ttype)
        elif tp == 'L':
            for c in w:
                tseq.append(ttype)
            tseq.append(ttype+'-l')
        elif tp == 'I':
            for c in w:
                tseq.append(ttype)
            tseq.append(ttype)
        else: # O
            for c in w:
                tseq.append(ttype)
            tseq.append(ttype+'-l')
    sent['cseq'] = cseq
    sent['tseq'] = tseq
    sent['wiseq'] = wiseq

def extend_sent(sent):
    cseq, tseq, wiseq, ciseq = [], [], [], []
    wi, ci = 0, 0
    for w, t in zip(sent['ws'], sent['ts']):
        if t == 'O': tp, ttype = 'O', 'O'
        else: tp, ttype = t.split('-')
        # ttype = ttype[0]

        cseq.extend([c for c in w])
        wiseq.extend([wi for c in w])
        cseq.append(' ') # for space
        wiseq.append(-1) # for space
        # wiseq.append(wi) # for space
        wi+=1
        if tp == 'U':
            if len(w) > 1:
                tseq.append('b-'+ttype)
                for c in w[1:-1]:
                    tseq.append('i-'+ttype)
                tseq.append('l-'+ttype)
            else:
                tseq.append('u-'+ttype)
            tseq.append('o') # for space
        elif tp == 'B':
            tseq.append('b-'+ttype)
            for c in w[1:]:
                tseq.append('i-'+ttype)
            tseq.append('i-'+ttype) # for space
        elif tp == 'L':
            for c in w[:-1]:
                tseq.append('i-'+ttype)
            tseq.append('l-'+ttype)
            tseq.append('o') # for space
        elif tp == 'I':
            for c in w:
                tseq.append('i-'+ttype)
            tseq.append('i-'+ttype) # for space
        else: # O
            for c in w:
                tseq.append('o')
            tseq.append('o') # for space
    sent['cseq'] = cseq[:-1]
    sent['tseq'] = tseq[:-1]
    sent['wiseq'] = wiseq[:-1]

def get_sent_indx(dset):
    start = 0
    indexes = []
    for sent in dset:
        indexes.append((start,start+len(sent['cseq'])))
        start += len(sent['cseq'])
    return indexes

def main():
    trn, dev, tst = get_sents()
    trn = random.sample(trn,1000)
    dev = random.sample(trn,100)

    for d in (trn,dev,tst):
        for sent in d:
            extend_sent2(sent)

    dvec = DictVectorizer(dtype=np.float32, sparse=False)
    lblenc = LabelEncoder()
    dvec.fit(get_cfeatures(wi, ci, sent)  for sent in trn for c,wi,ci in zip(sent['cseq'],sent['wiseq'],count(0)))
    lblenc.fit([t for sent in trn for t in sent['tseq']])
    print dvec.get_feature_names()
    print lblenc.classes_

    nf = len(dvec.get_feature_names())
    nc = len(lblenc.classes_)
    print '# of sents: ', map(len, (trn,dev,tst))
    print '# of feats: ', nf 
    print '# of lbls: ', nc

    Xtrn = dvec.transform(get_cfeatures(wi, ci, sent)  for sent in trn for c,wi,ci in zip(sent['cseq'],sent['wiseq'],count(0)))
    Xdev = dvec.transform(get_cfeatures(wi, ci, sent)  for sent in dev for c,wi,ci in zip(sent['cseq'],sent['wiseq'],count(0)))
    Xtst = dvec.transform(get_cfeatures(wi, ci, sent)  for sent in tst for c,wi,ci in zip(sent['cseq'],sent['wiseq'],count(0)))

    print Xtrn.shape, Xdev.shape

    ytrn = lblenc.transform([t for sent in trn for t in sent['tseq']])
    ydev = lblenc.transform([t for sent in dev for t in sent['tseq']])
    ytst = lblenc.transform([t for sent in tst for t in sent['tseq']])

    print ytrn.shape, ydev.shape

    trnIndx = get_sent_indx(trn)
    devIndx = get_sent_indx(dev)
    tstIndx = get_sent_indx(tst)

    print len(trnIndx), len(devIndx)

def tseq2ts(sent):
    cindx = [[t[1] for t in g] for k,g in groupby(izip(sent['wiseq'],count(0)),lambda x:x[0]) if k!=-1]
    assert len(sent['ws']) == len(cindx)
    tcseq = [[sent['tpredseq'][i] for i in ind] for ind in cindx]
    ts = []
    for tseq in tcseq:
        ttype = tseq[0].split('-')[1] if '-' in tseq[0] else 'O'  # different decision can be used
        if tseq[0].startswith('b') and tseq[-1].startswith('i'):
            ts.append('B-'+ttype)
        elif tseq[0].startswith('i') and tseq[-1].startswith('i'):
            ts.append('I-'+ttype)
        elif tseq[0].startswith('i') and tseq[-1].startswith('l'):
            ts.append('L-'+ttype)
        elif tseq[0].startswith('b') and tseq[-1].startswith('l') or tseq[0].startswith('u'):
            ts.append('U-'+ttype)
        elif len(tseq)==1 and tseq[0].startswith('l'):
            ts.append('L-'+ttype)
        elif len(tseq)==1 and tseq[0].startswith('b'):
            ts.append('B-'+ttype)
        else:
            ts.append('O')
    return ts

if __name__ == '__main__':
    trn, dev, tst = get_sents()
    sent = random.choice(trn)
    extend_sent(sent)
    print '\t'.join(sent['cseq'])
    print '\t'.join(sent['tseq'])
    print '\t'.join(map(str,sent['wiseq']))
    print map(len,[sent['cseq'], sent['tseq'], sent['wiseq']])
    print tseq2ts(sent)
    print sent['ts']