# ArtificialIntelligenceProject
AI project combining ontology reasoning (OWL + Owlready2) and deep learning (Siamese U-Net) to demonstrate knowledge representation and satellite image change detection.

Google Colab Link - https://colab.research.google.com/drive/1Bhf39JapXBlpYeJIlqZacG643RmpiNwy?usp=sharing 


---

## Navigation
- [Project Overview](#project-overview)
- [Knowledge Representation System](#knowledge-representation-system)
- [Deep Learning System](#deep-learning-system)
- [Technologies Used](#technologies-used)
- [Conclusion](#conclusion)

---

## Project Overview

This project demonstrates the integration of two complementary approaches in Artificial Intelligence:

* **Knowledge Representation and Reasoning (KR)** using ontologies and logical inference
* **Deep Learning (DL)** for detecting structural changes in satellite imagery

The objective is to explore how **symbolic AI systems** and **deep learning models** can coexist within the same project and address different types of problems.

The repository contains two main components:

* a Knowledge Representation system for medical reasoning
* a Deep Learning system for satellite image change detection

This work follows an academic perspective by studying both **symbolic** and **subsymbolic** paradigms of Artificial Intelligence within a unified experimental framework.

---

## Knowledge Representation System

### Objective

The knowledge representation component models structured medical domain knowledge using an **OWL ontology** and performs **automated reasoning** to verify relationships between entities.

The ontology represents relationships between:

* diseases
* symptoms
* body parts
* patients
* biological sex

Using **Description Logic and OWL**, the system can detect inconsistencies and infer new knowledge.

### Files

medical_ontology.rdf  
medical_ontology_clean.rdf  
medical_data.ttl  
medical_ontology.db  
ontology_reasoning.py  
medical_final.owl  

### Running the reasoning system

Requirements:

python  
owlready2  
sqlite3  
java  

Run:

python ontology_reasoning.py

This script loads the ontology, maps database entities to ontology individuals, performs reasoning, and generates the inferred ontology:

medical_final.owl

The file can be opened in **Protégé** to inspect the reasoning results.

---

## Deep Learning System

### Objective

The deep learning component implements a neural network capable of detecting structural changes between satellite images captured at different time periods.

The task is formulated as a **pixel-wise binary segmentation problem**, where the model predicts whether each pixel corresponds to a changed region.

The implemented architecture is a **Siamese U-Net**, which processes two temporal images and learns to identify meaningful differences.

### File

DetectingObjectChangesInImages.ipynb

The notebook contains the full deep learning pipeline:

* dataset loading  
* preprocessing and patch extraction  
* model architecture definition  
* training procedure  
* evaluation and visualization  

### Dataset

The model is trained using the **LEVIR-CD dataset**, a benchmark dataset for building change detection.

Each sample contains:

* satellite image at time **T1**
* satellite image at time **T2**
* ground-truth change mask

Images are divided into **256 × 256 patches** to improve training efficiency.

### Results

| Metric | Value |
|------|------|
| IoU | 0.3666 |
| F1-score | 0.5365 |

These results demonstrate that the Siamese network can detect meaningful structural changes in satellite imagery.

---

## Technologies Used

* Python
* TensorFlow / Keras
* NumPy
* Matplotlib
* SQLite
* Protégé
* Google Colab

---

## Conclusion

This project highlights two major paradigms of Artificial Intelligence:

* **Symbolic AI**, through ontology-based reasoning and structured knowledge representation
* **Subsymbolic AI**, through deep neural networks trained on visual data

By implementing both systems in the same project, the work shows how reasoning methods and machine learning models can be studied together within a modern AI context.
