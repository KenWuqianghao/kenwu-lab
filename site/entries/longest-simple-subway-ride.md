---
title: A New York subway ride can stop at 239 stations with no repeat, equal to a proven bound
date: 2026-11-23
tags: transit, optimization, maths
status: Checked
summary: On one MTA timetable day, a 12:46:00 ride stops at 239 of 424 station complexes, and an integer program shows that no ride can stop at more.
---

Ride the New York subway as long as you like, but never stop at the same station twice. How many stations can one ride reach?

We took the MTA timetable of one Tuesday, 8 December 2026. We counted stations as the 424 MTA station complexes. A station counts only when the train stops there with the rider on board. The limit is 24 hours.

## Method

First, an integer program finds the longest simple path on the map of all stop-to-stop hops, which gives an upper bound. Chains of stations with two neighbours become one object, so the HiGHS solver does NYC in less than 2 minutes. Second, the program places the path on the timetable and cuts any part that no start time permits.

## What we found

The NYC ride stops at 239 stations, equal to the bound. It covers 177.14 km in 12:46:00. It has one wait of 1:26:00 at Briarwood for an evening E train. If the ride must not pass a station that it stops at, the best is 236, also equal to its bound, with no wait over 9:30. With no wait over 15 minutes, the best ride found stops at 237, but the bound of 239 is not reached.

The same method gives London 126 of 271 stations, Berlin U-Bahn 81 of 175 and Berlin S-Bahn 84 of 168. Each is equal to its bound.

## How it was checked

An independent audit of an earlier version found the integer program and the ride checker sound. It also found that two complexes were split, South Ferry / Whitehall St in NYC and Bank / Monument in London. The project merged them, added a rule against a change of direction on the same train, and solved again. The new numbers have no second audit. For this write-up, the ride checker was run again on the NYC and London rides, and all were valid.

## Limits

The result holds for one timetable day and these station units. The online game SingleRide asks a similar question, and its best posted score is 173. That is not a fair comparison. The game is played live on its own map, and that map permits up to 242. We found no published proven optimum, but the search was not wide.

Timetable data from the MTA, Transport for London (Powered by TfL Open Data, taken from the Bus Open Data Service, Open Government Licence v3.0) and VBB Verkehrsverbund Berlin-Brandenburg GmbH (CC BY 4.0). No publisher endorses this work or warrants that the data is accurate.

*Code available on request. The data is third-party and is not redistributed.*
