import multiprocessing
import deluge.ui.ui_entry 
import deluge.ui.gtk3 

if __name__ == '__main__':
    multiprocessing.freeze_support()
    deluge.ui.ui_entry.start_ui()