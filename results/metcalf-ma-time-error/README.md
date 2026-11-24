# A systematic time error in the DASCH metadata of J. H. Metcalf's early "ma" plates, and Pluto on four Harvard plates of 1908 and 1909

The DASCH exposure times of J. H. Metcalf's plates from Taunton (1905-1913) contain a systematic error. One rule with no free parameter gives the error: Metcalf's logged local mean time, counted from noon, was read as local sidereal time. The predicted shift is about +6 h in December, 0 h in late March and ±12 h in September.

At the corrected times, a faint source is at Pluto's predicted position on ma00731 and ma00733 (1908 Dec 21, 22), more weakly on ma00729 (Dec 20), and on ma00937 (1909 Dec 12). Peter Graham published the image on ma00731 first ([doi:10.5281/zenodo.24376800](https://doi.org/10.5281/zenodo.24376800)). The time-error rule, ma00733 and ma00937 are not in that paper. Experts must examine the glass plates to confirm the identification.

[Read the paper](paper/paper.pdf)

## Checks

The script [checks/ci.sh](checks/ci.sh) runs on each change:

1. It reruns the time test ([data/timetest/analyze.py](data/timetest/analyze.py)) from the committed DASCH and MPC inputs. The output must be identical to [data/results/time_test.txt](data/results/time_test.txt). This test gives the 47 of 54 MPC times and the shuffle result.
2. It compares the MD5 checksum of `paper/paper.pdf` with the PDF in the Zenodo record.

The plate cutouts and the Pluto measurements need the DASCH image service. They are not rerun here.

Archived on Zenodo: [doi:10.5281/zenodo.24510122](https://doi.org/10.5281/zenodo.24510122)
