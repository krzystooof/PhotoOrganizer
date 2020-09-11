#!/usr/bin/env python3

import os
import shutil
import sys
from pathlib import Path
import time

import exifread
import datetime
from enum import Enum


class FileType(Enum):
    TRASH = 1
    VIDEO = 2
    PHOTO = 3

class FolderStructure(Enum):
    YYYY = 1
    YYYY_MM = 2
    YYYY_MM_DD = 3
    MM = 5
    MM_DD = 6
    DD = 7
    DD_MM = 8
    YYYY_DD_MM =9
    DD_MM_YYYY=10
    MM_DD_YYYY=11

    @classmethod
    def exists(cls, name):
        return name in FolderStructure.__members__



def read_date(image_path):
    try:
        with open(image_path, 'rb') as file:
            tags = exifread.process_file(file)
            try:
                # return Image Taken Time
                return str(tags["EXIF DateTimeOriginal"])
            except KeyError:
                # if cant find Image Taken Time
                return None
    except IsADirectoryError:
        return None


def check_file_exist(path, file_name):
    if os.path.isfile(path + os.sep + file_name):
        return True
    else:
        return False


def move(old_path, new_path, file_name):
    # do not overwrite - check if file exist
    output_file_name = file_name
    while check_file_exist(new_path, output_file_name):
        extension = get_file_extension(output_file_name)
        name = get_file_name(output_file_name)
        name += "n"
        output_file_name = name + extension
    try:
        shutil.move(old_path + os.sep + file_name, new_path + os.sep + output_file_name)
    except FileNotFoundError:
        # if directory doesnt exist - create directory and start again
        os.makedirs(new_path)
        move(old_path, new_path, file_name)


def move_to_output(image_path: str, date_taken: str, folder_structure: FolderStructure):
    splitted_date = date_taken.split(':')
    year = splitted_date[0]
    month = splitted_date[1]
    day = splitted_date[2][:2]

    old_path, file_name = os.path.split(image_path)
    structure = str(folder_structure.name).split("_")
    new_path = output_path
    for item in structure:
        if item == "YYYY":
            new_path += os.sep + year
        elif item == "MM":
            new_path += os.sep + month
        elif item == "DD":
            new_path += os.sep + day
    move(old_path, new_path, file_name)


def move_to(file_path, new_path):
    old_path, file_name = os.path.split(file_path)

    move(old_path, new_path, file_name)


def save_log(message):
    log_file_path = log_path + os.sep + "photo_organizer.log"
    # open with cursor in after last line
    with open(log_file_path, 'a') as log_file:
        log_file.write(str(datetime.datetime.now()) + ": " + message + "\n")


def create_lock():
    lock_file_path = input_path + os.sep + "photo_organizer.lock"
    try:
        # open for exclusive
        with open(lock_file_path, 'x') as lock_file:
            lock_file.write(str(datetime.datetime.now))
        save_log("Created lock")
    except FileExistsError:
        print("Directory locked - another process in progress")
        save_log("Directory locked - another process in progress")
        quit(1)


def delete_lock():
    lock_file_path = input_path + os.sep + "photo_organizer.lock"
    os.remove(lock_file_path)
    save_log("Deleted lock")


def show_help():
    print("Mandatory arguments:")
    print("-> -i <input directory> ")
    print("-> -o <output directory>")
    print("Optional arguments:")
    print("* videos moving and selecting directory:")
    print("-> --videos (move to default videos directory) or --videos <directory> (move to specified directory)")
    print("* photos without date taken moving and selecting directory:")
    print("-> --notime (move to default videos directory) or --notime <directory> (move to specified directory)")
    print("* files that are not photos or videos moving and selecting directory or removing:")
    print("-> --trash (remove from filesystem) or --trash <directory> (move to specified directory)")
    quit(2)


def get_argument(arg_prefix: str):
    arguments = sys.argv
    for index, arg in enumerate(arguments):
        if arg_prefix == arg:
            arg_value = arguments[index + 1]
            if arg_value[0] == "-":
                return None
            return arg_value
    raise ValueError("No argument with selected prefix")


def get_file_extension(path):
    extension = os.path.splitext(path)[1].lower()
    return str(extension)


def get_file_name(path):
    return os.path.splitext(path)[0]


def move_heic():
    # move heic movies to heic photos directories
    for path in Path(no_time_data_path).rglob('*.HEIC'):
        path = str(path)
        old_path, file_name = os.path.split(path)
        name_without_extension = get_file_name(file_name)
        extension = get_file_extension(file_name).upper()
        serached_name = name_without_extension[:-3]  # movies - <photo file name> + (1)
        # search for file in other directiories, if found move file to this directory
        searched_path = []
        for path2 in Path(output_path).rglob(serached_name + extension):
            searched_path.append(str(path2))
        if len(searched_path) == 1:
            searched_path, container = os.path.split(searched_path[0])
            move_to(path, searched_path)


def remove_empty_directories():
    for path in Path(input_path).rglob('*'):
        path = str(path)
        if os.path.isdir(path):
            try:
                os.rmdir(path)
            except OSError:
                # directiory not empty
                pass


def get_file_type(extension: str):
    if extension == 'png' or \
            extension == 'jpg' or \
            extension == 'gif' or \
            extension == 'jpeg' or \
            extension == 'heif' or \
            extension == 'heic':
        return FileType.PHOTO
    elif extension == 'mov' or \
            extension == 'mp4' or \
            extension == 'm4v' or \
            extension == 'wmv' or \
            extension == 'mpg' or \
            extension == 'avi':
        return FileType.VIDEO
    elif extension == 'xmp' or \
            extension == 'json' or \
            extension == 'info' or \
            extension == 'db' or \
            extension == 'lnk' or \
            extension == 'xml' or \
            extension == 'tmp' or \
            extension == 'ini' or \
            extension == 'xcf' or \
            extension == 'nri' or \
            extension == 'mswmm':
        return FileType.TRASH


def move_files(videos_path:str, no_time_data_path:str, trash_path:str,folder_structure):
    moved = 0
    for path in Path(input_path).rglob('*.*'):
        path = str(path)
        if get_file_extension(path)[1:] != 'lock':
            date_taken = read_date(path)
            print(path + ": " + str(date_taken))
            if date_taken is not None:
                move_to_output(path, date_taken,folder_structure)
                moved += 1
            else:
                extension = get_file_extension(path)[1:]
                if get_file_type(extension) == FileType.PHOTO:
                    if no_time_data_path is not None:
                        move_to(path, no_time_data_path)
                        moved += 1
                elif get_file_type(extension) == FileType.VIDEO:
                    if videos_path is not None:
                        move_to(path, videos_path)
                        moved += 1
                elif get_file_type(extension) == FileType.TRASH:
                    if trash_path == "nopath":
                        os.remove(path)
                    elif trash_path is None:
                        pass
                    else:
                        move_to(path, videos_path)
    return moved


if __name__ == '__main__':
    log_path = str(Path.home())
    try:
        input_path = get_argument("-i")
    except ValueError:
        print("PLEASE SPECIFY INPUT DIRECTORY")
        show_help()
    try:
        output_path = get_argument("-o")
    except ValueError:
        print("PLEASE SPECIFY OUTPUT DIRECTORY")
        show_help()
    try:
        videos_path = get_argument("--videos")
        if videos_path is None:
            videos_path = output_path + os.sep + "videos"
    except ValueError:
        videos_path = None
    try:
        no_time_data_path = get_argument("--notime")
        if no_time_data_path is None:
            no_time_data_path = output_path + os.sep + "no_time"
    except ValueError:
        no_time_data_path = None
    try:
        trash_path = get_argument("--trash")
        if trash_path is None:
            trash_path = "nopath"
    except ValueError:
        trash_path = None
    try:
        folder_structure = get_argument("--structure")
        if folder_structure is None or not FolderStructure.exists(folder_structure):
            print("FOLDER STRUCTURE SHOULD BE ONE OF:")
            print(list(FolderStructure))
            show_help()
    except ValueError:
        folder_structure = FolderStructure.YYYY_MM_DD
    while True:
        print(str(time.asctime()) + " Starting. Input: " + input_path + ". Output: " + output_path)

        create_lock()

        moved = move_files(videos_path, no_time_data_path, trash_path,folder_structure)

        remove_empty_directories()

        move_heic()

        delete_lock()

        time.sleep(60)
