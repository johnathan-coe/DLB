#!/usr/bin/python
from os import scandir, environ as env
import re
from datetime import datetime as dt
from functools import reduce

def read_file(name):
    with open(name, "r") as f: return f.read().strip()

def entries():
    return map(lambda f: run_template(read_file(f.path)), scandir("Entries"))

def run_template(template, args={}):  
    # {{ name }}
    repls = [(r, args.get(n, n+" Unavailable")) for r, n in re.findall(r"({{\s*(.*?)\s*}})", template)]
    # { name }content{ /name }
    props = re.findall("({\s*(.*?)\s*}(.*?){\s*/\\2\s*})", template, re.DOTALL)
    repls, vals = repls+[(p[0], "") for p in props], {"."+p[1]: p[2] for p in props}
    
    return reduce(lambda a, kv: a.replace(*kv), repls, template), vals

def index():       
    results = sorted(entries(), key=lambda t: dt.strptime(t[1][".published"], "%Y-%m-%d %H:%M"), reverse=True)    
    index = read_file("index.html")
    match, body = re.search(r"(<!-- dlb -->(.*?)<!-- /dlb -->)", index, re.DOTALL).groups()   
   
    bodies = [run_template(body, {"content": c, **vars})[0] for c, vars in results]
    return index.replace(match, "\n".join(bodies))

def standalone(q): 
    content, props = next(filter(lambda x: x[1][".link"]=="?"+q, entries()), ("<h1>Not Found</h1>", {}))
    return run_template(read_file("entry.html"), {"content": content, **props})[0]    

if __name__ == "__main__":
    q = env.get("QUERY_STRING", "")
    print("Content-type: text/html\n\n", standalone(q) if q else index(), sep="")
