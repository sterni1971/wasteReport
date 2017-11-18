# wasteReport
```
usage: wasteReport.py [-h] (-u | -n | -g | -gn | -a | -p) [-s STARTTIME]
                      [-e ENDTIME] [-o ORDER] [-r] [-f FILTER]

Create slurm job report

optional arguments:
  -h, --help            show this help message and exit
  -u, --uid             Report uid
  -n, --user            Report user
  -g, --gid             Report gid
  -gn, --group          Report group
  -a, --account         Report account
  -p, --partition       Report partition
  -s STARTTIME, --starttime STARTTIME
                        Start date
  -e ENDTIME, --endtime ENDTIME
                        End date
  -o ORDER, --order ORDER
                        Sort key [LostSeconds|Efficency]
  -r, --reverse         reverse sort order
  -f FILTER, --filter FILTER
                        add filter term

FILTER := accounts=account_list
          gid=gid_list
          group=group_list
          jobs=job(.step)
          name=jobname_list
          nnodes=N
          nodelist=node_list
          uid=uid_list
          user=user_list
          (for details see 'man sacct')
```
