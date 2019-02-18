
import scipy.cluster.vq as vq

class Analyzer:
    def __init__(self, Kmax, Kmin = 0):
        self.Kmin, self.Kmax = Kmin, Kmax
        self.clusters = []
    
    def getResults(self):
        return self.clusters
    
    def analyze(self, X):
        self.k_means(X)

    def k_means(self, X):
        pass
        
    

        


