# Tekton
Programmatic ROM editing for Super Metroid

## What is Tekton?
Tekton provides an interface for users to modify parts of the Super Metroid ROM. It requires minimal knowledge of hex editing or ROM memory addresses.

Tekton is in extremely early development and currently doesn't have any noteworthy features.

## Will Tekton replace SMILE?
No. Tekton will have different use cases than SMILE.

## Tests

    python -m unittest discover -s tests

The test suite requires the end user to put a copy of the original Super Metroid ROM at **tests/fixtures/original_rom.sfc**

The ROM's md5 checksum should be **21f3e98df4780ee1c667b84e57d88675**