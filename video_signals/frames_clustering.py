"""
Clustering video frames to spot most common scenes/frame types for our topic.
We use embeddings from VGG16 to cluster images.
"""

from keras.preprocessing.image import load_img
from keras.applications.vgg16 import preprocess_input

from keras.applications.vgg16 import VGG16
from keras.models import Model

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import os
import numpy as np
import matplotlib.pyplot as plt
import pickle

path_up = os.path.dirname(os.getcwd())

frames_path = path_up + '/video_frames'

# change the working directory to frames folder
os.chdir(frames_path)

videos_images = []

# Retrieve the list of image names from directory
with os.scandir(frames_path) as files:
    for file in files:
        if file.name.endswith('.jpg'):
            videos_images.append(file.name)


model = VGG16()
model = Model(inputs=model.inputs, outputs=model.layers[-2].output)


def extract_features(file, model):
    # load the image as a 224x224 array
    img = load_img(file, target_size=(224, 224))
    img = np.array(img)
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape(1, 224, 224, 3)
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx, use_multiprocessing=True)
    return features


data = {}
p = path_up + "/feature_vectors"


for vid_img in videos_images:
    #  extract the features and update the dictionary
    try:
        feat = extract_features(vid_img, model)
        data[vid_img] = feat
    # if error, save the embeddings
    except:
        with open(p, 'wb') as file:
            pickle.dump(data, file)

# Get list of filenames and features
filenames = np.array(list(data.keys()))
feat = np.array(list(data.values()))

feat = feat.reshape(-1, 4096)

# reduce the amount of dimensions in the feature vector
variance = 0.8
pca = PCA(variance)
pca.fit(feat)
x = pca.transform(feat)

# Find best # of clusters
sse = []
list_k = list(range(3, 15))

for k in list_k:
    km = KMeans(n_clusters=k, random_state=22, n_init='auto')
    km.fit(x)

    sse.append(km.inertia_)

# Plot sse against k
plt.figure(figsize=(6, 6))
plt.plot(list_k, sse)
plt.xlabel(r'Number of clusters *k*')
plt.ylabel('Sum of squared distance');
plt.show()

# cluster feature vectors
n_clusters_ = 7  # Change depending on best number
kmeans = KMeans(n_clusters=n_clusters_, random_state=22, n_init='auto')
kmeans.fit(x)

# holds the cluster id and the images { id: [images] }
groups = {}
for file, cluster in zip(filenames, kmeans.labels_):
    if cluster not in groups.keys():
        groups[cluster] = []
        groups[cluster].append(file)
    else:
        groups[cluster].append(file)


# Create a visualization to see the cluster
def view_cluster(cluster):
    plt.figure(figsize = (25,25));
    # gets the list of filenames for a cluster
    files = groups[cluster]
    # only allow up to 16 images to be shown at a time
    if len(files) > 16:
        print(f"Clipping cluster size from {len(files)} to 16")
        files = files[:16]
    # plot each image in the cluster
    for index, file in enumerate(files):
        plt.subplot(4,4,index+1);
        img = load_img(file)
        img = np.array(img)
        plt.imshow(img)
        plt.axis('off')
    plt.savefig(path_up + '/video_signals/clusters/cluster_' + str(cluster) + '.png')
    plt.close()


for clus in range(n_clusters_):
    view_cluster(clus)

with open(path_up + '/files/clusters.pickle', 'wb') as f:
    pickle.dump(groups, f)

