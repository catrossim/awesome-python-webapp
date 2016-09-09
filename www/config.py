# config.py

import config_default

class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)
    def __setattr__(self, key, value):
        self[key] = value

def merge(default, override):
    result = Dict()
    for k, v in default.iteritems():
        if k in override:
            if isinstance(v, dict):
                result[k] = merge(v, override=[k])
            else:
                result[k] = override[k]
        else:
            result[k] = v
    return result

configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass

if __name__=='__main__':
    from config import configs
    print configs
