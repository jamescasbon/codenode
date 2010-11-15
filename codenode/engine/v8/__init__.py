import os
from cStringIO import StringIO
import tempfile
import operator

import rpy2.robjects.lib.ggplot2 as ggplot2
from rpy2.robjects.packages import importr
from rpy2 import robjects

import PyV8 as v8
from _PyV8 import JSObject

from codenode.engine import protocol
import whitelist
grdevices = importr('grDevices')


def js_kwargs(f):
    """ wrap a function that takes kwargs to accept a dict.
    
        i.e. instead of f(a=1), new function would take f({'a':1}).
    """

    def wrapper(*args):
        if args:            
            if isinstance(args[-1], JSObject):
                kws = v8.convert(args[-1])
                args = args[:-1]
            else:
                kws = {}
            return f(*args, **kws)
        else: 
            return f()
    return wrapper

    
    
class JSPackage(object):
    """ Wrap a R package to be usable from v8 """
    
    _wrappers = {
        robjects.Vector: lambda x: x,
        robjects.Function: js_kwargs
    }
    
    def __init__(self, module, whitelist=None, expose_all=False):
        module = importr(module)
        
        if expose_all:
            whitelist = [x for x in dir(module) if not x.startswith('_')]
        
        for name in whitelist:
                
            obj = getattr(module, name)
            for base, wrapper in self._wrappers.items():      
                if isinstance(obj, base):
                    # print 'wrapping', name,  base, wrapper   
                    setattr(self, name.replace('.', '_'), wrapper(obj))
                       
            
            
    
class JSGGplot(object):
    """ Wrap ggplot2 to be usable from v8 """
    def __init__(self, wrapper=js_kwargs):
        for name in dir(ggplot2):
            obj = getattr(ggplot2, name)
            
            if hasattr(obj, 'im_self') and issubclass(obj.im_self, ggplot2.GBaseObject):
                setattr(self, name, wrapper(obj))
                
                # print 'registered function', name
    
    def ggplot(self, data):
        return ggplot2.ggplot(data)
        
    def aes_string(self, kws):
        return ggplot2.aes_string(**kws)
        
    def add(self, x, y):
        return x + y
        
        
def serialize_plot(plot):
    fname = tempfile.mktemp()
    grdevices.png(file=fname, width=600, height=600)
    print(plot)
    grdevices.dev_off()
    data = protocol.encode_image(file(fname).read())
    os.unlink(fname)
    return data

    

class EngineContext(v8.JSClass):
    def __init__(self):
        self.ggplot = JSGGplot()
        self.datasets = JSPackage('datasets', expose_all=True)
        self.stats = JSPackage('stats', expose_all=True)
        self.base = JSPackage('base', whitelist=whitelist.base_allowed)
        self._buffer = StringIO()
        
    def writeln(self, arg):
        print arg, arg.__class__, isinstance(arg, ggplot2.GGPlot)
        if isinstance(arg, ggplot2.GGPlot):
            print 'X' * 80
            self._buffer.write("__outputimage__%s__outputimage__\n" % serialize_plot(arg))

        else:
            self._buffer.write("%s\n" % arg)
    
    def _get_and_empty_buffer(self):
        # self._buffer.seek(0)
        buf = self._buffer.getvalue()
        self._buffer = StringIO()
        return buf
        
    def add(self, x, y):
        return x.ro * y
        
    def mul(self, x, y):
        return x.ro + y

    def sub(self, x, y):
        return x.ro - y
        
    def div(self, x, y):
        return x.ro / y
    
    def pow(self, x, y):
        return x.ro ** y
    
# cannot create a print method directly
setattr(EngineContext, 'print', EngineContext.writeln)
        
        
class Interpreter(object):

    def __init__(self, context=None):
        self.input_count = 0
        self.ec = EngineContext()
        self.ctxt = v8.JSContext(self.ec)
        self.ctxt.enter()

    def evaluate(self, input_string):
        err = ''
        try:
            self.ctxt.eval(input_string)
            out = self.ec._get_and_empty_buffer()
        except Exception, e:
            err = str(e)   
            out = ''     
        self.input_count += 1
        result = protocol.result_dict(
            input_string, out, err=err,
            cmd_count=self.input_count, in_count=self.input_count
        )
        return result

    def complete(self, input_string):
        """
        Complete a name or attribute.
        """
        return {'out':[]}


if __name__ == '__main__':
    i = Interpreter()   
    print i.evaluate("print(stats.rnorm(100, {'mean': 1}))")
    print i.evaluate("""var plot = ggplot.ggplot(datasets.mtcars);
    plot = ggplot.add(plot, ggplot.aes_string({x:'wt', y:'mpg', colour:'cyl'}));
    plot = ggplot.add(plot, ggplot.geom_point());
    print(plot);
    """)
