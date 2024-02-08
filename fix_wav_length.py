#!/usr/bin/env python3
# python 3.9+ (using PEP585 type hints)

import struct

from typing import BinaryIO

def readAt(f: BinaryIO, at: int, num_bytes: int) -> bytes:
    f.seek(at)
    b = f.read(num_bytes)
    if len(b) != num_bytes:
        raise RuntimeError('At %d, insufficient bytes read!' % (at,))
    return b

def expect(f: BinaryIO, at: int, content: bytes) -> None:
    b = readAt(f, at, len(content))
    if b != content:
        raise RuntimeError('At %d, expected %r, got %r' % (at, content, b))

def replace(f: BinaryIO, at: int, content: bytes) -> None:
    f.seek(at)
    f.write(content)

def readChunk(f: BinaryIO, pos: int) -> tuple[bytes, int]:
    chunkId = readAt(f, pos, 4)
    chunkSize = struct.unpack('<I', readAt(f, pos+4, 4))[0]
    return chunkId, chunkSize

def fix_wav_length(f: BinaryIO) -> str:
    """
    Fix wav length in the wav header.
    This the length value might be incorrect,
    especially when reading wav from a streaming pipeline.

    The length is corrected "in-place".
    It can be also used as a library function.

    :param f: Opened file descriptior with `mode='rb+'`, or os.BytesIO object.
    :return: String "DONE".
    """
    f.seek(0, 2) # seek to end
    fileSize = f.tell()
    f.seek(0)
    expect(f, 0, b'RIFF')
    pos = 8
    while True:
        chunkId, chunkSize = readChunk(f, pos)
        effSize = (chunkSize + 3) & (~3) # round up to 4
        if chunkId == b'WAVE':
            pos += 4
            continue
        if chunkId == b'data':
            replace(f, pos+4, struct.pack('<I', fileSize - pos - 8))
            replace(f, 4, struct.pack('<I', fileSize - 8))
            return "DONE"
        pos += 8 + effSize

if __name__ == '__main__':
    import sys
    for filename in sys.argv[1:]:
        try:
            with open(filename, 'rb+') as fd:
                fix_wav_length(fd)
        except RuntimeError as e:
            print("Error processing %r: %s" % (filename, e.message), file=sys.stderr)
