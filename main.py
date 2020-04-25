import os
import shutil
import subprocess
import sys
from pathlib import Path

import exifread
import datetime

input_path = ""
output_path = ""
after_command = ""
log_path = str(Path.home())

#TODO move .heic videos from no_time to .heic photo folder (video name = photo name +(1)

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
    print("Usage: " + name + " <photo input directory> <photo output directory> optionally: <'command to execute after "
                             "organizing'>")
    print("\tex." + name + " Downloads/Wedding/ Photos/ '7z a backup/photos.zip Photos/*'")


def get_arguments(argvs):
    if len(argvs) is 3:
        return argvs[1], argvs[2], ""
    elif len(argvs) is 4:
        return argvs[1], argvs[2], argvs[3]
    else:
        show_help(argvs[0])
        quit(2)


def get_file_extension(path):
    extension = os.path.splitext(path)[1].lower()
    return str(extension)


def get_file_name(path):
    return os.path.splitext(path)[0]


if __name__ == '__main__':
    input_path, output_path, after_command = get_arguments(sys.argv)

    create_lock()

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
                videos_path = output_path + os.sep + "videos"
                no_time_data_path = output_path + os.sep + "no_time"

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
                # delete
                elif get_file_extension(path)[1:] == 'xmp':
                    os.remove(path)
                elif get_file_extension(path)[1:] == 'json':
                    os.remove(path)

    # remove empty directories
    for path in Path(input_path).rglob('*'):
        path = str(path)
        if os.path.isdir(path):
            try:
                os.rmdir(path)
            except OSError:
                # directiory not empty
                pass

    after_message = ""
    if moved > 0 and len(after_command) > 0:
        print("Calling " + after_command)
        exit_status = subprocess.call(after_command.split(' '))
        after_message = after_command + "exit status: " + exit_status
    message = str(moved) + " Photos moved from " + input_path + " to " + output_path
    if len(after_message) > 0:
        message += "\n\t" + after_message
    save_log(message)

    delete_lock()
