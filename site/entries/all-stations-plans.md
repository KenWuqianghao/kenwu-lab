---
title: Timetable plans that visit every metro station, checked leg by leg
date: 2026-11-24
tags: transit, optimization, data
status: Checked
summary: Checked timetable plans visit every station of six metro systems. The BART plan, 6:11:00, equals a bound from an earlier rule set. Human times are faster.
image: assets/all-stations-plans/berlin-s-run.png
---
The "subway challenge" asks how fast a person can visit every station of a metro system. We asked for the fastest plan on one frozen published timetable, with a program that checks each leg.

The checker reads the GTFS timetable and a route file. It accepts a station only when a train stops there with the traveller on board. It checks each change against a minimum change time and each foot leg against an OpenStreetMap distance. A change of direction costs 180 s, or 60 s for a turnaround at a terminus. An annealer searches the station order.

NYC Subway (472 stations) takes 22:36:30. London Underground (272 stations) takes 18:29:00. Berlin U-Bahn (175 stations) takes 7:32:00. Berlin S-Bahn (168 stations) takes 14:36:30. The NYC, London and Berlin U-Bahn plans are each slower than the human record for that city (22:14:10, 17:46:48 and 6:53:24). The record rules permit buses, and our rules do not.

![Map of the Berlin S-Bahn lines with the plan drawn in line colours, next to a panel that shows 14:36:30 and 168 of 168 stations](assets/all-stations-plans/berlin-s-run.png)

The Berlin S-Bahn plan. Timetable data from VBB Verkehrsverbund Berlin-Brandenburg GmbH (CC BY 4.0). Water outlines © OpenStreetMap contributors (ODbL).

A second program computes lower bounds. Any full route also visits a small target set, such as the dead ends. A Held-Karp search over that set gives a time that no full route can beat. For BART (50 stations), the plan and the bound are both 6:11:00. Human times for BART are 5:09:35 and 5:47:42, so the plan is slower. For the Hamburg U-Bahn (93 stations), the plan takes 4:45:00 and the bound is 4:34:00.

An independent audit re-ran the checker and agreed with the London and Berlin U-Bahn times. It also found little slack. Some changes have 30 s, one foot leg ends 2 s before its train, and the timetable has no delays. We re-ran the checker on the current NYC, BART and Hamburg plans. All are valid.

The bounds used 180 s for every change of direction, also at a terminus. We did not run them again under the 60 s terminus rule, so the BART optimality is not confirmed under the current rules. Nobody else has reviewed the bound program. Earlier computed routes exist for NYC (rigter.ink, Trail of Bits), the Berlin S-Bahn (ZIB-Report 15-13) and London (Rappos 2005).

Other timetables are from the MTA, Transport for London (Powered by TfL Open Data), BART and Hamburger Verkehrsverbund GmbH (hvv, dl-de/by-2-0). The London data was taken from the Bus Open Data Service. It contains public sector information licensed under the Open Government Licence v3.0, and OS data © Crown copyright and database rights 2016. Foot distances contain information from OpenStreetMap (ODbL). No publisher endorses this work or warrants that the data is accurate.

*Code available on request. The data is third-party and is not redistributed.*
