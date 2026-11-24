---
title: Optimal tours of every NFL, MLB and NBA venue under a real-flight model
date: 2026-11-18
tags: sports, optimization, data
status: Checked
summary: Under a fixed flight model, the shortest NFL 2025 tour of all 32 home teams takes 72 d 20 h 31 min, 25 minutes less than the Guinness tour.
---

Some fans attend a home game of every team in a league, and Guinness lists the fastest tours. How close did those tours come to the fastest tour that the real schedule allowed?

We took the real schedules and the US Bureau of Transportation Statistics on-time data. A tour can use only flights that really operated, at their real times. Each leg has fixed buffers. These are 20 minutes to leave the game, 60 minutes at the airport before departure, 40 minutes for a connection, and 15 minutes from the car to the seat. The clock runs from the start of the first game to the actual end of the last one.

A connection scan gives the earliest arrival from each game to every other venue. Then, for each one-day start window, an integer program (HiGHS) finds the shortest tour or proves that none is shorter.

Under this model the optima are NFL 2025 in 72 d 20 h 31 min, MLB 2025 in 23 d 17 h 14 min and NBA 2025-26 in 27 d 18 h 50 min. The NFL tour that Guinness lists for 2025 took 72 d 20 h 56 min, only 25 minutes more than the model optimum. The MLB tour that Guinness lists was 10 h 31 min longer, first pitch to last out. A 2025-26 NBA tour reported in the press (not ratified) was 5 d 5 h 36 min longer by box-score times.

An independent audit checked the schedule data and the time handling and found no time-zone or daylight-saving error. It also found two defects in the tour checker, and the project fixed them. The flight-model optima came after the audit. We re-ran the checker on the NFL and MLB tour files, and both are valid at the spans above.

"Optimal" holds only under this model and these buffers. The buffers are strict, and under them two legs of the real MLB tour are not possible. With tighter buffers the optima are shorter (NFL 69 d 21 h 02 min, MLB 20 d 19 h 12 min). The flight data has no Toronto flights, so the model reaches Toronto only by car. The human travellers had constraints that the model does not have. Nobody else re-ran the integer programs.

*Code available on request. The data is third-party and is not redistributed.*
