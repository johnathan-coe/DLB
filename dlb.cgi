#!/usr/bin/python
from os import scandir, environ as env
import re
from datetime import datetime as dt
from functools import reduce


# Read the content of an entire file
def read_file(name):
    with open(name, "r") as f:
        return f.read().strip()


# Grab post data from all entries
def entries():
    # Get a list of all entries
    entry_list = scandir("Entries")
    # Run the entry template over all entries
    return [run_template(read_file(f.path)) for f in entry_list]


# Grab metadata and content from a post, substituting in 
def run_template(template, args={}):  
    # Find references to variables ({{ name }}) in template
    references = re.findall(r"({{\s*(.*?)\s*}})", template)
    # Get variable values
    repls = [(r, args.get(n, n+" Unavailable")) for r, n in references]
    
    # Find variable declarations ({ name }content{ /name }) in template
    props = re.findall("({\s*(.*?)\s*}(.*?){\s*/\\2\s*})", template, re.DOTALL) 
    # Put declarations in dictionary 
    vals = {"."+p[1]: p[2] for p in props}

    # Replacements to perform on the string
    repls = repls+[(p[0], "") for p in props] 
    # Perform replacements 
    out = reduce(lambda a, kv: a.replace(*kv), repls, template)

    return out.strip(), vals


# Generate listing page for all entries
def index():
    # Sort entries from newest to oldest
    results = sorted(entries(), key=lambda t: dt.strptime(t[1][".published"], "%Y-%m-%d %H:%M"), reverse=True)    

    index = read_file("index.html")

    # Find the tags pertaining to a single listing
    match, body = re.search(r"(<!-- dlb -->(.*?)<!-- /dlb -->)", index, re.DOTALL).groups()   
    
    # Run for every listing
    bodies = [run_template(body, {"content": c, **vars})[0] for c, vars in results]

    # Join them all together and place them in the index
    return index.replace(match, "\n".join(bodies))


# Generate the page for a single entry, given its query string
def standalone(q):
    # Find the entry associated with this query string
    content, props = next(filter(lambda x: x[1][".link"]=="?"+q, entries()), ("<h1>Not Found</h1>", {}))

    # Run the template for the entry
    return run_template(read_file("entry.html"), {"content": content, **props})[0]    


# Entrypoint
if __name__ == "__main__":
    q = env.get("QUERY_STRING", "")
    # Output a standalone entry if a query string is provided, otherwise get a listing
    print("Content-type: text/html\n\n", standalone(q) if q else index(), sep="")
