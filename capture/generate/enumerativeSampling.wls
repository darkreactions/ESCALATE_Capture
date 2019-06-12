#!/usr/bin/env wolframscript
(* ::Package:: *)

(*return a list of the maximum concentration present for each chemical species, given the dictionary of reagent concentration vectors*)
speciesMax[reagents_Association]:=Max/@Transpose@Values@reagents

(* compute the grid of points in concentration space, and check for whether they are within the analytical convex hull*)
achievableGrid[
  reagents_Association, (*usual reagents dictionary definition*)
  maximumConcentration_Real:9, (*optional argument for maximum concentration*)
  deltaV_Real:10., (*approximate volume increment at scale*)
  totalVolume_Real:500. (*target final volume*)
  ]:=
  With[
    {axisGrids=Range[#1,0,-#1*(deltaV/totalVolume)]&/@speciesMax[dropZeroColumns@reagents],
     insideHullQ=RegionMember@allowedExperiments[dropZeroColumns@reagents,maximumConcentration]},
    Select[insideHullQ]@
      Flatten[
        Outer[List,##]&@@axisGrids,
        2]
  ]

dropZeroColumns[reagents_Association,uniqueChemicalNames_List]:=With[
  {nonzeroSpeciesColumns=Flatten[Position[Max/@Transpose[Values[reagents]],_?Positive]]},
  { (#1[[nonzeroSpeciesColumns]]&)/@reagents,
    uniqueChemicalNames[[nonzeroSpeciesColumns]]}]

generateEnumerations[
  reagentDefs_Association, (*usual reagents dictionary definition*)
  uniqueChemicalNames_List, (*as provided by ESCALATE; names for each column in the reagentDef lists*)
  deltaV_Real:10., (*approximate volume increment at scale*)
  maxMolarity_Real:9., (*optional argument for maximum concentration*)
  finalVolume_Real:500. ,(*target final volume*)
  processValues_Symbol:Round]:=Module[{nonzeroReagentDefs,nonzeroChemicalNames,hull,concentrationSpaceResults,volumeSpaceResults},
    {nonzeroReagentDefs,nonzeroChemicalNames}=dropZeroColumns[reagentDefs,uniqueChemicalNames];
    hull=allowedExperiments[nonzeroReagentDefs,maxMolarity];
    concentrationSpaceResults=achievableGrid[nonzeroReagentDefs,maxMolarity,deltaV,finalVolume];
    volumeSpaceResults=Map[processValues,finalVolume *convertConcentrationsToVolumes[nonzeroReagentDefs,concentrationSpaceResults],{2}];
    <|"concentrations"->AssociationThread[nonzeroChemicalNames,Transpose[concentrationSpaceResults]],
      "volumes"->volumeSpaceResults|>]