import multiprocessing
import deluge.core.daemon_entry

if __name__ == '__main__':
    multiprocessing.freeze_support()
    deluge.core.daemon_entry.start_daemon()