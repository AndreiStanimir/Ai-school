import os
import numpy as np

path = "../../images/"
fnames = os.listdir(path)
images = np.zeros((len(fnames), 400, 600))

for i in range(len(fnames)):
    image = np.load(os.path.join(path, fnames[i]))
    images[i] = image
#print(images)
print(np.sum(images))
print(np.sum(images,axis=(1,2)))
print(np.argmax(np.sum(images,axis=(1,2))))
mean_image= np.mean(images,axis=0)

from skimage import io
io.imshow(mean_image.astype(np.uint8)) # petru a putea fi afisata
# imaginea trebuie sa aiba
# tipul unsigned int
io.show()