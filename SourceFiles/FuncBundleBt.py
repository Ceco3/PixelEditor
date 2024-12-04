from .Canvas import Reflect
from .Mouse import Mouse

class scheme:
    def __init__(self, body, key) -> None:
        self.body = body
        self.key = key

    def generate_value(self, object):
        if self.key == None:
            return getattr(object, self.body)
        return getattr(object, self.body)[self.key]
    
class function_bundle:
    def __init__(self) -> None:
        self.functions = {
            0 : User_variables.Set,
            1 : Reflect,
        }

        self.args = {
            0 : ["ImageName", scheme("stats", "txt")],
            1 : ["SaveDir", scheme("stats", "txt")],
            2 : ["LoadDir", scheme("stats", "txt")],
            3 : [scheme("layer_selected", None)]
        }

    def bind(self, clickableBt, function_key, args_key):
        clickableBt.bound = (function_key, args_key)

    def operate(self, clickableBt, generator):
        "Consider using <attach> instead!"
        fun_key, args_key = clickableBt.bound
        args = []
        for arg in self.args[args_key]:
            if arg.__class__ != scheme:
                args.append(arg)
                continue
            args.append(arg.generate_value(generator))

        if generator == Mouse:
            self.functions[fun_key](args)
            return
        self.functions[fun_key](*args)

FunctionBundle = function_bundle()