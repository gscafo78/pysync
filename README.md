<img src="https://github.com/gscafo78/pysync/blob/main/img/pysync_logo.gif" alt="PySync Logo" width="500" height="150">

PySync
===

![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=gscafo78.pysinc)
[![License: GPL](https://img.shields.io/badge/License-GPL-blue.svg)](https://github.com/gscafo78/repocreate/blob/main/LICENSE)
![Python Version](https://img.shields.io/badge/Python-3.11.2-blue)
[![Email](https://img.shields.io/badge/Email-giovanni.scafetta@gmx.com-blue)](mailto:giovanni.scafetta@gmx.com)


## Overview

This script is designed to synchronize two folders, ensuring that the destination folder is updated to match the source folder. It offers various options for file synchronization, including hash checking, file deletion, and attribute preservation.

## Features

- Synchronize files from a source folder to a destination folder.
- Option to check file hashes before copying.
- Remove files not present in the source folder before or after synchronization.
- Preserve file attributes such as permissions and timestamps.
- Change file ownership during synchronization.
- Display progress during file transfer.
- Verbose mode for detailed logging.

## Requirements

- Python 3.x
- Required Python packages: `os`, `argparse`, `sys`, `time`, `logging`
- Custom modules: `filemanager.logger`, `filemanager.filemanager`, `filemanager.hashcheker`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/gscafo78/pysync.git
```

2. Navigate to the project directory:

```bash
cd pysync
```
3. Ensure all dependencies are installed and available in your Python environment.

## Usage

Run the script with the required arguments:

```bash
python3 pysync.py --src <source_folder> --dst <destination_folder> [options]
```

### Options

- `--src`: Source folder path (required).
- `--dst`: Destination folder path (required).
- `--hash-chk`: Check file hash if the file exists in the destination.
- `--delete`: Remove files not in the source before synchronization.
- `--delete-after`: Remove files not in the source after synchronization.
- `--chown`: Change file ownership using `USER:GROUP` format.
- `--progress`: Show progress during file transfer.
- `--attribute`: Copy files with their attributes.
- `--verbose`: Enable verbose mode for detailed logging.
- `--version`: Display the script version.
  
### Example

Synchronize two folders with hash checking and verbose output:

```bash
python3 pysync.py --src /path/to/source --dst /path/to/destination --hash-chk --progress
```
## License

This project is licensed under the  [GNU General Public License v3.0 (GLPv3)](LICENSE).

## Author

For questions or support, please contact [giovanni.scafetta@gmx.com](mailto:giovanni.scafetta@gmx.com).

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## Acknowledgments

This script utilizes custom modules for file management and logging. Ensure these modules are correctly implemented and available in your project structure.