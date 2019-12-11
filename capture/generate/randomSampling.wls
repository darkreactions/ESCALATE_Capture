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

Clear[allowedExperiments, sampleConcentrations, dropZeroColumns,generateExperiments]

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

ConvexSolution[corners_?MatrixQ, cand_?VectorQ]:=Module[{w,ws},
  w = Array[ws,Length@corners];
  FindInstance[
   (w.corners==cand)&&(Total[w]==1)&&(And@@Table[w[[i]]>=0,{i,Length@w}]),
    w]]

(*updated: 27 Nov 2019 to use the FindInstance[] above*)
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?MatrixQ]:=With[
  {stocks =Values[reagentDefs],
   reagentNames = Keys[reagentDefs]}, (*names of each reagent, used at conclusion*)
  AssociationThread[
    reagentNames->Transpose@Map[First@Values@ConvexSolution[stocks,#]&,experiments]]]



(*convenience function for single experiments*)
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?VectorQ]:=
  First /@ convertConcentrationsToVolumes[reagentDefs,{experiments}]

(*handle the case where there is a column of zeros in the reagentDictionary*)
dropZeroColumns[reagents_Association]:=With[
  {nonzeroSpeciesColumns=Flatten@Position[Max /@ Transpose@Values@reagents, _?Positive]},
  #[[nonzeroSpeciesColumns]]& /@ reagents]


(*testing of stochastic experiments until a candidate solution is found*)
Clear[solve, sampleUntilSuccessful]

solve[corners_,cand_]:=With[
  {solution=ConvexSolution[corners,cand]},
  If[solution==={}, Null, Throw[First@Values@solution]]]

sampleUntilSuccessful[corners_,boundingCuboid_]:=
  Catch[
    Do[ (*really uggly, but this tries batches of 1000 points, and repeats 100x.  
          If the success rate is less than 10^-5 we should probably not do rejection sampling 
          and use Hit-and-Run sampling instead, c.f. https://mathoverflow.net/questions/9854/uniformly-sampling-from-convex-polytopes *)
      solve[corners,#]&/@RandomPoint[boundingCuboid,1000],
    100] ]


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
  ]:=With[
  {speciesDimensionality = Length@First@dropZeroColumns@reagentDefs},
  If[speciesDimensionality <= 3,
    generate3DExperiments[reagentDefs, nExpt, maxMolarity, finalVolume, processValues],
    generateHitAndRunExperiments[reagentDefs, nExpt, maxMolarity, finalVolume, processValues]]]
    
  
generateHitAndRunExperiments[
  reagentDefs_Association, (*key=reagents, value=list of species concentrations*) 
  nExpt_Integer:96, (*number of experiments to generate*)
  maxMolarity_Real:9., (*maximum concentrations for all species*)
  finalVolume_Real:500.,(*scale up the unit volumes to this total volume*)
  processValues_Symbol:Round (*optional function to apply to volumes*)
  ]:=Module[{nonzeroReagentDefs,hullCorners,boundingCuboid,dimensionality,results},
  nonzeroReagentDefs=dropZeroColumns[reagentDefs];
  dimensionality=Length@First@nonzeroReagentDefs;
  hullCorners=Values@nonzeroReagentDefs;
  boundingCuboid=RegionIntersection[
    BoundingRegion@hullCorners,
    Cuboid[ConstantArray[0,dimensionality], ConstantArray[maxMolarity,dimensionality]]];
   results=ParallelTable[sampleUntilSuccessful[hullCorners,boundingCuboid], {nExpt}];
   AssociationThread[
     Keys@reagentDefs->
     Transpose@Map[processValues,finalVolume*results]]]

generate3DExperiments[ (*use of ConvexHullMesh only works in \[LessEqual]3 D*)
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


(* overloaded generalization of generateExperiments;
first argument is the reagents def datastructure for all reagents;
second argument is the defs for the excluded (e.g., old) reagents
Otherwise behavior is the same; samples points only points not in the second experimental space;
added by jschrier on 08.31.2019
*)

generateExperiments[
  reagentsDef_Association,(*key=reagents,value=list of species concentrations*)
  excludedReagentsDef_Association,(*region to excluded*)
  nExpt_Integer:96,(*number of experiments to generate*)
  maxMolarity_Real:9.,(*maximum concentrations for all species*)
  finalVolume_Real:500.,(*scale up the unit volumes to this total volume*)
  processValues_Symbol:Round (*optional function to apply to volumes*)]:=
  With[
    {nonzeroReagentsDef=dropZeroColumns[reagentsDef],
     nonzeroExcludedReagentsDef=dropZeroColumns[excludedReagentsDef]},
     If[Length@First@nonzeroReagentsDef >3, Print["Difference Sampling only implemented for <= 3 species"]; Abort[];];
    With[ (*this is the primary difference from the single-set definition*)
      {hull=Apply[RegionDifference,
                    Map[allowedExperiments[#,maxMolarity]&,
                        {nonzeroReagentsDef,nonzeroExcludedReagentsDef}]
                 ]//BoundaryDiscretizeRegion},
     If[Volume[hull]>0,(*this proceeds as in the other version*)
	  Map[processValues,(*level 2 map on to each entry in the lists to round to int*)
        finalVolume*(*scale up volume*)
        convertConcentrationsToVolumes[nonzeroReagentsDef,sampleConcentrations[hull,nExpt]],{2}], (*return usual key/value pair*)
        "Volume of remaining space is zero" (*goofy error message*)
        ]
        ]]

