from optparse import *
from qcdutils_mpl import plot, hist
import re, urllib, csv, math

usage = "python qcdutils_plot.py\n" \

version = "qcdutils_plotv1.0\n" \
          "  Copyright (c) 2007 Massimo Di Pierro\n" \
	  "  All rights reserved\n" \
          "  License: GPL 2.0\n\n" \
	  "  Written by Massimo Di Pierro <mdipierro@cs.depaul.edu>\n"

description = "plot the output of ibootstrap.py"

def clean(text):
    return re.sub('\s+','',text.replace('/','_div_'))

class IPlot:
    def __init__(self,filename,items=[],
                 raw=False,
                 autocorrelations=False,
                 trails=False,
                 bootstrap_samples=False):
        if raw:
            self.plot_raw_data(filename+'_raw_data.csv')
        if autocorrelations:
            self.plot_autocorrelations(filename+'_autocorrelations.csv')
        if trails:
            self.plot_trails(filename+'_trails.csv')
	if bootstrap_samples:
            self.plot_samples(filename+'_samples.csv')
	self.plot_min_mean_max(filename+'_min_mean_max.csv',items)

    def plot_raw_data(self,filename):
        print 'plotting raw data...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag = items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            plot(data = {'':[point for point in enumerate(items[1:])]},
                 xlab='step',ylab=tag,filename = filename2)
            filename2 = filename[:-4]+'_%s_hist.png' % clean(tag)
            print filename2
            hist(data = items[1:],
                 xlab=tag,ylab='frequency',filename = filename2)            
            # mu=E(lambda x:x,data)
            # sd=math.sqrt(E(lambda x:(x-mu)**2,data))

    def plot_autocorrelations(self,filename):
        print 'plotting autocorrelations...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag = items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            plot(data = {'':[point for point in enumerate(items[1:])]},
                 xlab='step',ylab=tag,filename = filename2)
            
    def plot_trails(self,filename):
        print 'plotting moving averages (trails)...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag = items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            plot(data = {'':[point for point in enumerate(items[1:])]},
                 xlab='step',ylab=tag,filename = filename2)

    def plot_samples(self,filename):
        print 'plotting bootstrap samples...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag= items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            hist(data = items[1:],
                 xlab=tag,ylab="frequency",filename=filename2)


    def plot_min_mean_max(self,filename,xlab=['t']):
        print 'plotting summary with error bars (%s)...' % ','.join(xlab)
	lines=list(csv.reader(open(filename,'r'),
                              delimiter=',',quoting=csv.QUOTE_NONNUMERIC))
	tags=lines[0] 
	if not xlab or xlab[0]=='': xlab=[tags[1]]
	index=0
	for tag in tags:
	    if tag[0]=='[': break
	sets={}
	for items in lines[1:]:
	   tag, data = items[0], items[1:]       
	   legend=""
	   for i in range(1,len(tags)-3):
	       if not tags[i] in xlab:
                   legend+="%s=%g " % (tags[i],data[i-1])
	   if not sets.has_key(legend):
	       points=sets[legend]=[]
	   else:
	       points=sets[legend]
	   t=data[index]
           x,yminus,y,yplus = t, data[-3],data[-2],data[-1]
           points.append((t,y,0.5*(yplus-yminus)))
	for legend in sets.keys():
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            plot(data = {legend:sets[legend]},
                 xlab=tags[index+1],ylab=tags[0],filename = filename2)
  
def shell_iplot():
    parser=OptionParser(usage,None,Option,version)
    parser.description=description
    parser.add_option('-i','--input_prefix',default='ibootstrap',dest='input_prefix',
		      help='the prefix used to build input filenames')
    parser.add_option('-r','--raw',action='store_true',
                      default=False,dest='raw',
		      help='make raw data plots')
    parser.add_option('-a','--autocorrelations',action='store_true',
                      default=False,dest='autocorrelations',
		      help='make autocorrelation plots')
    parser.add_option('-t','--trails',action='store_true',
                      default=False,dest='trails',
		      help='make trails plots')
    parser.add_option('-b','--bootstrap-samples',action='store_true',
                      default=False,dest='bootstrap_samples',
		      help='make bootstrap samples plots')
    parser.add_option('-v','--plot_variables',default='',dest='plot_variables',
		      help='plotting variables')
    parser.add_option('-f','--fit',default=[],dest='fits',
		      action='append',
		      help='fits to be performs on results')
    (options, args) = parser.parse_args()
    if options.fits:
	print 'sorry -f not implemented yet!'
    plot=IPlot(options.input_prefix,options.plot_variables.split(','),
               raw=options.raw,
               autocorrelations=options.autocorrelations,
               trails=options.trails,
               bootstrap_samples=options.bootstrap_samples)

if __name__=='__main__': shell_iplot()
