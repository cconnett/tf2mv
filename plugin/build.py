import yaml
import subprocess
import os.path
import sys

requiredFiles = [
    'sourcemod/addons/sourcemod/scripting/spcomp',
    'sourcemod/addons/sourcemod/extensions/curl.ext.so',
    'sourcemod/addons/sourcemod/scripting/include/cURL.inc',
    ]

if not all(os.path.exists(path) for path in requiredFiles):
    # I'm so lazy.  I should just download it for you.
    print "Please download sourcemod and put unpack it named 'sourcemod'."
    print "http://www.sourcemod.net/dl.php?filename=sourcemod-1.3.7-linux.tar.gz"
    print "Please also download the cURL extension and unpack it in to 'sourcemod'."
    print "https://code.google.com/p/sourcemod-curl-extension/downloads/list"
    sys.exit(2)

config = yaml.load(file('../config.yml').read())
sitefile = file('site.inc', 'w')
print >> sitefile, '#define PLUGIN_VERSION  "1.0.0"' #TODO: git-describe version here
print >> sitefile, '#define TARGET_URL      "{0[application][url]}"'.format(config)
print >> sitefile, '#define TARGET_PORT      {0[application][port]}'.format(config)
sitefile.close()
subprocess.call(['./sourcemod/addons/sourcemod/scripting/spcomp', 'tf2mv.sp', '-psite.inc'])
