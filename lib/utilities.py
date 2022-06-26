import binascii
import string
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


################################################################################
# Hexdump pretty printer
################################################################################


def get_data_dump(data):
    """Return a pretty binary data representation in a Hexdump fashion."""
    dump = ""
    index = 0
    while index < len(data):
        data_slice = data[index : index + 16]
        offset_str = _get_offset_string(index)
        data_str = _get_hexdump_string(data_slice)
        ascii_str = _get_asciidump_string(data_slice)
        dump += f"{offset_str} {data_str:<47} {ascii_str}\n"
        index += 16
    return dump


def _get_offset_string(index):
    offset = hex(index)[2:]
    offset = offset.zfill(8)
    return offset


def _get_hexdump_string(data):
    hexdump = binascii.hexlify(data).decode("ascii")
    spaced_hexdump = ""
    index = 0
    while index < len(hexdump):
        spaced_hexdump += hexdump[index : index + 2] + " "
        index += 2
    return spaced_hexdump.strip()


def _get_asciidump_string(data):
    asciidump = ""
    for char in data:
        char = chr(char)
        if char in string.printable and not char in "\r\n\t":
            asciidump += char
        else:
            asciidump += "."
    return asciidump
