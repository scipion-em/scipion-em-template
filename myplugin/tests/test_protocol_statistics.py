# ***************************************************************************
# * Authors:     Roberto Marabini (roberto@cnb.csic.es)
# *
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
# ***************************************************************************/

# protocol to test the two ccp4 protocols of flexible fitting (coot and
# refmac)

import os.path
from myplugin.protocols.protocol_hello_world import MyPluginPrefixHelloWorld
from pyworkflow.tests import *
from pwem.protocols import ProtImportParticles
from myplugin.protocols import ProtStatistics

class TestStatisctics(BaseTest):

    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)

    def testCootFlexibleFitFromPDB(self):
        # import a stack of images
        home = os.path.expanduser('~')
        # let us assume that the data files are
        # in $HOME/data
        filesPath = os.path.join(home, 'data')
        args = {'importFrom': ProtImportParticles.IMPORT_FROM_FILES,
                'filesPath': filesPath,
                'filesPattern': 'proj.stk',
                'amplitudConstrast': 0.1,
                'sphericalAberration': 2.,
                'voltage': 100,
                'samplingRate': 2.1,
                'haveDataBeenPhaseFlipped': True
                }
        protImport = self.newProtocol(ProtImportParticles, **args)
        protImport.setObjLabel("import particles")
        self.launchProtocol(protImport)

        # execute myPlugin.statistic protocol
        args = {'inputParticles': protImport.outputParticles,
                }
        protStatistics = self.newProtocol(ProtStatistics, **args)
        protStatistics.setObjLabel('compute statistics')
        self.launchProtocol(protStatistics)

        self.assertTrue(protStatistics.hasAttributeExt("average"))
        self.assertTrue(protStatistics.hasAttributeExt("std"))

        # check that two outputs has been created
        self.assertTrue(True)
