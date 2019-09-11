from wolframclient.evaluation import WolframLanguageSession

from capture.devconfig import wolfram_kernel_path

class WolframSampler:

    def __init__(self):
        """A wrapper to generateExperiments.wls

        Written as a class so the Wolfram session is only once at __init__ time.
        """
        self.session = WolframLanguageSession(kernel=wolfram_kernel_path)
        self.session.evaluate('<<./capture/generate/randomSampling.wls')
        self.session.evaluate('<<./capture/generate/enumerativeSampling.wls')
        self._randomlySample = self.session.function('generateExperiments')
        self._enumerativelySample = self.session.function('generateEnumerations')

    def randomlySample(self, reagentVectors, oldReagents=None, nExpt=96, maxMolarity=9., finalVolume=500.):
        """Randomly sample possible experiments in the convex hull of concentration space defined by the reagentVectors

        Runs Josh's Mathematica function called `generateExperiments` defined in `randomSampling.wls`
        Shadows default arguments set at Wolfram level.
        Currently does not expose processVaules argument.

        :param reagentVectors: a dictionary of vector representations of reagents living in species-concentration space
        :param nExpt: the number of samples to draw
        :param maxMolarity: the maximum concentration of any species: defines a hypercube bounding the convex hull
        :param finalVolume: a scalar to act on the concentrations to convert to desired volume
        :return: a dictionary mapping: {reagents => list(volumes)} where list(volumes) has length nExpt
        :raises TypeError: since Mathematica will fail silently on incorrect types
        """
        if not isinstance(reagentVectors, dict):
            raise TypeError('reagentVectors must be dict, got {}'.format(type(reagentVectors)))
        if not isinstance(nExpt, int):
            raise TypeError('nExpt must be int, got {}'.format(type(nExpt)))
        if not isinstance(maxMolarity, float):
            raise TypeError('maxMolarity must be float, got {}'.format(type(maxMolarity)))
        if not isinstance(finalVolume, float):
            raise TypeError('finalVolume must be float, got {}'.format(type(finalVolume)))
        if oldReagents:
            if not isinstance(oldReagents, dict):
                raise TypeError('oldReagents must be dict, got {}'.format(type(oldReagents)))

        if oldReagents:
            result = self._randomlySample(reagentVectors, oldReagents, nExpt, maxMolarity, finalVolume)
            if "Volume of remaining space is zero" in result:
                raise ValueError('New reagents define a convex hull that is covered by that of old reagents.')
        else:
            result = self._randomlySample(reagentVectors, nExpt, maxMolarity, finalVolume)
            
        return result

    def enumerativelySample(self, reagentVectors, uniqueChemNames, deltaV=10., maxMolarity=9., finalVolume=500.):
        """Enumeratively sample possible experiments in the convex hull of concentration space defined by the reagentVectors

        Runs Josh's Mathematica function called `achievableGrid` defined in `enumerativeSampling.wls`
        Shadows default arguments set at Wolfram level.

        :param reagentVectors: a dictionary of vector representations of reagents living in species-concentration space
        :param uniqueChemNames: list of chemicals making up the reagents
        :param maxMolarity: the maximum concentration of any species: defines a hypercube bounding the convex hull
        :param deltaV: the spacing of reagent volumes that define the spacing of the grid in concentration space
        :param finalVolume: a scalar to act on the concentration points to convert to desired volume
        :return:  a dictionary mapping: {reagents => list(volumes)}
        :raises TypeError: since Mathematica will fail silently on incorrect types
        """

        if not isinstance(reagentVectors, dict):
            raise TypeError('reagentVectors must be dict, got {}'.format(type(reagentVectors)))
        if not isinstance(uniqueChemNames, list):
            raise TypeError('uniqueChemNames must be a list, got {}').format(type(uniqueChemNames))
        if not isinstance(maxMolarity, float):
            raise TypeError('maxMolarity must be float, got {}'.format(type(maxMolarity)))
        if not isinstance(deltaV, float):
            raise TypeError('deltaV must be float, got {}'.format(type(deltaV)))
        if not isinstance(finalVolume, float):
            raise TypeError('finalVolume must be float, got {}'.format(type(finalVolume)))

        return self._enumerativelySample(reagentVectors, uniqueChemNames, deltaV, maxMolarity, finalVolume)

    def terminate(self):
        """Kill the session thread"""
        self.session.terminate()
