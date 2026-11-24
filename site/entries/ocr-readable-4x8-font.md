---
title: A searched 4x8 pixel font that Tesseract reads with under 1 % errors
date: 2026-11-24
tags: typography, optimization, ml
status: Checked
summary: A hill-climbed 4x8 lower-case font (32 pixels) passes a 1 % OCR error limit in Tesseract 5.5.4, where the smallest stock font that passes uses 78.
image: assets/ocr-readable-4x8-font/lower_4x8_8x.png
---

How few pixels does a font need before a standard OCR engine can read it? We fixed one engine, Tesseract 5.5.4 with its English model and `--psm 6`. The page is drawn at one pixel per font pixel. Then it is scaled up without smoothing to about 32 pixels per text line. A font passes if Tesseract makes at most 1 % character errors on a page of prose and on a page of random dictionary words.

Existing pixel fonts set the baseline. For lower-case text, the smallest one that passes is X11 6x13, with 78 pixels per character. Tom Thumb, a well-known 4x6 font, gets 11.22 % and 14.23 %.

A hill-climb changed single glyph pixels. It kept a change only when the frozen evaluator showed fewer errors. For lower case it found a 4x8 font (32 pixels) that passes, with 0.35 % errors on prose and 0.65 % on words. For letters, digits and capitals, the smallest pass is 6x12 (72 pixels). For full printable ASCII, no cell passed both sets.

![Twelve lines of lower-case prose in the searched 4x8 pixel font, shown at 8x scale, with isolated dots above and below many letters](assets/ocr-readable-4x8-font/lower_4x8_8x.png)

The searched 4x8 font on the prose page, enlarged 8 times.

![Random dictionary words in the searched 4x8 pixel font, shown at 8x scale](assets/ocr-readable-4x8-font/lower_4x8_words_8x.png)

The same font on a page of random words.

The climb tuned the font on the test pages. For this reason a held-out set was added, from a different book and with new random words, and a font must pass both. The held-out set never selects a font. The 4x8 font gets 0.60 % on held-out prose and 0.95 % on held-out words, 19 errors in 1,992 characters. That is one error below the limit. For this page we re-ran the frozen evaluator on a copy of the project, and both sets gave the same numbers.

The result holds for one engine, one model and one scale factor. The glyphs have stray pixels above and below many letters, and we did not test if people can read them. Our search for earlier fonts that were optimised for OCR took about 25 minutes and is not complete. The test texts are public domain books from Project Gutenberg and a system word list.

*Code and data: available on request.*
