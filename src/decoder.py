import numpy as np
import logging
from itertools import *
from tabulate import tabulate

class ViterbiDecoder(object):

    def __init__(self, trn, feat):
        from collections import defaultdict as dd

        self.feat = feat

        self.states = dd(set)
        for sent in trn:
            wistates =  map(lambda x:int(x<0), sent['wiseq'])
            tseq = feat.tseqenc.transform([t for t in sent['tseq']])
            for (tprev,t), (wstate_prev, wstate) in zip(zip(tseq[1:],tseq), zip(wistates[1:], wistates)):
                indx = int(''.join(map(str,(wstate_prev,wstate))), 2)
                # states[(wstate_prev,wstate)].add((tprev,t))
                self.states[indx].add((tprev,t))
        self.transition_tensor = np.zeros((len(self.states.keys()), feat.NC, feat.NC)) + np.log(np.finfo(float).eps)
        for i, valids in self.states.iteritems():
            for k,l in valids:
                self.transition_tensor[i,k,l] = 1
        for i in range(self.transition_tensor.shape[0]):
            logging.debug(self.transition_tensor[i])

    def decode(self, sent, logprobs, debug=False):
        from viterbi import viterbi_log_multi
        to_indx = lambda wstate_prev, wstate: int(''.join(map(str,(wstate_prev,wstate))), 2)

        wistates =  map(lambda x:int(x<0), sent['wiseq'])
        tstates = list(imap(to_indx, [0]+wistates, wistates))
        emissions = map(lambda x:x[0], enumerate(sent['cseq']))
        tseq_ints = viterbi_log_multi(logprobs.T, self.transition_tensor, emissions, tstates)

        if debug:
            ddata = [sent['cseq']]
            ddata.extend(logprobs.T)
            ddata.extend([wistates,tstates,emissions])
            print tabulate(ddata, floatfmt='.2f')
        return tseq_ints

    def sanity_check(self, sent, tseq_ints):
        tseq = self.feat.tseqenc.inverse_transform(tseq_ints)
        if any(len(set(group)) != 1 for k, group in groupby(filter(lambda x: x>-1, zip(sent['wiseq'], tseq)))):
            return False
        sp_indxs = [i for i,wi in enumerate(sent['wiseq']) if wi == -1]
        if any(not (tseq[i-1] == tseq[i] == tseq[i+1]) for i in sp_indxs if tseq[i] != 'o'):
            return False
        return True

class MaxDecoder(object):

    def __init__(self, trn, feat):
        pass

    def decode(self, sent, logprobs, debug=False):
        return np.argmax(logprobs, axis=-1).flatten()

    def sanity_check(self, sent, tseq_ints):
        return True

def main():
    from utils import get_sents, sample_sents
    from encoding import any2io
    import featchar, rep

    import random
    from collections import defaultdict as dd
    trn, dev, tst = get_sents('eng')

    r = rep.Repstd()

    for sent in trn:
        sent['ts'] = any2io(sent['ts'])
        sent.update({
            'cseq': r.get_cseq(sent), 
            'wiseq': r.get_wiseq(sent), 
            'tseq': r.get_tseq(sent)})

    feat = featchar.Feat('basic')
    feat.fit(trn,dev,tst)

    vdecoder = ViterbiDecoder(trn, feat)

    sent = random.choice(filter(lambda x: len(x['cseq']) < 10 and len(x['cseq']) > 6, trn))
    randvals = np.random.rand(len(sent['cseq']),feat.NC)
    randlogprobs = np.log(randvals / np.sum(randvals,axis=0))
    tseq = vdecoder.decode(sent, randlogprobs, debug=True)
    print tseq

if __name__ == '__main__':
    main()