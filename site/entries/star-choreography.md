---
title: A numerically found 10-body choreography that traces a five-pointed star
date: 2026-11-24
tags: maths, physics, optimization
status: Audited
summary: Ten equal masses on one Newtonian orbit near a star shape (score 0.0272 against 0.0645 for a circle), closing to 2.47e-23 in an independent integrator.
image: assets/star-choreography/newton-star.png
---
A choreography is a periodic motion of N equal masses in which all bodies follow one closed curve, one behind the other. The best-known example is the three-body figure eight. We asked a simple question. Which choreographies under Newtonian gravity come nearest to a given picture, such as a star, a square or a trefoil?

The search wrote the curve as a Fourier series with the choreography symmetry built in. It solved the equations of motion with Levenberg-Marquardt. Often it started from a solution for a stronger force (1/r^3) and moved to gravity (1/r^2). A frozen verifier then integrated each orbit for one full period in double-double arithmetic. A score measured the distance between the orbit and the target outline. The baseline is a circle of N bodies.

![Red closed curve with five small loops over a grey five-pointed star outline, with ten black dots for the bodies](assets/star-choreography/newton-star.png)

The numerically found 10-body orbit (red) and the target star (grey). The dots are the ten bodies at one instant.

The best result is a numerically found choreography of 10 bodies on a curve with five small loops, near a five-pointed star. Its score is 0.0272, and the circle scores 0.0645. A 12-body orbit near a square scores 0.0192 against 0.0336. A 10-body trefoil scores 0.0121 against 0.0917.

An independent audit used its own Gragg-Bulirsch-Stoer integrator, with no shared code. The published start of the star returns to itself after one period to 2.47e-23 of the orbit size. The square closes to 4.99e-23 and the trefoil to 5.05e-19. Energy drift stays below 1e-31 relative. A computer-assisted check for the star also passes in our own program, but nobody else has reviewed that program.

These orbit types are known. The star and the square have the structure of resonant Lyapunov orbits of the rotating regular polygon (Calleja, Doedel and García-Azpeitia), and the topology of the Montaldi-Steckles classes D(6,5) and D(6,4). We did not find the 10-body and 12-body members in the published sources that we opened. We did not open every online catalogue.

Each orbit is the best of one search pool of about 65 to 600 local solutions, with at most 16 bodies. Better matches can exist. All orbits are strongly unstable. From a 34-digit start, the star loses its shape after about 4 periods. A change of one part in a million breaks it in about one period. The model uses point masses in a plane with exactly equal masses.

*Code and data: available on request.*
