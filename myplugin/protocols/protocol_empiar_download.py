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
    _outputClassName = 'SetOfMovies'  # Defining the output class
    registerFiles = []                # saves the name of the movies that have been downloaded
    _stepsCheckSecs = 3               # time in seconds to check the steps

    def __init__(self, **args):
        EMProtocol.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL  # Defining that the protocol contain parallel steps

    # --------------- DEFINE param functions ---------------
    def _defineParams(self, form):
        form.addSection(label='Entry')
        # EMPIAR dataset ID
        form.addParam('entryID', params.StringParam, default='10200',
                      label='EMPIAR ID',
                      important=True,
                      allowsNull=False,
                      help='EMPIAR entry ID')
        # Stop criteria
        form.addParam('amountOfImages', params.IntParam,
                      default=5,
                      label='Amount of Images',
                      validators=[Positive],
                      help='Time that the protocol will be running expressed '
                           'in seconds')
        # Parallel section defining the number of threads and mpi to use
        form.addParallelSection(threads=3, mpi=1)

    # --------------- INSERT steps functions ----------------

    def _insertAllSteps(self):
        # read the dataset xml file from EMPIAR
        self.readXmlFile = self._insertFunctionStep('readXmlFileStep')
        # download the movies and register them in pararell
        self.downloadImages = self._insertFunctionStep('downloadImagesStep')
        # close the registered dataset set
        self.closeSet = self._insertFunctionStep('closeSetStep', wait=True)
    # --------------- STEPS functions -----------------------

    def readXmlFileStep(self):
        """
        Read the xml file of a specific dataset from EMPIAR repository
        """
        xmlFileID = self.entryID.get()  # dataset ID
        empiarXmlUrl = 'https://www.ebi.ac.uk/pdbe/emdb/empiar/api/entry/'  # URL of EMPIAR API
        empiarXmlUrl += xmlFileID
        try:
            xmlFile = requests.get(empiarXmlUrl, allow_redirects=True)  # getting the xml file
            content = (json.loads(xmlFile.content.decode('utf-8')))  # extract the xml content
            empiarName = 'EMPIAR-' + xmlFileID
            self.empiarName = String(empiarName)  # dataset name
            self.corresponingAuthor = content[empiarName]['corresponding_author']  # dataset authors
            self.organization = String(self.corresponingAuthor['author']['organization'])  # authors organization
            self.depositionDate = String(content[empiarName]['deposition_date'])  # dataset deposition date
            self.title = String(content[empiarName]['title'])  # dataset title
            self.imageSets = content[empiarName]['imagesets']  # dataset images information
            self.releaseDate = String(content[empiarName]['release_date'])  # dataset release date
            self.datasetSize = String(content[empiarName]['dataset_size'])  # dataset size
            self.samplingRate = Float(self.imageSets[0]['pixel_width'])  # images sampling rate
            self.dataFormat = String(self.imageSets[0]['data_format'])  # images format
            self._store(self)
        except Exception as ex:
            self.setFailed(msg="There was an error downloading the EMPIAR raw "
                               "images: %s!!!" % ex)

    def downloadImagesStep(self):
        """
        This method connect to EMPIAR repository and download a set of images
        into a specific directory
        """
        # import time
        # time.sleep(10)
        # return

        # Connection information
        server = 'ftp.ebi.ac.uk'
        username = 'anonymous'
        password = ''

        # Directory information
        directory = ('/empiar/world_availability/' + self.entryID.get() +
                     '/data/Movies')

        # Establish the connection
        ftp = ftplib.FTP(server)
        ftp.login(username, password)

        # Change to the proper directory
        ftp.cwd(directory)

        # Loop through files and download each one individually into a specific
        # directory until the stop criteria met
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

    def closeSetStep(self):
        """
        Close the registered set
        """
        self.outputMovies.setStreamState(SetOfMovies.STREAM_CLOSED)
        self.outputMovies.write()
        self._store()

    def _stepsCheck(self):
        """ Input movie set can be loaded or None when checked for new inputs
            If None, we load it.
            To allow streaming register a movies we need to detect a new
            movie ready to register into the extra path folder
            Add as prerequisites(registerImageStep) to the last step(closeSetStep)
        """
        depStepsList = []
        if len(self.registerFiles) < self.amountOfImages.get():
            for file in os.listdir(self._getExtraPath()):
                if file not in self.registerFiles:
                    self.registerFiles.append(file)
                    # Creating a new step to register the new movie
                    newStep = self._insertFunctionStep('registerImageStep',
                                                        file,
                                                        prerequisites=[])
                    depStepsList.append(newStep)
                    # adding as prerequisites the new step to closeSetStep
                    self._steps[self.closeSet - 1].addPrerequisites(*depStepsList)

            if len(self.registerFiles) >= self.amountOfImages.get(): # The closeSetStep is ready to launch
                self._steps[self.closeSet-1].setStatus(STATUS_NEW)

            # Updating the protocol steps
            self.updateSteps()

    def registerImageStep(self, file):
        """
        Register an image taking into account a file path
        """
        newImage = Movie(location=self._getExtraPath(file))
        newImage.setSamplingRate(self.samplingRate.get())
        self._addMovieToOutput(newImage)

    def _addMovieToOutput(self, movie):
        """
        Returns the output set, if not available create an empty one
        """
        if hasattr(self, 'outputMovies'):  # the output is defined
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