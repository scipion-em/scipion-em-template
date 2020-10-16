# -*- coding: utf-8 -*-
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
# *  e-mail address 'you@yourinstitution.email'
# *
# **************************************************************************


"""
This protocol subtracts two volumes
"""
from os.path import exists
from pyworkflow.protocol import Protocol, params
from pyworkflow.utils import Message

from pwem.emlib.image import ImageHandler
from pwem.objects import Volume
from pwem.protocols.protocol import EMProtocol

class MyPluginSubtractVolume(EMProtocol):
    """
    This protocol performs the operation V1-V2 between volumes
    """
    _label = 'subtract volume'

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('V1', params.PointerParam, pointerClass='Volume', label='Volume1',
                      allowsNull=False)
        form.addParam('V2', params.PointerParam, pointerClass='Volume', label='Volume2',
                      allowsNull=False)

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('subtractStep', self.V1.getObjId(), self.V2.getObjId())
        self._insertFunctionStep('createOutputStep')

    def subtractStep(self, objId1, objId2):
        fnVol1 = ImageHandler.locationToXmipp(self.V1.get())
        fnVol2 = ImageHandler.locationToXmipp(self.V2.get())
        fnOut = self._getPath("diff.mrc")
        args = "-i %s --minus %s -o %s"%(fnVol1, fnVol2, fnOut)
        self.runJob("xmipp_image_operate",args)

    def createOutputStep(self):
        fnOut = self._getPath('diff.mrc')
        if exists(fnOut):
            volume=Volume()
            volume.setFileName(fnOut)
            volume.setSamplingRate(self.V1.get().getSamplingRate())
            self._defineOutputs(outputVolume=volume)
            self._defineSourceRelation(self.V1.get(),volume)
            self._defineSourceRelation(self.V2.get(),volume)

    # --------------------------- INFO functions -----------------------------------
    def _methods(self):
        methods = []

        if self.isFinished():
            methodStr = "We subtracted %s from %s to produce %s."%\
                        (self.getObjectTag('V2'),self.getObjectTag('V1'), self.getObjectTag('outputVolume'))
            methods.append(methodStr)
        return methods

    def _validate(self):
        errors = []
        if self.V1.get().getSamplingRate()!=self.V2.get().getSamplingRate():
            errors.append("The two volumes should have the same pixel size")
        X1, Y1, Z1 = self.V1.get().getDimensions()
        X2, Y2, Z2 = self.V2.get().getDimensions()
        if X1!=X2 or Y1!=Y2 or Z1!=Z2:
            errors.append("The two volumes should have the same dimensions")
        return errors