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
from myplugin.protocols import ProtThumbnail
from pwem.emlib.image import ImageHandler

class TestThumbnail(BaseTest):

    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)

    def testThumbnail_01(self):
        # import a stack of images
        filesPath = os.path.dirname(__file__)
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
        size = 64.
        args = {'inputParticles': protImport.outputParticles,
                'size': 64,
                }
        protThreshold = self.newProtocol(ProtThumbnail, **args)
        protThreshold.setObjLabel('compute thumbnail')
        self.launchProtocol(protThreshold)
        # check that setOfPArticles has been created
        self.assertTrue(protThreshold.hasAttributeExt("setPart"))
        # check that a stack file has been created
        ih = ImageHandler()
        fileName = protThreshold._getExtraPath("out.stk")
        self.assertTrue(ih.existsLocation(fileName))
        # check attribute size exists
        self.assertTrue(protThreshold.hasAttributeExt("setPart.thumbnail_size"))
        if protThreshold.hasAttributeExt("setPart.thumbnail_size"):
            self.assertAlmostEqual(size, protThreshold.setPart.thumbnail_size.get())
