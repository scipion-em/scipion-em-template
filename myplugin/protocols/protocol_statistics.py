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
class ProtStatistics(Protocol):
    """
    This protocol will print hello world in the console
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'Statistics'

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

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('computeStatistics')
        self._insertFunctionStep('createOutputStep')

    def computeStatistics(self):
        # get set of particles
        setOfParticles = self.inputParticles.get()
        # get dimensions
        x, y, z = setOfParticles.getDim()
        n = setOfParticles.getSize()
        # alloc 2 np arrays
        averageNP = np.zeros([x,y], dtype =np.float32)
        squareNP = np.zeros([x,y], dtype =np.float32)
        for particle in setOfParticles:
            # read image
            particleImage = ImageHandler().read(particle.getLocation())
            matrix = particleImage.getData()
            averageNP += matrix
            squareNP += matrix * matrix
        n = float(n)
        averageNP /= n
        particleImage.setData(averageNP)
        particleImage.write(self._getExtraPath("average.mrc"))
        squareNP -= n * (averageNP * averageNP)
        squareNP /= n
        particleImage.setData(squareNP)
        particleImage.write(self._getExtraPath("std.mrc"))

#TODO:
#  1) make this program work
#  2) add convert case
#  3) viewer selecting fieldssampling rate and some mic parameter

        #sums = sums + ((img - global_mean) ** 2) / len(images)

        #for particle in setOfParticles:
        #    # read image
        #    matrix = ImageHandler().read(particle.getLocation()).getData()
        #    averageNP.add(matrix)

    def createOutputStep(self):
        # Create two particle objects
        # so far empty ones
        average = Particle()
        std = Particle()
        self._defineOutputs(average=average)
        self._defineOutputs(std=std)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        if self.isFinished():
            summary.append("This protocol has printed *%s* %i times." % (self.message, self.times))
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
