import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plotmewf1(Mdf, rxndict):
    ## Cleanup for plotting our chemistry that we care about (not a scalable approach)
    headlist = []
    for header in (Mdf.columns):
        if 'chemical1' in header:
            pass
        else:
            headlist.append(header.split('l')[1].split(' ')[0])
    # always plot the conc of each combination of reagents (ideally)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')
    x = Mdf['chemical2 [M]']
    y = Mdf['chemical3 [M]']
    z = Mdf['chemical5 [M]']
    ax.set_xlabel('%s [M]'%rxndict['chem2_abbreviation'])
    ax.set_ylabel('%s [M]'%rxndict['chem3_abbreviation'])
    ax.set_zlabel('%s [M]'%rxndict['chem5_abbreviation'])
    ax.scatter(x,y,zs=z)
#    ax.plot(x,y,z)
    plt.show()

