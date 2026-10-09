from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np

lithologies = ['Shale', 'Sandstone', 
               'Limestone', 'Dolomite', 
               'Anhydrite', 'Coal', 'Tuff']
well1 = [47, 35, 10, 1, 0, 2, 5]
well2 = [7, 10, 51, 22, 10, 0, 0]

lithologies = [*lithologies, lithologies[0]]
well1 = [*well1, well1[0]]
well2 = [*well2, well2[0]]

label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(lithologies))

fig, ax = plt.subplots(figsize=(10,10), subplot_kw=dict(polar=True))
ax.plot(label_loc, well1, lw=2)
ax.plot(label_loc, well2, lw=2)
ax.fill(label_loc, well1, alpha=0.3)
ax.fill(label_loc, well2, alpha=0.3)
lines, labels = plt.thetagrids(np.degrees(label_loc), labels=lithologies)
plt.show()