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


def ch_own(root_dir,chown_list = None):
    """
    Changes the owner and group of a file or directory.
    """
    if chown_list is not None:
        gid=get_uid_gid(chown_list)[1]
        uid=get_uid_gid(chown_list)[0]
        for root, dirs, files in os.walk(root_dir):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                logging.debug(f"subfolders: {dir_path}")
                try:
                    os.chown(dir_path, uid, gid)
                    logging.debug(f"User ID {uid}, Group ID {gid} applied to: {dir_path}")
                except Exception as e:
                    logging.error(f"Failed to change user or group for {dir_path}: {e}")
        

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
        parts = user_group.split(':')
        
        # Initialize uid and gid
        uid = None
        gid = None
        
        # Assign values based on the number of parts
        if len(parts) == 2:
            user, group = parts[0] or None, parts[1] or None
        elif len(parts) == 1:
            user = parts[0] or None
            group = None
        else:
            raise ValueError("Input should be in 'user:group' format")
        
        if user is not None:
            uid = pwd.getpwnam(user).pw_uid
        else:
            uid = -1
        if group is not None:
            gid = grp.getgrnam(group).gr_gid
        else:
            gid = -1
        
        return uid, gid
    
    except KeyError as e:
        return f"Error: {e} not found"
    except ValueError as ve:
        return f"Error: {ve}"
    

def sizes_equal(file_path1, file_path2):
  """
  Returns True if the sizes of the two files are equal, False otherwise.

  Args:
      file_path1 (str): Path to the first file.
      file_path2 (str): Path to the second file.

  Returns:
      bool: Whether the file sizes are equal.
  """
  try:
      size1 = os.path.getsize(file_path1)
      size2 = os.path.getsize(file_path2)
      if size1 == size2:
          logging.debug("the file sizes are equal")    
          return True
      else:
          logging.debug("the file sizes aren't equal")    
          return False
  except FileNotFoundError:
      logging.error("One or both files not found.")
      return False


class FileManager:
  """
  A class to manage file operations such as copying files and preserving file attributes.
  """

  def __init__(self, 
               src_file,
               dst_file, 
               root_dir = None,
               preserve_permissions = False, 
               group = None, 
               owner = None, 
               status_bar = False):
      """
      Initializes the FileManager with source and destination file paths.

      Parameters:
      src_file (str): The path to the source file.
      dst_file (str): The path to the destination file.
      preserve_permissions (bool): If True, preserves the file's permissions.
      group (int): Change the file's group ID
      owner (int): Change the file's owner ID.
  
      """
      self.src_file = src_file
      self.dst_file = dst_file
      self.status_bar = status_bar
      self.preserve_permissions = preserve_permissions 
      self.group =  group 
      self.owner =  owner
      self.root_dir = root_dir


  def copy_file(self):
    """
    Copies the source file to the destination path, preserving metadata, with a progress bar.
    """
    try:
        dst_dir = os.path.dirname(self.dst_file)
        os.makedirs(dst_dir, exist_ok=True)
        if self.status_bar:
            try:
                # Determine the size of the source file
                file_size = os.path.getsize(self.src_file)

                # Open the source and destination files
                with open(self.src_file, 'rb') as src_file, open(self.dst_file, 'wb') as dst_file:
                    # Set up the progress bar
                    if len(self.dst_file) > 110:
                        description = f"...{self.dst_file[-107:]}"
                    else:
                        description = f"{self.dst_file[-110:]}"

                    with tqdm(total=file_size, 
                              unit='B', 
                              unit_scale=True, 
                              desc=f"{description}", 
                            #   desc=f"{self.dst_file.split('/')[-1]}", 
                              unit_divisor=1024,
                              bar_format="{desc:<110} {bar} [ {n_fmt:>5}/{total_fmt:>5} | {percentage:>6.2f} % | {rate_fmt:>8} ]",
                              dynamic_ncols = True) as pbar:
                            #   ncols=220) as pbar:
                        
                        # Read and write the file in chunks
                        for chunk in iter(lambda: src_file.read(1024 * 1024), b''):
                            dst_file.write(chunk)
                            pbar.update(len(chunk))

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
        
        if self.preserve_permissions: 
            shutil.copystat(self.src_file, self.dst_file)
            logging.debug(f"Permissions applied: {self.dst_file}")

        # Apply preserved group ID
        if self.group is not None:
            os.chown(self.dst_file, -1, self.group)
            logging.debug(f"Group ID applied: {self.dst_file}")
        
        # Apply preserved owner ID
        if self.owner is not None:
            os.chown(self.dst_file, self.owner, -1)
            logging.debug(f"Owner ID applied: {self.dst_file}")
            

    except Exception as e:
        logging.error(f"Error setting up directories: {e}")


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
      logging.info(f"Starting deleting files not in source...")
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
