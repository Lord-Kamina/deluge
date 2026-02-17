import multiprocessing
import deluge.ui.web

if __name__ == '__main__':
    multiprocessing.freeze_support()
    deluge.ui.web.start()