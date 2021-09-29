import win32con
import win32file
import pywintypes

FLAG = win32con.LOCKFILE_EXCLUSIVE_LOCK
OVERLAPPED = pywintypes.OVERLAPPED()

def lock_file(f):
    hfile = win32file._get_osfhandle(f.fileno())
    win32file.LockFileEx(hfile, FLAG, 0, -0x10000, OVERLAPPED)

def unlock_file(f):
    hfile = win32file._get_osfhandle(f.fileno())
    win32file.UnlockFileEx(hfile, 0, -0x10000, OVERLAPPED)
