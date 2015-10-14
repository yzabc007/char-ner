import argparse, subprocess
from utils import ROOT_DIR

STR = """#!/bin/bash
#$ -N exper
#$ -q all.q@{}
#$ -S /bin/bash
##$ -l h_rt=05:00:00 #how many mins run
#$ -pe smp {}
#$ -cwd
#$ -o /tmp/job.out
#$ -e /tmp/job.err
#$ -M okuru13@ku.edu.tr
#$ -m bea
 
source ~/setenv.sh
cd /mnt/kufs/scratch/okuru13/char-ner
MKL_NUM_THREADS={} THEANO_FLAGS=mode=FAST_RUN,device={},floatX=float32 python src/{}.py {}
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="creatjob")
    parser.add_argument("--p", type=bool, default=False, help='just print, dont submit') 
    parser.add_argument("--script", default='exper')
    parser.add_argument("--script_args", required=True) 
    parser.add_argument("--m", required=True, choices=\
            ['biyofiz-4-0','biyofiz-4-1','biyofiz-4-2','biyofiz-4-3','parcore-6-0']) 
    parser.add_argument("--d", required=True, choices=['gpu','cpu'])
    parser.add_argument("--smp", default=18, type=int)
    args = parser.parse_args()

    args.smp = 1 if args.d == 'gpu' else args.smp

    job_text = STR.format(args.m, args.smp, args.smp, args.d, args.script, args.script_args)
    print job_text

    if not args.p:
        proc = subprocess.Popen(
            'qsub',stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,shell=True)
        proc.stdin.write(job_text)
        proc.stdin.close()
        result = proc.stdout.read()
        proc.wait()
        print 'result:', result