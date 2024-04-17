# boot.py
import esp
import gc

esp.osdebug(None)  # Turn off vendor OS debugging messages
gc.collect()       # Garbage collect resource
