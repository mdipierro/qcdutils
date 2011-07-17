import os, tempfile, random, cStringIO, math
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
