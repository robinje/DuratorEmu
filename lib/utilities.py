import threading


def simple_thread(func, daemon=True):
    """Start function in another thread, discarding return value."""
    thread = threading.Thread(target=func)
    thread.daemon = daemon
    thread.start()
    return thread


def read_cstring(file_object):
    """Read the 0-terminated string from file_object and return the bytes
    object (terminator excluded)."""
    cstring = b""
    while True:
        char = file_object.read(1)
        if char and char != b"\x00":
            cstring += char
        else:
            break
    return cstring


def read_struct(file_object, struct):
    """Read a struct.Struct from file_object and return the unpacked tuple."""
    data = file_object.read(struct.size)
    return struct.unpack(data)
