#!/usr/bin/env wolframscript
(* ::Package:: *)

(* <jschrier@fordham.edu> 24 May 2019 *)

Clear[allowedExperiments, sampleConcentrations, convertConcentrationsToVolumes, x, dropZeroColumns,generateExperiments]

(*define the convex hull of allowed experiments*)
allowedExperiments[reagents_Association, {minConcentration_List, maxConcentration_List}]:=With[
  {compositionBoundary=ConvexHullMesh@Values@reagents,
  imposedBoundary=Cuboid[minConcentration,maxConcentration]},
  RegionIntersection[compositionBoundary, imposedBoundary ]//BoundaryDiscretizeRegion]

(*overloaded versions that take a list of maxima or a scalar maximum*)
allowedExperiments[reagents_Association, maxConcentration_List]:=allowedExperiments[reagents,{0*maxConcentration,maxConcentration}]

allowedExperiments[reagents_Association,maxConcentration_?NumericQ]:=With[
  {correctDimensionalityVector=ConstantArray[1,Length@First@reagents]},
allowedExperiments[reagents, {0*correctDimensionalityVector,maxConcentration*correctDimensionalityVector}]]


(*generate random uniformly sampled experiments in concentration space*)
sampleConcentrations[allowedHull_BoundaryMeshRegion,nExpts_Integer:96]:=RandomPoint[allowedHull,nExpts]


(*given the reagent dictionary and the concentration vector describing one experiment, return a dictionary describing the volumes of reagent*)
(*the geometric constraint approach is slightly slower (by 0.05 seconds/sample), but I think it is clearer; we are not CPU bound here*)
(*this version  takes a list of lists of all experiments and returns a dictionary of reagent name->lists of volumes for all experiments*)
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?MatrixQ]:=Module[
  {stocks=Transpose[ Append[1]/@Values[reagentDefs]], (*add unit volume to each entry*)
  reagentNames=Keys[reagentDefs], (*names of each reagent, used at conclusion*)
  d=1+Length@First@reagentDefs,(*dimensionality of the species including the unit volume*)
  v,space},
  v=Array[x,{d}]; (*list of volume variables*)
  space=Cuboid[ConstantArray[0,d],ConstantArray[1,d]];

  ParallelMap[
    NArgMin[ 
      Norm[ stocks.v-Append[#,1] ], (*function to minimize*)
      Element[v,space],
      AccuracyGoal->0.0001,
      PrecisionGoal->0.0001 ]&,
   experiments]//
     AssociationThread[reagentNames,Transpose[#]] &(*return a dictionary of reagent name\[Rule]volumes pairs*)
]

(*convenience function for single experiments*)
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?VectorQ]:=
  First /@ convertConcentrationsToVolumes[reagentDefs,{experiments}]

(*handle the case where there is a column of zeros in the reagentDictionary*)
dropZeroColumns[reagents_Association]:=With[
  {nonzeroSpeciesColumns=Flatten@Position[
    Max/@Transpose@Values@reagents,
     _?Positive]},
  #[[nonzeroSpeciesColumns]]&/@reagents]

(*main interface from python*)
(*return a dictionary of lists (pandas dataframe format) of dispense volumes*)
(*use wl.Identity from Python (instead of wl.Round) to change final processing step*)
(*generating the dictionary of lists is ~1% faster, so I've rewritten it to emphasize this, rather than maintaining two functions*)
generateExperiments[
  reagentDefs_Association, (*key=reagents, value=list of species concentrations*) 
  nExpt_Integer:96, (*number of experiments to generate*)
  maxMolarity_Real:9., (*maximum concentrations for all species*)
  finalVolume_Real:500.,(*scale up the unit volumes to this total volume*)
  processValues_Symbol:Round (*optional function to apply to volumes*)
  ]:=With[{nonzeroReagentDefs=dropZeroColumns[reagentDefs]},
    With[
    {hull=allowedExperiments[nonzeroReagentDefs,maxMolarity]},
    Map[
	processValues, (*level 2 map on to each entry in the lists to round to int*)
	finalVolume*(*scale up volume*)
	convertConcentrationsToVolumes[nonzeroReagentDefs,sampleConcentrations[hull,nExpt]],
	{2}]
  ]](*returns a dictionary (keys=reagent names, values=lists of dispense volumes*)





