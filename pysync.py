#!/usr/bin/python3

import os
import argparse
import sys
import time
import logging
from filemanager.logger import Logger
from filemanager.filemanager import FileManager, get_uid_gid, list_files_recursively, src2dst
from filemanager.hashcheker import HashChecker


'''
@author: Giovanni SCAFETTA
@version: 0.0.4
@description: This script is realized to syncronize two folders.
@license: GLPv3
'''


VERSION = "0.0.4"


def parse_arguments():
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser(description="Clone source folder to destination folder.")
  parser.add_argument("--src", required=True, help="Source Folder")
  parser.add_argument("--dst", required=True, help="Destination Folder")
  parser.add_argument("--hash-chk", action='store_true', help="Check hash if file exists in destination")
  parser.add_argument("--delete", action='store_true', help="Remove files not in source before sync")
  parser.add_argument("--delete-after", action='store_true', help="Remove files not in source after sync")
  parser.add_argument("--chown", required=False, help="Username/groupname mapping (USER:GROUP)")
  parser.add_argument("--progress", action='store_true', help="Show progress during transfer")
  parser.add_argument("--attribute", action='store_true', help="Copy files and attributes")
  parser.add_argument("--verbose", action='store_true', help="Verbose mode")
  parser.add_argument("--version", action='version', version=f"%(prog)s {VERSION}")

  # Check if no arguments are provided
  if len(sys.argv) == 1:
      parser.print_help()
      sys.exit(1)

  return parser.parse_args()

def validate_folders(src, dst):
  """Validate the existence of source and destination folders."""
  if not os.path.exists(src):
      logging.error(f"Error: Source folder '{src}' does not exist.")
      sys.exit(1)
  if not os.path.exists(dst):
      logging.error(f"Error: Destination folder '{dst}' does not exist.")
      sys.exit(1)

def synchronize_files(args, src_files, dst_files):
  """Synchronize files from source to destination."""
  fm = FileManager(args.src, args.dst)
  if args.delete:
      fm.remove_files_not_in_source(src_files, dst_files)
      fm.remove_empty_folders()

  for file in src_files:
      dst_file = src2dst(file, args.src, args.dst)
      if dst_file not in dst_files or (args.hash_chk and not HashChecker("md5", file, dst_file).file2file()):
          copy_file(file, dst_file, args)

  if args.delete_after:
      fm.remove_files_not_in_source(src_files, dst_files)
      fm.remove_empty_folders()

def copy_file(src_file, dst_file, args):
  """Copy a file from source to destination with attributes."""
  fm = FileManager(src_file, dst_file, preserve_permissions=args.attribute, preserve_times=args.attribute,
                   group=get_uid_gid(args.chown)[1] if args.chown else None,
                   owner=get_uid_gid(args.chown)[0] if args.chown else None,
                   status_bar=args.progress)
  fm.read_file_attributes()
  fm.copy_file()
  fm.apply_attributes_to_file()

def main():
  """Main function to parse arguments and manage synchronization."""
  args = parse_arguments()
  Logger.setup_logging(args.verbose)
  validate_folders(args.src, args.dst)

  
  try:
      src_files = list_files_recursively(args.src)
      dst_files = list_files_recursively(args.dst)
      logging.info("Starting the synchronization process...")
      start_time = time.time()  # Record the start time

      synchronize_files(args, src_files, dst_files)

      end_time = time.time()  # Record the end time
      elapsed_time = end_time - start_time
      hours, remainder = divmod(elapsed_time, 3600)
      minutes, seconds = divmod(remainder, 60)

      logging.info(f"The synchronization process has been completed after {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds.")
  except KeyboardInterrupt:
      logging.info("Operation cancelled by user.")
      sys.exit(0)

if __name__ == "__main__":
  main()

