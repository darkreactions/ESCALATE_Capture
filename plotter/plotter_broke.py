import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FormatStrFormatter


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
#    ax = fig.add_subplot(111, projection='3d')
    ax = Axes3D(fig)
    x = Mdf['chemical2 [M]']
    y = Mdf['chemical3 [M]']
    z = Mdf['chemical5 [M]']
#    ax.set_xlabel('%s [M]'%rxndict['chem2_abbreviation'])
#    ax.set_ylabel('%s [M]'%rxndict['chem3_abbreviation'])
#    ax.set_zlabel('%s [M]'%rxndict['chem5_abbreviation'])
#    ax.plot(x, z,color='gray', marker='o', linestyle='None',zdir='y', zs= 5.0)
#    ax.plot(y, z,color='gray', marker='o', linestyle='None',zdir='x', zs= 0.0)
    ax.plot(x, y,color='black', marker='o', linestyle='None',zdir='z', zs= 0.0, alpha=0.3)
    ax.view_init(elev=20, azim=-51)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.locator_params(nbins=6)
    plt.tick_params(axis='both', which='major', labelsize=14)
    ax.scatter(x,y,zs=z, s=40)
#    ax.plot(x,y,z)
    plt.show()

