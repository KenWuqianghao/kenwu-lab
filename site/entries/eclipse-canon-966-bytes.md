---
title: A 966-byte C program reproduces all 11,898 eclipses of NASA's five-millennium canon
date: 2026-11-23
tags: astronomy, code-golf, optimization
status: Audited
summary: A 966-byte C program prints all 11,898 canon eclipses with correct date and type. Textbook Meeus alone already gets 11,891 dates.
---
NASA's Five Millennium Canon of Solar Eclipses, by Fred Espenak and Jean Meeus, lists 11,898 solar eclipses from 2000 BCE to 3000 CE. We asked how small a C program can be and still reproduce the full list. Each line must have the date, the type (partial, annular, total or hybrid) and the time of greatest eclipse.

The method is not new. Jean Meeus published an eclipse algorithm in Astronomical Algorithms (1998, chapter 54). Run as printed, with no tuning, it already gets 11,891 of the 11,898 dates and 11,847 of the types. Our work was to compress that algorithm and refit its constants against the canon.

The result is a 966-byte C program. It prints all 11,898 eclipses with the correct date and type, and no extra lines. All times are within 30 minutes. The median time error is 45 seconds and the maximum is 272 seconds. The program holds a list of 4 hard-coded exceptions. Without that list, the program is 921 bytes and gets 4 types wrong. Three of the four are hybrid eclipses with one annular end, and their type depends on conventions such as the lunar radius.

To test for overfit, we fitted a copy on the years up to 2000 only. On 2001 to 3000 it got 2,386 of 2,388 dates right and printed 1 extra line. Unfitted Meeus does as well on those years. So the fit does not reproduce unseen years better than the textbook does. It only removes the last 7 date errors and about 50 type errors.

An independent audit downloaded the catalogue again (same SHA-256), re-ran the evaluator and found it sound. It confirmed the 966 bytes and the full score, and it measured the time errors given above.

The dates are in Terrestrial Dynamical Time. For 1,676 eclipses (14 %), the civil (UT) date is different. The program reproduces one NASA computation and is not an independent prediction. We found no other size-limited eclipse program with a byte count, but that search was short.

Eclipse predictions courtesy of Fred Espenak, NASA/Goddard Space Flight Center, from eclipse.gsfc.nasa.gov.

*Code and data: available on request.*
