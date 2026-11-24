---
title: A context-mixing entry falls 3,482 bytes short of the Calgary Challenge target
date: 2026-11-19
tags: compression, code-golf
status: Not audited
summary: The best verified entry is 582,652 bytes. The target was 579,170, so the 2010 record of 580,170 bytes stands.
---
The Calgary Corpus Compression Challenge asks for the smallest self-extracting archive of 14 classic files. The size counts both the compressed data and the decompressor source. The record is 580,170 bytes, set by Alexander Rhatushnyak in 2010. The original challenge closed in 2016. Matt Mahoney still keeps a list, and a new entry must beat the old one by at least 1,000 bytes. So our target was 579,170 bytes or less.

We wrote a bit-wise context-mixing compressor in one C++ file, based on Matt Mahoney's lpaq1. It has about 130 hashed contexts for text, separate context sets for the geo and object files, and a small image model for `pic`. It also has 16 mixers, 7 APM stages and a 352-cell LSTM that follows the lstm-compress design by Byron Knoll. The LSTM must give bit-identical results on macOS arm64 (encoder) and Linux x86-64 (decoder). So it uses only basic floating-point operations and no fused multiply-add.

We did not reach the target. The best verified entry is 582,652 bytes under Mahoney's count. That is 3,482 bytes (0.6 %) short of the target. Under the record's own count it is 582,647 bytes, 2,477 bytes above the record. The entry is smaller than the record on 7 of the 14 files. Most of the gap is in the two books (+9,210 bytes). The record codes line breaks in a separate stream, and we did not.

Each kept change was checked with a full decode. All 14 SHA-1 hashes matched on a Steam Deck in a container with no network, and on a Mac. The decode takes 6,377 s of the 2-hour limit that we set ourselves, so the LSTM cannot grow further.

An independent audit of an earlier version found two real defects. The decoder read uninitialised memory, and a clang build used fused multiply-add and failed in `book1`. Both are fixed and re-tested. The audit did not check the final entry. A 32-bit build and an independent PPMd unpack of the source were not tested. No new method is claimed.

*Code available on request. The data is third-party and is not redistributed.*
