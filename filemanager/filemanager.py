import os
import shutil
import logging
from tqdm import tqdm
import pwd
import grp
from concurrent.futures import ThreadPoolExecutor, as_completed


def split_path(path, root):
  """
  Splits a path into its directory and filename components,
  removing the root and returning the remaining path as a string.
  """
  # Step 1: Split the path into components
  components = path.split('/')
  
  # Step 2: Determine how many components to remove based on the root
  to_remove = len(root.split('/'))
  
  # Step 3: Remove the root components
  remaining_components = components[to_remove:]
  
  # Step 4: Join the remaining components into a single string
  result = '/'.join(remaining_components)
  
  # Step 5: Return the joined string
  return result


def src2dst(src_file, src_dir, dst_dir):
  '''
  Converts a source file path to a destination file path.
  '''
  logging.debug(f"Converts a source file path to a destination file path. {src_file}")
  file_part = split_path(src_file, src_dir)
  return f"{dst_dir}/{file_part}"
        

def list_files_recursively(directory):
  """
  Lists all files in a directory and its subdirectories using multithreading.

  Parameters:
  directory (str): The path to the directory to list files from.

  Returns:
  list: A list of file paths.
  """
  file_list = []
  try:
      logging.info(f"Reading files from {directory}...")

      # Define a function to process each directory
      def process_directory(root, files):
          local_file_list = []
          for file in files:
              file_path = os.path.join(root, file)
              local_file_list.append(file_path)
              logging.debug(f"File found: {file_path}")
          return local_file_list

      # Use ThreadPoolExecutor to process directories in parallel
      with ThreadPoolExecutor() as executor:
          futures = []
          for root, _, files in os.walk(directory):
              futures.append(executor.submit(process_directory, root, files))

          for future in as_completed(futures):
              file_list.extend(future.result())

      logging.debug(f"Total files found: {len(file_list)}")
      logging.info(f"Files from {directory} have been read.")
  except Exception as e:
      logging.error(f"Error listing files: {e}")
  return file_list


def get_uid_gid(user_group):
  '''
  Pass user and group name and return uid and gid, ex. www-data:www-data
  '''
  try:
      user, group = user_group.split(':')
      uid = pwd.getpwnam(user).pw_uid
      gid = grp.getgrnam(group).gr_gid
      return uid, gid
  except KeyError as e:
      return f"Error: {e} not found"
  except ValueError:
      return "Error: Input should be in 'user:group' format"


class FileManager:
  """
  A class to manage file operations such as copying files and preserving file attributes.
  """

  def __init__(self, 
               src_file,
               dst_file, 
               preserve_permissions = False, 
               preserve_times = False, 
               group = None, 
               owner = None, 
               status_bar = False):
      """
      Initializes the FileManager with source and destination file paths.

      Parameters:
      src_file (str): The path to the source file.
      dst_file (str): The path to the destination file.
      preserve_permissions (bool): If True, preserves the file's permissions.
      preserve_times (bool): If True, preserves the file's access and modification times.
      group (int): Change the file's group ID
      owner (int): Change the file's owner ID.
  
      """
      self.src_file = src_file
      self.dst_file = dst_file
      self.status_bar = status_bar
      self.preserve_permissions = preserve_permissions 
      self.preserve_times = preserve_times 
      self.group =  group 
      self.owner =  owner

      self.attributes = {}  # Dictionary to store file attributes
      # logging.debug(f"FileManager initialized with source: {src_file} and destination: {dst_file}")

  def read_file_attributes(self):
      """
      Reads and stores specific attributes of the source file based on the provided flags.
      """
      
      try:
          # Preserve permissions
          if self.preserve_permissions:
              self.attributes['permissions'] = os.stat(self.src_file).st_mode
              logging.debug(f"Permissions preserved: {self.attributes['permissions']}")
          
          # Preserve access and modification times
          if self.preserve_times:
              self.attributes['access_time'] = os.path.getatime(self.src_file)
              self.attributes['modification_time'] = os.path.getmtime(self.src_file)
              logging.debug(f"Access time preserved: {self.attributes['access_time']}, Modification time preserved: {self.attributes['modification_time']}")
          
          # group ID
          if self.group is not None:
              self.attributes['group'] = self.group
              logging.debug(f"New Group ID: {self.attributes['group']}")

          # owner ID
          if self.owner is not None:
              self.attributes['owner'] = self.owner
              logging.debug(f"New Owner ID: {self.attributes['owner']}")
      
      except Exception as e:
          logging.error(f"Error reading file attributes: {e}")
          self.attributes = {}  # Reset attributes if an error occurs


  def copy_file(self):
    """
    Copies the source file to the destination path, preserving metadata, with a progress bar.
    """
    try:
        # Step 1: Extract directory paths
        dst_dir = os.path.dirname(self.dst_file)

        # Step 3: Check and create destination directory if it doesn't exist
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            # Apply preserved group ID
            if 'group' in self.attributes:
                os.chown(dst_dir, -1, self.attributes['group'])
                logging.debug(f"Group ID applied: {self.attributes['group']}")
          
            # Apply preserved owner ID
            if 'owner' in self.attributes:
                os.chown(dst_dir, self.attributes['owner'], -1)
                logging.debug(f"Destination directory created: {dst_dir}")

        # Step 4: Copy the file with progress bar if enabled
        if self.status_bar:
            try:
                # Determine the size of the source file
                file_size = os.path.getsize(self.src_file)

                # Open the source and destination files
                with open(self.src_file, 'rb') as src_file, open(self.dst_file, 'wb') as dst_file:
                    # Set up the progress bar
                    with tqdm(total=file_size, 
                              unit='B', 
                              unit_scale=True, 
                              desc=f"{self.dst_file}", 
                              unit_divisor=1024) as pbar:
                            #   ncols=200) as pbar:
                        
                        # Read and write the file in chunks
                        for chunk in iter(lambda: src_file.read(1024 * 1024), b''):
                            dst_file.write(chunk)
                            pbar.update(len(chunk))

                # Copy file metadata
                shutil.copystat(self.src_file, self.dst_file)
                logging.debug(f"File copied from {self.src_file} to {self.dst_file}")

            except Exception as e:
                logging.error(f"Error copying file with progress bar: {e}")

        else:
            try:
                # Copy the file and its metadata
                shutil.copy2(self.src_file, self.dst_file)
                logging.info(f"{self.src_file} => {self.dst_file}")
            except Exception as e:
                logging.error(f"Error copying file: {e}")

    except Exception as e:
        logging.error(f"Error setting up directories: {e}")


  def apply_attributes_to_file(self):
      """
      Applies the stored attributes to the destination file.
      """
      try:
          # Apply preserved permissions
          if 'permissions' in self.attributes:
              os.chmod(self.dst_file, self.attributes['permissions'])
              logging.debug(f"Permissions applied: {self.attributes['permissions']}")
          
          # Apply preserved access and modification times
          if 'access_time' in self.attributes and 'modification_time' in self.attributes:
              os.utime(self.dst_file, (self.attributes['access_time'], self.attributes['modification_time']))
              logging.debug(f"Access and modification times applied: {self.attributes['access_time']}, {self.attributes['modification_time']}")
          
          # Apply preserved group ID
          if 'group' in self.attributes:
              os.chown(self.dst_file, -1, self.attributes['group'])
              logging.debug(f"Group ID applied: {self.attributes['group']}")
          
          # Apply preserved owner ID
          if 'owner' in self.attributes:
              os.chown(self.dst_file, self.attributes['owner'], -1)
              logging.debug(f"Owner ID applied: {self.attributes['owner']}")
          
          logging.debug(f"Attributes applied to {self.dst_file}")
      except Exception as e:
          logging.error(f"Error applying attributes to file: {e}")
  
  def remove_empty_folders(self):
    """Recursively remove empty folders from the specified path."""
    # Check if the path is a directory
    if not os.path.isdir(self.dst_file):
        logging.info(f"The path '{self.dst_file}' is not a directory or does not exist.")
        return

    # Walk through the directory
    for root, dirs, files in os.walk(self.dst_file, topdown=False):
        # Check each directory
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # If the directory is empty, remove it
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    logging.info(f"Removed empty folder: {dir_path}")
                except Exception as e:
                    logging.info(f"Error removing {dir_path}: {e}")  


  def remove_files_not_in_source(self, 
                                 src_list, 
                                 dst_list):
      src_compare_list = []
      dst_compare_list = []
      
      for file in src_list:
        src_compare_list.append(src2dst(file, self.src_file, "" ))
      
      for file in dst_list:
        dst_compare_list.append(src2dst(file, self.dst_file, "" ))
      
      result = [f"{self.dst_file}{element}" for element in dst_compare_list if element not in src_compare_list]
      logging.debug(f"Files to delete: {result}")
      
      for file in result:
        try:
            os.remove(file)
            logging.info(f"File '{file}' has been deleted successfully.")
        except FileNotFoundError:
            logging.info(f"File '{file}' not found.")
        except PermissionError:
            logging.info(f"Permission denied: Unable to delete '{file}'.")
        except Exception as e:
            logging.info(f"An error occurred while deleting the file: {e}")

      return
