import os
import subprocess
import sys
from pathlib import Path

import exifread
import datetime

input_path = ""
output_path = ""
trash_path = ""
after_command = ""
log_path = str(Path.home())


def read_date(image_path):
    with open(image_path, 'rb') as file:
        tags = exifread.process_file(file)
        try:
            # return Image Taken Time
            return str(tags["EXIF DateTimeOriginal"])
        except KeyError:
            # if cant find Image Taken Time - I belive this only occurs when file is not a photo
            return None


def move(old_path, new_path, file_name):
    try:
        os.rename(old_path + os.sep + file_name, new_path + os.sep + file_name)
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


def move_to_trash(file_path):
    old_path, file_name = os.path.split(file_path)

    move(old_path, trash_path, file_name)


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
        save_log("Output file locked - another process in progress")
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


if __name__ == '__main__':
    input_path, output_path, after_command = get_arguments(sys.argv)

    create_lock(input_path)
    trashed = 0
    moved = 0
    for path in Path(input_path).rglob('*.*'):
        path = str(path)
        date_taken = read_date(path)
        if date_taken is not None:
            move_to_output(path, date_taken)
            moved += 1
        else:
            move_to_trash(path)
            trashed += 1
    after_message = ""
    if moved > 0 and len(after_command) > 0:
        try:
            subprocess.run(after_command).check_returncode()
            after_message = after_command + " succeed"
        except subprocess.CalledProcessError:
            after_message = after_command + " failed"
    message = str(moved) + " Photos moved from " + input_path + " to " + output_path + ", " + str(
        trashed) + " trashed to " + trash_path
    if len(after_message) > 0:
        message += "\n\t" + after_message
    save_log(message)
    delete_lock()
