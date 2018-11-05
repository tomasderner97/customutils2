import matplotlib.pyplot as plt
from PIL import Image
import scipy as sp

img = Image.open("./musicnotes.png")
plt.imshow(sp.asarray(img), interpolation="spline16")
plt.show()
