"""
FastTargetPred Results Analyzer

This module provides functions to extract, analyze, and present FastTargetPred results
in a clean, structured format for easy communication and further analysis.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import json


@dataclass
class Target:
    """Represents a single target prediction."""

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


@dataclass
class CompoundResults:
    """Represents complete FastTargetPred results for a compound."""

    compound_name: str
    smiles: str
    fingerprint_type: str
    similarity_threshold: float
    execution_time: float
    num_targets_found: int
    targets: List[Target]


class FastTargetPredAnalyzer:
    """Analyzer for FastTargetPred results."""

    def __init__(self, fasttargetpred_path: str = "FastTargetPred.py"):
        """
        Initialize the analyzer.

        Args:
            fasttargetpred_path: Path to the FastTargetPred.py script
        """
        self.fasttargetpred_path = Path(fasttargetpred_path)

    def run_prediction(
        self,
        compound_input: str,
        input_type: str = "smiles",
        fingerprint: str = "ECFP4",
        threshold: float = 0.7,
        max_targets: int = 10,
        **kwargs,
    ) -> str:
        """
        Run FastTargetPred on a compound and return raw output.

        Args:
            compound_input: SMILES string (name:SMILES) or SDF file path
            input_type: "smiles" or "sdf"
            fingerprint: Fingerprint type (ECFP4, ECFP6, MACCS, PL)
            threshold: Similarity threshold
            max_targets: Maximum number of targets to report
            **kwargs: Additional FastTargetPred arguments

        Returns:
            Raw output string from FastTargetPred
        """
        cmd = [
            "python",
            str(self.fasttargetpred_path),
            "-fp",
            fingerprint,
            "-tc",
            str(threshold),
            "-nbt",
            str(max_targets),
        ]

        # Add additional arguments
        for key, value in kwargs.items():
            if key in ["db", "sd", "o", "f", "cpu"]:
                cmd.extend([f"-{key}", str(value)])
            elif key in ["bppt", "noinfo"]:
                if value:
                    cmd.append(f"-{key}")

        if input_type == "smiles":
            cmd.extend(["-smiles", compound_input])
        else:
            cmd.append(compound_input)

        # Run the command
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=self.fasttargetpred_path.parent
        )

        if result.returncode != 0:
            raise RuntimeError(f"FastTargetPred failed: {result.stderr}")

        return result.stdout

    def parse_results(self, raw_output: str) -> CompoundResults:
        """
        Parse raw FastTargetPred output into structured results.

        Args:
            raw_output: Raw output string from FastTargetPred

        Returns:
            CompoundResults object with structured data
        """
        lines = raw_output.strip().split("\n")

        # Extract basic information
        compound_name = ""
        smiles = ""
        fingerprint_type = ""
        similarity_threshold = 0.0
        execution_time = 0.0
        targets = []

        # Parse execution time
        for line in lines:
            if "Elapsed time for the entire script:" in line:
                time_match = re.search(r"(\d+\.?\d*)\s+seconds", line)
                if time_match:
                    execution_time = float(time_match.group(1))

        # Find compound section and extract compound name
        compound_section_started = False
        current_target_lines = []

        for i, line in enumerate(lines):
            # Detect compound name
            compound_match = re.match(r"Compound\s*:\s*>([^<]+)<", line)
            if compound_match:
                compound_name = compound_match.group(1).strip()
                compound_section_started = True
                continue

            if compound_section_started and line.strip():
                # Parse target information lines
                # Target lines start with rank number
                if re.match(r"\s*\d+\s+[A-Z0-9]+\s+[\d.]+", line):
                    if current_target_lines:
                        # Process previous target
                        target = self._parse_target_info(current_target_lines)
                        if target:
                            targets.append(target)
                        current_target_lines = []

                    # Start new target
                    current_target_lines = [line]
                elif (
                    line.strip().startswith("               ") and current_target_lines
                ):
                    # Continuation line (indented with spaces)
                    current_target_lines.append(line)
                elif line.strip() and current_target_lines:
                    # End of targets section
                    target = self._parse_target_info(current_target_lines)
                    if target:
                        targets.append(target)
                    current_target_lines = []
                    break

        # Process last target if exists
        if current_target_lines:
            target = self._parse_target_info(current_target_lines)
            if target:
                targets.append(target)

        return CompoundResults(
            compound_name=compound_name,
            smiles=smiles,  # Could be extracted from input if needed
            fingerprint_type=fingerprint_type,  # Could be extracted from command args
            similarity_threshold=similarity_threshold,  # Could be extracted from command args
            execution_time=execution_time,
            num_targets_found=len(targets),
            targets=targets,
        )

    def _parse_target_info(self, target_lines: List[str]) -> Optional[Target]:
        """Parse target information from multiple lines."""
        if not target_lines:
            return None

        full_text = " ".join(line.strip() for line in target_lines)

        # Extract basic target info
        match = re.match(
            r"(\d+)\s+([A-Z0-9]+)\s+([\d.]+)\s+([A-Z0-9]+)\s+([A-Z0-9_]+)\s+(.+)",
            full_text,
        )
        if not match:
            return None

        rank = int(match.group(1))
        chembl_compound_id = match.group(2)
        similarity_score = float(match.group(3))
        target_chembl_id = match.group(4)
        uniprot_id = match.group(5)
        rest_info = match.group(6)

        # Parse protein information - more robust parsing
        protein_name = ""
        gene_name = ""
        organism = ""

        # Look for "reviewed" keyword followed by protein name
        reviewed_match = re.search(
            r"reviewed\s+([^(]+?)(?:\s*\([^)]*\))?\s*([A-Z0-9_]*)\s+([A-Za-z\s]+\([A-Za-z\s]+\))",
            rest_info,
        )
        if reviewed_match:
            protein_name = reviewed_match.group(1).strip()
            gene_name = reviewed_match.group(2).strip()
            organism = reviewed_match.group(3).strip()
        else:
            # Fallback: try to extract at least protein name
            protein_parts = rest_info.split()
            if len(protein_parts) > 1:
                # Find "reviewed" and take the next parts as protein name
                try:
                    reviewed_idx = protein_parts.index("reviewed")
                    if reviewed_idx + 1 < len(protein_parts):
                        # Take words until we hit something that looks like a gene or organism
                        protein_words = []
                        for i in range(reviewed_idx + 1, len(protein_parts)):
                            word = protein_parts[i]
                            if word.isupper() and len(word) < 10:  # Likely gene name
                                gene_name = word
                                break
                            if "(" in word and ")" in word:  # Likely organism
                                organism = (
                                    " ".join(protein_parts[i : i + 2])
                                    if i + 1 < len(protein_parts)
                                    else word
                                )
                                break
                            protein_words.append(word)
                        protein_name = " ".join(protein_words).strip()
                except ValueError:
                    pass

        # Extract biological processes (GO terms)
        biological_processes = []
        go_pattern = r"([^;]+?)\s+\[GO:\d+\]"
        go_matches = re.findall(go_pattern, rest_info)
        biological_processes = [
            process.strip() for process in go_matches if process.strip()
        ]

        # Extract diseases
        diseases = []
        disease_pattern = r"DISEASE:\s*([^{]+?)\s*\[[^\]]+?\]:[^{]*?\{[^}]*?\}"
        disease_matches = re.findall(disease_pattern, rest_info)
        for disease_match in disease_matches:
            disease_name = disease_match.strip()
            if (
                disease_name and len(disease_name) < 200
            ):  # Reasonable disease name length
                diseases.append(disease_name)

        # Extract pathways (Reactome IDs)
        pathways = []
        pathway_matches = re.findall(r"R-[A-Z0-9-]+", rest_info)
        pathways = list(set(pathway_matches))  # Remove duplicates

        # Clean up names
        protein_name = re.sub(r"\s+", " ", protein_name).strip()
        gene_name = gene_name.strip()
        organism = re.sub(r"\s+", " ", organism).strip()

        return Target(
            rank=rank,
            chembl_compound_id=chembl_compound_id,
            similarity_score=similarity_score,
            target_chembl_id=target_chembl_id,
            uniprot_id=uniprot_id,
            protein_name=protein_name,
            gene_name=gene_name,
            organism=organism,
            target_class="",  # Not easily extractable from current format
            biological_processes=biological_processes,
            diseases=diseases,
            pathways=pathways,
        )

    def analyze_compound(
        self, compound_input: str, input_type: str = "smiles", **kwargs
    ) -> CompoundResults:
        """
        Complete analysis of a compound: run prediction and parse results.

        Args:
            compound_input: SMILES string (name:SMILES) or SDF file path
            input_type: "smiles" or "sdf"
            **kwargs: FastTargetPred arguments

        Returns:
            CompoundResults object with complete analysis
        """
        # Store parameters for later use
        fingerprint = kwargs.get("fingerprint", "ECFP4")
        threshold = kwargs.get("threshold", 0.7)

        raw_output = self.run_prediction(compound_input, input_type, **kwargs)
        results = self.parse_results(raw_output)

        # Update results with the parameters used
        results.fingerprint_type = fingerprint
        results.similarity_threshold = threshold

        # Extract SMILES if provided in compound_input
        if input_type == "smiles" and ":" in compound_input:
            results.smiles = compound_input.split(":", 1)[1]

        return results

    def create_summary_report(self, results: CompoundResults) -> str:
        """
        Create a clean, readable summary report.

        Args:
            results: CompoundResults object

        Returns:
            Formatted summary report as string
        """
        report = []
        report.append("=" * 80)
        report.append(f"FastTargetPred Analysis Report: {results.compound_name}")
        report.append("=" * 80)
        report.append("")

        # Basic information
        report.append("COMPOUND INFORMATION:")
        report.append(f"  Name: {results.compound_name}")
        if results.smiles:
            report.append(f"  SMILES: {results.smiles}")
        report.append(f"  Fingerprint: {results.fingerprint_type}")
        report.append(f"  Similarity Threshold: {results.similarity_threshold}")
        report.append(f"  Execution Time: {results.execution_time:.2f} seconds")
        report.append(f"  Targets Found: {results.num_targets_found}")
        report.append("")

        # Target predictions
        if results.targets:
            report.append("TARGET PREDICTIONS:")
            report.append("-" * 40)

            for target in results.targets:
                report.append(f"\n{target.rank}. {target.protein_name}")
                report.append(f"   Similarity Score: {target.similarity_score:.3f}")
                report.append(f"   ChEMBL Target: {target.target_chembl_id}")
                report.append(f"   UniProt ID: {target.uniprot_id}")
                report.append(f"   Gene: {target.gene_name}")
                report.append(f"   Organism: {target.organism}")

                if target.biological_processes:
                    report.append("   Biological Processes:")
                    for process in target.biological_processes[:5]:  # Limit to top 5
                        report.append(f"     • {process}")
                    if len(target.biological_processes) > 5:
                        report.append(
                            f"     ... and {len(target.biological_processes) - 5} more"
                        )

                if target.diseases:
                    report.append("   Associated Diseases:")
                    for disease in target.diseases[:3]:  # Limit to top 3
                        report.append(f"     • {disease}")
                    if len(target.diseases) > 3:
                        report.append(f"     ... and {len(target.diseases) - 3} more")

                if target.pathways:
                    report.append(f"   Pathways: {', '.join(target.pathways[:5])}")
                    if len(target.pathways) > 5:
                        report.append(f"     ... and {len(target.pathways) - 5} more")
        else:
            report.append("No targets found above the similarity threshold.")

        report.append("\n" + "=" * 80)
        return "\n".join(report)

    def export_to_json(
        self, results: CompoundResults, output_file: Optional[str] = None
    ) -> str:
        """
        Export results to JSON format.

        Args:
            results: CompoundResults object
            output_file: Optional output file path

        Returns:
            JSON string
        """
        data = {
            "compound_name": results.compound_name,
            "smiles": results.smiles,
            "fingerprint_type": results.fingerprint_type,
            "similarity_threshold": results.similarity_threshold,
            "execution_time": results.execution_time,
            "num_targets_found": results.num_targets_found,
            "targets": [
                {
                    "rank": target.rank,
                    "chembl_compound_id": target.chembl_compound_id,
                    "similarity_score": target.similarity_score,
                    "target_chembl_id": target.target_chembl_id,
                    "uniprot_id": target.uniprot_id,
                    "protein_name": target.protein_name,
                    "gene_name": target.gene_name,
                    "organism": target.organism,
                    "target_class": target.target_class,
                    "biological_processes": target.biological_processes,
                    "diseases": target.diseases,
                    "pathways": target.pathways,
                }
                for target in results.targets
            ],
        }

        json_str = json.dumps(data, indent=2)

        if output_file:
            with open(output_file, "w") as f:
                f.write(json_str)

        return json_str

    def create_csv_report(
        self, results: CompoundResults, output_file: Optional[str] = None
    ) -> str:
        """
        Create a CSV report for easy analysis in spreadsheet applications.

        Args:
            results: CompoundResults object
            output_file: Optional output file path

        Returns:
            CSV string
        """
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Compound_Name",
                "Rank",
                "Similarity_Score",
                "Target_ChEMBL_ID",
                "UniProt_ID",
                "Protein_Name",
                "Gene_Name",
                "Organism",
                "Num_Biological_Processes",
                "Num_Diseases",
                "Num_Pathways",
                "Top_Biological_Process",
                "Top_Disease",
                "Sample_Pathways",
            ]
        )

        # Data rows
        for target in results.targets:
            writer.writerow(
                [
                    results.compound_name,
                    target.rank,
                    target.similarity_score,
                    target.target_chembl_id,
                    target.uniprot_id,
                    target.protein_name,
                    target.gene_name,
                    target.organism,
                    len(target.biological_processes),
                    len(target.diseases),
                    len(target.pathways),
                    target.biological_processes[0]
                    if target.biological_processes
                    else "",
                    target.diseases[0] if target.diseases else "",
                    "; ".join(target.pathways[:3]),
                ]
            )

        csv_str = output.getvalue()
        output.close()

        if output_file:
            with open(output_file, "w") as f:
                f.write(csv_str)

        return csv_str


def quick_analysis(
    compound_input: str,
    input_type: str = "smiles",
    fasttargetpred_path: str = "FastTargetPred.py",
    **kwargs,
) -> str:
    """
    Quick analysis function for immediate results.

    Args:
        compound_input: SMILES string (name:SMILES) or SDF file path
        input_type: "smiles" or "sdf"
        fasttargetpred_path: Path to FastTargetPred.py
        **kwargs: FastTargetPred arguments

    Returns:
        Formatted summary report
    """
    analyzer = FastTargetPredAnalyzer(fasttargetpred_path)
    results = analyzer.analyze_compound(compound_input, input_type, **kwargs)
    return analyzer.create_summary_report(results)


# Example usage
if __name__ == "__main__":
    # Example with caffeine
    analyzer = FastTargetPredAnalyzer()

    # Analyze caffeine
    results = analyzer.analyze_compound(
        "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        fingerprint="ECFP4",
        threshold=0.7,
        max_targets=5,
    )

    print(analyzer.create_summary_report(results))

    # Export to JSON
    json_output = analyzer.export_to_json(results, "caffeine_results.json")

    # Export to CSV
    csv_output = analyzer.create_csv_report(results, "caffeine_results.csv")
