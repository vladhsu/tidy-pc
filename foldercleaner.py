import os
import shutil
import hashlib
import logging
import json

logging.basicConfig(level=logging.INFO)



# Create load config funcion
def loadConfiguration(configFile):
    if not os.path.isfile(configFile):
        logging.error(f"Config file {configFile} does not exist.")
        raise ValueError(f"Config file {configFile} does not exist.")
    try:
        with open(configFile) as file:
        # Load config file from a JSON file
            return json.load(file)
    except:
        json.JSONDecodeError(f"Config file {configFile} is not a valid JSON file.")
        raise ValueError(f"Config file {configFile} is not a valid JSON file.")


def organiseFiles(sourceFolder, config):

    if not os.path.exists(sourceFolder):
        logging.error(f"Source folder does not exist.")
        raise FileNotFoundError(f"Source folder does not exist.")
    
    fileTypes = config.get("fileTypes", {})

    # Create folders for each file type
    for folder in fileTypes.values():
        folderPath = os.path.join(sourceFolder, folder)
        try:
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
        except OSError:
            logging.error(f"Failed to create directory {folderPath}.")
            raise

    # Create a dictionary to keep track of file hashes
    fileHashes = {}

    # Iterate over the files in the source folder
    for filename in os.listdir(sourceFolder):
        filePath = os.path.join(sourceFolder, filename)
        if os.path.isfile(filePath):
            # Calculate the file hash
            fileHash = hashFile(filePath)

            # Check for duplicates
            if fileHash in fileHashes.values():
                duplicateFolder = os.path.join(sourceFolder, "Duplicates")
                try:
                    if not os.path.exists(duplicateFolder):
                        os.makedirs(duplicateFolder)
                except OSError:
                    logging.error(f"Failed to create directory {duplicateFolder}.")
                    raise

                destinationFilePath = os.path.join(duplicateFolder, filename)
                try:
                    shutil.move(filePath, destinationFilePath)
                except shutil.Error:
                    logging.error(f"Failed to move file {filePath} to {destinationFilePath}.")
                    raise
            else:
                if filename in fileHashes.keys():
                    # If a file with the same name but different content exists
                    base, extension = os.path.splitext(filename)
                    i = 1
                    while filename in fileHashes.keys():
                        filename = f"{base}({i}){extension}"
                        i += 1
                fileHashes[filename] = fileHash

                # Determine the destination folder based on the file type
                fileExtension = filename.split(".")[-1]
                destinationFolder = fileTypes.get(fileExtension, "Others")
                destinationFolderPath = os.path.join(sourceFolder, destinationFolder)
                try:    
                    if not os.path.exists(destinationFolderPath):
                        os.makedirs(destinationFolderPath)
                except OSError:
                    logging.error(f"Failed to create directory {destinationFolderPath}.")
                    raise

                # Move the file to the correct destination
                destinationFilePath = os.path.join(destinationFolderPath, filename)
                try:
                    shutil.move(filePath, destinationFilePath)
                except shutil.Error:
                    logging.error(f"Failed to move file {filePath} to {destinationFilePath}.")
                    raise


def hashFile(filePath, num_bytes=1024):

    #Calculate the hash of the file
    hasher = hashlib.sha256()

    try:
        with open(filePath, 'rb') as f:
            data = f.read(num_bytes)
            if len(data) < num_bytes:
                logging.warning(f"File {filePath} is smaller than {num_bytes} bytes")
            hasher.update(data)
            f.seek(-num_bytes, 2)
            data = f.read(num_bytes)
            if len(data) < num_bytes:
                logging.warning(f"File {filePath} is smaller than {num_bytes} bytes")
            hasher.update(data)
    except FileNotFoundError:
        logging.error(f"File {filePath} not found.")
        raise
    except IOError:
        logging.error(f"Error opening file {filePath}.")
        raise

    return hasher.hexdigest()
