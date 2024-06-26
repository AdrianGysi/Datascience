import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import LabelEncoder
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list, fcluster
from sklearn.preprocessing import StandardScaler


data=pd.read_csv("dataset.csv")
data_outcome=pd.read_csv("outcome.csv")
data_shape=data.shape
unnamed=data["Unnamed: 0"]
missing_values_count = data.isnull().sum()
missing_values_count.nunique()
zero_values_count = (data == 0).sum()
pik3ca=zero_values_count["TP53"]
relevant_genes=["PGR","ESR1","BRCA1","BRCA2","PIK3CA", "RUNX1", "CDH1", "TP53", "TBX3", "PTEN", "FOXA1", "MAP3K1", "GATA3", "AKT1", "NBL1", "DCTD", "RB1", "SF3B1", "CBFB", "OR9A2", "NCOA3", "RBMX", "MAP2K4", "TROVE2", "NADK", "CASP8", "CTSS", "ACTL6B", "LGALS1", "KRAS", "KCNN3", "FBXW7", "LRIG2", "PIK3R1", "PARP4", "ZNF28", "HLA-DRB1", "ERBB2", "ZMYM3", "RAB42", "CTCF", "ATAD2", "CDKN1B", "GRIA2", "NCOR1", "HRNR", "GPRIN2", "PAX2", "ACTG1", "AQP12A", "PIK3C3", "MYB", "IRS4", "TBL1XR1", "RPGR", "CCNI", "ARID1A", "CD3EAP", "ADAMTS6", "OR2D2", "TMEM199", "MST1", "RHBG", "ZFP36L1", "TCP11", "CASZ1", "GAL3ST1", "FRMPD2", "GPS2", "ZNF362"]
used_data=data[relevant_genes].copy()
used_data["outcome"]=data_outcome["BRCA_subtype"]
used_data=used_data.dropna()

X = used_data.copy().drop('outcome', axis=1)
Y = used_data['outcome']

label_encoders = {}
le = LabelEncoder()
used_data["outcome"] = le.fit_transform(used_data["outcome"])
Y_encoded = le.fit_transform(Y)
label_encoders["outcome"] = le


#
def plot_function(X, labels, titles, n_rows=1, n_cols=2, figsize=(16, 6), pca_applied=False):
    """
    function to plot clusters and true labels

    Parameters:
        X (numpy array): The feature matrix. It is a 2 dimensional matrix with N_samples * 2
        labels (list of arrays): list that stores the arrays that contain the labels (both true labels and labels
                                 assogned by the clustering algorithm)
        titles (list of strings): titles of each subplot
        n_rows (int): number of rows in the subplot
        n_rows (int): number of columns in the subplot
        figsize (tuple): figure dimensions
        pca_applied (bool): If X is the results of a PCA or it's the original dataset

    Output:
        None. It simply shows the figure
    """
    # Create subplots
    fig, axs = plt.subplots(n_rows, n_cols, figsize=figsize, sharex=True, sharey=True)
    # Flatten the array of subplots into a 1-dimensional array.
    try:
        iterations = axs.flatten()
    except:
        # if we have only one row and one column
        iterations = [axs]
    for i, ax in enumerate(iterations):
        y = labels[i]
        title_plot = titles[i]
        # Scatter plot.
        scatter = ax.scatter(X[:, 0],
                             X[:, 1],
                             c=y,
                             cmap='jet',
                             s=5)

        legend = ax.legend(*scatter.legend_elements(),
                           loc="best",
                           title='labels')

        if pca_applied:
            xlab = 'PCA comp 1'
            ylab = 'PCA comp 2'
        else:
            xlab = 'feature 1'
            ylab = 'feature 2'
        ax.add_artist(legend)
        ax.set_xlabel(xlab)
        ax.set_ylabel(ylab)
        ax.set_title(title_plot)

    plt.show()


# initialize KMeans with 2 clusters
kmeans = KMeans(n_clusters = 5, n_init = 'auto')
# fit kmeans
kmeans.fit(used_data)
# extract labels
assigned_clusters = kmeans.labels_

# call plot function
plot_function(X = X.values,
              labels = [Y_encoded, assigned_clusters],
              titles = ['True labels', 'Cluster assigned'],
              n_rows = 1,
              n_cols = 2
             )

if len(np.unique(assigned_clusters)) == 1:
    silhouette = 0.0
else:
    silhouette = silhouette_score(X = X, labels = assigned_clusters)
ari = adjusted_rand_score(labels_true = Y_encoded, labels_pred = assigned_clusters)
print(f'Silhouette score is: {silhouette}')
print(f'ARI score is: {ari}')



scaler = StandardScaler()
scaled_data = scaler.fit_transform(X)
scaled_df = pd.DataFrame(scaled_data, columns=X.columns)

# Randomize the rows and columns
randomized_df = scaled_df.sample(frac=1, axis=0).sample(frac=1, axis=1)

# Plot heatmap before clustering
plt.figure(figsize=(12, 10))
sns.heatmap(randomized_df, cmap='viridis', annot=False)
plt.title("Heatmap Before Clustering (Randomized)")
plt.show()

# Perform hierarchical clustering on rows and columns separately
linkage_matrix_rows = linkage(randomized_df, method='ward')
linkage_matrix_cols = linkage(randomized_df.T, method='ward')

# Get the order of the rows and columns
dendro_rows = dendrogram(linkage_matrix_rows, no_plot=True)
dendro_cols = dendrogram(linkage_matrix_cols, no_plot=True)
ordered_df = randomized_df.iloc[dendro_rows['leaves'], :].iloc[:, dendro_cols['leaves']]

# Plot heatmap after clustering
plt.figure(figsize=(12, 10))
sns.heatmap(ordered_df, cmap='viridis', annot=False)
plt.title("Heatmap After Hierarchical Clustering")
plt.show()

# Visualize the dendrogram for rows
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix_rows, labels=randomized_df.index, leaf_rotation=90)
plt.title("Dendrogram (Rows)")
plt.xlabel("Sample Index")
plt.ylabel("Distance")
plt.show()

# Visualize the dendrogram for columns
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix_cols, labels=randomized_df.columns, leaf_rotation=90)
plt.title("Dendrogram (Columns)")
plt.xlabel("Feature Index")
plt.ylabel("Distance")
plt.show()







