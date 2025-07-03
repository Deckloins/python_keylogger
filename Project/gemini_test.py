import pywinctl
import logging # You can keep your other imports as needed

def get_active_window_title():
    """
    Gets the title of the currently active window using a robust,
    cross-platform method.

    Returns:
        str: The title of the active window, or None if it cannot be determined.
    """
    try:
        active_window = pywinctl.getActiveWindow()
        if active_window:
            return active_window.title
        else:
            # This can happen if there is no active window (e.g., in a headless environment)
            return None
    except Exception as e:
        logging.error(f"An error occurred while getting the active window title: {e}")
        return None

# --- Main execution block for testing ---
if __name__ == "__main__":
    title = get_active_window_title()
    if title:
        print(f"Active Window Title: {title}")
    else:
        print("Could not retrieve the active window title.")