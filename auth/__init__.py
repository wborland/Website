from flask import g, request, session, redirect, url_for
from functools import wraps

def required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):

        try:
            s = session['intern']
            if s != 'ok':
                session['redirect'] = fn.__name__
                print("Bad " + fn.__name__)
                return redirect(url_for('login'))

        except:
            session['redirect'] = fn.__name__
            print("Bad " + fn.__name__)
            return redirect(url_for('login'))

        return fn(*args, **kwargs)

    return decorated