# **************************************************************************
# *
# * Authors:  Carlos Oscar Sanchez Sorzano (coss@cnb.csic.es), Oct 2020
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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

from pyworkflow.viewer import DESKTOP_TKINTER, WEB_DJANGO
from pwem.viewers.views import ObjectView
from pwem.viewers.showj import RENDER, SAMPLINGRATE
from pwem.viewers import DataViewer

from xmippLib import Image
from pwem.emlib.image import ImageHandler

from myplugin.protocols.protocol_volume_filter import MyPluginFilterVolume


class MyPluginFilterVolumeViewer(DataViewer):
    """ Visualize the output of protocol volume filter """
    _label = 'viewer volume filter'
    _targets = [MyPluginFilterVolume]
    _environments = [DESKTOP_TKINTER, WEB_DJANGO]
    
    def _visualize(self, obj, **args):
        from os.path import exists
        fnDiff = self.protocol._getTmpPath('diff.mrc')
        fnFilt = self.protocol._getPath('filteredVolume.mrc')
        inputVol = self.protocol.inputVolume.get()
        if not exists(fnDiff) and exists(fnFilt):
            # Read the input and filtered images as Xmipp image objects
            Voriginal = Image(ImageHandler.locationToXmipp(inputVol))
            Vfiltered = Image(fnFilt)

            # Compute difference and save to tmp
            # Note that this is using an Image class (not numpy) and it knows of EM images
            Vdiff = Voriginal-Vfiltered
            Vdiff.write(fnDiff)

        if exists(fnFilt):
            # Visualize an existing Scipion object
            DataViewer._visualize(self, self.protocol.outputVolume)

        if exists(fnDiff):
            # Visualize a file
            objView = ObjectView(self._project, "Original-Filtered", fnDiff,
                                 viewParams={RENDER: 'image',
                                             SAMPLINGRATE: inputVol.getSamplingRate()})
            self._views.append(objView)
        return self._views

