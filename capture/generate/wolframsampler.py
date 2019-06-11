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
        self._enumerativelySample = self.session.function('achievableGrid')

    def randomlySample(self, reagentVectors, nExpt=96, maxMolarity=9., finalVolume=500.):
        """Randomly sample possible experiments in the convex hull of concentration space defined by the reagentVectors

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

        return self._randomlySample(reagentVectors, nExpt, maxMolarity, finalVolume)

    def terminate(self):
        """Kill the session thread"""
        self.session.terminate()
