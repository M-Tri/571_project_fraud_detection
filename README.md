# ***File Structure***

```text
.
├── README.md
├── .gitignore
└── source_code/
    ├── DBSCAN.py
    ├── add_labels_to_data.py
    ├── data_to_graph.py
    ├── extract_emails.py
    ├── kmean_clustering.py
    ├── louvain.py
    └── source_data_extraction.py
```

# ***Graph-Based Anomaly Detection in Enron Emails***

This commit finalizes the "Fraud Detection In Enrol emails using Graph Based Anomaly Detection" report, including all code, processed data, results, and the final manuscript.

The core of the work involves transforming the Enron email corpus into a weighted directed communication graph and applying three unsupervised anomaly detection methods: K-Means, DBSCAN, and Louvain.

### Main parts:

* **Data Transformation** 
* **K-Means Clustering** 
* **DBSCAN Outlier Detection**
* **Louvain Community Detection** 

### Conclusion:

The comparative analysis confirms that no single algorithm dominates (in line with literature): K-Means isolates anomalies, DBSCAN detects outliers, and Louvain uncovers fraud rings.