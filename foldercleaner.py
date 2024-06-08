import os
import shutil
import hashlib
import logging
import json
from PySide6.QtWidgets import QInputDialog, QMessageBox
from PySide6.QtCore import Qt
from collections import Counter

logging.basicConfig(level=logging.INFO)

LARGE_FILE_SIZE_THRESHOLD = 100000000

def loadConfiguration(configFile):
    if not os.path.isfile(configFile):
        logging.error(f"Config file {configFile} does not exist.")
        raise ValueError(f"Config file {configFile} does not exist.")
    try:
        with open(configFile) as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error(f"Config file {configFile} is not a valid JSON file.")
        raise ValueError(f"Config file {configFile} is not a valid JSON file.")

def get_user_action_for_large_file(parent, file_path):
    file_size = os.path.getsize(file_path)
    if file_size > LARGE_FILE_SIZE_THRESHOLD:
        options = ["Organise", "Archive", "Delete", "Skip"]
        item, ok = QInputDialog.getItem(parent, "Large File Detected",
                                        f"{os.path.basename(file_path)} is large. What would you like to do with this file?",
                                        options, 0, False)
        if ok and item:
            return item
    return "Organise"

def handle_large_file(parent, file_path):
    action = get_user_action_for_large_file(parent, file_path)
    if action == "Skip":
        return False  # Skip this file
    elif action == "Delete":
        os.remove(file_path)  # Delete this file
        return False
    elif action == "Archive":
        archives_folder = os.path.join(os.path.dirname(file_path), 'Archives')
        if not os.path.exists(archives_folder):
            os.makedirs(archives_folder)

        file_hash = hashFile(file_path)
        for root, dirs, files in os.walk(archives_folder):
            for file in files:
                existing_file_path = os.path.join(root, file)
                existing_file_hash = hashFile(existing_file_path)
                if file_hash == existing_file_hash:
                    return False

        archive_name = os.path.join(archives_folder, os.path.basename(file_path))
        shutil.make_archive(archive_name, 'zip', os.path.dirname(file_path), os.path.basename(file_path))
        os.remove(file_path)
        return False
    return True

def organiseFiles(parent, sourceFolder, config):
    if not os.path.exists(sourceFolder):
        logging.error(f"Source folder does not exist.")
        raise FileNotFoundError(f"Source folder does not exist.")
    
    fileTypes = config.get("fileTypes", {})

    fileHashes = {}

    for filename in os.listdir(sourceFolder):
        filePath = os.path.join(sourceFolder, filename)
        if os.path.isdir(filePath):
            continue

        if os.path.isfile(filePath) and not handle_large_file(parent, filePath):
            continue

        fileHash = hashFile(filePath)
        fileExtension = filename.split(".")[-1]
        destinationFolder = fileTypes.get(fileExtension, "Others")
        destinationFolderPath = os.path.join(sourceFolder, destinationFolder)

        is_duplicate = False
        if os.path.exists(destinationFolderPath):
            for existingFile in os.listdir(destinationFolderPath):
                existingFilePath = os.path.join(destinationFolderPath, existingFile)
                existingFileHash = hashFile(existingFilePath)
                if fileHash == existingFileHash:
                    is_duplicate = True
                    duplicateFolder = os.path.join(sourceFolder, "Duplicates")
                    if not os.path.exists(duplicateFolder):
                        os.makedirs(duplicateFolder)
                    destinationFilePath = os.path.join(duplicateFolder, filename)
                    shutil.move(filePath, destinationFilePath)
                    logging.info(f"Moved {filePath} to {destinationFilePath} as duplicate.")
                    break

        if not is_duplicate:
            base, extension = os.path.splitext(filename)
            i = 1
            new_filename = filename
            while new_filename in fileHashes:
                new_filename = f"{base}({i}){extension}"
                i += 1
            fileHashes[new_filename] = fileHash

            if not os.path.exists(destinationFolderPath):
                os.makedirs(destinationFolderPath)

            destinationFilePath = os.path.join(destinationFolderPath, new_filename)
            shutil.move(filePath, destinationFilePath)
            logging.info(f"Moved {filePath} to {destinationFilePath}.")

def deleteDuplicatesFolder(sourceFolder):
    duplicateFolder = os.path.join(sourceFolder, "Duplicates")
    if os.path.exists(duplicateFolder):
        try:
            shutil.rmtree(duplicateFolder)
            logging.info(f"Deleted the Duplicates folder.")
            return True
        except Exception as e:
            logging.error(f"Failed to delete the Duplicates folder: {str(e)}")
            return False

def hashFile(filePath, num_bytes=1024):
    hasher = hashlib.sha256()
    try:
        with open(filePath, 'rb') as f:
            file_size = os.path.getsize(filePath)
            if file_size <= num_bytes:
                data = f.read()
                hasher.update(data)
            else:
                data = f.read(num_bytes)
                hasher.update(data)
                f.seek(-num_bytes, 2)
                data = f.read(num_bytes)
                hasher.update(data)
    except FileNotFoundError:
        logging.error(f"File {filePath} not found.")
        raise
    except IOError:
        logging.error(f"Error opening file {filePath}.")
        raise
    return hasher.hexdigest()

def get_file_type_statistics(dir):
    file_types = Counter()
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            file_extension = os.path.splitext(filename)[1]
            file_types[file_extension] += 1
    return file_types
