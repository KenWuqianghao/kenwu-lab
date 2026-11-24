---
title: The longest accidental Pilish passage in the C4 web corpus has 11 digits
date: 2026-11-17
tags: data, maths, tools
status: Checked
summary: A full scan of the C4 web corpus found an 11-digit accidental Pilish passage. The longest published example we found has 10 digits.
---
Pilish is writing in which the length of each word gives the next digit of pi (3, 1, 4, 1, 5, 9 and so on). People write Pilish on purpose. Mnemonics such as "How I want a drink, alcoholic of course..." are examples. We asked a different question. How long a passage of Pilish occurs by accident in ordinary text? The longest accidental example that we found published has 10 digits (cadaeic.net, August 2023).

We froze the rules before the search. They define words, line breaks and Mike Keith's "Standard Pilish" digit map. They also exclude deliberate Pilish. A passage does not count if it matches a known mnemonic, if the text near it mentions pi, digits or circles, or if the document mentions Pilish.

We used two methods. A C scanner read all 1024 shards of the C4 web corpus, which hold 364,868,892 documents and 128,548,864,485 words. An API walker searched the infini-gram indexes for word sequences of the correct lengths.

Both methods found the same best passage, 11 digits long:

> "and I have a large selection of custom props. For these"

The word lengths are 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5. The passage is on a photographer's web page in C4 (shard 895, record 161306). Our checker scores it 11 digits under both Standard and Basic Pilish, and the exclusion rules do not remove it. The full scan found five more passages with 10 digits and 29 with 9 digits that pass the rules.

The C scanner and the Python reference agree on 2,392,394 passage starts and 20,000 random test documents. The checker reproduces both known 10-digit examples. The full-scan results were scored again from the saved files.

No independent audit has checked this result. The prior-art check uses one source. The exclusion rules are not perfect. They let through a 15-digit passage that is a known mnemonic in a letter cipher, so we do not count it. Some 9-digit passages that pass the rules may be deliberate. The live page is now gone, so the C4 record is the public source.

*Code available on request. The data is third-party and is not redistributed.*
