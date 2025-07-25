# FastTargetPred v2.0

[![Orcid: Jakob](https://img.shields.io/badge/Jakob-bar?style=flat&logo=orcid&labelColor=white&color=grey)](https://orcid.org/0000-0002-2841-7284)

> [!CAUTION]
> **⚠️ IMPORTANT DISCLAIMER - USE AT YOUR OWN RISK ⚠️**
>
> **This repository has been ENTIRELY modernized and updated using AI assistance. The original FastTargetPred codebase has been significantly modified, including:**
> - Complete code refactoring and modernization
> - New dependency management systems
> - Updated Python syntax and type annotations
> - New SMILES input functionality
> - Integrated results analysis tools
>
> **While extensive testing has been performed, users should exercise extreme caution:**
> - ✅ Test thoroughly with your specific use cases before relying on results
> - ✅ Validate outputs against known reference compounds
> - ✅ Compare results with the original FastTargetPred version where possible
> - ⚠️ Use at your own risk for research and production environments
> - ⚠️ No warranty is provided for accuracy or functionality
>
> **The original research and algorithms probably maybe remain intact, but the implementation has been extensively modified.**

FastTargetPred is a modern target prediction tool for molecular compounds that has been updated to use contemporary Python practices and dependency management.

## Key Improvements in v2.0

### 1. Modern Dependency Management
- Added `pyproject.toml` for modern Python package configuration
- Added `requirements.txt` for backward compatibility
- Proper dependency specification with version constraints
- Support for optional dependencies (development, jupyter)

### 2. Updated Python Version Support
- **Minimum Python version: 3.8+** (previously 3.7+)
- Modern type annotations throughout the codebase
- Updated syntax using f-strings and modern Python features
- Better error handling and type safety

### 3. Integrated MayaChemTools Support
- No longer requires MayaChemTools to be in PATH
- Automatically uses bundled `mayachemtools` directory
- Fallback to system PATH if bundled version not available
- Improved error messages and setup guidance

### 4. SMILES String Input Support
- **New feature**: Accept SMILES strings directly as input
- Format: `name1:SMILES1 name2:SMILES2` or just `SMILES`
- Automatic conversion to SDF format using RDKit
- 3D coordinate generation and optimization
- Mutually exclusive with SDF file input

## Installation

### Prerequisites

1. **MayaChemTools Setup**: Download and unzip MayaChemTools into the `mayachemtools/` folder:
   ```bash
   # The mayachemtools directory should be present in the root directory
   # If not already bundled, download from the official source and unzip here
   ```

2. **Research Dataset (Optional)**: For access to the complete research dataset including 160,000 tetrapeptides and ChEMBL29 compounds:
   ```bash
   # Download the Zenodo research dataset
   wget https://zenodo.org/records/5751499/files/Zenodo_Final-data-_for_FastTargetPred-and-Tetrapeptides_data.zip
   unzip Zenodo_Final-data-_for_FastTargetPred-and-Tetrapeptides_data.zip
   ```

   The dataset contains:
   - 714,780 ChEMBL29 compounds with pre-computed fingerprints
   - 160,000 systematically enumerated tetrapeptides
   - Target prediction results and similarity analyses

### Using pip (Recommended)
```bash
# Install in development mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### Using conda (Alternative)
```bash
# Create a new environment
conda create -n fasttargetpred python=3.8
conda activate fasttargetpred

# Install dependencies
conda install numpy matplotlib pandas
conda install -c conda-forge rdkit

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

#### Using SDF Files (Traditional)
```bash
# Basic usage with SDF file
fasttargetpred input.sdf

# With custom database and fingerprint
fasttargetpred input.sdf -db db/chembl25_active -fp ECFP4 MACCS

# Multiple SDF files
fasttargetpred file1.sdf file2.sdf file3.sdf
```

#### Using SMILES Strings (New Feature)
```bash
# SMILES with names
fasttargetpred -smiles "aspirin:CC(=O)OC1=CC=CC=C1C(=O)O" "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C"

# SMILES without names (uses SMILES as name)
fasttargetpred -smiles "CC(=O)OC1=CC=CC=C1C(=O)O" "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"

# Tetrapeptide example (from research dataset)
fasttargetpred -smiles "LAAA:[H]N[C@@H](CC(C)C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(O)=O" -fp ECFP4 -tc 0.5

# Another tetrapeptide example - AEDG (Ala-Glu-Asp-Gly) using lower threshold for better coverage
fasttargetpred -smiles "AEDG:N[C@@H](C)C(=O)N[C@@H](CCC(O)=O)C(=O)N[C@@H](CC(O)=O)C(=O)NCC(O)=O" -fp ECFP4 -tc 0.3
```

#### Processing Results
```bash
# Generate HTML report from CSV output
fasttargetpred-workup -i output.csv -o report.html

# With structure images (requires RDKit)
fasttargetpred-workup -i output.csv -o report.html -sdf input.sdf

# With statistics plots
fasttargetpred-workup -i output.csv -o report.html -p
```

### Programmatic Usage

```python
from src.main import main
from src.arg_parsing import UserArguments

# Use the modernized API
# (Implementation details would depend on specific use case)
```

## Dependencies

### Required
- Python 3.8+
- NumPy >= 1.20.0
- Matplotlib >= 3.4.0
- RDKit >= 2022.3.1 (for SMILES support)
- Pandas >= 1.3.0

### Optional
- Jupyter >= 1.0.0 (for notebook support)
- pytest >= 6.0 (for development)
- black >= 22.0 (for code formatting)
- flake8 >= 4.0 (for linting)
- mypy >= 0.910 (for type checking)

## Key Changes from v1.x

### Breaking Changes
- **Minimum Python version increased from 3.7 to 3.8**
- Some internal APIs have changed (mainly affects programmatic usage)
- Command-line interface remains largely compatible

### New Features
- SMILES string input support with `-smiles` flag
- Automatic 3D coordinate generation for SMILES inputs
- Better error messages and validation
- Modern type annotations throughout

### Improvements
- No longer requires MayaChemTools in PATH
- Better dependency management with `pyproject.toml`
- Cleaner, more maintainable code structure
- Enhanced error handling and user feedback

## Migration Guide

### From v1.x to v2.0

1. **Update Python**: Ensure you're using Python 3.8 or later
2. **Install dependencies**: Use `pip install -r requirements.txt` or `pip install -e .`
3. **MayaChemTools**: No longer needs to be in PATH - uses bundled version
4. **SMILES support**: New feature - try it with `-smiles` flag instead of SDF files

### Command Line Compatibility
Most existing command lines should work without changes:
```bash
# v1.x (still works in v2.0)
python FastTargetPred.py input.sdf -db db/chembl25_active

# v2.0 (preferred)
fasttargetpred input.sdf -db db/chembl25_active
```

## Development

### Setting up Development Environment
```bash
# Clone and install in development mode
git clone https://github.com/ludovicchaput/FastTargetPred.git
cd FastTargetPred
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

### Building C Extensions
```bash
# Compile platform-specific C extensions
python setup.py /path/to/python/include
```

## License

This project maintains the same license as the original FastTargetPred.

## Authors

- Valentin Guillaume
- Ludovic Chaput

## Changelog

### v2.0.0
- ✨ **New**: SMILES string input support
- ✨ **New**: Modern dependency management with pyproject.toml
- ✨ **New**: Integrated MayaChemTools (no PATH requirement)
- 🔧 **Changed**: Minimum Python version 3.8+
- 🔧 **Changed**: Modern type annotations throughout
- 🔧 **Changed**: Improved error handling and user feedback
- 🐛 **Fixed**: Various type safety and compatibility issues

### v1.x
- Initial release with SDF file support
- Basic target prediction functionality


## Original README

What does FastTargetPred do ?
FastTargetPred allows to predict putative protein target(s) for a query compound or for a collection of compounds.

How to install FastTargetPred ?
1. Download the entire folder
2. Download the free chemistry toolkit MayaChemTools directory (http://www.mayachemtools.org/)
3. To launch FastTargetPred, you must use Python version 3.7 or superior.
   The help program includes every instruction to run the program. You can run it with the following command:
   python3.7 FastTargetPred.py -help


For more information, a user guide is provided: FastTargetPred_manual.pdf.
