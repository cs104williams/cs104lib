__all__ = []

import uuid
import traceback
from IPython.core.display import display, HTML
from IPython.utils.text import strip_ansi
from ansi2html import Ansi2HTMLConverter
import sys

def is_user_file(filename):
    return "/datascience" not in filename and \
           '/site-packages' not in filename and \
           '/cs104' not in filename

def is_known_lib_file(filename):
    return "/datascience" in filename or \
           '/cs104' in filename

html_prefix = \
 """<style type="text/css">
    .ansi2html-content { display: inline; white-space: pre-wrap; word-wrap: break-word; }
    .body_foreground { color: #3e424d; }
    .body_background { background-color: #FFDDDD; }
    .ansi1 { font-weight: bold; }
    .ansi31 { color: #e75c58; }
    .ansi32 { color: #00a250; }
    .ansi34 { color: #208ffb; }
    .ansi36 { color: #60c6c8; }
    </style>"""


_root = "http://cs.williams.edu/~cs104/auto/python-library-ref.html"

_special = {
    ("datascience/tables.py", "set_title") : "set labels",
    ("datascience/tables.py", "set_xlabel") : "set labels",
    ("datascience/tables.py", "set_ylabel") : "set labels",
    ("datascience/tables.py", "set_xlim") : "set limits",
    ("datascience/tables.py", "set_ylim") : "set limits",
    

def id_for_name(name):
    

def shorten_stack(shell, etype, evalue, tb, tb_offset=None): 
    id = uuid.uuid1().hex
    
    # Take the full stack trace and convert into HTML.  
    conv = Ansi2HTMLConverter()
    itb = shell.InteractiveTB
    ansi = "".join(itb.stb2text(itb.structured_traceback(etype, evalue, tb, tb_offset)))
    full = conv.convert(ansi, full=False)
    full = html_prefix + full
    
    frames = traceback.extract_tb(tb)
    
    # The files for each frame in the traceback:
    #   * files[0] will always be the ipython entry point
    #   * files[1] will always be in the notebook
    files = [ frame.filename for frame in frames ]
    
    # Find the top-most frame that corresponds to the notebook.  We will
    #  ignore all the frames above that, since the code is not meaningful
    #  to us.
    notebook_filename = files[1]
    last_notebook_filename = len(files) - 1
    while last_notebook_filename > 0 and not is_user_file(files[last_notebook_filename]):
        last_notebook_filename -= 1

    # Guess the hashtag in the python ref page for the offending library call
    if last_notebook_filename < len(files) - 1 and is_known_lib_file(files[last_notebook_filename + 1]):
        lib_entrypoint_for_last_notebook_frame = frames[last_notebook_filename + 1]
        see_also = f"\n\u001b[1mSee also: \u001b[0m{_root}#{lib_entrypoint_for_last_notebook_frame.name}\n"
    else:
        see_also = None
        
    # Go the the last notebook frame and drop the rest
    tail = tb
    for i in range(last_notebook_filename):
        tail = tail.tb_next    
    tail.tb_next = None
                
    # Hide any stack frames in the middle of the traceback
    #  that correspond to library code, using the sneaky
    #  special var trick.
    for f in traceback.walk_tb(tb):
        frame = f[0]
        filename = frame.f_code.co_filename
        if not is_user_file(filename):
            locals = frame.f_locals
            locals['__tracebackhide__'] = 1

    # Show the stack trace in stderr
    shell.showtraceback((etype, evalue, tb), tb_offset)
    if see_also != None:
        print(see_also, file=sys.stderr)
    
    # Make the HTML full version we can show with a click.
    text = f"""
        <div align="right">
            <a style='inherit;font-size:12px;' 
               onclick='var x = document.getElementById("{id}"); \
               if (x.style.display === "none") \
                 x.style.display = "block"; \
                 else x.style.display = "none";'> \
              Full Details
            </a>
        </div>
        <pre style="font-size:14px;display:none; \
                    color: #3e424d;  \
                    background-color:#FFDDDD;" 
             id="{id}">{full}</pre>
    """
    display(HTML(text))

# this registers a custom exception handler for the whole current notebook
try:
    ipy = get_ipython()
    if ipy != None:
        ipy.set_custom_exc((Exception,), shorten_stack)
except NameError:
    pass
