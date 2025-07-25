# FastTargetPred Results Analyzer

A comprehensive Python module for extracting, analyzing, and formatting FastTargetPred results into clean, structured reports that can be easily communicated and analyzed further.

## Overview

The `results_analyzer.py` module provides a complete solution for processing FastTargetPred output, extracting biological target information, and presenting it in multiple formats (text reports, JSON, CSV). This is particularly useful for:

- **Drug Discovery**: Analyzing potential targets for drug compounds
- **Peptide Research**: Understanding biological activities of tetrapeptides and other peptides
- **Chemical Biology**: Systematic target prediction analysis
- **Research Communication**: Creating clean reports for publications and presentations

## Features

✅ **Complete Target Information Extraction**
- Protein names, genes, organisms
- Similarity scores and ChEMBL IDs
- Biological processes (Gene Ontology)
- Associated diseases
- Pathway information (Reactome)

✅ **Multiple Output Formats**
- Clean text summary reports
- JSON for programmatic access
- CSV for spreadsheet analysis

✅ **Easy Integration**
- Simple Python API
- Command-line utility
- Works with SMILES strings or SDF files

✅ **Comprehensive Analysis**
- Execution time tracking
- Parameter documentation
- Error handling

## Installation

The analyzer is part of the modernized FastTargetPred package. Make sure you have:

```bash
# Activate the FastTargetPred environment
source .venv/bin/activate

# The analyzer is ready to use in src/results_analyzer.py
```

## Quick Start

### 1. Basic Usage (Python API)

```python
from src.results_analyzer import FastTargetPredAnalyzer

# Initialize analyzer
analyzer = FastTargetPredAnalyzer()

# Analyze a compound
results = analyzer.analyze_compound(
    "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    fingerprint="ECFP4",
    threshold=0.7,
    max_targets=5
)

# Print summary report
print(analyzer.create_summary_report(results))

# Export to files
analyzer.export_to_json(results, "caffeine_results.json")
analyzer.create_csv_report(results, "caffeine_results.csv")
```

### 2. Quick Analysis Function

```python
from src.results_analyzer import quick_analysis

# One-line analysis
report = quick_analysis(
    "aspirin:CC(=O)OC1=CC=CC=C1C(O)=O",
    threshold=0.6,
    max_targets=10
)
print(report)
```

### 3. Command-Line Usage

```bash
# Analyze a compound via command line
python analyze_compound.py "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C"

# With custom parameters
python analyze_compound.py "aspirin:CC(=O)OC1=CC=CC=C1C(O)=O" \
    --fingerprint MACCS \
    --threshold 0.6 \
    --max-targets 10 \
    --output-json aspirin_results.json

# From SDF file
python analyze_compound.py --file compound.sdf --output-csv results.csv
```

## Detailed API Documentation

### FastTargetPredAnalyzer Class

#### Methods

**`analyze_compound(compound_input, input_type="smiles", **kwargs)`**
- Complete analysis of a compound
- Returns `CompoundResults` object with structured data
- Parameters:
  - `compound_input`: SMILES string ("name:SMILES") or SDF file path
  - `input_type`: "smiles" or "sdf"
  - `fingerprint`: ECFP4, ECFP6, MACCS, PL (default: ECFP4)
  - `threshold`: Similarity threshold (default: 0.7)
  - `max_targets`: Maximum targets to report (default: 10)

**`create_summary_report(results)`**
- Creates a human-readable text report
- Perfect for presentations and documentation

**`export_to_json(results, output_file=None)`**
- Exports to JSON format for programmatic access
- Includes all extracted information

**`create_csv_report(results, output_file=None)`**
- Creates CSV for spreadsheet analysis
- One row per target prediction

### Data Structures

#### CompoundResults
```python
@dataclass
class CompoundResults:
    compound_name: str
    smiles: str
    fingerprint_type: str
    similarity_threshold: float
    execution_time: float
    num_targets_found: int
    targets: List[Target]
```

#### Target
```python
@dataclass
class Target:
    rank: int
    chembl_compound_id: str
    similarity_score: float
    target_chembl_id: str
    uniprot_id: str
    protein_name: str
    gene_name: str
    organism: str
    target_class: str
    biological_processes: List[str]
    diseases: List[str]
    pathways: List[str]
```

## Examples

### 1. Drug Analysis

```python
# Analyze caffeine
results = analyzer.analyze_compound(
    "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    fingerprint="ECFP4",
    threshold=0.7
)

# Results show adenosine receptors as top targets
print(f"Found {results.num_targets_found} targets")
print(f"Top target: {results.targets[0].protein_name}")
```

### 2. Tetrapeptide Analysis

```python
# Analyze tetrapeptide from research dataset
tetrapeptide = "LAAA:[H]N[C@@H](CC(C)C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(O)=O"
results = analyzer.analyze_compound(tetrapeptide, threshold=0.5)

# Export for further analysis
analyzer.create_csv_report(results, "tetrapeptide_LAAA_targets.csv")
```

### 3. Batch Analysis

```python
# Analyze multiple compounds
compounds = [
    ("caffeine", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"),
    ("aspirin", "CC(=O)OC1=CC=CC=C1C(O)=O"),
    ("ibuprofen", "CC(C)CC1=CC=C(C=C1)C(C)C(O)=O")
]

all_results = []
for name, smiles in compounds:
    results = analyzer.analyze_compound(f"{name}:{smiles}")
    all_results.append(results)

    # Create individual reports
    analyzer.export_to_json(results, f"results/{name}_targets.json")
```

## Working with Research Data

The analyzer works perfectly with the Zenodo research dataset:

```python
# Analyze compounds from the ChEMBL29 dataset
import gzip

# Read tetrapeptides from research data
with gzip.open("Zenodo_dataset/tetrapeptides.dir/160000_TETRAPEPTIDES.smi.Z", 'rt') as f:
    for line in f:
        if line.strip():
            smiles, name = line.strip().split()
            results = analyzer.analyze_compound(f"{name}:{smiles}")

            # Export results for each tetrapeptide
            analyzer.create_csv_report(results, f"tetrapeptide_results/{name}.csv")
```

## Output Examples

### Text Report
```
================================================================================
FastTargetPred Analysis Report: caffeine
================================================================================

COMPOUND INFORMATION:
  Name: caffeine
  SMILES: CN1C=NC2=C1C(=O)N(C(=O)N2C)C
  Fingerprint: ECFP4
  Similarity Threshold: 0.7
  Execution Time: 2.19 seconds
  Targets Found: 2

TARGET PREDICTIONS:
----------------------------------------

1. Acetylcholinesterase
   Similarity Score: 1.000
   ChEMBL Target: CHEMBL220
   UniProt ID: P22303
   Gene: ACHE
   Organism: Homo sapiens (Human)
   Biological Processes:
     • acetylcholine catabolic process
     • neurotransmitter biosynthetic process
     • synaptic transmission
   Associated Diseases:
     • Alzheimer's disease
   Pathways: R-HSA-112311, R-HSA-422085
```

### JSON Output
```json
{
  "compound_name": "caffeine",
  "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
  "fingerprint_type": "ECFP4",
  "similarity_threshold": 0.7,
  "execution_time": 2.19,
  "num_targets_found": 2,
  "targets": [
    {
      "rank": 1,
      "similarity_score": 1.0,
      "target_chembl_id": "CHEMBL220",
      "protein_name": "Acetylcholinesterase",
      "biological_processes": [...],
      "diseases": [...],
      "pathways": [...]
    }
  ]
}
```

### CSV Output
```csv
Compound_Name,Rank,Similarity_Score,Target_ChEMBL_ID,UniProt_ID,Protein_Name,Gene_Name,Organism,Num_Biological_Processes,Num_Diseases,Num_Pathways,Top_Biological_Process,Top_Disease,Sample_Pathways
caffeine,1,1.0,CHEMBL220,P22303,Acetylcholinesterase,ACHE,Homo sapiens (Human),21,0,3,acetylcholine catabolic process,,R-HSA-112311; R-HSA-422085; R-HSA-1483191
```

## Use Cases

### 1. **Drug Discovery Research**
- Identify potential off-targets for drug compounds
- Compare target profiles between similar compounds
- Generate target reports for regulatory submissions

### 2. **Peptide Drug Development**
- Analyze biological activities of designed peptides
- Screen tetrapeptide libraries for specific targets
- Compare natural vs. synthetic peptide activities

### 3. **Chemical Biology Studies**
- Systematic target prediction for compound libraries
- Identify biological pathways affected by compounds
- Create target-compound interaction networks

### 4. **Academic Research**
- Generate clean figures and tables for publications
- Export data for statistical analysis
- Create supplementary datasets

## Tips and Best Practices

1. **Threshold Selection**
   - Use 0.7-0.8 for high-confidence predictions
   - Use 0.5-0.6 for exploratory analysis
   - Use 0.3-0.4 for comprehensive screening

2. **Fingerprint Choice**
   - ECFP4: Good general purpose
   - ECFP6: Better for complex molecules
   - MACCS: Good for drug-like compounds
   - PL: Alternative structural representation

3. **Data Export**
   - JSON: For programmatic analysis
   - CSV: For Excel/R/Python pandas
   - Text: For reports and presentations

4. **Batch Processing**
   - Process compounds in groups
   - Use consistent parameters across batches
   - Export results with systematic naming

## Integration with Other Tools

The analyzer output can be easily integrated with:

- **R/Bioconductor**: Load CSV for statistical analysis
- **Python pandas**: Load JSON/CSV for data science
- **Cytoscape**: Create network visualizations
- **Excel**: Direct CSV import for basic analysis
- **Matplotlib/Seaborn**: Create publication-quality plots

## Example Scripts

- `simple_example.py`: Basic usage examples
- `analyze_compound.py`: Command-line utility
- `demo_analyzer.py`: Interactive demonstration

## Support and Contributing

This analyzer is part of the modernized FastTargetPred v2.0 package. It supports:
- Python 3.8+
- All FastTargetPred fingerprint types
- SMILES and SDF input formats
- ChEMBL database integration

For questions or improvements, refer to the main FastTargetPred documentation.
