#!D:\5.Workspace\Python\V-Medsub-py\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pysrt==1.1.1','console_scripts','srt'
__requires__ = 'pysrt==1.1.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pysrt==1.1.1', 'console_scripts', 'srt')()
    )
