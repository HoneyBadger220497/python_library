import matplotlib.pyplot as plt
import matplotlib.patches as pt
from matplotlib import rc
import numpy as np

class Phasor():
    """Use Phasor to draw Phasor diagramms.
       Add new arrows by calling add_current(), add_voltage() or
       add_power() respectively. Those are of the form
       add_...(start,end,color,label_string,LineStyle,fill(bool))

       After adding all arrows, call draw() to plot the diagram.
       All vectors assigned as voltages get normalized with
       respect to the largest voltage added, etc. so that all
       arrows are in units of the according physical quantity.

       The constructor of Phasor takes a 'show'-Argument (bool)
       to decide whether or not the diagram should be drawn immediately
       as well as a 'latex_interpreter'-Argument (bool), set this to True
       if you want the labels to be interpreted with latex.
       """

    def __init__(self, show = True, latex_interpreter = True):
        self.currents = []
        self.voltages = []
        self.powers = []
        self.fs = 15
        self.show = show
        self.lim = (-1,1)

        rc('xtick', labelsize=20)     
        rc('ytick', labelsize=20)

        if latex_interpreter:
            rc('text', usetex=True)

    def add_current(self,start,end,color,string,LineStyle,fill):
        self.currents.append([start,end,color,string,LineStyle,fill])

    def add_voltage(self,start,end,color,string,LineStyle,fill):
        self.voltages.append([start,end,color,string,LineStyle,fill])

    def add_power(self,start,end,color,string,LineStyle,fill):
        self.powers.append([start,end,color,string,LineStyle,fill])

    def set_fontsize(self,fs):
        self.fs = fs

    def set_limits(self,lim):
        self.lim = (-lim,lim)

    def draw(self):
        ax = plt.axes(aspect = 'equal')
        plt.xlim(self.lim)
        plt.ylim(self.lim)

        for cat in [self.currents,self.voltages,self.powers]:
            colors = [s[2] for s in cat]
            strings = [s[3] for s in cat]
            lineStyles = [s[4] for s in cat]
            fills = [s[5] for s in cat]

            vecs = [np.array(cp[1])-np.array(cp[0]) for cp in cat]
            norms = [np.linalg.norm(v) for v in vecs]
            if len(norms) > 0:
                norm = np.max(norms)
            points = [[np.array(v[0])/norm,np.array(v[1])/norm] for v in cat]

            for p,s,c,l,f in zip(points, strings, colors, lineStyles, fills):
                P = p[0]
                Q = p[1]
                PQ = Q - P

                n_PQ = np.array([[0,-1],[1,0]])@PQ/np.linalg.norm(PQ)
                phi = np.arctan2(PQ[1],PQ[0])*180/np.pi % 180

                if 65 < phi < 115:
                    phi -= 90
                elif 115 < phi < 180:
                    phi -= 180

                if abs(n_PQ[0]) <= 1e-3 and n_PQ[1] < 0:
                    fact = 0.15
                elif abs(n_PQ[0]) <= 1e-3 and n_PQ[1] > 0:
                    fact = 0.02
                elif abs(n_PQ[1]) <= 1e-3 and n_PQ[0] < 0:
                    fact = 0.1
                elif abs(n_PQ[1]) <= 1e-3 and n_PQ[0] < 0:
                    fact = 0.05
                elif n_PQ[0] > 0 and n_PQ[1] > 0:
                    fact = 0.015
                elif n_PQ[0] < 0 and n_PQ[1] > 0:
                    fact = 0.1
                elif n_PQ[0] < 0 and n_PQ[1] < 0:
                    fact = 0.1
                elif n_PQ[0] > 0 and n_PQ[1] < 0:
                    fact = 0.05

                t_coords = P + PQ/2 + n_PQ*fact

                a = pt.FancyArrow(P[0],P[1],PQ[0],PQ[1],\
                                head_width = 0.05,\
                                head_length = 0.05,\
                                length_includes_head = True,\
                                color = c,\
                                linestyle = l,\
                                fill = f)
                ax.add_patch(a)
                plt.text(t_coords[0],t_coords[1],s,rotation=phi,color=c,size=self.fs)

        if self.show:
            plt.show()
