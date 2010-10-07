import sys
import cloud
import traceback
from code import softspace

from codenode.engine.interpreter import Interpreter as Python


def cloud_run(code, locals_):
    exec code in locals_
    return locals_
        

class Interpreter(Python):
    
    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which is reraised.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        """
        try:
            job = cloud.call(cloud_run, code, self.locals)
            cloud.join(job)
            result = cloud.result(job)
            self.locals.update(result) 
            info = cloud.info(job, ['stderr', 'stdout'])[job]
            sys.stdout.write(info['stdout'])
            sys.stderr.write(info['stderr'])
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise OperationAborted('Interrupted')
        except cloud.CloudException, e:
            self.showcloudtraceback(e)
        except:
            self.showtraceback()
        else:
            if softspace(sys.stdout, 0):
                print
        
    def showcloudtraceback(self, exception):
        """ Show a traceback from a cloud exception
        """
        tb = exception.parameter.split('\n')
        
        # drop everything up to the execution line 
        while True:
            next = tb.pop(0)
            if 'exec code' in next: 
                break
        
        tb.insert(0, "Traceback (most recent call last):")
        tb = '\n'.join(tb)
        map(self.write, tb)
        