"""
Created: Aug 4, 2015: Wanted to replace the update_medges function with a dict
based routine. Idea is to receive the two arrays, gcoarr, gcnarr, convert them
both to dicts, do the searching and update the mtses. Convert the final dict to
a numpy array of two string and one np.ndarray.

Aug 5, 2015: The old logic of concatenating the names/nums did not work, so had
to change it to dict of dicts based idea. Want to find out why that concatenate
logic is not working, but going to hold that out.

Added another version of update_medges_1p exclusively for one process based
calls. Probably all that process set up and everything are adding to the memory
fluff for memory profiling.

Aug 6, 2015: was using an extra set of square brackets when assigning the
remaining elements of newarr to outarr. removed them from both the functions.
"""
import time
import numpy as np
from pympler.asizeof import asizeof
import bisect

@profile
def update_medges_dict(oldarr, newarr):
    """
    convert new array which will be searched to a dict and use a sequential loop
    to go over each old entries to update them. Store the id location of the new
    entries along with mts in the new dict avatar.
    """
    st1=time.time()
    reqspace = newarr.shape[0]
    print 'gcn shape:{0} gco shape:{1}'.format(reqspace, oldarr.shape[0])
    newdict={}
    for idrec, rec in enumerate(newarr):
        if rec[0] in newdict:
            newdict[rec[0]][rec[1]] = (rec[2], idrec)
        else:
            newdict[rec[0]] = { rec[1]:(rec[2],idrec) }
#        newdict[rec[0]+rec[1]]=(rec[2], idrec) #need this id for final extraction
    outarr = np.empty(reqspace, dtype=[('fperson', np.object),\
                                       ('sperson', np.object),\
                                       ('mts', np.ndarray)])
    oldextras=[]
    new_in_old=[]
    outid = 0
    #go over each of the old entries 
    for idrec, rec in enumerate(oldarr):
#        tosearchid = rec[0] + rec[1]
        if rec[0] in newdict:
            tempdict = newdict[rec[0]]
            if rec[1] in tempdict:
                (tempmts, tempnewid) = tempdict[rec[1]]
                new_in_old.append(tempnewid)
                oldmts = rec[2][:]
                outarr[outid]=(rec[0], rec[1],np.vstack((oldmts, tempmts))[:]) 
                outid = outid + 1
            else:
                oldextras.append(idrec)
        else:
            oldextras.append(idrec)
    print 'extra tuples in old g:', len(oldextras)
    print 'outarr shape:', outarr.shape
    only_new = set(xrange(reqspace))-set(new_in_old)
    print 'only_new:', len(only_new), 'new_in_old:', len(new_in_old)
    assert len(only_new)+len(new_in_old) == reqspace,\
            "count mismatch in update_medges_dict"
    outarr[outid:] = newarr[list(only_new)]
    print 'time for update_medges_dict: {0:.3f} seconds'.\
            format(time.time()-st1)
    final_asizeof = asizeof(newdict)+\
            asizeof(oldarr)+asizeof(newarr)+\
            asizeof(oldextras)+\
            asizeof(new_in_old)+\
            asizeof(only_new)+asizeof(outarr)
    print 'final asizeof', final_asizeof
    return outarr[:]
##########################################
def search_person_1p(oldpersons, gcnarr_names):
    gcn_farr, gcn_sarr = gcnarr_names
    target_length = len(gcn_farr)
    retlist=[]
    #revise the search logic based on the assumption 
    #that fperson < sperson. The lists gcoarr and gcnarr are constructed
    #such that this relation is true
    for oldid, (oldfperson, oldsperson) in oldpersons:
        in_newid = -1
        new_pos = bisect.bisect_left(gcn_farr, oldfperson) 
        found_sperson = False
        try:
            while gcn_farr[new_pos] == oldfperson:
                if gcn_sarr[new_pos] == oldsperson:
                    found_sperson = True
                    break
                new_pos = new_pos+1
            if found_sperson:
                in_newid = new_pos
        except IndexError:
            #person pair not found in the new month
            print 'bisect failed : {0} {1} {2} {3}'.\
                    format(new_pos, target_length, oldfperson, oldsperson)
        retlist.append((oldid, in_newid))
        #extras are separated based on -1
    return retlist
#######################
@profile
def update_medges_1p(gcoarr, gcnarr):
    st1=time.time()
    inds = np.argsort(gcnarr['fperson'])
    np.take(gcnarr, inds, out=gcnarr)
    reqspace = gcnarr.shape[0]
    gcocount = gcoarr.shape[0]
    print 'gcn shape:{0} gco shape:{1}'.format(reqspace, gcocount)
    old_fpersons = gcoarr['fperson']
    old_spersons = gcoarr['sperson']
    gcnfarr = gcnarr['fperson']
    gcnsarr = gcnarr['sperson']
    old_in_new = []
    extras = [] #diffCC old people joined by a new node in the current yr
    old_persons = zip(xrange(gcocount), zip(old_fpersons, old_spersons))
    print 'one elem:', old_persons[0]
    procs = []
    old_new_innew=[]
#    old_new_innew = search_person_1p(oldpersons, (gcn_farr, gcn_sarr)))
    #insert search person function here
    for oldid, (oldfperson, oldsperson) in old_persons:
        in_newid = -1
        new_pos = bisect.bisect_left(gcnfarr, oldfperson) 
        found_sperson = False
        try:
            while gcnfarr[new_pos] == oldfperson:
                if gcnsarr[new_pos] == oldsperson:
                    found_sperson = True
                    break
                new_pos = new_pos+1
            if found_sperson:
                in_newid = new_pos
        except IndexError:
            #person pair not found in the new month
            print 'bisect failed : {0} {1} {2} {3}'.\
                    format(new_pos, target_length, oldfperson, oldsperson)
        old_new_innew.append((oldid, in_newid))
    print 'old_new_innew:', old_new_innew[0]
    temppersontups = np.array(old_new_innew,\
                            dtype=[('oldid',np.int64),('newid',np.int64)])
    extras = temppersontups[temppersontups['newid']==-1]['oldid']
    print 'extra tuples in old g', extras.shape[0]
    old_in_new = list(temppersontups[temppersontups['newid']!=-1])
    new_in_old = zip(*old_in_new)[1]
    only_new = set(xrange(reqspace))-set(new_in_old)
    print 'new count:only_new:{0} old_in_new:{1}'.\
            format(len(only_new),len(old_in_new))
    assert len(only_new)+len(old_in_new) == reqspace, \
            "count mismatch in update_medges"
    outarr = np.empty(reqspace, dtype=[('fperson', np.object),\
                                       ('sperson', np.object),\
                                       ('mts', np.ndarray)] )
    outid = 0
    for oldid, newid in old_in_new:
        assert gcoarr[oldid][2]!=None, "gcoarr_mts cannot be none"
        fperson = gcnarr[newid][0]
        sperson = gcnarr[newid][1]
        old_mts = gcoarr[oldid][2]
        new_mts = gcnarr[newid][2]
        outarr[outid] = (fperson, sperson,\
                         np.vstack((old_mts, new_mts))[:])
        outid = outid + 1
    assert outid == len(old_in_new)
    outarr[outid:reqspace] = gcnarr[list(only_new)]
    print 'time for update medges_1p: {0:.3f} seconds'.format(time.time()-st1)
    final_asizeof = asizeof(old_fpersons)+asizeof(old_spersons)+\
            asizeof(gcoarr)+asizeof(gcnarr)+\
            asizeof(old_persons)+asizeof(old_new_innew)+\
            asizeof(temppersontups)+asizeof(extras)+\
            asizeof(old_in_new)+asizeof(new_in_old)+\
            asizeof(only_new)+asizeof(outarr)+asizeof(inds)
    print 'final asizeof', final_asizeof
    return outarr[:]
###################
