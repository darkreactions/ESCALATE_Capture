#!/usr/bin/env wolframscript
(* ::Package:: *)

(* ::Section:: *)
(*The code*)


(* This module implements UNIFORM RANDOM SAMPLING WITHIN A CONVEX HULL DEFINED BY *)
(* REAGENT VECTORS IN CHEMICAL CONCENTRATION SPACE *)


(* <jschrier@fordham.edu> 24 May 2019 *)
(* correction: 06 June 2019; fixing error with AccuracyGoal and PrecisionGoal causing problem in transfer to cloud; I had misinterpretted
how these are specified, and Mathematica 12 (on kernels and clouds) had different defaults; the older defaults allow the problem to slip by.*)

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
  d = 1+Length@First@reagentDefs,(*dimensionality of the species including the unit volume*)
  v,space},
  v = Array[x,{d}]; (*list of volume variables*)
  space=Cuboid[ConstantArray[0,d],ConstantArray[1,d]];

  ParallelMap[
    NArgMin[ 
      Norm[ stocks.v-Append[#,1] ], (*function to minimize*)
      Element[v,space],
      AccuracyGoal->3, (*note: this is specified as numbers of digits of precision*)
      PrecisionGoal->3 ]&,
   experiments]//
     AssociationThread[reagentNames,Transpose[#]] &(*return a dictionary of reagent name\[Rule]volumes pairs*)
]



(* illustrating an alternate version without gemetric constraints *)
(*
Clear[convertConcentrationsToVolumes]
convertConcentrationsToVolumes[reagentDefs_Association,experiments_?MatrixQ]:=Module[
  {stocks=Transpose[ Append[1]/@Values[reagentDefs]], (*add unit volume to each entry*)
  reagentNames=Keys[reagentDefs], (*names of each reagent, used at conclusion*)
  d=1+Length@First@reagentDefs,(*dimensionality of the species including the unit volume*)
  v,constraintOnTotal,constraintOnSign},
  v=Array[x,{d}]; (*list of volume variables*)
 
  constraintOnTotal=(Total[v]\[Equal]1);
  constraintOnSign = And @@ Thread[v \[GreaterEqual] 0];

  ParallelMap[
    NArgMin[ 
      {Norm[ stocks.v-Append[#,1] ], (*function to minimize*)
      constraintOnTotal&&constraintOnSign},
      v,
      AccuracyGoal\[Rule]3,
      PrecisionGoal\[Rule]3 ]&,
   experiments]//
     AssociationThread[reagentNames,Transpose[#]] &(*return a dictionary of reagent name\[Rule]volumes pairs*)
]
*)

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




(* ::Section:: *)
(*Basic Usage demos*)


(* ::Input:: *)
(*reagents=<|*)
(*"reagent1"->{0.75,0.38,0}, *)
(*"reagent2"->{0,5.84,0}, *)
(*"GBL"->{0,0,0}, *)
(*"FAH"->{0,0,26.5}|>; *)


(* ::Input:: *)
(*reagents*)
(*dropZeroColumns[reagents]*)


(* ::Input:: *)
(*RepeatedTiming[generateExperiments[reagents,1]] (*just one point*)*)


(* ::Input:: *)
(*(*use default settings values*)*)
(*Timing[*)
(*o1=generateExperiments[reagents]; *)
(*]*)
(**)


(* ::Subsection:: *)
(*Visualization of the results*)


(* ::Input:: *)
(*Total[o1]*)


(* ::Input:: *)
(*Histogram[o1,ChartLayout->"Stacked",ChartLegends->Automatic]*)


(* ::Input:: *)
(*y=Table[*)
(*prop->reagents[prop]*#/500&/@o1[prop],*)
(*{prop,Keys[o1]}]//Transpose;*)


(* ::Input:: *)
(*Show[*)
(*Graphics3D[Point[Plus@@Values[#]&/@y]],*)
(*RegionPlot3D[allowedExperiments[reagents,9],PlotStyle->Opacity[0.2]]]*)


(* ::Input:: *)
(*Show[*)
(*ConvexHullMesh[(Values@reagents)[[All,;;2]]],*)
(*Graphics@ Point@(Plus@@Values[#]&/@y)[[All,;;2]]]*)


(* ::Section::Closed:: *)
(*(24 May 2019) Debug for MTynes*)


(* ::Text:: *)
(*(24 May 2019)  Tynes reports an error with the following reagent dictionary.  I have confirmed that this is the "proper" behavior\[LongDash]the system is undefined.  A column cannot be all zero for all entries, or the system is not properly defined*)


(* ::Input:: *)
(*tynes=<|"R1"->{0,0,0},"R2"->{2.85, 0, 2.23},"R3"->{4.18,0,0}|>*)


(* ::Input:: *)
(*<|"R1"->{0,0,0},"R2"->{2.85`,0,2.23`},"R3"->{4.18`,0,0}|>*)


(* ::Subsection:: *)
(*Confirm:  dropping the zeroes solves the problem*)


(* ::Input:: *)
(*tynes2=<|"R1"->{0,0},"R2"->{2.85,  2.23},"R3"->{4.18,0}|>*)


(* ::Input:: *)
(*generateExperiments[tynes2]*)


(* ::Subsection:: *)
(*Solution: down-project the vectors into axes that actually vary.*)


(* ::Text:: *)
(*Note:  Code to drop zero columns is integrated into revised versions of the function above. Below is a confirmation that it operates correctly*)


(* ::Input:: *)
(*tynes*)
(*dropZeroColumns[tynes]*)
(*generateExperiments[%,10]*)


(* ::Section:: *)
(*(31 May 2019) Cloud Deployment of the function*)


(* ::Text:: *)
(*(31 May 2019)  A week later IP wants this as a cloud function. Easy to pull off now that we have the Wolfram Link figured out.  See instructions under "To the Cloud" heading on: *)
(*https://blog.wolfram.com/2019/05/16/announcing-the-wolfram-client-library-for-python/*)
(**)
(*(Written on the airplane LGA-DFW, deployed and tested at the Centurion Lounge in DFW.)*)
(**)
(*(05 June 2019)  Cloud deploy exposed an interesting bug with *)


(* ::Subsubsection::Closed:: *)
(*An initial failed attempt...*)


(* ::Input:: *)
(*Clear[generateExperimentsAPI]*)
(*generateExperimentsAPI=APIFunction[*)
(*{"reagentDefs"->"Expression", (*as JSON representation of the datastructure*)*)
(*"nExpt"->"Integer"->96,*)
(*"maxMolarity"->"Number"->9.,*)
(*"finalVolume"->"Number"->500.,*)
(*"processValues"->Restricted["String",{{"Round","Identity"}}]->"Round"}, (*restrict for security*)*)
(*generateExperiments[*)
(*(*ImportString[#reagentDefs,"JSON"]//Association,*) (*alt: JSON string*)*)
(*#reagentDefs,*)
(*#nExpt,#maxMolarity,#finalVolume,*)
(*ToExpression[#processValues]]&*)
(*,*)
(*"JSON"]*)


(* ::Subsubsection:: *)
(*Modification:  Take reagentDefs input as JSON, and return a JSON output*)


(* ::Input:: *)
(*generateExperimentsAPIv2=APIFunction[*)
(*{"reagentDefs"->"String", (*as JSON representation of the datastructure*)*)
(*"nExpt"->"Integer"->96,*)
(*"maxMolarity"->"Number"->9.,*)
(*"finalVolume"->"Number"->500.,*)
(*"processValues"->Restricted["String",{{"Round","Identity"}}]->"Round"}, (*restrict for security*)*)
(*ExportString[*)
(*generateExperiments[*)
(*ImportString[#reagentDefs,"RawJSON"],*)
(*#nExpt,#maxMolarity,#finalVolume,*)
(*ToExpression[#processValues]],*)
(*"JSON","Compact"->True]&*)
(*,*)
(*"JSON"]*)


(* ::Input:: *)
(**)


(* ::Subsection:: *)
(*Local test of cloud function*)


(* ::Input:: *)
(*reagents=<| (*ye-old demo reagent definitions*)*)
(*"reagent1"->{0.75,0.38,0}, *)
(*"reagent2"->{0,5.84,0}, *)
(*"GBL"->{0,0,0}, *)
(*"FAH"->{0,0,26.5}|>; *)
(**)
(*reagentsJSON=ExportString[reagents,"JSON","Compact"->True] (*make a JSON version*)*)


(* ::Input:: *)
(*results=generateExperimentsAPIv2[<|"reagentDefs"->reagentsJSON,"nExpt"->10|>]*)


(* ::Subsection:: *)
(*Cloud deployment*)


(* ::Input:: *)
(*deployedFunction=CloudDeploy[*)
(*Delayed[generateExperimentsAPIv2],*)
(*CloudObject["api/public/escalate/generateExperiments"],*)
(*Permissions->"Public"*)
(*]*)


(* ::Input:: *)
(*CloudObjectInformation[deployedFunction]*)


(* ::Subsection:: *)
(*Cloud test from within Mathematica environment*)


(* ::Text:: *)
(*Observe:  This is just a a HTTP GET post.  reagentDefs datastructure  is serialized as JSON string and URL-encoded. Other parameters are passed in the usual way.  Notice that there is no reason to specify things that aren't defaults*)


(* ::Input:: *)
(*URLExecute[*)
(*deployedFunction, *)
(*{"reagentDefs"->reagentsJSON,"nExpt"->5}] (*returns a JSON *)*)


(* ::Subsubsection:: *)
(*What does the GET request look like?  *)


(* ::Input:: *)
(*URLBuild[deployedFunction, *)
(*{"reagentDefs"->reagentsJSON,"nExpt"->5}]*)


(* ::Text:: *)
(*If you really want...you can paste this into your web-browser to execute the call...you'll see the JSON in your browser.*)


(* ::Subsection:: *)
(*Calling the function from Wolfram Client Library for Python*)


(* ::Text:: *)
(*https://blog.wolfram.com/2019/05/16/announcing-the-wolfram-client-library-for-python/*)
(*See section on "To the Cloud" for Python code example*)
(**)
(*For more details: https://reference.wolfram.com/language/WolframClientForPython/*)
(*Specifically: https://reference.wolfram.com/language/WolframClientForPython/docpages/basic_usages.html#wolfram-cloud-interactions*)
(**)
(*Notes:*)
(*Username:  jschrier0*)
(*Alternate username:  user-66926eb8-20e9-4399-a998-388c4ba08586*)
(*API endpoint:    api/public/escalate/generateExperiments*)
(**)


(* ::Subsection:: *)
(*Calling the function from Requests (in python)*)


(* ::Text:: *)
(*Sure, why not.  The function defined above is just an HTTP GET with the following fields:*)
(**)
(*{"reagentDefs"->"String", (*as JSON representation of the datastructure*)*)
(*"nExpt"->"Integer"->96,*)
(*"maxMolarity"->"Number"->9.,*)
(*"finalVolume"->"Number"->500.,*)
(*"processValues"->Restricted["String",{{"Round","Identity"}}]->"Round"}, *)
(**)
(*And you can of course leave off any of the optional arguments.  Just serialize the dictionary of lists defining the set of reagents and you are good to go.*)


(* ::Section:: *)
(*Are there negative values returned?*)


(* ::Text:: *)
(*(31 May 2019) Debugging attempts.*)
(*(05 June 2019) Identified the cause of the problem; AccuracyGoal and PrecisionGoal settings are number of digits, not deltas; by setting these to 0.0001, I was effectively asking for zero digits of precision.  The defaults on Mathematica 11.3 somehow ignored this, whereas the *)


(* ::Subsection:: *)
(*No examples of negative values in 1000 calls*)


(* ::Input:: *)
(*results=generateExperiments[reagents,1000];*)


(* ::Input:: *)
(*Length@Select[#,NonNegative]&/@results*)
(*Length@Select[#,Negative]&/@results*)
(**)


(* ::Input:: *)
(*results=generateExperiments[reagents,100]; (*faster iterative debugging to only look at 100 local jobs*)*)


(* ::Input:: *)
(*Length@Select[#,NonNegative]&/@results*)
(*Length@Select[#,Negative]&/@results*)


(* ::Subsection:: *)
(*No negative examples when calling to /from the JSON serializer*)


(* ::Input:: *)
(*results=ImportString[#,"JSON"]&@generateExperimentsAPIv2[<|"reagentDefs"->reagentsJSON,"nExpt"->1000|>];*)


(* ::Input:: *)
(*Length@Select[#,NonNegative]&/@Association[results]*)
(*Length@Select[#,Negative]&/@Association[results]*)


(* ::Subsection:: *)
(*Errors when using the deployed function?*)


(* ::Text:: *)
(*(31 May 2019) Aha!  Errors exist when calling the cloud-deployed version, that do not exist in the local version*)
(**)
(*I initially thought It may be an error in the cloud code, with regards to regions. But replacing this with the algebraic constraint version above does not seem to solve the problem.  *)
(**)
(*(05 June 2019) Solution:  Fixed for consistent behavior.  However, this can take a long time, which times out the *)
(**)


(* ::Input:: *)
(*deployedFunction*)


(* ::Input:: *)
(*(results=URLExecute[*)
(*deployedFunction, *)
(*{"reagentDefs"->reagentsJSON,"nExpt"->96}];)//Timing*)


(* ::Input:: *)
(*results*)


(* ::Input:: *)
(*resultsAssoc=ImportString[results,"JSON"]//Association*)


(* ::Input:: *)
(*Position[#,_?Negative]&/@resultsAssoc*)


(* ::Input:: *)
(*Keys@results*)


(* ::Input:: *)
(*negative=#[[64]]&/@results*)


(* ::Input:: *)
(*?reagents*)


(* ::Input:: *)
(*Length@Select[#,NonNegative]&/@%*)
(*Length@Select[#,Negative]&/@%%*)


(* ::Subsection:: *)
(*Any examples when calling to the web?*)


(* ::Input:: *)
(*URLBuild[deployedFunction, *)
(*{"reagentDefs"->reagentsJSON,"nExpt"->1000}]*)
(**)
(*request*)


(* ::Input:: *)
(*Length@Select[#,NonNegative]&/@results*)
(*Length@Select[#,Negative]&/@results*)
