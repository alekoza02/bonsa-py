import numpy as np

class Crescita:
    def __init__(self) -> None:
        self.data = np.array([1,2,3])
        self.valore_std = 10
    
    def aggiungi(self):
        self.data = np.append(self.data, len(self.data) + 1)
        
        return self.data
    
    def aggiungi_std(self):
        self.data = np.append(self.data, self.valore_std)
        
        return self.data
    

if __name__ == '__main__':
    c = Crescita()
    print(c.aggiungi())
    print(c.aggiungi())
    print(c.aggiungi())
    print(c.aggiungi())
    print(c.aggiungi_std())
    print(c.aggiungi())
    
    c.valore_std = 0
    
    print(c.aggiungi_std())
    print(c.aggiungi())