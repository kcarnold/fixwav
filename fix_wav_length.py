import struct

def readAt(f, at, bytes):
    f.seek(at)
    b = f.read(bytes)
    if len(b) != bytes:
        raise RuntimeError('At %d, insufficient bytes read!' % (at,))
    return b

def expect(f, at, content):
    b = readAt(f, at, len(content))
    if b != content:
        raise RuntimeError('At %d, expected %r, got %r' % (at, content, b))

def replace(f, at, content):
    f.seek(at)
    f.write(content)

def readChunk(f, pos):
    chunkId = readAt(f, pos, 4)
    chunkSize = struct.unpack('<I', readAt(f, pos+4, 4))[0]
    return chunkId, chunkSize

def fix_wav_length(filename):
    f = open(filename, 'rb+')
    f.seek(0, 2) # seek to end
    fileSize = f.tell()
    f.seek(0)
    expect(f, 0, 'RIFF')
    pos = 8
    while True:
        chunkId, chunkSize = readChunk(f, pos)
        effSize = (chunkSize + 3) & (~3) # round up to 4
        if chunkId == 'WAVE':
            pos += 4
            continue
        if chunkId == 'data':
            replace(f, pos+4, struct.pack('<I', fileSize - pos - 8))
            replace(f, 4, struct.pack('<I', fileSize - 8))
            return "DONE"
        pos += 8 + effSize

if __name__ == '__main__':
    import sys
    for filename in sys.argv[1:]:
        try:
            fix_wav_length(filename)
        except RuntimeError, e:
            print >>sys.stderr, "Error processing %r: %s" % (filename, e.message)
