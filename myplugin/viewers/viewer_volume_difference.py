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

import matplotlib.cm as cm
import matplotlib.pyplot as plt

from pyworkflow.protocol.params import EnumParam, IntParam, BooleanParam
from pyworkflow.viewer import DESKTOP_TKINTER, WEB_DJANGO
from pwem.viewers import EmProtocolViewer

from xmippLib import Image
from pwem.emlib.image import ImageHandler

from myplugin.protocols.protocol_volume_difference import MyPluginSubtractVolume


class MyPluginVolumeDifferenceViewer(EmProtocolViewer):
    """ Visualize the output of volume difference """
    _label = 'viewer volume difference'
    _targets = [MyPluginSubtractVolume]
    _environments = [DESKTOP_TKINTER, WEB_DJANGO]

    SLICE_Z = 0
    SLICE_Y = 1
    SLICE_X = 2

    def _defineParams(self, form):
        form.addSection(label='Visualization')
        form.addParam('viewSlice', EnumParam, choices=['Z','Y','X'], default=self.SLICE_Z,
                      display=EnumParam.DISPLAY_HLIST,
                      label="Slice along:")
        form.addParam('sliceNo', IntParam, default=-1,
                      label="Slice",
                      help="From 1 to N. -1 is the central slice")
        form.addParam('centralLine', BooleanParam, default=False,
                      label="Plot central line")

    def _getVisualizeDict(self):
        return {
            'sliceNo': self._showSlice
        }

    def _showSlice(self, paramName=None):
        if hasattr(self.protocol,"outputVolume"):
            fnDiff = ImageHandler.locationToXmipp(self.protocol.outputVolume)
            Vdiff = Image(fnDiff).getData() # As numpy array
            Zdim, Xdim, Ydim = Vdiff.shape
            sliceNo = self.sliceNo.get()
            if sliceNo==-1:
                if self.viewSlice.get()==self.SLICE_Z:
                    sliceNo = int(Zdim/2)
                elif self.viewSlice.get()==self.SLICE_Y:
                    sliceNo = int(Ydim/2)
                elif self.viewSlice.get()==self.SLICE_X:
                    sliceNo = int(Xdim/2)
            slice = None
            if self.viewSlice.get() == self.SLICE_Z and (sliceNo>=0 and sliceNo<Zdim):
                slice=Vdiff[sliceNo, :, :]
            elif self.viewSlice.get() == self.SLICE_Y and (sliceNo>=0 and sliceNo<Ydim):
                slice=Vdiff[:, sliceNo, :]
            elif self.viewSlice.get() == self.SLICE_X and (sliceNo>=0 and sliceNo<Ydim):
                slice=Vdiff[:, :, sliceNo]

            if slice is not None:
                fig, ax = plt.subplots()
                if not self.centralLine:
                    im = ax.imshow(slice, interpolation='bilinear', cmap=cm.gray,
                                   origin='lower', extent=[0,1,0,1],
                                   vmax=abs(slice).max(), vmin=-abs(slice).max())
                else:
                    Ydim, _ = slice.shape
                    profile = slice[int(Ydim/2),:]
                    plt.plot(profile)
                plt.show()
