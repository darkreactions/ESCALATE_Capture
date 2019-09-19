#!/usr/bin/env wolframscript
(* ::Package:: *)

(* ::Section:: *)
(*The code*)


(* This module implements UNIFORM RANDOM SAMPLING WITHIN A CONVEX HULL DEFINED BY *)
(* REAGENT VECTORS IN CHEMICAL CONCENTRATION SPACE *)


(* <jschrier@fordham.edu> 24 May 2019 *)
(* correction: 06 June 2019; fixing error with AccuracyGoal and PrecisionGoal causing problem in transfer to cloud; I had misinterpretted
how these are specified, and Mathematica 12 (on kernels and clouds) had different defaults; the older defaults allow the problem to slip by.*)
(*revision: 27 Aug 2019 (jschrier):  Changed definition of problem dimensionality d in convertConcentrationsToVolumes[] function. I was using an accidental degeneracy between the number of species and the number of reagents to define the problem dimension.  Thinking about this reveals the correct choice.  I also want to up the Accuracy and Precision goals, so as to be closer to 500 uL on the nose (previous goal of 3 digits had values within 1%, now we are <1%) Detailed notes in 2019.08.27_escalate_multistock_debug.nb   *) 

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
sampleConcentrations[allowedHull_BoundaryMeshRegion,nExpts_Integer:96] := RandomPoint[allowedHull,nExpts]


(*given the reagent dictionary and the concentration vector describing one experiment, return a dictionary describing the volumes of reagent*)
(*the geometric constraint approach is slightly slower (by 0.05 seconds/sample), but I think it is clearer; we are not CPU bound here*)
(*this version  takes a list of lists of all experiments and returns a dictionary of reagent name->lists of volumes for all experiments*)

Clear[convertConcentrationsToVolumes]
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?MatrixQ]:=Module[
  {stocks = Transpose[ Append[1]/@Values[reagentDefs]], (*add unit volume to each entry*)
   reagentNames = Keys[reagentDefs], (*names of each reagent, used at conclusion*)
   d = Length@Keys@reagentDefs,(*dimensionality of the volume space to work in*)
   v,space},
  v = Array[x,{d}]; (*list of volume variables*)
  space=Cuboid[ConstantArray[0,d],ConstantArray[1,d]];

  ParallelMap[
    NArgMin[ 
      Norm[ stocks.v-Append[#,1] ], (*function to minimize*)
      Element[v,space],
      AccuracyGoal->4, (*note: this is specified as numbers of digits of precision*)
      PrecisionGoal->4 ]&,
   experiments]//
     AssociationThread[reagentNames,Transpose[#]] &(*return a dictionary of reagent name\[Rule]volumes pairs*)
]



(*convenience function for single experiments*)
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?VectorQ]:=
  First /@ convertConcentrationsToVolumes[reagentDefs,{experiments}]

(*handle the case where there is a column of zeros in the reagentDictionary*)
dropZeroColumns[reagents_Association]:=With[
  {nonzeroSpeciesColumns=Flatten@Position[Max /@ Transpose@Values@reagents, _?Positive]},
  #[[nonzeroSpeciesColumns]]& /@ reagents]


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



