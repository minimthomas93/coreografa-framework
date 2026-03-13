# Core´ografa – Directed Comparative Fuzz Testing Framework for Functionally Equivalent Systems

Coreografa is a grammar-based framework for automated performance analysis.
It combines feedback-directed input generation with performance metric analysis
to explore how input properties influence the behaviour of software systems.

This repository contains the implementation used in the Master's thesis:

## Overview

Coreografa generates structured inputs using grammar-based fuzzing and evaluates
their impact on runtime and memory consumption. The framework supports analysing
multiple implementations of the same functionality under identical inputs.

The evaluation in the thesis includes several subject systems:

- Sorting algorithms (QuickSort, Bubble Sort, Insertion Sort)
- Regular expression engines
- XML processors
- SQL engines
- HTML-to-PDF rendering systems (WeasyPrint)

## Repository Structure

coreografa-framework
│
├── requirements.txt
├── README.md
└── src
  └── evaluation
    └── across_func
      ├── coreografa_lib # Core framework implementation
      ├── eval_subjects # Subject systems and grammars
      └── eval_results # Generated outputs 


## Installation

Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt

In some environments, additional packages may need to be installed manually if import errors occur. For example:
pip install fandango-fuzzer scipy matplotlib big_o statsmodels xmljson defusedxml apsw weasyprint


## Running Experiments

The main experiment workflow can be executed using:

python -m evaluation.across_func.coreografa_lib.example


This will execute the evaluation workflows for all configured subject systems
and generate performance summaries and plots.

## Requirements

The project depends on several Python libraries, including:

- fandango-fuzzer
- numpy
- scipy
- regex
- pytest

All required dependencies are listed in `requirements.txt`.

## Thesis

This repository accompanies the Master's thesis submitted to  
**Saarland University**.

The implementation is provided to support reproducibility of the experiments.

## License

This project is provided for academic and research purposes.
