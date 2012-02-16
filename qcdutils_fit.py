#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# create by: Massimo Di Pierro<mdipierro@cs.depaul.edu>
# license: GPL2.0

### TODO... integrate qcdutils_fit with qcdutils_plot

from math import *
import re, random, copy, sys, csv
from optparse import *
from numpy import matrix
from numpy.linalg import *
try:
    from qcdutils_plot import draw
except ImportError:
    print 'no qcdutils_plot.py, cannot draw'
    draw = None

usage = \
    "qcdutils_fit.py [OPTIONS] 'expression@values'\n" \
    "  Example: qcdutils-fit.py 'a*x+b@a=3,b=0'\n" \
    "  default filename is qcdutils_results.csv\n" \
    "  ...., 'x', 'min', 'mean', 'max'\n" \
    "  ...., 23, 10, 11, 12\n" \
    "  ...., etc etc etc\n"

version = \
    "qcdutils_fit v1.0\n" \
    "  Copyright (c) 2011 Massimo Di Pierro\n" \
    "  All rights reserved\n" \
    "  License: GPL 2.0\n\n" \
    "  Written by Massimo Di Pierro <mdipierro@cs.depaul.edu>\n"

description = \
    "This program takes data produced by qcdutils and fits it\n" \
    "it also does correlated fits by using the built-in function\n" \
    "(a==b)"

def partial(f,i,h=1e-4):
    """
    definition of paritial derivative, df/dx_i
    """
    def df(x,f=f,i=i,h=h):
        x[i]+=h
        u = f(x)
        x[i]-=2*h
        v = f(x)
        x[i]+=h
        return (u-v)/2/h
    return df

def gradient(f, x, h=1e-4):
    """
    gradient of f in x
    """
    s = xrange(len(x))
    return matrix([[partial(f,r,h)(x)] for r in s])

def hessian(f, x, h=1e-4):
    """
    hessian of f in x
    """
    s = xrange(len(x))
    grad = [partial(f,r,h) for r in s]
    return matrix([[partial(grad[r],r,h)(x) for c in s] for r in s])

def norm(A):
    """
    defines norm of a matrix to check convergence
    """
    rows, cols = A.shape
    return max([sum(abs(A[r,c]) for r in xrange(rows)) \
                    for c in xrange(cols)])

def tolist(A):
    rows, cols = A.shape
    return [A[r,0] for r in xrange(rows)]

def optimize_newton_multi_imporved(f, x, ap=1e-6, rp=1e-4, ns=200):
    """
    Multidimensional Newton optimizer
    on failure is performs a steepest descent
    """
    fx = f(x)
    x = matrix([[element] for element in x])
    h = 10.0
    for k in xrange(ns):
        print tolist(x), fx
        grad = gradient(f,tolist(x))
        (grad,H) = (gradient(f,tolist(x)), hessian(f,tolist(x)))
        if norm(H) < ap:
            raise ArithmeticError, 'unstable solution'
        (fx_old, x_old, x) = (fx, x, x-(1.0/H)*grad)
        fx = f(tolist(x))
        while fx>fx_old: # revert to steepest descent
            (fx, x) = (fx_old, x_old)
            n = norm(grad)
            (x_old, x) = (x, x - grad/n*h)
            (fx_old, fx) = (fx, f(tolist(x)))
            h = h/2
        h = norm(x-x_old)*2
        if k>2 and h/2<max(ap,norm(x)*rp):
            x = tolist(x)
            return x, hessian(f,x)
    raise ArithmeticError, 'no convergence'


def fit(data, f, b, ap=1e-6, rp=1e-4, ns=200, bayesian=None):
    def g(b,data=data,f=f,bayesian=bayesian):
        chi2 = sum(((y-f(x,b))/dy)**2 for x,y,dy in data)
        if bayesian:
            chi2 += bayesian(b)
        return chi2
    b, H = optimize_newton_multi_imporved(g,b,ap,rp,ns)
    chi2 = sum(((y-f(x,b))/dy)**2 for x,y,dy in data)
    return b, chi2, H

class Fitter(object):
    def __init__(self,expression,points,symbols=None,
                 condition='True',modules=None):

        if not symbols and len(points[0])==4: symbols=['x']
        if not symbols and len(points[0])==5: symbols=['x','y']
        if not symbols and len(points[0])==6: symbols=['x','y','z']
        if not symbols and len(points[0])==7: symbols=['x','y','z','t']
        if not symbols: raise Exception

        if not modules: modules = ['math']
        self.expression = expression # 'ax+b*exp(y)'
        self.points = points
        self.symbols = symbols       # ['x','y']
        self.priors = {}             # {'a':(1,0.1), 'b':(2,1)]
        self.locals = {}             # {'exp':<function...>}
        for module in modules:
            exec("from %s import *" % module) in self.locals
        self.data = []               # [((x,y),o,do) for x,y,o,do in points]
        nx = len(symbols)            # 2
        self.variables = [           # ['a','b']
            key for key in re.compile('[a-zA-Z_]+\w*').findall(expression) \
                if not key in self.locals and not key in symbols and not key in \
                ('is', 'if','else','int','float','div')]
        for point in points:
            symbol_dict = {}
            for i,symbol in enumerate(symbols):                
                symbol_dict[symbol] = point[i]
            self.locals.update(symbol_dict)            
            if eval(condition,{},self.locals):
                if len(point)==nx+3:
                    err = (point[nx+2]-point[nx])/2
                else:
                    raise ArithmeticError, "oops"
                self.data.append((symbol_dict,point[nx+1],err))
        self.values = {}
        self.ap=1e-6
        self.rp=1e-4
        self.ns=1000

    def f(self,x,b):
        """
        x = values for self.variables
        b = dict with the b values
        """
        self.locals.update(x)
        self.locals.update(
            dict((self.variables[i], bi) for i,bi in enumerate(b)))        
        return eval(self.expression,{},self.locals)

    def bayesian(self,b):
        dchi2 = 0.0
        for i,bi in enumerate(self.variables):
            if bi in self.priors:
                b0,db = self.priors[bi]
                dchi2 += ((b[i]-b0)/db)**2
        return dchi2

    def fit(self,**initial_values):
        b = [initial_values[bi] for bi in self.variables]
        for key,value in initial_values.items():
            if key[0]=='_':
                self.priors[key[1:]]=(initial_values[key[1:]], value)
        b, chi2, H = fit(self.data,self.f,b,ap=self.ap, rp=self.rp, ns=self.ns, 
                         bayesian=self.priors and self.bayesian)
        b = dict((v,b[i]) for (i,v) in enumerate(self.variables))
        return b, chi2, H

    def extrapolate(self,**x):
        """                                                    
        assuming a fit has been done... extrapolate to the point at coordinates
        """
        self.locals.update(x)
        return eval(self.expression,{},self.locals)


    def save_fit(self,filename):
	"""
	under development
	"""
	writer=csv.writer(open(filename,'w'),delimiter=',',
                          quoting=csv.QUOTE_NONNUMERIC)
	expression=self.expression+'@'+','.join(
            "%s=%g" % (k,self.locals[k]) for k in self.variables)
	others=["[min]", "[mean]", "[max]","[%s]" % expression,"[error]"]
	writer.writerow(self.symbols+others)
	#for p in self.last_fit:   #### last fit???
	#    writer.writerow(p)

def test():      
    points = [(x,y,2.0*x+3.0*y*y-0.01,2.0*x+3.0*y*y,2.0*x+3.0*y*y+0.01) \
                  for x in range(10) for y in range(10)]                  
    fitter = Fitter("a*x+b*y*y",points,symbols=('x','y'))
    print fitter.fit(a=1.0,b=2.0,_a=0.5)
    print fitter.extrapolate(x=11,y=11)


def read_min_mean_max_file(filename):
    """
    reads a standard qcdutils_results.csv file,
    extract all the points and symetrizes the error bars
    """
    reader=csv.reader(open(filename,'r'),delimiter=',',
                      quoting=csv.QUOTE_NONNUMERIC)
    lines=list(reader)
    symbols=lines[0][1:-3]
    for i in range(len(symbols)):
	if symbols[i]=='[min]': 
	    symbols=symbols[:i]
	    break
    i+=3
    points=[line[1:] for line in lines[1:]]
    return symbols,points

def test_fitter():
    print 'generating points with z=x*sin(y)+4*y and dz=1'
    points=[[float(x),float(y),1.0*x*sin(y)+4*y-1,x*sin(y)+4*y,x*sin(y)+4*y+1] \
                for x in range(10) for y in range(10)]
    print 'fitting with a*x*sin(y)+b*y should get a=1, b=4'
    fitter = Fitter("a*x*sin(y)+b*y",points,symbols=['x','y'])
    b, chi2, H = fitter.fit(a=0.0,b=0.0)
    print "a=", b['a'], "b=", b['b']
    print "chi2=",chi2
    print "Hessian=",H
    print "x->200, y->200, f->",fitter.extrapolate(x=200,y=200)

def test_correlated_fitter():
    print 'generating points with z=x*sin(y)+4*y and dz=1'
    points=[[x,y,x*sin(y)+4*y-1,x*sin(y)+4*y,x*sin(y)+4*y+1] \
                for x in range(3) for y in range(100)]
    print 'fitting with (a0*(x==0)+a1*(x==1)+a2*(x==2))*sin(y)+c*y'
    fitter=Fitter("(a0*(x==0)+a1*(x==1)+a2*(x==2))*sin(y)+b*y",points,
              symbols=['x','y'])
    print fitter.fit(a0=0.0,a1=0.0,a2=0.0,b=0.0)

def main_fitter():
    loc={}
    parser = OptionParser(usage, None, Option, version)
    parser.add_option("-i", "--input",
		      type="string", dest="input",
		      default="qcdutils_results.csv",
		      help="input file (default qcdutils_results.csv)")
    parser.add_option("-c", "--condition",
		      type="string", dest="condition",
		      default="True",
		      help="sets a filter on the points to be fitted")
    parser.add_option("-p", "--plot",
		      dest="plot",type='string',
		      default='',
		      help="plots the hessian (not implemented yet)")
    parser.add_option("-t", "--test",
		      dest="test",action='store_true',
		      default=False,
		      help="test a fit")
    parser.add_option("-e", "--extrapolate",
		      type='string',dest="extrapolations",
		      default=[],action='append',
		      help="extrpolation point")
    parser.add_option("-a", "--absolute_precision",
		      type='float',dest="ap",
		      default=0.000001,
		      help="absolute precision")
    parser.add_option("-r", "--relative_precision",
		      type='float',dest="rp",
		      default=0.0001,
		      help="relative precision")
    parser.add_option("-n", "--number_steps",
		      type='int',dest="ns",
		      default=1000,
		      help="number of steps")
                      
    options,args=parser.parse_args()
    if options.test:
	test_fitter()
	return
    filename=options.input
    expression,initial=args[0].split('@')
    symbols,points=read_min_mean_max_file(filename)
    fitter=Fitter(expression,points,symbols,condition=options.condition)
    fitter.ap = options.ap
    fitter.rp = options.rp
    fitter.ns = options.ns
    variables=eval('dict(%s)' % initial,loc)
    variables,chi2,hessian=fitter.fit(**variables)
    for key,value in variables.items():
        print '%s = %g' % (key, value)
    print 'chi2=',chi2
    print 'chi2/dof=',chi2/max(len(fitter.data)-len(variables)-1,1)
    print 'covariance=',inv(hessian)        

    pointsets = [dict(data=[(p[0],p[-2],0.5*(p[-1]-p[-3])) for p in points])]
    for item in options.extrapolations:
        coordinates=eval('dict(%s)' % item,{},loc)	
        e=fitter.extrapolate(**coordinates) 
        print 'extrapolation %s -> %s' % (item,str(e))
        pointsets.append(dict(marker='s',                              
                              data=[(coordinates[symbols[0]],e,0)]))
        points.append((coordinates[symbols[0]],e))
    b = [variables[bi] for bi in fitter.variables]    
    x_min = min(p[0] for p in points)
    x_max = max(p[0] for p in points)
    xs = [x_min+0.01*(x_max-x_min)*i for i in range(0,101)]
    try:
        linesets = [dict(data=[(x,fitter.f({symbols[0]:x},b)) for x in xs],
                         color='red', style='--',
                         legend = '%s@%s' % (expression,','.join('%s=%.3g' % i for i in variables.items())))]
    except:
        print 'sorry, unable to plot fitting line'
        linesets = []
    draw(title='',
         xlab=symbols[0],
         ylab=expression.replace('"','').replace('<','').replace('>',''),
        pointsets = pointsets,
        linesets=linesets,filename=options.input.rsplit('.',1)[0]+'.fit.png' )

if __name__=='__main__': main_fitter()
