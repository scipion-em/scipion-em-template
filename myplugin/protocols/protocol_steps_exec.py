# **************************************************************************
# *
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk)
# *
# * MRC Laboratory of Molecular Biology (MRC-LMB)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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

from pyworkflow.protocol import Protocol, params, STEPS_PARALLEL, STEPS_SERIAL
from pyworkflow.utils import Message


class ProtStepsExecutor(Protocol):
    """ Protocol to test various steps executors. """
    _label = 'steps executor'

    def __init__(self, **kwargs):
        Protocol.__init__(self, **kwargs)
        self.stepsExecutionMode = STEPS_PARALLEL
        # self.stepsExecutionMode = STEPS_SERIAL

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label=Message.LABEL_INPUT)
        form.addHidden(params.USE_GPU, params.BooleanParam, default=False,
                       label="Use GPU?")
        form.addHidden(params.GPU_LIST, params.StringParam, default='0',
                       label="Choose GPU ID")
        form.addParam('stepsNum', params.IntParam,
                      default=5,
                      label='Number of protocol "process" steps')
        form.addParam('doFail', params.BooleanParam, default=False,
                      label="Fail the middle step?",
                      help="Fail the middle processing step for "
                           "testing purposes.")

        form.addParallelSection(threads=6, mpi=1)

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        initId = self._insertFunctionStep('initStep')
        procSteps = []

        for i in range(self.stepsNum.get()):
            st = self._insertFunctionStep('processStep', i+1, prerequisites=[initId])
            procSteps.append(st)

        self._insertFunctionStep('createOutputStep', prerequisites=procSteps)

    def initStep(self):
        print("Using %s" % self._stepsExecutor)
        print("Using MpiCommand:", self.getHostConfig().getMpiCommand())
        print("Using SubmitCommand:", self.getHostConfig().getSubmitCommand())

        if self.usesGpu():
            print("Using gpuList:", self.getGpuList())

    def processStep(self, stepId):
        args = ""
        if self.usesGpu():
            args = " && echo gpuId = %(GPU)s"

        if self.doFail and stepId == int(self.stepsNum.get() / 2):
            # fail the middle step for testing purposes
            self.runJob("hostname && sleep 5 && exit 1", args)
        else:
            self.runJob("hostname && sleep 5", args)

    def createOutputStep(self):
        print("Protocol completed!")
