#!/usr/bin/env wolframscript
(* ::Package:: *)


speciesMax[reagents_Association] := Max /@ Transpose@Values@reagents

(* compute the grid of points in concentration space, and check for \
whether they are within the analytical convex hull*)

achievableGrid[reagents_Association,
  maximumConcentration_Real: 9,
  deltaV_Real: 10.,
  totalVolume_Real: 500.] :=
 With[
  {axisGrids =
    Range[#1, 0, -#1*(deltaV/totalVolume)] & /@ speciesMax[reagents],
   insideHullQ =
    RegionMember@allowedExperiments[reagents, maximumConcentration]},
  Select[insideHullQ]@
   Flatten[
    Outer[List, ##] & @@ axisGrids,
    2]
  ]