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

from pwem.protocols import EMProtocol
from pyworkflow.protocol import params, Positive, String


class EmpiarDownloader(EMProtocol):
    """
    Download image sets from empiar
    """
    _label = 'Empiar downloader'

    # --------------- DEFINE param functions ---------------
    def _defineParams(self, form):
        form.addSection(label='Entry')
        form.addParam('entryID', params.StringParam,
                      label='EMPIAR ID',
                      important=True,
                      help='EMPIAR entry ID')
        form.addParam('downloadByTime', params.BooleanParam, default=False,
                      label='Download by time?')
        form.addParam('timeSleep', params.IntParam,
                      condition='downloadByTime==True',
                      label='Time Sleep',
                      validators=[Positive],
                      help='Time that the protocol will be running')
        form.addParam('amountOfImages', params.IntParam,
                      condition='downloadByTime==False',
                      label='Amount of images to download',
                      validators=[Positive],
                      help='Amount of images to download from a specific set')

        form.addParam('filesPath', params.PathParam, default=self._getExtraPath(),
                      label="Download directory",
                      help="Directory where the images will be downloaded.")


    # --------------- INSERT steps functions ----------------

    def _insertAllSteps(self):
        self._downloadXmlFile()
        self._downloadSetOfImages()

    # --------------- STEPS functions -----------------------

    def _downloadXmlFile(self):
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
            self._store(self)
        except Exception as ex:
            self.setFailed(msg="There was an error downloading the EMPIAR raw images !!!")


    def _downloadSetOfImages(self):
        import time
        time.sleep(5)
        if not self.downloadByTime:
            imagesToDownload = self.amountOfImages
            for imageSet in self.imageSets:
                if imagesToDownload > 0:
                    noImages = int(imageSet['num_images_or_tilt_series'])
                    directory = imageSet['directory']
                    for i in range(noImages):

                        imagesToDownload -= 1
                    print(imageSet)
                else:
                    break

        return

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


