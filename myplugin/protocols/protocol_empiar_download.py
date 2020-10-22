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
import threading
import os

from pwem import SAMPLING_FROM_IMAGE
from pwem.protocols import (ProtImportMovies,  ProtImportMicrographs)
from pwem.protocols.protocol_import.micrographs import ProtImportMicBase
from pyworkflow.protocol import (params, Positive, String, Boolean, Integer,
                                 Float)
import pyworkflow.utils as pwutils


class EmpiarDownloader(ProtImportMovies, ProtImportMicrographs):
    """
    Download image sets from empiar
    """
    _label = 'empiar downloader'
    _outputClassName = 'SetOfMovies'

    # --------------- DEFINE param functions ---------------
    def _defineParams(self, form):
        self._defineCommondParams()
        form.addSection(label='Entry')
        form.addParam('entryID', params.StringParam, default='10200',
                      label='EMPIAR ID',
                      important=True,
                      allowsNull=False,
                      help='EMPIAR entry ID')

        form.addParam('entryType', params.EnumParam, default=0,
                      choices=['Movies', 'Micrographs'],
                      label='Type of data')
        form.addParam('filesPattern', params.StringParam, default='*.tif',
                      label='Pattern',
                      help="Pattern of the files to be imported.\n\n"
                           "The pattern can contain standard wildcards such as\n"
                           "*, ?, etc, or special ones like ### to mark some\n"
                           "digits in the filename as ID.\n\n"
                           "NOTE: wildcards and special characters "
                           "('*', '?', '#', ':', '%') cannot appear in the "
                           "actual path.")

        form.addSection('Streaming')
        form.addParam('timeout', params.IntParam,
                      default=43200,
                      label='Time Out',
                      validators=[Positive],
                      help='Time that the protocol will be running expressed in seconds')
        form.addParam('fileTimeout', params.IntParam, default=20,
                      label="File timeout (secs)",
                      help="Interval of time (in seconds) after which, if a file has "
                           "not changed, we consider it as a new file. \n")

    def _defineCommondParams(self):
        self.importFrom = Integer(self.IMPORT_FROM_FILES)
        self.dataStreaming = Boolean(True)
        self.haveDataBeenPhaseFlipped = Boolean(False)
        self.inputIndividualFrames = Boolean(False)
        self.blacklistSet = String(None)
        self.blacklistDateFrom = String()
        self.blacklistDateTo = String()
        self.blacklistFile = String()
        self.copyFiles = False
        self.dataStreaming = Boolean(True)
        self.samplingRateMode = Integer(SAMPLING_FROM_IMAGE)
        self.samplingRate = Float(1.0)
        self.voltage = Float(300.0)
        self.sphericalAberration = Float(2.7)
        self.amplitudeContrast = Float(0.1)
        self.magnification = Integer(50000)
        self.doseInitial = Float(0)
        self.dosePerFrame = Float(None)
        self.flag = False
        self._store(self)

    # --------------- INSERT steps functions ----------------

    def _insertAllSteps(self):
        self._insertFunctionStep('_downloadXmlFile')
        self._insertFunctionStep('importImages')
    # --------------- STEPS functions -----------------------

    def _downloadXmlFile(self):
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
            self.filesPath = String(self._getExtraPath())
            self.dataFormat = String(content[empiarName]['data_format'])

            if self.entryType.get() == 0:
                self._outputClassName = 'SetOfMovies'
            else:
                self._outputClassName = 'SetOfMicrograph'
            self._store(self)
        except Exception as ex:
            self.setFailed(msg="There was an error downloading the EMPIAR raw "
                               "images !!!")

    def importImages(self):
        """
        Import a set of images from EMPIAR repository
        """
        import time
        threadImportImages = threading.Thread(name="loading_plugin",
                                            target=self._downloadSetOfImages)
        threadImportImages.start()
        while not self.flag:
            time.sleep(2)
        self.importImagesStreamStep(self.filesPattern.get(), voltage=self.voltage,
                                    sphericalAberration=self.sphericalAberration,
                                    amplitudeContrast=self.amplitudeContrast,
                                    magnification=self.magnification)

    def _downloadSetOfImages(self):
        """
        This method connect to EMPIAR repository and download a set of images
        into a specific directory
        """
        # Connection information
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
        for filename in ftp.nlst():
            fileAbsPath = os.path.join(self.filesPath.get(), filename)
            if not os.path.exists(fileAbsPath):
                fhandle = open(fileAbsPath, 'wb')
                print(pwutils.yellowStr('Getting: ' + filename), flush=True)
                ftp.retrbinary('RETR ' + filename, fhandle.write)
                fhandle.close()
                self.flag = True
                if self.streamingHasFinished():
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

    def setSamplingRate(self, movieSet):
        ProtImportMicBase.setSamplingRate(self, movieSet)
        acq = movieSet.getAcquisition()
        acq.setDoseInitial(self.doseInitial.get())
        acq.setDosePerFrame(None)

    def getCopyOrLink(self):
        return self.ignoreCopy