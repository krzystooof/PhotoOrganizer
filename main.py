import os
from pathlib import Path

import exifread
import datetime

input_path = ""
output_path = ""
trash_path = ""
after_command = ""


def read_date(image_path):
    with open(image_path, 'rb') as file:
        tags = exifread.process_file(file)
        try:
            return str(tags["EXIF DateTimeOriginal"])
        except KeyError:
            return None


def move(old_path, new_path, file_name):
    try:
        os.rename(old_path + os.sep + file_name, new_path + os.sep + file_name)
    except FileNotFoundError:
        os.makedirs(new_path)


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

    new_path = trash_path
    move(old_path, new_path, file_name)


def save_log(message):
    home = str(Path.home())
    log_file_path = home + os.sep + "photo_organizer.log"
    with open(log_file_path, 'a') as log_file:
        log_file.write(str(datetime.datetime.now()) + ": " + message + "\n")


def create_lock():
    lock_file_path = input_path + os.sep + "photo_organizer.lock"
    try:
        with open(lock_file_path, 'x') as lock_file:
            lock_file.write(str(datetime.datetime.now))
        save_log("Created lock")
    except FileExistsError:
        save_log("Output file locked - another process in progress")
        quit()


if __name__ == '__main__':
    # TODO get arguments and assign them

    create_lock()
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
    # TODO execute after_command
    # TODO delete lock
