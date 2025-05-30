# Files2DB

The goal of this project is to be able to concatenate a multitude of flat plain files (.csv, .xlsx) into a single, standardized database. 

1. [Problematic](#1-problematic)
2. [Python script](#2-python-script)
    - [Script structure](#21-script-structure)
    - [Installation](#22-installation)
    - [Launch](#23-launch-of-the-script)

## 1. Problematic

### 1.1 Starting data

- Multitude of Excel files and CSV files
- Modalities of variable not standardized
- Identity of a line is bound to complex keys

### 1.2 Goal

- Single working file
- Normalized data
- Needs to formaly identify each observation
- Simple data update
- Overview of errors
- Traceability and reproducibility

### 2.3 Problems to solve

- Identification of the individual:
  - Not always the same information available, need to check through different candidate keys
- Data normalization
  - Usual and official name to be separated
  - Breed written differently and crossbred dogs poorly registered in Cani-DNA
  - Excel date (without comment)
- Dysplastic information:
  - Diagnosis at different ages, different readers
  - Not always the same measurement (distraction index, Norberg angle or FCI notation)
  - Bilateral or not
- Genealogy
  - Parents identified only by Name + Affixe

## 2. Python script

The use of a script will allow all the work of concatenating all the files to be done automatically. The goal is that it, from a csv file referencing all the Excel files to be integrated, accesses these files, iterates through them and updates a database integrating all the available data. This will make it easy to add a new file to update with new data.

- It will be necessary to have an output file for errors with their reasons and locations as well as a consultation file in csv format containing all the data.
- For each piece of information, the format of the information must be checked and modified if possible.
- A unique identifier for each observation must be generated.

### 2.1 Script structure

The goal of the script is first to aggregate all the data from the different files, then to normalize it and finally to save it in a database.

### 2.2 Installation

#### 2.2.1 Installation of the repository

First clone the repository

```bash
git clone https://github.com/LouisLeNezet/Files2DB.git
```

#### 2.2.2 Installation of the environment

You will need the conda environment mentioned in the `environment.yml` file

To install it use:

```bash
conda env create --file environment.yml
conda activate env_concat
```

#### 2.2.3 Update dependencies

To update the dependencies, run the following command:

```bash
conda env update --file environment.yml
```

### 2.3 Launch of the script

To launch the script

```bash
python files2db/cli.py --help
python files2db/cli.py "file/path"
```

This command line will launch the script directly in the command prompt with the file `file/path` that you have chosen.

## 3. Tests

To launch the tests, run the following command:

```bash
pytest --cov --cov-report=lcov
coverage lcov
```
