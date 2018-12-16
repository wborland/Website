from flask import g, request, session, redirect, url_for
from functools import wraps

def required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):

        try:
            s = session['intern']
            if s != 'ok':
                if '.' in fn.__module__:
                    session['redirect'] = fn.__module__.split(".",1)[1]  + "." + fn.__name__
                else:
                    session['redirect'] = fn.__name__

                return redirect(url_for('login'))

        except:
            print(fn.__module__)

            if '.' in fn.__module__:
                session['redirect'] = fn.__module__.split(".",1)[1]  + "." + fn.__name__
            else:
                session['redirect'] = fn.__name__

            return redirect(url_for('login'))

        return fn(*args, **kwargs)

    return decorated