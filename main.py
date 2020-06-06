#!/usr/bin/env python3

import os
import shutil
import sys
from pathlib import Path

import exifread
import datetime

input_path = "/media/veracrypt3/photos_to_add/"
output_path = "/media/veracrypt3/media/photos"
videos_path = output_path + os.sep + "videos"
no_time_data_path = output_path + os.sep + "no_time"
log_path = str(Path.home())

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


def move_to_output(image_path, date_taken):
    splitted_date = date_taken.split(':')
    year = splitted_date[0]
    month = splitted_date[1]
    day = splitted_date[2][:2]

    old_path, file_name = os.path.split(image_path)

    new_path = output_path + os.sep + year + os.sep + month + os.sep + day
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


def show_help(name):
    print("Usage: " + name + " <photo input directory> <photo output directory")
    print("\tex." + name + " Downloads/Wedding/ Photos/")


def get_arguments(argvs):
    if len(argvs) is 3:
        return argvs[1], argvs[2]
    else:
        show_help(argvs[0])
        quit(2)


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
        if len(searched_path) is 1:
            searched_path, container = os.path.split(searched_path[0])
            move_to(path, searched_path)


def remove_empty_directiories():
    for path in Path(input_path).rglob('*'):
        path = str(path)
        if os.path.isdir(path):
            try:
                os.rmdir(path)
            except OSError:
                # directiory not empty
                pass


def move_files():
    moved = 0

    for path in Path(input_path).rglob('*.*'):
        path = str(path)
        if get_file_extension(path)[1:] != 'lock':
            date_taken = read_date(path)
            print(path + ": " + str(date_taken))
            if date_taken is not None:
                move_to_output(path, date_taken)
                moved += 1
            else:

                # photos
                if get_file_extension(path)[1:] == 'png':
                    move_to(path, no_time_data_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'jpg':
                    move_to(path, no_time_data_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'gif':
                    move_to(path, no_time_data_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'jpeg':
                    move_to(path, no_time_data_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'heif':
                    move_to(path, no_time_data_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'heic':
                    move_to(path, no_time_data_path)
                    moved += 1
                # videos
                elif get_file_extension(path)[1:] == 'mov':
                    move_to(path, videos_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'mov':
                    move_to(path, videos_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'mp4':
                    move_to(path, videos_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'm4v':
                    move_to(path, videos_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'wmv':
                    move_to(path, videos_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'mpg':
                    move_to(path, videos_path)
                    moved += 1
                elif get_file_extension(path)[1:] == 'avi':
                    move_to(path, videos_path)
                    moved += 1
                # delete
                elif get_file_extension(path)[1:] == 'xmp':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'json':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'info':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'db':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'lnk':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'xml':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'tmp':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'ini':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'xcf':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'mswmm':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'nri':
                    os.remove(path)
    return moved


if __name__ == '__main__':
    # input_path, output_path = get_arguments(sys.argv)
    # videos_path = output_path + os.sep + "videos"
    # no_time_data_path = output_path + os.sep + "no_time"

    create_lock()

    moved = move_files()

    remove_empty_directiories()

    move_heic()

    delete_lock()
