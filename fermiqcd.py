import sys, os, re, urllib

FERMIQCD = 'http://fermiqcd.googlecode.com/hg/Libraries/'

def get_fermiqcd(path,force=False):
    path = os.path.join(path,'.fermiqcd')
    exe = os.path.join(path,'fermiqcd.exe')
    if force or not os.path.exists(exe):
        if not os.path.exists(path):
            os.mkdir(path)        
        print 'downloading %s' % FERMIQCD
        u = urllib.urlopen(FERMIQCD).read()
        for f in re.compile('\"(\w+\.\w+)\"').findall(u):
            print 'downloading %s' % (FERMIQCD+f)
            data = urllib.urlopen(FERMIQCD+f).read()
            open(os.path.join(path,f),'wb').write(data)
        dir = os.getcwd()
        os.chdir(path)
        print 'compiling....'
        print 'g++ -O3 -o fermiqcd.exe fermiqcd.cpp'
        os.system('g++ -O3 -o fermiqcd.exe fermiqcd.cpp')
        os.chdir(dir)
    return exe

def main():
    path = get_fermiqcd('./',force='-download' in sys.argv)
    os.system('%s %s' % (path,' '.join(sys.argv[1:])))

if __name__=='__main__': main()
