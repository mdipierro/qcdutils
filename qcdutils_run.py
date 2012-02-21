#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# create by: Massimo Di Pierro<mdipierro@cs.depaul.edu>
# license: GPL2.0

import sys, os, re, urllib

FERMIQCD = 'http://fermiqcd.googlecode.com/hg/Libraries/'
GROUP = 'fermiqcd@googlegroup.com'
USAGE = """
qcdutils_run.py is a tool to help you download and use fermiqcd from

    http://code.google.com/p/fermiqcd

When you run:
 
    python qcdutils_run.py [args]
 
It will:
- create a folder called fermiqcd/ in the current working directory
- connect to google code and download fermiqcd.cpp + required libraries
- if -mpi in [args] compile fermiqcd with mpiCC else with g++
- if -mpi in [args] run fermiqcd.exe with mpiCC else run it normally
- pass the [args] to the compiled fermiqcd.exe

Some [args] are handled by qcdutils_run.py:
-download force downloading of the libraries
-compile  force recompiling of code
-source   runs and compiles a different source file
-mpi=2    for use with mpi (mpiCC and mpirun but be installed)

Other [args] are handled by fermiqcd.cpp for example
-cold     make a cold gauge configuration
-load     load a gauge configuration
-quark    make a quark
-pion     make a pion
(run it with no options for a longer list of options)

You can find the source code in fermiqcd/fermiqcd.cpp

More examples:
    qcdutils_run.py -gauge:start=cold:nt=16:nx=4
    qcdutils_run.py -gauge:start=hot:nt=16:nx=4
    qcdutils_run.py -gauge:load=cold.mdp
    qcdutils_run.py -gauge:load=cold.mdp:steps=10:beta=5.7
    qcdutils_run.py -gauge:load=*.mdp -plaquette
    qcdutils_run.py -gauge:load=*.mdp -plaquette-vtk
    qcdutils_run.py -gauge:load=*.mdp -polyakov-vtk
    qcdutils_run.py -gauge:load=*.mdp -cool:steps=20 -topcharge-vtk
    qcdutils_run.py -gauge:load=*.mdp -quark:kappa=0.12:alg=minres-vtk
    qcdutils_run.py -gauge:load=*.mdp -quark:kappa=0.12 -pion
    qcdutils_run.py -gauge:load=*.mdp -quark:kappa=0.12 -pion-vtk
"""

def get_options_base(path):
    path = os.path.join(os.path.split(path)[0],"fermiqcd.cpp")
    if not os.path.exists(path): return
    data=open(path,"r").read()
    d = {}
    regex = re.compile('arguments\.have\("(.*?)"\)')
    for option in regex.findall(data):
        d[option]=d.get(option,{})
    regex = re.compile('arguments\.get\("(.*?)",\s*"(.*?)",\s*"?([^\"\)]*?)"?\)')
    for option, attribute, values in regex.findall(data):
        new_values = values.split('|')
        attributes = d[option] = d.get(option,{})
        values = attributes[attribute] = attributes.get(attribute,[])
        for value in new_values:
            if value and not value in values:
                values.append(value)
    return d

def get_options(path):    
    options = get_options_base(path)
    print 'Options:'
    for key in sorted(options): #['-gauge','-quark']+[a for a in sorted(options) if not a in ('-gauge','-quark')]:
        print '    %s' % key
        for attribute in sorted(options[key]):
            values = options[key][attribute]
            if values: values[0] = values[0]+' (default)'
            print '        %s = %s' % (attribute,' or '.join(values))

def get_fermiqcd(path,download=False,compile=False,mpi=False,
                 source='fermiqcd/fermiqcd.cpp'):
    path = os.path.join(path,os.path.dirname(source))
    filename = os.path.basename(source).split('.')[0]
    if mpi:
        exe = os.path.join(path,'%s-mpi.exe' % filename)
    else:
        exe = os.path.join(path,'%s.exe' % filename)
    if download or not os.path.exists(path):
        if not os.path.exists(path):
            os.mkdir(path)        
        print 'downloading %s' % FERMIQCD
        u = urllib.urlopen(FERMIQCD).read()
        for f in re.compile('\"(\w+\.\w+)\"').findall(u):
            print 'downloading %s' % (FERMIQCD+f)
            data = urllib.urlopen(FERMIQCD+f).read()
            open(os.path.join(path,f),'wb').write(data)
    if not os.path.exists(exe):
        compile = True
    if compile:
        dir = os.getcwd()
        os.chdir(path)
        if mpi:            
            if os.system('mpiCC')!=256:
                print 'mpiCC command not found on your system'
                sys.exit(1)
            command = 'mpiCC -lmpi -DPARALLEL -O3 -o %s-mpi.exe %s.cpp' % (filename,filename)
        else:
            if os.system('g++')!=256:
                print 'g++ command not found on your system'
                sys.exit(1)
            command = 'g++ -O3 -o %s.exe %s.cpp' % (filename, filename)
        print 'compiling....'        
        print command
        if os.system(command):
            print 'there were compilation errors'
            print 'please ask for advice at %s' % GROUP
            sys.exit(1)
        os.chdir(dir)
    return exe

def get_options_form(path):
    options = get_options_base(path)
    fields = []
    for key in sorted(options):
        k = key[1:].replace('-','_')
        fields.append("Field('%s','boolean',default=False')" % k)
        for attribute in sorted(options[key]):
            values = options[key][attribute]            
            d = values and values[0] or ''
            try:
                t = 'string'
                float(values[0])
                t = 'double' if '.' in values[0] else 'integer'
            except: pass
            if len(values)>1:
                v = repr(values)
                fields.append("Field('%s_%s','%s',default='%s',requires=IS_IN_SET(%s))" % \
                                  (k,attribute,t,d,v))
            else:
                fields.append("Field('%s_%s','%s',default='%s')" % \
                                  (k,attribute,t,d))
    return 'form = SQLFORM.factory('+',\n        '.join(fields)+')'
    

def main():
    ignore = ['-download','-compile','-mpi','-source','-h']
    if '-h' in sys.argv:
        print USAGE
        get_options('fermiqcd/')
    elif '-H' in sys.argv:
        print get_options_form('fermiqcd/')
    else:
        source = ([x[8:] for x in sys.argv if x.startswith('-source:')]+['fermiqcd/fermiqcd'])[0]
        path = get_fermiqcd(os.getcwd(),
                            download='-download' in sys.argv,
                            compile='-compile' in sys.argv,
                            mpi='-mpi' in sys.argv,
                            source=source)
        if '-options' in sys.argv:
            get_options(path)
        else:            
            args = ' '.join(x for x in sys.argv[1:] if not x in ignore)
            mpis = [x for x in sys.argv[1:] if x.startswith('-mpi')]
            if mpis:
                p = int(mpis[0][5:])
                command = 'mpirun -n %s %s %s' % (p, path,args)
            else:
                command = '%s %s' % (path,args)
            print "running..."
            print command
            os.system(command)

if __name__=='__main__': main()
