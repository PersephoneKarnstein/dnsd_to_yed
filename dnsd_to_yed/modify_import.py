import importlib, re
import sys

def modify_and_import(module_name, package, modification_func):
    spec = importlib.util.find_spec(module_name, package)
    source = spec.loader.get_source(module_name)
    new_source = modification_func(source)
    module = importlib.util.module_from_spec(spec)
    codeobj = compile(new_source, module.__spec__.origin, 'exec')
    exec(codeobj, module.__dict__)
    sys.modules[module_name] = module
    return module

def modification_func(source):
    node_update = importlib.util.find_spec('dnsd_to_yed.node_update')
    source_replacement = node_update.loader.get_source('dnsd_to_yed.node_update')
    fixed = re.sub("class Node:(.*\n)*?class Edge:", source_replacement, source)
    return fixed