#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# create by: Massimo Di Pierro<mdipierro@cs.depaul.edu>
# license: GPL2.0

from optparse import *
import re, urllib, csv, math
import os, tempfile, random, cStringIO

usage = "python qcdutils_plot.py\n" \

version = "qcdutils_plot 1.0\n" \
          "  Copyright (c) 2011 Massimo Di Pierro\n" \
	  "  All rights reserved\n" \
          "  License: GPL 2.0\n\n" \
	  "  Written by Massimo Di Pierro <mdipierro@cs.depaul.edu>\n"

description = "plot the output of qcdutils.py"

try:
    os.environ['MPLCONfigureDIR'] = tempfile.mkdtemp()
except:
    pass
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse

def E(f,data):
    return sum(f(x) for x in data)/len(data)

def save_figure(figure,filename):
    canvas=FigureCanvas(figure)
    if not filename:
        stream=cStringIO.StringIO()
        canvas.print_png(stream)
        return stream.getvalue()
    else:
        stream = open(filename,'wb')
        canvas.print_png(stream)
        try: stream.close()
        except: pass
        return filename

def hist(title='',xlab='x',ylab='y',nbins=20,
         data=[1,2,3,3,4,5,5,6,7,7,8,2,3,4,3,4,6],
         filename='image.png',gaussian_fit=True):
    figure=Figure(frameon=True)
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    ell=axes.hist(data,nbins)
    if gaussian_fit:
        mu = E(lambda x:x,data)
        var = E(lambda x:(x-mu)**2,data)
        a,b=min(data),max(data)
        x = [(a+(b-a)/nbins*i) for i in range(nbins+1)]
        norm = len(data)/math.sqrt(2.0*math.pi*var)
        y = [norm*math.exp(-(p-mu)**2/(0.5*var)) for p in x]
        axes.plot(x,y,linewidth="2",color="r")
    return save_figure(figure,filename)

def qqplot(title='',xlab='x',ylab='y',nbins=20,
           data=[1,2,3,3,4,5,5,6,7,7,8,2,3,4,3,4,6],
           filename='image.png'):
    figure=Figure(frameon=True)
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    mu = E(lambda x:x,data)
    var = E(lambda x:(x-mu)**2,data)
    sd = math.sqrt(var)
    # y = [norm*math.exp(-(p-mu)**2/(0.5*var)) for p in x]
    y = [x for x in data]
    y.sort()
    cdf1, cdf2 = [0.0], [0.0]
    for x in y:
        cdf1.append(cdf1[-1]+x)
        #cdf1.append(0.5-math.erf((x-mu)/sd)/2)
        cdf2.append(cdf1[-1]+x)
    axes.plot(cdf1,cdf2,linewidth="0")
    extremes=[cdf2[0],cdf2[-1]]
    axes.plot(extremes,extremes,linewidth="1")
    return save_figure(figure,filename)

def plot(title='',xlab='x',ylab='y',
         data={'xxx':[(0,0),(1,1),(1,2),(3,3)],
               'yyy':[(0,0,.2),(2,1,0.2),(2,2,0.2),(3,3,0.2)]},
         filename='image.png'):
    figure=Figure(frameon=True)
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    keys=sorted(data)
    for key in keys:
        stream = data[key]
        (x,y)=([],[])
        yerr = []
        for point in stream:
            x.append(point[0])
            y.append(point[1])
            if len(point)==3:
                yerr.append(point[2])
        if len(yerr)==len(x):
            axes.errorbar(x, y, yerr=yerr, fmt='o', linewidth="1")
        else:
            ell=axes.plot(x, y, linewidth="2")
    return save_figure(figure,filename)

def color2d(title='',xlab='x',ylab='y',
            data=[[1,2,3,4],[2,3,4,5],[3,4,5,6],[4,5,6,7]],
            filename='image.png'):
    figure=Figure(frameon=True)
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    image=axes.imshow(data)
    image.set_interpolation('bilinear')
    return save_figure(figure,filename)

def scatter(title='',xlab='x',ylab='y',
            data=None,filename='image.png'):
    if data==None:
        r=random.random
        data=[(r()*10,r()*10,r(),r(),r(),r(),r()) for i in range(100)]
    figure=Figure(frameon=True)
    figure.set_facecolor('white')
    axes=figure.add_subplot(111)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    for i,p in enumerate(data):
        p=list(p)
        while len(p)<4: p.append(0.01)
        e=Ellipse(xy=p[:2],width=p[2],height=p[3])
        axes.add_artist(e)
        e.set_clip_box(axes.bbox)
        e.set_alpha(0.5)
        if len(p)==7:
            e.set_facecolor(p[4:])
        data[i]=p
    axes.set_xlim(min(p[0]-p[2] for p in data), max(p[0]+p[2] for p in data))
    axes.set_ylim(min(p[1]-p[3] for p in data), max(p[1]+p[3] for p in data))
    return save_figure(figure,filename)

def test():
    plot(data=dict(set1=[(x,x**2,2.0*x) for x in range(10)]))

if __name__=='__main__':
    test()


def clean(text):
    return re.sub('\s+','',text.replace('/','_div_'))

class IPlot:
    def __init__(self,filename,items=[],
                 raw=False,
                 autocorrelations=False,
                 trails=False,
                 bootstrap_samples=False,
                 plot_range=(None,None)):
        if raw:
            self.plot_raw_data(filename+'_raw_data.csv')
        if autocorrelations:
            self.plot_autocorrelations(filename+'_autocorrelations.csv')
        if trails:
            self.plot_trails(filename+'_trails.csv')
	if bootstrap_samples:
            self.plot_samples(filename+'_samples.csv')
	self.plot_min_mean_max(filename+'_min_mean_max.csv',items,plot_range)

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
            filename2 = filename[:-4]+'_%s_qq.png' % clean(tag)
            print filename2
            qqplot(data = items[1:],
                   xlab='gaussian',ylab=tag,filename = filename2)            
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


    def plot_min_mean_max(self,filename,xlab=None,plot_range=(None,None)):
        print 'plotting summary with error bars (%s)...' % ','.join(xlab)
	lines=list(csv.reader(open(filename,'r'),
                              delimiter=',',quoting=csv.QUOTE_NONNUMERIC))
	tags=lines[0] 
	if not xlab or xlab[0]=='': xlab=tags[1:-3]
	index=0
	for tag in tags:
	    if tag[0]=='[': break
	sets={}
        min_t,max_t = plot_range 
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
           if (min_t==None or t>=min_t) and  (max_t==None or t<max_t):
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
    parser.add_option('-i','--input_prefix',default='qcdutils',dest='input_prefix',
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
    parser.add_option('-R','--range',default=':',dest='range',
		      help='range as in 0:1000')
    parser.add_option('-f','--fit',default=[],dest='fits',
		      action='append',
		      help='fits to be performs on results')
    (options, args) = parser.parse_args()
    if options.fits:
	print 'sorry -f not implemented yet!'
    def parse_range(x):
        a,b = x.split(':')
        a,b = (float(a) if a else None,float(b) if b else None)
        return (a,b)
    plot=IPlot(options.input_prefix,options.plot_variables.split(','),
               raw=options.raw,
               autocorrelations=options.autocorrelations,
               trails=options.trails,
               bootstrap_samples=options.bootstrap_samples,
               plot_range = parse_range(options.range))

if __name__=='__main__': shell_iplot()
