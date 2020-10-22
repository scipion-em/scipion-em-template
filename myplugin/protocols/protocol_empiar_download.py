# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
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

import json
import requests
import ftplib
import os
import shutil

from pwem.objects import Movie, SetOfMovies, Float
from pwem.protocols import EMProtocol
from pyworkflow.protocol import (params, Positive, String, STATUS_NEW,
                                 STEPS_PARALLEL)
import pyworkflow.utils as pwutils


class EmpiarDownloader(EMProtocol):
    """
    Download image sets from empiar
    """
    _label = 'empiar downloader'
    _outputClassName = 'SetOfMovies'
    registerFiles = []

    def __init__(self, **args):
        EMProtocol.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL

    # --------------- DEFINE param functions ---------------
    def _defineParams(self, form):
        form.addSection(label='Entry')
        form.addParam('entryID', params.StringParam, default='10200',
                      label='EMPIAR ID',
                      important=True,
                      allowsNull=False,
                      help='EMPIAR entry ID')
        form.addParam('amountOfImages', params.IntParam,
                      default=5,
                      label='Amount of Images',
                      validators=[Positive],
                      help='Time that the protocol will be running expressed in seconds')
        form.addParallelSection(threads=2, mpi=1)

    # --------------- INSERT steps functions ----------------

    def _insertAllSteps(self):
        self._insertFunctionStep('readXmlFileStep')
        self._insertFunctionStep('downloadImagesStep')
        self._insertFunctionStep('closeSetStep', wait=True)
    # --------------- STEPS functions -----------------------

    def closeSetStep(self):
        """
        Close the set
        """
        self.outputMovies.setStreamState(SetOfMovies.STREAM_CLOSED)
        self.outputMovies.write()
        self._store()

    def _stepsCheck(self):
        # Input movie set can be loaded or None when checked for new inputs
        # If None, we load it
        depStepsList = []
        if len(self.registerFiles) < self.amountOfImages.get():
            for file in os.listdir(self._getExtraPath()):
                if file not in self.registerFiles:
                    self.registerFiles.append(file)
                    lastSteps = self._insertFunctionStep('registerImageStep',
                                                         file, prerequisites=[1])
                    depStepsList.append(lastSteps)

                if len(self.registerFiles) >= self.amountOfImages.get():
                    self._steps[2].setStatus(STATUS_NEW)
                    self._steps[2].addPrerequisites(*depStepsList)

            self.updateSteps()

    def registerImageStep(self, file):
        """
        """
        newImage = Movie(location=self._getExtraPath(file))
        newImage.setSamplingRate(self.samplingRate.get())
        self._addMovieToOutput(newImage)

    def _addMovieToOutput(self, movie):
        """
        Returns the output set if not available create an empty one
        :return:
        """
        outputSet = None
        if hasattr(self, 'outputMovies'):
            outputSet = self.outputMovies
            outputSet.append(movie)
        else:
            outputSet = SetOfMovies.create(self._getPath())
            outputSet.setSamplingRate(self.samplingRate.get())
            outputSet.setStreamState(outputSet.STREAM_OPEN)
            outputSet.append(movie)
            self._defineOutputs(outputMovies=outputSet)
        outputSet.write()
        self._store()

    def readXmlFileStep(self):
        """
        Download file by file from a specific dataset from EMPIAR repository
        """
        xmlFileName = self.entryID.get()
        empiarXmlUrl = 'https://www.ebi.ac.uk/pdbe/emdb/empiar/api/entry/'
        empiarXmlUrl += xmlFileName
        try:
            xmlFile = requests.get(empiarXmlUrl, allow_redirects=True)
            content = (json.loads(xmlFile.content.decode('utf-8')))
            empiarName = 'EMPIAR-' + xmlFileName
            self.corresponingAuthor = content[empiarName]['corresponding_author']
            self.organization = String(self.corresponingAuthor['author']['organization'])
            self.depositionDate = String(content[empiarName]['deposition_date'])
            self.title = String(content[empiarName]['title'])
            self.imageSets = content[empiarName]['imagesets']
            self.releaseDate = String(content[empiarName]['release_date'])
            self.datasetSize = String(content[empiarName]['dataset_size'])
            self.empiarName = String(empiarName)
            self.samplingRate = Float(self.imageSets[0]['pixel_width'])
            # self.dataFormat = String(content[empiarName]['data_format'])

            self._store(self)
        except Exception as ex:
            self.setFailed(msg="There was an error downloading the EMPIAR raw "
                               "images: %s!!!" %ex)

    def downloadImagesStep(self):
        """
        This method connect to EMPIAR repository and download a set of images
        into a specific directory
        """
        # Connection information

        # import time
        # time.sleep(60)
        # return
        server = 'ftp.ebi.ac.uk'
        username = 'anonymous'
        password = ''

        # Directory information
        directory = '/empiar/world_availability/' + self.entryID.get() + '/data/Movies'

        # Establish the connection
        ftp = ftplib.FTP(server)
        ftp.login(username, password)

        # Change to the proper directory
        ftp.cwd(directory)

        # Loop through files and download each one individually into a specific
        # directory
        imagesCount = 1
        for filename in ftp.nlst():
            fileAbsPath = os.path.join(self._getTmpPath(), filename)
            if not os.path.exists(fileAbsPath):
                fhandle = open(fileAbsPath, 'wb')
                print(pwutils.yellowStr('Getting: ' + filename), flush=True)
                ftp.retrbinary('RETR ' + filename, fhandle.write)
                fhandle.close()
                shutil.move(fileAbsPath, self._getExtraPath(filename))
                imagesCount += 1
                if imagesCount > self.amountOfImages.get():
                    break
        ftp.close()

    def _summary(self):
        summary = []
        if hasattr(self, 'empiarName'):
            summary.append('Name: ' + str(self.empiarName))
            summary.append('Author: ' + str(self.organization))
            summary.append('Deposition Date: ' + str(self.depositionDate))
            summary.append('Title: ' + str(self.title))
            summary.append('Release Date: ' + str(self.releaseDate))
            summary.append('Dataset Size: ' + str(self.datasetSize))
        return summary

    def _validate(self):
        errors = []
        return errors