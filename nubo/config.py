import os
import json

CONFFILE = os.path.join(os.getenv('HOME'), '.nuborc')

def read_config():
    try:
        return json.loads(open(CONFFILE).read())
    except IOError:
        return {}

def write_config(values):
    old_values = read_config()

    updated = dict(old_values.items() + values.items())
    open(CONFFILE, 'w').write(json.dumps(updated, indent=4))

    os.chmod(CONFFILE, 0600)
    return updated
