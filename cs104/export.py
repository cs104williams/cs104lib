from ipylab import JupyterFrontEnd
from ipywidgets import Output
import otter

#
# Make a hook that saves the notebook before exporting it to avoid the common
# pitfall of not saving before exporting, and thus not having all of the outputs
# necessary to grade the manual questions.
#
# Basic idea here:
# https://stackoverflow.com/questions/66880698/how-to-cause-jupyter-lab-to-save-notebook-programmatically
#

_orig = otter.Notebook.export

def _call(*args, **kwargs):
    try:
        app = JupyterFrontEnd()
        out = Output()
        def save():
            with out:
                print("Saving notebook...")
                app.commands.execute('docmanager:save')
                print("Exporting notebook...")
                _orig(*args, **kwargs)
        app.on_ready(save)
        return out
    except:
        return _orig(*args, **kwargs)

setattr(otter.Notebook, "export", _call)