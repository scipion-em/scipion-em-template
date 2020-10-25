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
Describe your python module here:
This module will provide the traditional Hello world example
"""
from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from pwem.objects.data import (SetOfParticles, Particle)
import numpy as np
from pwem.emlib.image import ImageHandler
from pwem.protocols import EMProtocol

class ProtThumbnail(EMProtocol):
    """
    This protocol will apply a threshold to a set of images
    """
    _label = 'Thumbnail'

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inputParticles', params.PointerParam,
                      pointerClass='SetOfParticles',
                      label="Input particles", important=True,
                      help='Select the input particles.')
        form.addParam('size', params.IntParam,
                      label="Size", help="xdim of output thumbnail")

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('computeThumbnail')
        self._insertFunctionStep('createOutputStep')

    def computeThumbnail(self):
        from PIL import Image
        # get set of particles
        setPart = self.inputParticles.get()
        size = self.size.get()
        fileName = self._getExtraPath("out.stk")
        outTmpFileName = ('/tmp/tmp.jpg')
        for index, particle in enumerate(setPart):
            ih = ImageHandler()
            imageScipion = ih.read(particle.getLocation())
            imageScipion.write(outTmpFileName)
            imPIL = Image.open(outTmpFileName)
            imPIL.thumbnail((size, size))
            imPIL.save("/tmp/out.jpg")
            imageScipion = ih.read("/tmp/out.jpg")
            imageScipion.write((index +1, fileName))

    def createOutputStep(self):
        # Create two particle objects
        # so far empty ones
        setPartOut = self._createSetOfParticles()
        setPartIn = self.inputParticles.get()
        fileName = self._getExtraPath("out.stk")
        sampling = setPartIn.getSamplingRate()
        setPartOut.setSamplingRate(sampling)
        for index, particle in enumerate(setPartIn):
            part = Particle()
            part.setFileName("%d@%s" %
                                 (index +1, fileName))
            part.setSamplingRate(sampling)
            setPartOut.append(part)
        setPartOut.thumbnail_size = self.size
        self._defineOutputs(setPart=setPartOut)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        if self.isFinished():
            summary.append("Size of thumbnail is %d", self.size.get())
        return summary

    def _methods(self):
        methods = []

        #if self.isFinished():
        #    methods.append("%s has been printed in this run %i times." % (self.message, self.times))
        #    if self.previousCount.hasPointer():
        #        methods.append("Accumulated count from previous runs were %i."
        #                       " In total, %s messages has been printed."
        #                       % (self.previousCount, self.count))
        return methods
