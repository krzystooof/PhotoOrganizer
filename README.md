# Photo Organizer
A simple app that organize movies and videos into folders.

Example result folder tree:
```
.
├── 2019
│   ├── 02
│   │   └── 09
│   └── 04
│       └── 28
├── 2020
│   └── 01
│       ├── 01
│       ├── 03
│       ├── 04
│       └── 05
├── no_time
└── videos
```

Where `no_time` contains all files that script couldn't find EXIF media taken date, except below.

### For iPhone users:
The camera app in `High Efficiency` mode takes photos in `HEIC` format.
Moreover if you are using `live` option - after capturing there are two files created:
- `photo` with some name (ex. `IMG_001.HEIC`)
- `video` with name same as `photo` but ending with `(1)` (ex. `IMG_001(1).HEIC`)

The script cannot read EXIF info from `video`, but after moving it will look for localization of photos for every `HEIC` `video`. If it can find it, script will move `video` to `photo` folder.

## Arguments:
### Mandatory:
* `-i <input directory>` directory where PhotoOrganizer will operate
* `-o <output directory>` directory where results in given folder structure will be created