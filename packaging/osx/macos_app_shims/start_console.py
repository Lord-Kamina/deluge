import multiprocessing
import deluge.ui.console

if __name__ == '__main__':
    multiprocessing.freeze_support()
    deluge.ui.console.start()