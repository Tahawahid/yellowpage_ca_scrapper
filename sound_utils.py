"""Sound notification utilities"""

import sys
import winsound


class SoundNotifier:
    @staticmethod
    def play_completion_sound():
        """Play sound when scraping is complete"""
        try:
            # For Windows
            if sys.platform == "win32":
                winsound.MessageBeep(winsound.MB_OK)
            else:
                # For Unix/Linux/Mac - using system bell
                print('\a')  # Bell character
        except Exception as e:
            print(f"Could not play sound: {e}")
    
    @staticmethod
    def play_error_sound():
        """Play error sound"""
        try:
            if sys.platform == "win32":
                winsound.MessageBeep(winsound.MB_ICONHAND)
            else:
                print('\a')  # Bell character
        except Exception as e:
            print(f"Could not play sound: {e}")