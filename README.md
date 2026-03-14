[![codecov](https://codecov.io/gh/louislenezet/files2db/branch/dev/graph/badge.svg)](https://codecov.io/gh/louislenezet/files2db)
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](https://opensource.org/licenses/gpl-3-0)

# Files2DB

<table>
  <tr>
    <td>
      <p>
        <i>One script to rule them all, one script to find them, one script to bring them all and in a database bind them.</i>
      </p>
      <p>
        <strong>files2db</strong> is a python tool to help anyone concatenate, normalize and check a multitude of flat plain files (.csv, .xlsx) into a single, standardized database.
      </p>
      <ul>
        <li><a href="#1-problematic">Problematic</a></li>
        <li><a href="#2-python-script">Python script</a>
          <ul>
            <li><a href="#21-script-structure">Script structure</a></li>
            <li><a href="#22-installation">Installation</a></li>
            <li><a href="#23-launch-of-the-script">Launch</a></li>
          </ul>
        </li>
      </ul>
    </td>
    <td style="text-align:right;">
      <img src="assets/logo_files2db.png" alt="Files2DB Logo" height="100%"/>
    </td>
  </tr>
</table>

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

- Identification of an observation:
  - Not always the same information available, need to check through different candidate keys
- Data normalization
  - Need to split some of the information into several columns
  - Need to merge some of the information into a single column
  - Need to convert the format of the information
  - Excel date (no comment)
- Data validation:
  - Need to check the format of the information
  - Need to check the consistency of the information:

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
python -m files2db.cli --help
python -m files2db.cli "file/path"
```

This command line will launch the script directly in the command prompt with the file `file/path` that you have chosen.

## 3. Tests

To launch the tests, run the following command:

```bash
pytest --cov --cov-report=lcov
coverage lcov -o lcov.info
```

## 4. License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
