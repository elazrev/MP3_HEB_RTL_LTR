from typing import Optional, Dict, Any
import os
from mutagen import File, id3
from .file_operations import FileOperations, FileOperationError
import logging


class MP3Operations:
    """Utility class for MP3 file operations"""

    def __init__(self):
        """Initialize MP3Operations"""
        self.file_ops = FileOperations()
        self.logger = logging.getLogger(__name__)

    def read_mp3_tags(self, file_path: str) -> Dict[str, Any]:
        """
        Safely read MP3 tags.

        Args:
            file_path (str): Path to MP3 file

        Returns:
            Dict[str, Any]: Dictionary with MP3 tags

        Raises:
            FileOperationError: If reading tags fails
        """
        try:
            # Verify file exists and is readable
            if not os.path.exists(file_path):
                raise FileOperationError(f"File not found: {file_path}")

            # Check file permissions
            ops = self.file_ops.get_safe_file_operations(file_path)
            if not ops['can_read']:
                raise FileOperationError(f"Cannot read file: {', '.join(ops['errors'])}")

            # Read tags
            audio = File(file_path)
            if not isinstance(audio.tags, id3.ID3):
                raise FileOperationError("File has no ID3 tags")

            # Extract tags
            tags = {
                'title': str(audio.tags.get('TIT2', '')),
                'artist': str(audio.tags.get('TPE1', '')),
                'album': str(audio.tags.get('TALB', '')),
                'filename': os.path.basename(file_path)
            }

            # Extract album art if exists
            for tag in audio.tags.values():
                if isinstance(tag, id3.APIC):
                    tags['album_art'] = tag.data
                    break

            return tags

        except Exception as e:
            self.logger.error(f"Error reading MP3 tags from {file_path}: {str(e)}")
            raise FileOperationError(f"Failed to read MP3 tags: {str(e)}")

    def write_mp3_tags(self, file_path: str, tags: Dict[str, Any]) -> bool:
        """
        Safely write MP3 tags.

        Args:
            file_path (str): Path to MP3 file
            tags (Dict[str, Any]): Tags to write

        Returns:
            bool: True if successful

        Raises:
            FileOperationError: If writing tags fails
        """
        try:
            # Verify file exists and is writable
            if not os.path.exists(file_path):
                raise FileOperationError(f"File not found: {file_path}")

            # Check file permissions
            ops = self.file_ops.get_safe_file_operations(file_path)
            if not ops['can_write']:
                raise FileOperationError(f"Cannot write to file: {', '.join(ops['errors'])}")

            # Create backup
            backup_path = self.file_ops.create_backup(file_path)
            if not backup_path:
                raise FileOperationError("Failed to create backup")

            try:
                # Write tags
                audio = File(file_path)
                if not isinstance(audio.tags, id3.ID3):
                    audio.add_tags()

                # Update each tag
                if 'title' in tags:
                    audio.tags['TIT2'] = id3.TIT2(encoding=3, text=[tags['title']])
                if 'artist' in tags:
                    audio.tags['TPE1'] = id3.TPE1(encoding=3, text=[tags['artist']])
                if 'album' in tags:
                    audio.tags['TALB'] = id3.TALB(encoding=3, text=[tags['album']])

                # Save changes
                audio.save()

                # Remove backup on success
                os.remove(backup_path)
                return True

            except Exception as e:
                # Restore from backup if writing failed
                self.file_ops.restore_from_backup(backup_path)
                raise FileOperationError(f"Failed to write tags: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error writing MP3 tags to {file_path}: {str(e)}")
            raise FileOperationError(f"Failed to write MP3 tags: {str(e)}")

    def rename_mp3_file(self, old_path: str, new_name: str) -> Optional[str]:
        """
        Safely rename MP3 file.

        Args:
            old_path (str): Current file path
            new_name (str): New filename (not full path)

        Returns:
            Optional[str]: New file path if successful, None otherwise

        Raises:
            FileOperationError: If renaming fails
        """
        try:
            # Clean and validate new filename
            clean_name = self.file_ops.clean_filename(new_name)
            if not clean_name.lower().endswith('.mp3'):
                clean_name += '.mp3'

            # Create new path
            new_path = os.path.join(os.path.dirname(old_path), clean_name)

            # Ensure unique path
            new_path = self.file_ops.ensure_unique_path(new_path)

            # Perform safe rename
            success, error = self.file_ops.safe_rename(old_path, new_path)
            if not success:
                raise FileOperationError(f"Failed to rename file: {error}")

            return new_path

        except Exception as e:
            self.logger.error(f"Error renaming MP3 file {old_path}: {str(e)}")
            raise FileOperationError(f"Failed to rename MP3 file: {str(e)}")