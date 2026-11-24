---
title: Lossless compression of Neuralink N1 recordings reaches 3.563, near an estimated floor
date: 2026-11-16
tags: compression, data
status: Not audited
summary: A one-file C codec gets ratio 3.563077 under the unmodified eval.sh, against 3.548790 for the m0at codec. Lossless 200x is not possible.
---
Neuralink posted a compression challenge with 743 short recordings from its N1 implant (146,800,526 bytes). The target is 200x lossless compression. The score is raw bytes divided by the compressed bytes plus the size of the encoder and decoder programs. Public entries that we found reached about 3.35 to 3.55, among them phoboslab's neuralink_brainwire (3.35) and a codec by m0at.

We wrote a new codec in one C file. The first finding is about the hardware. Each 16-bit sample is a fixed function of a 10-bit ADC code, and the ADC steps have very unequal widths, from 0 to about 4 nominal steps. The widths are the same in every file. A model that knows the step widths codes about 2% smaller. We did not check if others reported this before. The rest of the codec uses standard parts. These are an order-16 adaptive linear predictor, a noise scale from three running variances, a trained kernel shape and a range coder.

With the unmodified `eval.sh` in a Linux container, our codec gets a ratio of 3.563077 (41,200,487 bytes with both programs) on all 743 files, all lossless. The strongest public codec that we found and ran, by m0at, gets 3.548790. `eval.sh` prints the two ratios cut to two decimals, as 3.56 and 3.54. All trained tables used only half of the files. On the other 371 files our codec gets 3.54788 and m0at 3.53456, a margin of 0.375%.

We also estimated how much is left. A Gaussian-process entropy estimate from the spectrum gives 4.585 to 4.589 bits per sample without the ADC model. With the ADC table and the other parts, we estimate a floor near 4.47 to 4.48 bits per sample. Our coded streams use 4.4899. A ratio of 200x would need about 0.08 bits per sample. The noise alone carries about 4.4, so lossless 200x is not possible on this data.

The margin is small. The tables describe this one ADC, and a different device would lose that gain. Decoding on a different platform from the encoder was checked on 3 files only. No independent review was done. The entropy floor is our own estimate. The "strongest public codec" label rests only on the entries we found.

*Code available on request. The data is third-party and is not redistributed.*
