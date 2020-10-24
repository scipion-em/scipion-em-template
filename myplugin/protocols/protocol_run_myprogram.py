# -*- coding: utf-8 -*-
# *****************************************************************************
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
# *****************************************************************************


"""
Describe your python module here:
This module will provide a simple shell script example
"""
from pyworkflow.protocol import Protocol, params
from pyworkflow.utils import Message

from .. import Plugin


class MyPluginPrefixMyProgram(Protocol):
    """
    This protocol will run a simple shell script
    IMPORTANT: Classes names should be unique, better prefix them
    """
    _label = 'my program'

    # -------------------------- DEFINE param functions -----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
        Params:
            form: this is the form to be populated with sections and params.
        """
        # You need a params to belong to a section:
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('message', params.LabelParam,
                      label='This protocol has no input parameters, '
                            'so just execute it!')

    # --------------------------- STEPS functions -----------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('runStep')

    def runStep(self):
        params = ''
        program = Plugin.getProgram()

        self.runJob(program, params)

    # --------------------------- INFO functions ------------------------------
    def _summary(self):
        """ Summarize what the protocol has done"""
        summary = []

        if self.isFinished():
            summary.append("This protocol has finished.")
        return summary
