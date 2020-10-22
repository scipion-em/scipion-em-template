# **************************************************************************
# *
# * Authors:     Scipion Team
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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
import pyworkflow.tests as pwtests
from ..constants import SUM, SUBSTRACT, MULTIPLY, DIVIDE
from ..protocols import MyPluginPrefixHelloWorld


class TestProtocolMyCalculator(pwtests.BaseTest):
    #################################### AUX TEST METHODS #######################################
    @classmethod
    def setUpClass(cls):
        # Set up for test project
        pwtests.setupTestProject(cls)
        # Get test dataset, downloading it from remote if not locally present
        ds = pwtests.DataSet.getDataSet('devCourse')
        # Parse dataset to get the desired data for testing
        cls.op1 = cls._getValueFromFile(ds.getFile('calculator/operand1'))
        cls.op2 = cls._getValueFromFile(ds.getFile('calculator/operand2'))
        # Set tolerance for operation result checking
        cls.tol = 1e-6

    @staticmethod
    def _getValueFromFile(file):
        with open(file) as f:
            operand = [float(x) for x in next(f).split()]  # read first line
            return operand[0]  # Only one line with one element present for this test

    def _runCalculatorTest(self, operation):
        '''Base test for calculator tests'''
        # Define protocol inputs
        protCalculator = self.newProtocol(
            MyPluginPrefixHelloWorld,
            operation=operation,
            operand1=self.op1,
            operand2=self.op2
        )
        # Set protocol label to be shown on the project GUI
        protCalculator.setObjLabel('%s of two numbers' % operation)
        # Execute protocol
        protCalculator = self.launchProtocol(protCalculator)
        # Get protocol output
        result = getattr(protCalculator, 'result', None)
        # Validate output
        self.assertTrue(abs(result.get() - self._genTestOutput(operation)) <= self.tol)

    def _genTestOutput(self, operation):
        '''Generate output to be tested'''
        if operation == SUM:
            result = self.op1 + self.op2
        elif operation == SUBSTRACT:
            result = self.op1 - self.op2
        elif operation == MULTIPLY:
            result = self.op1 * self.op2
        else:
            result = self.op1 / self.op2

        return result

    #################################### TESTS #######################################

    def testSum(self):
        self._runCalculatorTest(SUM)

    def testSubstract(self):
        self._runCalculatorTest(SUBSTRACT)

    def testMultiply(self):
        self._runCalculatorTest(MULTIPLY)

    def testDivide(self):
        self._runCalculatorTest(DIVIDE)
