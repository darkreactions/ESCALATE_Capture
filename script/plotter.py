import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plotme(x,y,z):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')
    ax.scatter(x,y,zs=z)
    ax.set_xlabel('[M]' )
#    ax.plot(x,y,z)
    plt.show()

