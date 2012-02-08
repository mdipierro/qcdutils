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

def draw(title='title',xlab='x',ylab='y',filename='tmp.png',
         linesets=None, pointsets=None, histsets=None, ellisets=None,
         xrange=None, yrange=None):
    figure = Figure(frameon=False)
    figure.set_facecolor('white')
    axes = figure.add_subplot(111)
    axes.grid(True)
    if title: axes.set_title(title)
    if xlab: axes.set_xlabel(xlab)
    if ylab: axes.set_ylabel(ylab)
    if xrange: axes.set_xlim(xrange)
    if yrange: axes.set_ylim(yrange)
    legend = [],[]

    for histset in histsets or []:
        data = histset['data']
        bins = histset.get('bins',20)
        color = histset.get('color','blue')
        q = axes.hist(data,bins, color=color)
        if 'legend' in histset:
            legend[0].append(q[0])
            legend[1].append(histset['legend'])
        if 'gaussian_fit' in histset:
            mu = sum(data)/len(data)
            var = sum((x-mu)**2 for x in data)/len(data)
            a,b = min(data),max(data)
            norm = (b-a)*len(data)/bins/math.sqrt(2.0*math.pi*var)
            v = [(a+(b-a)/bins*i) for i in range(bins+1)]
            data = [(x,norm*math.exp(-(x-mu)**2/(2.0*var))) for x in v]            
            if not linesets: linesets=[]
            linesets.append(dict(
                    legend='fit: mu=%.3g, sigma=%.3g' % (mu,math.sqrt(var)),
                    data = data,
                    color='red'))

    for lineset in linesets or []:
        data = lineset['data']
        color = lineset.get('color','black')
        linestyle = lineset.get('style','-')
        linewidth = lineset.get('width',2)
        x = [p[0] for p in data]
        y = [p[1] for p in data]
        q = axes.plot(x, y, linestyle=linestyle,
                      linewidth=linewidth, color=color)
        if 'legend' in lineset:
            legend[0].append(q[0])
            legend[1].append(lineset['legend'])

    for pointset in pointsets or []:
        data = pointset['data']
        color = pointset.get('color','black')
        marker = pointset.get('marker','o')
        linewidth = pointset.get('width',2)
        x = [p[0] for p in data]
        y = [p[1] for p in data]
        yerr = [p[2] for p in data]
        q = axes.errorbar(x, y, yerr=yerr, fmt=marker,
                          linewidth=linewidth, color=color)
        if 'legend' in pointset:
            legend[0].append(q[0])
            legend[1].append(pointset['legend'])


    for elliset in ellisets or []:
        data = elliset['data']
        color = elliset.get('color','blue')
        for point in data:
            x, y = point[:2]
            dx = point[2] if len(point)>2 else 0.01
            dy = point[3] if len(point)>3 else dx
            ellipse = Ellipse(xy=(x,y),width=dx,height=dy)
            axes.add_artist(ellipse)
            ellipse.set_clip_box(axes.bbox)
            ellipse.set_alpha(0.5)
            ellipse.set_facecolor(color)

    if legend[0]: axes.legend(legend[0],legend[1])
    canvas = FigureCanvas(figure)
    canvas.print_png(open(filename,'wb'))

def test():
    draw(pointsets=[dict(data=dict(set1=[(x,x**2,2.0*x) for x in range(10)]))])

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
            draw(linesets=[dict(data=[point for point in enumerate(items[1:])])],
                 xlab='step',ylab=tag,filename = filename2)
            filename2 = filename[:-4]+'_%s_hist.png' % clean(tag)
            print filename2
            draw(histsets=[dict(data = items[1:],gaussian_fit=True)],
                 xlab=tag,ylab='frequency',filename = filename2)            
            filename2 = filename[:-4]+'_%s_qq.png' % clean(tag)

    def plot_autocorrelations(self,filename):
        print 'plotting autocorrelations...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag = items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            draw(linesets=[dict(data=[point for point in enumerate(items[1:])])],
                 xlab='step',ylab=tag,filename = filename2)
            
    def plot_trails(self,filename):
        print 'plotting moving averages (trails)...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag = items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            draw(linesets=[dict(data=[point for point in enumerate(items[1:])])],
                 xlab='step',ylab=tag,filename = filename2)

    def plot_samples(self,filename):
        print 'plotting bootstrap samples...'
	for items in csv.reader(open(filename,'r'),
                                delimiter=',',quoting=csv.QUOTE_NONNUMERIC):
            tag= items[0]
            filename2 = filename[:-4]+'_%s.png' % clean(tag)
            print filename2
            draw(histsets=[dict(data = items[1:],gaussian_fit=True)],
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
            filename2 = filename[:-4]+'.png'
            print filename2
            draw(pointsets = [dict(data=sets[legend])],
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
    (options, args) = parser.parse_args()
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
