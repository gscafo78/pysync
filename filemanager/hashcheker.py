import hashlib

class HashChecker:
  def __init__(self, hash_type, file_path_a, file_path_b=None, hash_string=None):
      """
      Initializes the HashChecker with the specified hash type and file paths.

      :param hash_type: The type of hash to use ('md5' or 'sha256').
      :param file_path_a: Path to the first file.
      :param file_path_b: Path to the second file (optional, used in hashtohash).
      :param hash_string: Hash string to compare against (optional, used in filetohash).
      :raises ValueError: If the hash_type is not one of the allowed values.
      """
      # Define the allowed hash types
      allowed_hash_types = ['md5', 'sha256']

      # Check if the provided hash_type is valid
      if hash_type not in allowed_hash_types:
          raise ValueError(f"Invalid hash_type. Allowed values are: {allowed_hash_types}")

      # Initialize instance variables
      self.hash_type = hash_type
      self.file_path_a = file_path_a
      self.file_path_b = file_path_b
      self.hash_string = hash_string

  def filetohash(self):
      """
      Verifies if the hash of the file matches the provided hash string.

      :return: True if the file's hash matches the provided hash string, False otherwise.
      :raises FileNotFoundError: If the file at file_path_a is not found.
      :raises Exception: For any other errors that occur during file reading or hashing.
      """
      # Select the hash function based on hash_type
      if self.hash_type == 'md5':
          hash = hashlib.md5()
      elif self.hash_type == 'sha256':
          hash = hashlib.sha256()

      try:
          # Open the file in binary read mode
          with open(self.file_path_a, "rb") as file:
              # Read the file in chunks to avoid memory issues with large files
              while chunk := file.read(8192):
                  hash.update(chunk)

          # Compute the hash of the file
          file_hash = hash.hexdigest()

          # Compare the computed hash with the provided hash string
          return file_hash == self.hash_string
      except FileNotFoundError:
          # Handle the case where the file is not found
          print(f"File not found: {self.file_path_a}")
          return False
      except Exception as e:
          # Handle any other exceptions that may occur
          print(f"An error occurred: {e}")
          return False

  def file2file(self):
      """
      Compares the hash of two files.

      :return: True if the hashes of the two files match, False otherwise.
      :raises FileNotFoundError: If either file at file_path_a or file_path_b is not found.
      :raises Exception: For any other errors that occur during file reading or hashing.
      """
      # Check if the second file path is provided
      if not self.file_path_b:
          print("Second file path is not provided.")
          return False

      # Select the hash function based on hash_type
      if self.hash_type == 'md5':
          hash_a = hashlib.md5()
          hash_b = hashlib.md5()
      elif self.hash_type == 'sha256':
          hash_a = hashlib.sha256()
          hash_b = hashlib.sha256()

      try:
          # Compute hash for the first file
          with open(self.file_path_a, "rb") as file_a:
              while chunk := file_a.read(8192):
                  hash_a.update(chunk)

          # Compute hash for the second file
          with open(self.file_path_b, "rb") as file_b:
              while chunk := file_b.read(8192):
                  hash_b.update(chunk)

          # Compare the two computed hashes
          return hash_a.hexdigest() == hash_b.hexdigest()

      except FileNotFoundError as e:
          # Handle the case where one of the files is not found
          print(f"File not found: {e.filename}")
          return False
      except Exception as e:
          # Handle any other exceptions that may occur
          print(f"An error occurred: {e}")
          return False