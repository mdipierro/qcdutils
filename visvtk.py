#!/usr/bin/python
import sys
import os
import re
import struct
import glob
import math
import uuid
import optparse
import fnmatch
import logging
import random

USAGE  = """
This is a utility script to manipulate vtk files containing scalar files.
Files can be split, interpolated, and converted to jpeg images.
The conversion to jpeg is done by dynamically generating a visit script 
that reads the files, and computes optimal contour plots.

Examples:

1) make a dummy vtk file

   visvtk -m 10 folder/test.vtk

2) reads fields from multiple vtk files

   visvtk -r field folder/*.vtk

3) extract fields as multiple files

   visvtk -s field folder/*.vtk

(fields in files will be renamed as "slice")
4) interpolate vtk files

   visvtk -i 9 folder/*.vtk

5) render a vtk file as a jpeg image

   visvtk -p 'AnnotationAttributes[axes3D.bboxFlag=0];ResampleAttributes[samplesX=160;samplesY=160;samplesZ=160];ContourAttributes[SetMultiColor(9,$orange)]' 'folder/*.vtk'

Filename convetions
===================

Original file: 
- file.vtk 

File split into slice files:
- file_00000000.vtk
- file_00010000.vtk
- file_00020000.vtk
- file_00030000.vtk

Interpoltade files
- file_00000000.vtk
- file_00000001.vtk (interpolated)
- file_00010000.vtk
- file_00010001.vtk (interpolated)
- file_00020000.vtk
- file_00020001.vtk (interpolated)
- file_00030000.vtk

Generated script:
- visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2.py

Images from interpolated slices:
- file_00000000.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00000000.jpeg                    
- file_00000001.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00010000.jpeg
- file_00010000.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00020000.jpeg
- file_00010001.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00030000.jpeg
- file_00020000.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00040000.jpeg
- file_00020001.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00050000.jpeg
- file_00030000.vtk -> visitvtk_2fac1b86-5b86-42ee-8552-d1577d308dd2_00060000.jpeg

You can use streampclip to turn the jpegs into a movie
"""

HEAD = """# vtk DataFile Version 2.0
%(filename)s
BINARY
DATASET STRUCTURED_POINTS
DIMENSIONS %(x)s %(y)s %(z)s
ORIGIN     0   0   0
SPACING    1   1   1
POINT_DATA %(volume)s
SCALARS %(field)s float
LOOKUP_TABLE default
"""

# reasonable defaults

DEFAULTS = {
  'AnnotationAttributes':'legendInfoFlag = 0;databaseInfoFlag = 0;userInfoFlag = 0;backgroundColor = (0,0,0,255);foregroundColor = (255,255,255,255);axes3D.visible = 0;axes3D.autoSetTicks = 1;axes3D.autoSetScaling = 1;axes3D.lineWidth = 1;axes3D.tickLocation = this.axes3D.Inside;axes3D.axesType = this.axes3D.ClosestTriad;axes3D.triadFlag = 0;axes3D.bboxFlag = 1;axes3D.xAxis.title.visible = 1;axes3D.xAxis.title.font.font = this.axes3D.xAxis.title.font.Arial;axes3D.xAxis.title.font.scale = 1;axes3D.xAxis.title.font.useForegroundColor = 1;axes3D.xAxis.title.font.color = (0, 0, 0, 255);axes3D.xAxis.title.font.bold = 0;axes3D.xAxis.title.font.italic = 0;axes3D.xAxis.title.userTitle = 0;axes3D.xAxis.title.userUnits = 0;axes3D.xAxis.title.title = "X-Axis";axes3D.xAxis.title.units = "";axes3D.xAxis.label.visible = 1;axes3D.xAxis.label.font.font = this.axes3D.xAxis.label.font.Arial  # Arial, Courier, Times;axes3D.xAxis.label.font.scale = 1;axes3D.xAxis.label.font.useForegroundColor = 1;axes3D.xAxis.label.font.color = (0, 0, 0, 255);axes3D.xAxis.label.font.bold = 0;axes3D.xAxis.label.font.italic = 0;axes3D.xAxis.label.scaling = 0;axes3D.xAxis.tickMarks.visible = 1;axes3D.xAxis.tickMarks.majorMinimum = 0;axes3D.xAxis.tickMarks.majorMaximum = 1;axes3D.xAxis.tickMarks.minorSpacing = 0.02',
'ResampleAttributes': 'useExtents = 1;samplesX = 100;samplesY = 100;samplesZ = 100',
'ContourAttributes': 'SetMinFlag(1);SetMaxFlag(1); SetMin($minimum); SetMax($maximum); SetMultiColor(0, $yellow); SetMultiColor(1, (0,0,0,0)); SetMultiColor(2, (0,0,0,0)); SetMultiColor(3, (0,0,0,0)); SetMultiColor(4, (0,0,0,0)); SetMultiColor(5, (0,0,0,0)); SetMultiColor(6, (0,0,0,0)); SetMultiColor(7, (0,0,0,0)); SetMultiColor(8, (0,0,0,0)); SetMultiColor(9, $red)'
}

# conveninence variables

VARIABLES = {'black':(0, 0, 0, 255), 'navy':(0, 0, 128, 255), 'darkblue':(0, 0, 139, 255), 'mediumblue':(0, 0, 205, 255), 'blue':(0, 0, 255, 255), 'darkgreen':(0, 100, 0, 255), 'green':(0, 128, 0, 255), 'teal':(0, 128, 128, 255), 'darkcyan':(0, 139, 139, 255), 'deepskyblue':(0, 191, 255, 255), 'darkturquoise':(0, 206, 209, 255), 'mediumspringgreen':(0, 250, 154, 255), 'lime':(0, 255, 0, 255), 'springgreen':(0, 255, 127, 255), 'aqua':(0, 255, 255, 255), 'cyan':(0, 255, 255, 255), 'midnightblue':(25, 25, 112, 255), 'dodgerblue':(30, 144, 255, 255), 'lightseagreen':(32, 178, 170, 255), 'forestgreen':(34, 139, 34, 255), 'seagreen':(46, 139, 87, 255), 'darkslategray':(47, 79, 79, 255), 'darkslategrey':(47, 79, 79, 255), 'limegreen':(50, 205, 50, 255), 'mediumseagreen':(60, 179, 113, 255), 'turquoise':(64, 224, 208, 255), 'royalblue':(65, 105, 225, 255), 'steelblue':(70, 130, 180, 255), 'darkslateblue':(72, 61, 139, 255), 'mediumturquoise':(72, 209, 204, 255), 'indigo':(0, 0, 0, 255), 'darkolivegreen':(85, 107, 47, 255), 'cadetblue':(95, 158, 160, 255), 'cornflowerblue':(100, 149, 237, 255), 'mediumaquamarine':(102, 205, 170, 255), 'dimgray':(105, 105, 105, 255), 'dimgrey':(105, 105, 105, 255), 'slateblue':(106, 90, 205, 255), 'olivedrab':(107, 142, 35, 255), 'slategray':(112, 128, 144, 255), 'slategrey':(112, 128, 144, 255), 'lightslategray':(119, 136, 153, 255), 'lightslategrey':(119, 136, 153, 255), 'mediumslateblue':(123, 104, 238, 255), 'lawngreen':(124, 252, 0, 255), 'chartreuse':(127, 255, 0, 255), 'aquamarine':(127, 255, 212, 255), 'maroon':(128, 0, 0, 255), 'purple':(128, 0, 128, 255), 'olive':(128, 128, 0, 255), 'gray':(128, 128, 128, 255), 'grey':(128, 128, 128, 255), 'skyblue':(135, 206, 235, 255), 'lightskyblue':(135, 206, 250, 255), 'blueviolet':(138, 43, 226, 255), 'darkred':(139, 0, 0, 255), 'darkmagenta':(139, 0, 139, 255), 'saddlebrown':(139, 69, 19, 255), 'darkseagreen':(143, 188, 143, 255), 'lightgreen':(144, 238, 144, 255), 'mediumpurple':(147, 112, 216, 255), 'darkviolet':(148, 0, 211, 255), 'palegreen':(152, 251, 152, 255), 'darkorchid':(153, 50, 204, 255), 'yellowgreen':(154, 205, 50, 255), 'sienna':(160, 82, 45, 255), 'brown':(165, 42, 42, 255), 'darkgray':(169, 169, 169, 255), 'darkgrey':(169, 169, 169, 255), 'lightblue':(173, 216, 230, 255), 'greenyellow':(173, 255, 47, 255), 'paleturquoise':(175, 238, 238, 255), 'lightsteelblue':(176, 196, 222, 255), 'powderblue':(176, 224, 230, 255), 'firebrick':(178, 34, 34, 255), 'darkgoldenrod':(184, 134, 11, 255), 'mediumorchid':(186, 85, 211, 255), 'rosybrown':(188, 143, 143, 255), 'darkkhaki':(189, 183, 107, 255), 'silver':(192, 192, 192, 255), 'mediumvioletred':(199, 21, 133, 255), 'indianred':(0, 0, 0, 255), 'peru':(205, 133, 63, 255), 'chocolate':(210, 105, 30, 255), 'tan':(210, 180, 140, 255), 'lightgray':(211, 211, 211, 255), 'lightgrey':(211, 211, 211, 255), 'palevioletred':(216, 112, 147, 255), 'thistle':(216, 191, 216, 255), 'orchid':(218, 112, 214, 255), 'goldenrod':(218, 165, 32, 255), 'crimson':(220, 20, 60, 255), 'gainsboro':(220, 220, 220, 255), 'plum':(221, 160, 221, 255), 'burlywood':(222, 184, 135, 255), 'lightcyan':(224, 255, 255, 255), 'lavender':(230, 230, 250, 255), 'darksalmon':(233, 150, 122, 255), 'violet':(238, 130, 238, 255), 'palegoldenrod':(238, 232, 170, 255), 'lightcoral':(240, 128, 128, 255), 'khaki':(240, 230, 140, 255), 'aliceblue':(240, 248, 255, 255), 'honeydew':(240, 255, 240, 255), 'azure':(240, 255, 255, 255), 'sandybrown':(244, 164, 96, 255), 'wheat':(245, 222, 179, 255), 'beige':(245, 245, 220, 255), 'whitesmoke':(245, 245, 245, 255), 'mintcream':(245, 255, 250, 255), 'ghostwhite':(248, 248, 255, 255), 'salmon':(250, 128, 114, 255), 'antiquewhite':(250, 235, 215, 255), 'linen':(250, 240, 230, 255), 'lightgoldenrodyellow':(250, 250, 210, 255), 'oldlace':(253, 245, 230, 255), 'red':(255, 0, 0, 255), 'fuchsia':(255, 0, 255, 255), 'magenta':(255, 0, 255, 255), 'deeppink':(255, 20, 147, 255), 'orangered':(255, 69, 0, 255), 'tomato':(255, 99, 71, 255), 'hotpink':(255, 105, 180, 255), 'coral':(255, 127, 80, 255), 'darkorange':(255, 140, 0, 255), 'lightsalmon':(255, 160, 122, 255), 'orange':(255, 165, 0, 255), 'lightpink':(255, 182, 193, 255), 'pink':(255, 192, 203, 255), 'gold':(255, 215, 0, 255), 'peachpuff':(255, 218, 185, 255), 'navajowhite':(255, 222, 173, 255), 'moccasin':(255, 228, 181, 255), 'bisque':(255, 228, 196, 255), 'mistyrose':(255, 228, 225, 255), 'blanchedalmond':(255, 235, 205, 255), 'papayawhip':(255, 239, 213, 255), 'lavenderblush':(255, 240, 245, 255), 'seashell':(255, 245, 238, 255), 'cornsilk':(255, 248, 220, 255), 'lemonchiffon':(255, 250, 205, 255), 'floralwhite':(255, 250, 240, 255), 'snow':(255, 250, 250, 255), 'yellow':(255, 255, 0, 255), 'lightyellow':(255, 255, 224, 255), 'ivory':(255, 255, 240, 255), 'white':(255, 255, 255, 255)}

def notify(*a):
    """
    this function is used for printing
    """
    print ' '.join(str(x) for x in a)

def analysis(filename):
    """
    reads a filename and returns {'name':...,'minimum':...','maximum':...,'iso':...}
    where name is the scalar field name found in the file
    minimum and maximum and the extreme values of the fiels
    iso if a list of two suggested iso-surface threshold values so that blobs occupy 30% of volume
    """
    data = open(filename,'rb').read()
    header, data = data.split('LOOKUP_TABLE default\n')
    name = re.compile('SCALARS (?P<name>\w+)').search(header).group('name')
    volume = int(re.compile('POINT_DATA (?P<volume>\d+)').search(header).group('volume'))
    np = max(1,10000/volume)
    minimum,maximum = None,None
    points = []
    for i in xrange(volume):
        p = struct.unpack('>f',data[4*i:4*i+4])[0]
        if minimum==None or p<minimum:
            minimum = p
            points.append(p)
        if maximum==None or p>maximum:
            maximum = p
            points.append(p)
        if i%np==0:
            points.append(p)
    points.sort()
    if maximum*minimum>=0 and maximum>0:
        return dict(name=name,maximum=maximum,minimum=minimum,
                    iso=(0.0,points[int(2*len(points)/3)]))
    if maximum*minimum>=0 and minimum<0:
        return dict(name=name,maximum=maximum,minimum=minimum,
                    iso=(points[int(len(points)/3)],0.0))
    else:
        return dict(name=name,maximum=maximum,minimum=minimum,
                    iso=(points[int(len(points)/6)], -points[int(len(points)/6)]))

def makevtk(filename,size=10):
    """
    make a dummy filename of size^3 (1000 points by default)
    """
    file = open(filename,'wb')
    d = dict(filename = os.path.basename(filename),x=size,y=size,z=size,volume=size**3,field='slice')
    file.write(HEAD % d)
    nr = range(size)
    half = float(size)/2
    for x in nr:
        for y in nr:
            for z in nr:
                field = 1.0/math.sqrt(0.001+(half-x)**2+(half-y)**2+(half-z)**2)
                file.write(struct.pack('>f',field))

def split(filename,pattern):
    """
    takes a binary vtk file containing many scalars and splits it into many vtk files with a single scalar
    """
    regex_header = re.compile('.*LOOKUP_TABLE .*?\n$',re.DOTALL)
    regex = re.compile(fnmatch.translate('SCALARS '+pattern+' float'))
    file=open(filename,'rb')
    header=''
    i =0 
    filenames = []
    header = ''
    while True:
        header = '\n'.join(header.split('\n')[:-3])
        while True:
            c=file.read(1)
            if len(c)<1:
                i=-1
                break
            header+=c
            if regex_header.match(header):
                break
        if i<0: break
        header = re.compile('SCALARS .*? float').sub('SCALARS slice float',header)
        size = int(re.compile('POINT_DATA (?P<size>\d+)').search(header).group('size'))*4
        data = file.read(size)
        newfilename=filename.rsplit('.')[0]+'.%.4i0000.vtk' % i
        notify('writing...',newfilename)
        open(newfilename,'wb').write(header+data)
        filenames.append(newfilename)
        i+=1        
    return filenames

def interpolate_couple(filename1, filename2, frames=1):
    """
    generates new VTK files interpolating between two.
    the two files must have the same header and be ninary files with a single scalar.
    """
    if filename1[-6:-4]!='00': raise RuntimeError, "filename must end in 00.vtk"
    if filename2[-6:-4]!='00': raise RuntimeError, "filename must end in 00.vtk"
    file1=open(filename1,'rb')
    file2=open(filename2,'rb')
    header=''
    while True:
        c=file1.read(1)
        if len(c)<1: sys.exit(0)
        header+=c
        if header.endswith('LOOKUP_TABLE default\n'): break    
    size = int(re.compile('POINT_DATA (?P<size>\d+)').search(header).group('size'))
    data1 = file1.read(size*4)
    file2.seek(len(header))
    data2 = file2.read(size*4)
    points1 = struct.unpack('>%if' % size, data1)
    points2 = struct.unpack('>%if' % size, data2)
    workfiles = []
    for i  in range(1,frames+1):
        h = 1.0/(frames+1)
        points3 = [h*(frames+1-i)*points1[j]+h*i*points2[j] for j in range(size)]    
        data3 = struct.pack('>%if' % size, *points3)
        filename = '%s%.2i.vtk' % (filename1[:-6],i)
        notify('writing...',filename)
        open(filename,'wb').write(header+data3)
        workfiles.append(filename)
    return workfiles

def interpolate(filenames, nframes):
    """
    loops over all filenames and interpolates each couple of them
    """
    filenames.sort()
    workfiles = filenames
    for i in range(1,len(filenames)):
        workfiles += interpolate_couple(filenames[i-1],filenames[i],nframes)
        workfiles.append(filenames[i])
    return workfiles

def fix_variables(text):
    """
    replaces $name with value from VARIABLES
    """
    for key in VARIABLES:
        text = text.replace('$'+key,str(VARIABLES[key]))
    return text

def plot(workfiles,pipeline,format='jpeg',tmpfile=None):
    """
    generates a visit script that loops over files and compute contour plots as jpeg images
    as it loops over files, it rotates the image
    """
    if not tmpfile:
        tmpfile = 'visvtk_%s.py' % uuid.uuid4()
    res = analysis(workfiles[int(len(workfiles)/2)])
    res['tmpfile'] = tmpfile[:-3]
    file = open(tmpfile,'w')
    VARIABLES['minimum']=res['iso'][0]
    VARIABLES['maximum']=res['iso'][1]
    regex = re.compile('(?P<a>\w+)\[(?P<b>[^\]]*)\]')
    items = regex.findall(pipeline)
    file.write('def set_attributes():\n')
    for name, attributes in items:
        file.write('    this = %s()\n' % name)
        for attribute in DEFAULTS[name].split(';'):            
            if not attribute.strip(): continue
            file.write('    this.%s\n' % fix_variables(attribute.strip()))
        for attribute in attributes.split(';'):
            if not attribute.strip(): continue            
            file.write('    this.%s\n' % fix_variables(attribute.strip()).replace('=',' = ',1))
        if name == 'AnnotationAttributes':
            file.write("""
    SetAnnotationAttributes(this)
    this = RenderingAttributes()
    this.antialiasing = 1
    SetRenderingAttributes(this)
""")
        elif name == "ResampleAttributes":
            file.write("    SetOperatorOptions(this, 1)\n")
        else:
            file.write("    SetPlotOptions(this)\n")
    file.write('\n\nworkfiles = %s\n' % repr(workfiles))
    file.write("""
import sys, math
for number, filename in enumerate(workfiles):
    print 'loading: %%s' %% filename
    DeleteAllPlots()
    OpenDatabase(filename)
    AddPlot("Contour", "%(name)s", 1, 1)
    SetActivePlots(0)
    AddOperator("Resample", 1)
    SetActivePlots(0)
    set_attributes()
    DrawPlots()
    v = GetView3D()
    alpha = 0.005*number
    print 'rotating: %%s' %% alpha
    v.viewNormal = (math.sin(alpha),0.2,math.cos(alpha))
    SetView3D(v)
    s = SaveWindowAttributes()
    s.format = s.JPEG
    s.fileName = "%(tmpfile)s_%%.4i" %% (number)
    s.width, s.height = 1024,1024
    s.screenCapture = 0
    SetSaveWindowAttributes(s)
    SaveWindow()
sys.exit(0)
""" % res)
    file.close()
    os.system('/usr/local/visit/bin/visit -cli -nowin -s %s' % tmpfile)
 
def main():
    """
    main program
    """
    usage = USAGE
    version= ""
    parser = optparse.OptionParser(usage, None, optparse.Option, version)
    parser.add_option('-r',
                      '--read',
                      default='',
                      dest='read',
                      help='name of the field to read from the vtk file')
    parser.add_option('-s',
                      '--split',
                      default='',
                      dest='split',
                      help='name of the field to split from the vtk file')
    parser.add_option('-i',
                      '--interpolate',
                      default='',
                      dest='interpolate',
                      help='name of the vtk files to add/interpolate')
    parser.add_option('-m',
                      '--make',
                      default=None,
                      dest='make',
                      help='make a dummy vtk file with size^3 whete size if arg of make')
    parser.add_option('-p',
                      '--pipeline',
                      default='',
                      dest='pipeline',
                      help='visualizaiton pipeline instructions')
    (options, args) = parser.parse_args()
    if not args:
        notify('no source specified')
        sys.exit(1)
    elif options.make:
        makevtk(args[0],int(options.make))
        workfiles = [args[0]]
    else:
        workfiles = glob.glob(args[0])
    if options.split:
        if len(workfiles)!=1:
            notify("you cannot split more than one file")
            sys.exit(1)
        workfiles = split(workfiles[0],options.split)        
    pattern = options.read or options.split or '*'
    if options.interpolate:
        workfiles = interpolate(workfiles,int(options.interpolate))
    if options.pipeline:
        workfiles.sort()
        plot(workfiles,options.pipeline)
                      

if __name__ == '__main__': main()
