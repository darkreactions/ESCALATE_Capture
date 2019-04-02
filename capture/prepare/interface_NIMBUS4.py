import pandas as pd

#Defines what type of liquid class sample handler (pipette) will be needed for the run, these are hardcoded to the robot
def volarray(rdf, maxr):
    hv='HighVolume_Water_DispenseJet_Empty'
    sv='StandardVolume_Water_DispenseJet_Empty'
    lv='Tip_50ul_Water_DispenseJet_Empty'
    x=1
    vol_ar=[]
    while x <= maxr:
        name_maxvol=(rdf.loc[:,"Reagent%i (ul)" %(x)]).max()
        if name_maxvol >= 300:
            vol_ar.append(hv)
        elif name_maxvol >= 50 and name_maxvol <300:
            vol_ar.append(sv)
        elif name_maxvol < 50:
            vol_ar.append(lv)
        x+=1
    return(vol_ar)

#Constructs well array information based on the total number of wells for the run
#Future versions could do better at controlling the specific location on the tray that reagents are dispensed.  This would be place to start
# that code overhaul
# will not work for workflow 3
def MakeWellList(rxndict):
    wellorder=['A', 'C', 'E', 'G', 'B', 'D', 'F', 'H'] #order is set by how the robot draws from the solvent wells
    VialList=[]
    welllimit=rxndict['wellcount']/8+1
    count=1
    while count<welllimit:
        for item in wellorder:
            countstr=str(count)
            Viallabel=item+countstr
            VialList.append(Viallabel)
        count+=1
    df_VialInfo=pd.DataFrame(VialList)
    df_VialInfo.columns=['Vial Site']
    df_VialInfo['Labware ID:']=rxndict['plate_container'] 
    return(df_VialInfo)

# Clean up the final volume dataframe so the robot doesn't die
def cleanvolarray(erdf, maxr):
    columnlist = []
    templatelst = [0]*(len(erdf.iloc[0:]))
    for column in erdf.columns:
        columnlist.append(column)
    count = 1
    newcolumnslist = []
    while count <= maxr:
        reagentname =('Reagent%s (ul)' %count)
        if reagentname not in columnlist:
            newcolumnslist.append(reagentname)
        else:
            pass
        count+=1
    for item in newcolumnslist:
        newdf = pd.DataFrame(templatelst)
        newdf.columns = [item]
        erdf = pd.concat([erdf, newdf], axis=1, sort=True)
    erdf = erdf.reindex(sorted(erdf.columns), axis=1)
    return(erdf)

def preprobotfile(rxndict, vardict, erdf):
    df_Tray=MakeWellList(rxndict)
    vol_ar=volarray(erdf, vardict['max_robot_reagents'])
    Parameters={
    'Reaction Parameters':['Temperature (C):','Stir Rate (rpm):','Mixing time1 (s):','Mixing time2 (s):', 'Reaction time (s):',""], 
    'Parameter Values':[rxndict['temperature2_nominal'], rxndict['stirrate'], rxndict['duratation_stir1'], rxndict['duratation_stir2'], rxndict['duration_reaction'] ,''],
    }
    Conditions={
    'Reagents':['Reagent1', "Reagent2", "Reagent3", "Reagent4",'Reagent5','Reagent6','Reagent7'],
    'Reagent identity':['1', "2", "3", "4",'5','6','7'],
    'Liquid Class':vol_ar,
    'Reagent Temperature':[rxndict['reagents_prerxn_temperature']]*len(vol_ar)}
    df_parameters=pd.DataFrame(data=Parameters)
    df_conditions=pd.DataFrame(data=Conditions)
    outframe=pd.concat([df_Tray.iloc[:,0],erdf,df_Tray.iloc[:,1],df_parameters, df_conditions], sort=False, axis=1)
    robotfile = ("localfiles/%s_RobotInput.xls" %rxndict['RunID'])
    outframe.to_excel(robotfile, sheet_name='NIMBUS_reaction', index=False)
    return(robotfile) 