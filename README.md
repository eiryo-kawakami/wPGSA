# wPGSA
Python script used for wPGSA method to estimate relative activities of transcriptional regulators from transcriptome data.

##Introduction
Predicting responsible transcription regulators for given transcriptome data is one of the most promising computational approaches in understanding cellular processes and characteristics. To incorporate information about heterogeneous frequencies of transcription factor (TF)-binding events, we have developed a flexible framework for gene set analysis employing the weighted t-test procedure, namely weighted parametric gene set analysis (wPGSA). Using transcriptome data as an input, wPGSA predicts the activities of transcription regulators responsible for observed gene expression.

##Requirements

- Python
- Python modules: numpy, scipy, rpy2
- R

##Usage

`python wPGSA.py [logFC_file] [networkfile]`
