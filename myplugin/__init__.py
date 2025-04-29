# **************************************************************************
# *
# * Authors:     you (you@yourinstitution.email)
# *
# * your institution
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import pyworkflow.utils as pwutils
import pwem

from myplugin.constants import *

__version__ = "0.1"  # plugin version
_logo = "icon.png"
_references = ['you2019']


class Plugin(pwem.Plugin):
    _homeVar = MYPLUGIN_HOME
    _pathVars = [MYPLUGIN_HOME]
    _url = "https://github.com/scipion-em/scipion-em-template"
    _supportedVersions = [V1]  # binary version

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(MYPLUGIN_BINARY, "program")
        cls._defineEmVar(MYPLUGIN_HOME, f"myplugin-{V1}")

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch my program. """
        environ = pwutils.Environ(os.environ)

        # ...

        return environ

    @classmethod
    def getDependencies(cls):
        """ Return a list of dependencies. """
        neededProgs = []

        return neededProgs

    @classmethod
    def defineBinaries(cls, env):
        installCmds = [("make -j 4", "")]  # replace the target "" with e.g. "bin/myprogram"
        env.addPackage('myplugin', version=V1,
                       tar='void.tgz',
                       commands=installCmds,
                       neededProgs=cls.getDependencies(),
                       default=True)
