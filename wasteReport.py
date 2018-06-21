#!/usr/bin/python

from subprocess import Popen,PIPE
from collections import defaultdict
import argparse
import pwd
import grp


def mkSecond(timeStr):
    timeList=timeStr.split('-')

    if len(timeList)==2:
        day=int(timeList.pop(0))
    else:
        day=0

    shortTimeList=timeList[0].split(':')
    if len(shortTimeList)==2:
        hour=0
        min=int(shortTimeList[0])
        sec=int(round(float(shortTimeList[1])))
    else:
        hour=int(shortTimeList[0])
        min=int(shortTimeList[1])
        sec=int(shortTimeList[2])

    return day*24*3600+hour*3600+min*60+sec

class Job():
    def __init__(self,jobdata):
        #JobID,UID,GID,Account,CPUTimeRAW,TotalCPU
        (self.jobid,self.uid,self.gid,self.account,self.partition,self.cputimeraw,self.totalcpu)=jobdata

        try:
            self.uid=int(self.uid)
        except ValueError:
            print("WARN: Job {0}: Invalid userid: {1}".format(self.jobid,self.uid))
            self.uid=0

        self.gid=int(self.gid)
        self.cputimeraw=int(self.cputimeraw)
        try:
            self.totalcpu=mkSecond(self.totalcpu)
        except ValueError:
            print("WARN: Job {0}: Couldn't convert TotalCPU time string into seconds: {1}".format(self.jobid,self.totalcpu))
            self.totalcpu=0

        self.user=pwd.getpwuid(self.uid).pw_name
        self.group=grp.getgrgid(self.gid).gr_name


class Jobstore(object):
    """Store all jobs and prepare stats."""
    def __init__(self):
        self.jobList=[]

    def add(self,jobdata):
        self.job=Job(jobdata)
        self.jobList.append(self.job)

    def getStat(self,keyName):

        self.resStat=defaultdict(lambda:defaultdict(int))

        for self.j in self.jobList:
            self.id=getattr(self.j,keyName)
            self.resStat[self.id]['CPUTimeRAW']+=self.j.cputimeraw
            self.resStat[self.id]['TotalCPU']+=self.j.totalcpu
            self.resStat[self.id]['JOBCNT']+=1

        for self.r in self.resStat.keys():
            #print("{} : {}".format(self.resStat[self.r],self.resStat[self.r]['CPUTimeRAW']))
            if self.resStat[self.r]['CPUTimeRAW']==0:
                self.resStat[self.r]['LostSeconds']=0
                self.resStat[self.r]['Efficiency']=0
            else:
                self.resStat[self.r]['LostSeconds']=self.resStat[self.r]['CPUTimeRAW']-self.resStat[self.r]['TotalCPU']
                self.resStat[self.r]['Efficiency']=self.resStat[self.r]['TotalCPU']*100/float(self.resStat[self.r]['CPUTimeRAW'])

        return self.resStat


if __name__ == "__main__":
    helpText="""FILTER := accounts=account_list
          gid=gid_list
          group=group_list
          jobs=job(.step)
          name=jobname_list
          nnodes=N
          nodelist=node_list
          uid=uid_list
          user=user_list
          (for details see 'man sacct')"""
    parser = argparse.ArgumentParser(description='Create slurm job report',epilog=helpText,formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--uid", help="Report uid",action="store_const",const="uid",dest="statKey")
    group.add_argument("-n", "--user", help="Report user",action="store_const",const="user",dest="statKey")
    group.add_argument("-g", "--gid", help="Report gid",action="store_const",const="gid",dest="statKey")
    group.add_argument("-gn", "--group", help="Report group",action="store_const",const="group",dest="statKey")
    group.add_argument("-a", "--account", help="Report account",action="store_const",const="account",dest="statKey")
    group.add_argument("-p", "--partition", help="Report partition",action="store_const",const="partition",dest="statKey")
    parser.add_argument("-s", "--starttime", help="Start date")
    parser.add_argument("-e", "--endtime", help="End date")
    parser.add_argument("-o", "--order", help="Sort key [LostSeconds|Efficency]",default="LostSeconds")
    parser.add_argument("-r", "--reverse", help="reverse sort order",action="store_true")
    parser.add_argument("-f", "--filter", help="add filter term")

    args = parser.parse_args()

    #sacct --parsable2 --noheader --format jobid,uid,AllocCPUs,CPUTime,Elapsed --starttime 00:00
    cmdList=["sacct","--parsable2","--noheader","--state=COMPLETED","--format","JobID,UID,GID,Account,Partition,CPUTimeRAW,TotalCPU"]
    if args.starttime:
        cmdList.append("--starttime={}".format(args.starttime))
    if args.endtime:
        cmdList.append("--endtime={}".format(args.endtime))
    if args.filter:
        cmdList.append("--{}".format(args.filter))

    p1 = Popen(cmdList,stdout=PIPE)
    (stdout,stderr)=p1.communicate()

    jobs=Jobstore()
    for line in stdout.split('\n'):
        l=line.strip()

        if len(l)==0:
            continue

        try:
            jobLine=l.split('|')
        except:
            continue

        # first field is the job id. jobid with dots are sub jobs
        if '.' in jobLine[0]:
            continue

        jobs.add(jobLine)

    resHash=jobs.getStat(args.statKey)
    for u in sorted(resHash,key=lambda x: resHash[x][args.order],reverse=args.reverse):
        print("{0}:{1},Efficiency:{2:.1f}%,LostSeconds:{3}".format(args.statKey,u,resHash[u]['Efficiency'],resHash[u]['LostSeconds']))

