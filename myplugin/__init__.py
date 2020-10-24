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
import pwem
from pyworkflow.utils import Environ, Config

from .constants import *

_logo = "icon.png"
_references = ['you2019']


class Plugin(pwem.Plugin):
    _homeVar = MYPROGRAM_HOME
    _pathVars = [MYPROGRAM_HOME]
    _supportedVersions = [V1_0]
    _url = "https://github.com/scipion-em/scipion-em-template"

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(MYPROGRAM_HOME, 'myprogram-1.0')
        cls._defineVar(MYPROGRAM, 'example_script.sh')
        cls._defineVar(MYPROG_ENV_ACTIVATION, 'conda activate myprogenv-1.0')

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch myProgram. """
        environ = Environ(os.environ)
        if 'PYTHONPATH' in environ:
            # this is required for python virtual env to work
            del environ['PYTHONPATH']
        environ.update({'PATH': cls.getHome()}, position=Environ.BEGIN)
        return environ

    @classmethod
    def defineBinaries(cls, env):
        installCmd = [cls.getCondaActivationCmd()]
        # Create the environment
        installCmd.append('conda create -y -n myprogenv-1.0 python=3;')
        # Activate the new environment
        installCmd.append('conda activate myprogenv-1.0;')
        # Flag installation finished
        installCmd.append('touch IS_INSTALLED;')

        commands = [(" ".join(installCmd), 'IS_INSTALLED')]

        env.addPackage('myprogram', version=V1_0,
                       commands=commands,
                       tar='void.tgz',
                       default=True)

    @classmethod
    def getProgram(cls):
        """ Return the program binary that will be used. """
        program = '%s %s && %s' % (cls.getCondaActivationCmd(),
                                   cls.getMyProgEnvActivation(),
                                   cls.getVar(MYPROGRAM))
        return program

    @classmethod
    def getDependencies(cls):
        # try to get CONDA activation command
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = []
        if not condaActivationCmd:
            neededProgs.append('conda')

        return neededProgs

    @classmethod
    def getMyProgEnvActivation(cls):
        """ Remove the scipion home and activate the conda environment. """
        activation = cls.getVar(MYPROG_ENV_ACTIVATION)
        scipionHome = Config.SCIPION_HOME + os.path.sep

        return activation.replace(scipionHome, "", 1)
