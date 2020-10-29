import json
import requests
import ftplib
import os
import shutil

from pwem.objects import Movie, SetOfMovies, Float
from pwem.protocols import EMProtocol
from pyworkflow.protocol import params, String, STATUS_NEW, STEPS_PARALLEL
import pyworkflow.utils as pwutils


class EmpiarDownloader(EMProtocol):
    """
    Download movies sets from EMPIAR
    """
    _label = 'empiar downloader'
    _outputClassName = 'SetOfMovies'  # Defining the output class
    registeredFiles = []              # saves the name of the movies that have been already registered
    _stepsCheckSecs = 3               # time in seconds to check the steps

    def __init__(self, **args):
        EMProtocol.__init__(self, **args)
        self.stepsExecutionMode = STEPS_PARALLEL  # Defining that the protocol contain parallel steps

    def _defineParams(self, form):
        # add a section
        form.addSection("Entry")

        # add a parameter to capture the EMPIAR entry ID:
        # name --> entryId, String param, default value 10200, you choose the label
        # Ideally we want it in bold is "important", it should not be empty, and fill the help.
        form.addParam("entryId", params.StringParam, label="EMPIAR identifier", default="10200",
                      help="EMPIAR's entry identifier", important=True)
        # add another parameter to set a limit of downloaded files:
        # name-->amountOfImages, Integer param , default to 1, choose the label and the help
        # it has to be positive (use "validators" argument, it expects a list of
        # pyworkflow.protocol.params.Validator, look for the Positive Validator)
        form.addParam("amountOfImages", params.IntParam, label="Number of files", default=1,
                      help="Number of files to download", validators=[params.Positive])

        # Parallel section defining the number of threads and mpi to use
        form.addParallelSection(threads=3, mpi=1)

    def _insertAllSteps(self):
        self.readXmlFile = self._insertFunctionStep('readXmlFileStep')  # read the dataset xml file from EMPIAR
        self.downloadImages = self._insertFunctionStep('downloadImagesStep')  # download the movies and register them in parallel
        self.closeSet = self._insertFunctionStep('closeSetStep', wait=True)  # close the registered dataset set

    def downloadImagesStep(self):
        # Call the method provided below
        # Make the download happen in the tmp folder of the protocol and the final folder to be the extra folder
        downloadImagesFromEmpiar(self.entryId.get(),self._getTmpPath(),
                                 self._getExtraPath(),limit=self.amountOfImages.get())

    def registerImageStep(self, file):
        """
        Register an image taking into account a file path
        """
        # Create a Movie object having file as the location: see pwem.objects.data.Movie()
        newImage = Movie(location=self._getExtraPath(file))

        # Set the movie sampling rate to the sampling rate obtained in the readXmlFromEmpiar step
        newImage.setSamplingRate(self.samplingRate.get())

        # Pass the movie to _addMovieToOutput
        self._addMovieToOutput(newImage)

    def _stepsCheck(self):
        """ Adds as many registerImageStep as new files appears in the extra folder
        """
        # Declare a list to keep all new steps added (newSteps)
        newSteps = []

        # If the size of registeredFiles (object level attribute) is < amountOfImages (parameter)
        if len(self.registeredFiles) < self.amountOfImages.get():

            # loop through the files in the extra path
            for file in os.listdir(self._getExtraPath()):

                # if the file is not in our registeredFiles list
                if file not in self.registeredFiles:

                    # Append it to registeredFiles list
                    self.registeredFiles.append(file)

                    # Create a new step to register the new file
                    # use _insertFunctionStep with registerImageStep, file, and
                    # self.readXmlFile as a prerequisite
                    # and store the returned value in a variable (newStep)
                    newStep = self._insertFunctionStep("registerImageStep", file, prerequisites=[self.readXmlFile])

                    # append the newStep to the newSteps list declared at the beginning
                    newSteps.append(newStep)

        # Let's update the closeSetStep
        # Get the closeSetStep
        # Hint: any step is accessible with self._steps[stepId-1] --> what we stored in insertAllSteps
        closeSetStep = self._steps[self.closeSet-1]

        # Add the new steps as prerequisites for the closeSetStep
        # Use the addPrerequisites method of the closeSetStep
        # Be sure you pass the list as *newSteps
        closeSetStep.addPrerequisites(*newSteps)

        # If we have reached the limit of files (amountOfImages) compared to registeredFiles
        if len(self.registeredFiles) >= self.amountOfImages.get():

            # Free the waiting closeSet step by setting the Step.setStatus(STATUS_NEW)
            closeSetStep.setStatus(STATUS_NEW)

        # Update the protocol steps using updateSteps()
        self.updateSteps()

    def _addMovieToOutput(self, movie):
        """
        Returns the output set if not available create an empty one
        """
        # Do we have the attribute "outputMovies"?
        if hasattr(self, 'outputMovies'):  # the output is defined

            # Append the "movie" passed to the already existing output
            self.outputMovies.append(movie)

        # ... we do not have output yet. Probably first movie reported
        else:

            # Create the SetOfMovies using its create(path) method: pass the path of the protocol (hint: self._getPath())
            outputSet = SetOfMovies.create(self._getPath())

            # set the sampling rate: set.setSamplingRate() passing the stored sampling rate from the readXmlFromEmpiarStep
            # NOTE: Scipion objects are wrappers to actual python types. To get the python value use .get() method
            outputSet.setSamplingRate(self.samplingRate.get())

            # set the set's .streamState to open (set.setStreamState). Constant for the state is Set.STREAM_OPEN.
            outputSet.setStreamState(SetOfMovies.STREAM_OPEN)

            # append the movie to the new set just created
            outputSet.append(movie)

            # define the output in the protocol (_defineOutputs). Be sure you use outputMovies as the name of the output
            self._defineOutputs(outputMovies=outputSet)

        # In both cases, write the set to the disk. set.write() --> set.sqlite
        self.outputMovies.write()

        # Save the protocol with the new  status: protocol._store() --> run.db
        self._store()

    def readXmlFileStep(self):
        # Call the method provided below to get some data from the empiar xml
        title, samplingRate = readXmlFromEmpiar(self.entryId.get())

        # Store returned values as "persistent" attributes: String, Integer, Float
        self.title = String(title)
        self.samplingRate = String(samplingRate)

        # Use _store method to write them
        self._store()

    def closeSetStep(self):
        """
        Close the registered set
        """
        # Set the outputMovies streamState using setStreamState method with the value SetOfMovies.STREAM_CLOSED
        self.outputMovies.setStreamState(SetOfMovies.STREAM_CLOSED)

        # Save the outputMovies using the write() method
        self.outputMovies.write()

        # Save the protocol: Hint: _store()
        self._store()

    def _summary(self):
        summary = []

        # Check we have the summary attributes (readXmlStep has happened) (HINT: hasattr will do)
        if hasattr(self, "title"):
            # Add items to the summary list like:
            summary.append("Title: %s" % self.title)
            summary.append("Sampling rate: %s" % self.samplingRate)

            # How would you have more values in the summary? (HINT: return more values in readXmlFromEmpiar)

        return summary


# Helper methods #########################################################

def readXmlFromEmpiar(entryId):
        """
        Read the xml file of a specific dataset from EMPIAR repository
        """
        empiarXmlUrl = 'https://www.ebi.ac.uk/pdbe/emdb/empiar/api/entry/' + entryId  # URL of EMPIAR API

        xmlFile = requests.get(empiarXmlUrl, allow_redirects=True)               # getting the xml file
        content = (json.loads(xmlFile.content.decode('utf-8')))                  # extract the xml content
        empiarName = 'EMPIAR-' + entryId                                         # dataset name

        correspondingAuthor = content[empiarName]['corresponding_author']         # dataset authors
        organization = String(correspondingAuthor['author']['organization']) # authors organization
        depositionDate = String(content[empiarName]['deposition_date'])          # dataset deposition date
        title = String(content[empiarName]['title'])                             # dataset title
        imageSets = content[empiarName]['imagesets']                             # dataset images information
        releaseDate = String(content[empiarName]['release_date'])                # dataset release date
        datasetSize = String(content[empiarName]['dataset_size'])                # dataset size
        empiarName = String(empiarName)
        samplingRate = Float(imageSets[0]['pixel_width'])                   # images sampling rate
        dataFormat = String(imageSets[0]['data_format'])                    # images format

        # You may want to return more elements
        return title, samplingRate


def downloadImagesFromEmpiar(entryId, downloadFolder, finalFolder, limit=5):
    """
    This method connect to EMPIAR repository and download a set of images
    into a specific directory, once image is downloaded is moved to the final folder
    """
    # Connection information
    server = 'ftp.ebi.ac.uk'
    username = 'anonymous'
    password = ''

    # Directory information
    directory = '/empiar/world_availability/' + entryId + '/data/Movies'

    # Establish the connection
    ftp = ftplib.FTP(server)
    ftp.login(username, password)

    # Change to the proper directory
    ftp.cwd(directory)

    # Loop through files and download each one individually into a specific
    # directory until the stop criteria met
    imagesCount = 1
    for filename in ftp.nlst():
        fileAbsPath = os.path.join(downloadFolder, filename)
        if not os.path.exists(fileAbsPath):
            fhandle = open(fileAbsPath, 'wb')
            print(pwutils.yellowStr('Getting: ' + filename), flush=True)
            ftp.retrbinary('RETR ' + filename, fhandle.write)
            fhandle.close()
            shutil.move(fileAbsPath, os.path.join(finalFolder,filename))
            imagesCount += 1
            if imagesCount > limit:
                break
    ftp.close()
