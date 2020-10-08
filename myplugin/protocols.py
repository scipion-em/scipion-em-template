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


class MyPluginPrefixHelloWorld(Protocol):
    """
    This protocol will print hello world in the console
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'Hello world'

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('operation', params.StringParam,
                      default='Sum',
                      label='Operation', important=True,
                      help='Operation which will be applied.')

        form.addParam('operand1', params.IntParam,
                      default=1,
                      label='Operand 1', important=True,
                      help='First operand considered in the selected operation.')

        form.addParam('operand2', params.IntParam,
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
        # Type message body to be printed
        msg = '{operation} of {operand1} {prep} {operand2} is {result}'
        # Implement the four possible cases
        if operation == 'Sum':
            prep = 'plus'
            result = operand1 + operand2
        elif operation == 'Substract':
            prep = 'minus'
            result = operand1 - operand2
        elif operation == 'Multiply':
            prep = 'by'
            result = operand1 * operand2
        else:
            prep = 'by'
            result = operand1 / operand2
        # Print the result on the terminal by replacing the variables
        # between {} with the local values they have
        print(msg.format(**locals()))
        self.result = result

    # def createOutputStep(self):
    #     # register how many times the message has been printed
    #     # Now count will be an accumulated value
    #     timesPrinted = Integer(self.times.get() + self.previousCount.get())
    #     self._defineOutputs(result=self.result)

    # --------------------------- INFO functions -----------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        if self.isFinished():
            summary.append("This protocol has printed *%s* %i times." % (self.message, self.times))
        return summary

    def _methods(self):
        methods = []

        if self.isFinished():
            methods.append("%s has been printed in this run %i times." % (self.message, self.times))
            if self.previousCount.hasPointer():
                methods.append("Accumulated count from previous runs were %i."
                               " In total, %s messages has been printed."
                               % (self.previousCount, self.count))
        return methods
