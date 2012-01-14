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
-mpi      for use with mpi (mpiCC and mpirun but be installed)

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
    qcdutils_run.py -gauge:load=*.mdp -polyaov-vtk
    qcdutils_run.py -gauge:load=*.mdp -cool:steps=20 -topcharge-vtk
    qcdutils_run.py -gauge:load=*.mdp -quark:kappa=0.12:alg=minres-vtk
    qcdutils_run.py -gauge:load=*.mdp -quark:kappa=0.12 -pion
    qcdutils_run.py -gauge:load=*.mdp -quark:kappa=0.12 -pion-vtk
"""

def get_options(path):    
    path = os.path.join(os.path.split(path)[0],"fermiqcd.cpp")
    if not os.path.exists(path): return
    data=open(path,"r").read()
    print 'Options:'
    regex = re.compile('\("(.*?)",\s*"(.*?)",\s*"?(.*?)"?\)')
    d = {}
    options = []
    for item in regex.findall(data):
        d[item[0]]=d.get(item[0],[])+[(item[1],item[2])]
        if not item[0] in options:
           options.append(item[0])
    regex = re.compile('have\("(.*?)"\)')
    for item in regex.findall(data):
        d[item]=d.get(item,[])
        if not item in options:
           options.append(item)
    for key in options:
        print '    %s' % key
        done = set()
        for a,b in d[key]:
            if not a in done:
                b = b.replace('|',' or ')
                b = b.replace(' or ',' (default) or ',1)
                print '        %s = %s' % (a,b)
                done.add(a)

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

def main():
    ignore = ['-download','-compile','-mpi','-source','-h']
    if '-h' in sys.argv:
        print USAGE
        get_options('fermiqcd/')
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
            if '-mpi' in sys.argv:
                command = 'mpirun %s %s' % (path,args)
            else:
                command = '%s %s' % (path,args)
            print "running..."
            print command
            os.system(command)

if __name__=='__main__': main()
