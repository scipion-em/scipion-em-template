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
This protocol filters a single volume
"""
from os.path import exists
from pyworkflow.protocol import params
from pyworkflow.utils import Message

from pwem.emlib.image import ImageHandler
from pwem.objects import Volume
from pwem.protocols.protocol import EMProtocol
from xmipp3 import Plugin as xmipp3Plugin

class MyPluginFilterVolume(EMProtocol):
    """
    This protocol filters a single volume using Xmipp volume filter
    """
    _label = 'filter volume'

    SHAPE_GAUSSIAN = 0
    SHAPE_RAISEDCOSINE = 1

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inputVolume', params.PointerParam, pointerClass='Volume', label='Volume to filter',
                      allowsNull=False)

        form.addParam('filterShape', params.EnumParam, label='Filter shape', choices=['Gaussian','Raised cosine'],
                      default=self.SHAPE_GAUSSIAN,
                      help='The filter can have a Gaussian shape (the falloff is defined in real space), or '
                           'a raised cosine shape (the falloff is defined in Fourier space)')

        form.addParam('gaussianSigma', params.FloatParam, label='Gaussian sigma', condition='filterShape==SHAPE_GAUSSIAN',
                      default=2,
                      help='Sigma of the Gaussian in voxels')

        form.addParam('cutoffResolution', params.FloatParam, label='Cutoff resolution', condition='filterShape==SHAPE_RAISEDCOSINE',
                      default=5,
                      help='In Angstroms, up to this resolution the filter will have weight=1. '
                           'Then the transition band starts, its width is the transition bandwidth')

        form.addParam('transBandwidth', params.FloatParam, label='Transition bandwidth', condition='filterShape==SHAPE_RAISEDCOSINE',
                      default=0.02, expertLevel=params.LEVEL_ADVANCED,
                      help='In rad/vox, that is digital frequency units normalized to 0.5.'
                           'Having a too small transition bandwidth causes ripples in the filtered volume.')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('filterStep', self.inputVolume.getObjId())
        self._insertFunctionStep('createOutputStep')

    def filterStep(self, objId):
        # Grab volume from input
        vol = self.inputVolume.get()

        # Copy it locally and convert it to MRC file format
        ih = ImageHandler()
        fnVol = self._getPath('filteredVolume.mrc')
        ih.convert(vol, fnVol)

        # Filter it
        args = "-i %s "%fnVol
        if self.filterShape.get()==self.SHAPE_GAUSSIAN:
            args+="--fourier real_gaussian %f" % self.gaussianSigma
        else:
            Ts = vol.getSamplingRate()
            wlp = Ts/self.cutoffResolution.get()
            args += "--fourier low_pass %f %f" % (wlp,self.transBandwidth)
        xmipp3Plugin.runXmippProgram("xmipp_transform_filter",args)

    def createOutputStep(self):
        fnVol = self._getPath('filteredVolume.mrc')
        if exists(fnVol):
            volume=Volume()
            volume.setFileName(fnVol)
            volume.setSamplingRate(self.inputVolume.get().getSamplingRate())
            self._defineOutputs(outputVolume=volume)
            self._defineSourceRelation(self.inputVolume.get(),volume)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        if self.isFinished():
            if self.filterShape.get()==self.SHAPE_GAUSSIAN:
                summary.append("Gaussian filter, sigma=%f (voxels)"%self.gaussianSigma)
            else:
                summary.append("Raised cosine, lowpass filter, max.resolution=%f (A), transition bandwidth=%f (rad/vox)" %
                               (self.cutoffResolution,self.transBandwidth))
        return summary

    def _methods(self):
        methods = []

        if self.isFinished():
            methodStr = "The volume %s was lowpass filtered [[Jain1989]] with a "%self.getObjectTag('inputVolume')
            if self.filterShape.get() == self.SHAPE_GAUSSIAN:
                methodStr += "Gaussian filter whose sigma was %f voxels." % self.gaussianSigma
            else:
                methodStr += "raised cosine with a maximum resolution of %f A and transition bandwidth of %f (rad/vox)" %\
                              (self.cutoffResolution, self.transBandwidth)
            methods.append(methodStr)
            methodStr+=" The volume %s was created."%(self.getObjectTag('outputVolume'))
        return methods

    def _citations(self):
        return ['Jain1989']
