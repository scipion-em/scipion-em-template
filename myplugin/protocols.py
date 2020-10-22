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
from pyworkflow.protocol import Protocol, params
from pyworkflow.utils import Message
from .constants import SUM, SUBSTRACT, MULTIPLY, DIVIDE


class MyPluginPrefixHelloWorld(Protocol):
    """
    This protocol will print hello world in the console
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'Hello world'
    _result = None

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('operation', params.StringParam,
                      default=SUM,
                      label='Operation', important=True,
                      help='Operation which will be applied.')

        form.addParam('operand1', params.FloatParam,
                      default=1,
                      label='Operand 1', important=True,
                      help='First operand considered in the selected operation.')

        form.addParam('operand2', params.FloatParam,
                      default=1,
                      label='Operand 2', important=True,
                      help='Second operand considered in the selected operation.')

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('calculateStep')
        self._insertFunctionStep('createOutputStep')

    def calculateStep(self):
        # Get value introduced by the user for Operand 1
        operand1 = self.operand1.get()
        # Get value introduced by the user for Operand 2
        operand2 = self.operand2.get()
        # Get value selected by the user for Operation
        operation = self.operation.get()
        # Implement the four possible cases, storing the result as an attribute of the protocol
        if operation == SUM:
            self._result = operand1 + operand2
        elif operation == SUBSTRACT:
            self._result = operand1 - operand2
        elif operation == MULTIPLY:
            self._result = operand1 * operand2
        else:
            self._result = operand1 / operand2

    def createOutputStep(self):
        # register the operation result
        self._defineOutputs(result=params.Float(self._result))

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []
        if self.isFinished():
            summary.append(('Operation --> %s\n' +
                            'Operand 1 --> %1.2f\n' +
                            'Operand 2 --> %1.2f\n' +
                            'RESULT ==> %1.2f\n') %
                            (self.operation.get(), self.operand1.get(),
                             self.operand2.get(), self.result))
        return summary

    # def _methods(self):
    #     methods = []
    #
    #     if self.isFinished():
    #         methods.append("%s has been printed in this run %i times." % (self.message, self.times))
    #         if self.previousCount.hasPointer():
    #             methods.append("Accumulated count from previous runs were %i."
    #                            " In total, %s messages has been printed."
    #                            % (self.previousCount, self.count))
    #     return methods
