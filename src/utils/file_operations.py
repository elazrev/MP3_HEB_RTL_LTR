import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import logging
from datetime import datetime


class FileOperationError(Exception):
    """Custom exception for file operations"""
    pass


class FileOperations:
    """Utility class for safe file operations"""

    def __init__(self):
        """Initialize FileOperations with logging"""
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"file_operations_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    @staticmethod
    def create_backup(file_path: str) -> Optional[str]:
        """
        Create a backup of a file before modifying it.

        Args:
            file_path (str): Path to the file to backup

        Returns:
            Optional[str]: Path to the backup file if successful, None otherwise
        """
        try:
            backup_path = f"{file_path}.backup"
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            logging.error(f"Failed to create backup for {file_path}: {str(e)}")
            return None

    @staticmethod
    def restore_from_backup(backup_path: str) -> bool:
        """
        Restore a file from its backup.

        Args:
            backup_path (str): Path to the backup file

        Returns:
            bool: True if restoration was successful
        """
        try:
            original_path = backup_path.replace('.backup', '')
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, original_path)
                os.remove(backup_path)
                return True
            return False
        except Exception as e:
            logging.error(f"Failed to restore from backup {backup_path}: {str(e)}")
            return False

    @staticmethod
    def safe_rename(old_path: str, new_path: str) -> Tuple[bool, Optional[str]]:
        """
        Safely rename a file with backup and validation.

        Args:
            old_path (str): Current file path
            new_path (str): New file path

        Returns:
            Tuple[bool, Optional[str]]: (Success status, Error message if any)
        """
        try:
            # Check if paths are valid
            if not os.path.exists(old_path):
                return False, "Source file doesn't exist"

            if os.path.exists(new_path):
                return False, "Destination file already exists"

            # Create backup
            backup_path = FileOperations.create_backup(old_path)
            if not backup_path:
                return False, "Failed to create backup"

            # Attempt rename
            os.rename(old_path, new_path)

            # Verify rename was successful
            if os.path.exists(new_path):
                os.remove(backup_path)  # Remove backup on success
                return True, None

            # Restore from backup if rename failed
            FileOperations.restore_from_backup(backup_path)
            return False, "Failed to rename file"

        except Exception as e:
            logging.error(f"Error in safe_rename: {str(e)}")
            return False, str(e)

    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename from invalid characters.

        Args:
            filename (str): Original filename

        Returns:
            str: Cleaned filename
        """
        # Define invalid characters
        invalid_chars = '<>:"/\\|?*'

        # Replace invalid characters with underscore
        clean_name = ''.join('_' if c in invalid_chars else c for c in filename)

        # Ensure filename isn't too long (Windows has 255 char limit)
        if len(clean_name) > 255:
            name, ext = os.path.splitext(clean_name)
            clean_name = name[:255 - len(ext)] + ext

        return clean_name

    @staticmethod
    def ensure_unique_path(file_path: str) -> str:
        """
        Ensure the file path is unique by adding number suffix if needed.

        Args:
            file_path (str): Desired file path

        Returns:
            str: Unique file path
        """
        if not os.path.exists(file_path):
            return file_path

        directory = os.path.dirname(file_path)
        name, ext = os.path.splitext(os.path.basename(file_path))
        counter = 1

        while True:
            new_path = os.path.join(directory, f"{name}_{counter}{ext}")
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    @staticmethod
    def get_safe_file_operations(file_path: str) -> dict:
        """
        Get safe file operations for a given path.

        Args:
            file_path (str): Path to check

        Returns:
            dict: Dictionary with safe operations flags
        """
        operations = {
            'can_read': False,
            'can_write': False,
            'can_delete': False,
            'is_locked': False,
            'errors': []
        }

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                operations['errors'].append("File doesn't exist")
                return operations

            # Check read permission
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)
                operations['can_read'] = True
            except:
                operations['errors'].append("Can't read file")

            # Check write permission
            try:
                # Try to open file in append mode
                with open(file_path, 'ab') as f:
                    operations['can_write'] = True
            except:
                operations['errors'].append("Can't write to file")
                operations['is_locked'] = True

            # Check delete permission
            try:
                operations['can_delete'] = os.access(file_path, os.W_OK)
            except:
                operations['errors'].append("Can't delete file")

        except Exception as e:
            operations['errors'].append(f"Error checking file: {str(e)}")

        return operations

    @staticmethod
    def is_path_safe(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a file path is safe to use.

        Args:
            file_path (str): Path to check

        Returns:
            Tuple[bool, Optional[str]]: (Is safe, Error message if not safe)
        """
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(file_path)

            # Check for directory traversal attempts
            if '..' in abs_path:
                return False, "Path contains parent directory references"

            # Check if path is too long
            if len(abs_path) > 255:
                return False, "Path is too long"

            # Check if directory exists
            dir_path = os.path.dirname(abs_path)
            if not os.path.exists(dir_path):
                return False, "Directory doesn't exist"

            # Check for write permissions in directory
            if not os.access(dir_path, os.W_OK):
                return False, "No write permission in directory"

            return True, None

        except Exception as e:
            return False, str(e)