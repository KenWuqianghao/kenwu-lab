---
title: A fitted polynomial world map scores below Gott-Wagner on the Goldberg-Gott errors
date: 2026-11-24
tags: maths, optimization, data
status: Not audited
summary: A 132-coefficient polynomial map scores 3.7096 on the Goldberg-Gott error total, against 4.4832 for Gott-Wagner on the same sample.
image: assets/flatmap-lower-error/best_vs_winkel.png
---
A flat map of the whole Earth must distort something. Goldberg and Gott (2007) defined six error terms for a world map. They are isotropy, area, flexion, skewness, distance and boundary cuts. The sum of the squared, normalised terms gives one score, and lower is better. In 2021, Gott, Goldberg and Vanderbei named Gott-Wagner as the best one-piece map, with a score of 4.497. They also showed a two-sided disk with the north hemisphere on the front and the south hemisphere on the back. It scored 0.881.

We asked if a numerical search can find lower scores. We froze the scorer and the rules before the search. The scorer uses automatic differentiation for exact derivatives and copies the authors' sampling. It reproduces the published terms for 18 known one-piece maps. One map, Lambert Azimuthal, does not reproduce, and no result uses it. Our sample totals are a little different from the published totals (Gott-Wagner 4.531 against 4.497).

For a one-piece map, a polynomial map with 132 coefficients scores 3.7096 on the search sample. Gott-Wagner scores 4.4832 on the same sample, and Winkel Tripel scores 4.4935. On a second sample that the search never read, the scores are 3.7184 for our map and 4.4627 for Gott-Wagner. On a uniform sample with no polar cap, they are 3.9098 and 4.7731. Checks show no fold-over, no self-overlap and a positive Jacobian everywhere.

![Three world maps with red ellipses that show local distortion: the fitted map a42_pen01, Winkel Tripel and Gott-Wagner](assets/flatmap-lower-error/best_vs_winkel.png)

The fitted map (top) next to Winkel Tripel and Gott-Wagner. The ellipses show the local distortion.

For the two-sided disk, a radial profile with 10 coefficients scores 0.8512, against 0.8903 for the equidistant disk on the same sample. The 2021 paper fitted a quadratic radial term for this disk and chose not to tune it further.

![North and south faces of the fitted two-sided disk above the faces of the two-sided equidistant disk](assets/flatmap-lower-error/t02_vs_equidistant.png)

The two faces of the fitted disk (top row) and of the equidistant disk (bottom row).

No independent review has checked the scorer or the maps. The gain depends on the six published weights, and the 2021 authors warn against tuning a map to one weighting. The best map is a fitted polynomial, not a simple formula. Its uncapped score is higher than its capped score, so part of the gain comes from the capped bands near the poles. We did not search the literature for other numerically optimised projections. Coastlines are from Natural Earth.

*Code and data: available on request.*
