What happens when you lose power during recording? Well...

This little tool fixes the length information in the WAV file
header. To use it, just run `python fix_wav_length.py 1.wav 2.wav ...`

The WAV format is flexible, meaning the header can include arbitrary
other data as well. All the other "fixer" tools I found ignore this,
thinking that all WAV headers are 44 bytes. A few even check before
corrupting your file. This tool is a quick and dirty coding job and
I'm not proud of it, but it can deal with at least a few different
kinds of WAV headers and tries not to corrupt your file. Make a backup
anyway, though.

Oh, and be careful with files over 2 or 4 GB. Up to almost 4 GB should
probaly work, but the WAV format only gives you 4 bytes for a file
size including headers. Go ahead and fork and patch this to work like
http://offog.org/darcs/misccode/fix-wav-length if you need; it should
be easy.
