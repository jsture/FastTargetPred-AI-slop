#!/usr/bin/env python3
"""
FastTargetPred Compound Analyzer

A simple command-line tool to analyze compounds with FastTargetPred
and generate clean, structured reports.

Usage:
    python analyze_compound.py "compound_name:SMILES_string"
    python analyze_compound.py -f input.sdf

Examples:
    python analyze_compound.py "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
    python analyze_compound.py "aspirin:CC(=O)OC1=CC=CC=C1C(O)=O" --threshold 0.6
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from results_analyzer import FastTargetPredAnalyzer
except ImportError:
    print(
        "Error: Could not import results_analyzer. Make sure src/results_analyzer.py exists."
    )
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze compounds with FastTargetPred and generate structured reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
  %(prog)s "aspirin:CC(=O)OC1=CC=CC=C1C(O)=O" --threshold 0.6 --max-targets 10
  %(prog)s --file input.sdf --fingerprint MACCS
        """,
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "smiles", nargs="?", help='SMILES string in format "name:SMILES"'
    )
    input_group.add_argument("-f", "--file", help="SDF file path")

    # FastTargetPred options
    parser.add_argument(
        "--fingerprint",
        choices=["ECFP4", "ECFP6", "MACCS", "PL"],
        default="ECFP4",
        help="Fingerprint type (default: ECFP4)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Similarity threshold (default: 0.7)",
    )
    parser.add_argument(
        "--max-targets",
        type=int,
        default=10,
        help="Maximum number of targets to report (default: 10)",
    )
    parser.add_argument(
        "--database",
        default="db/chembl25_active",
        help="Database path (default: db/chembl25_active)",
    )

    # Output options
    parser.add_argument("--output-json", help="Export results to JSON file")
    parser.add_argument("--output-csv", help="Export results to CSV file")
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress summary report output"
    )

    args = parser.parse_args()

    # Determine input type and value
    if args.smiles:
        compound_input = args.smiles
        input_type = "smiles"
    else:
        compound_input = args.file
        input_type = "sdf"

    # Validate input
    if input_type == "smiles" and ":" not in compound_input:
        print("Error: SMILES input must be in format 'name:SMILES'")
        sys.exit(1)

    if input_type == "sdf" and not Path(compound_input).exists():
        print(f"Error: SDF file not found: {compound_input}")
        sys.exit(1)

    try:
        # Initialize analyzer
        analyzer = FastTargetPredAnalyzer()

        print("🔬 Analyzing compound with FastTargetPred...")
        print(f"   Input: {compound_input}")
        print(f"   Fingerprint: {args.fingerprint}")
        print(f"   Threshold: {args.threshold}")
        print(f"   Max targets: {args.max_targets}")
        print()

        # Run analysis
        results = analyzer.analyze_compound(
            compound_input,
            input_type=input_type,
            fingerprint=args.fingerprint,
            threshold=args.threshold,
            max_targets=args.max_targets,
            db=args.database,
        )

        # Print summary report
        if not args.quiet:
            print(analyzer.create_summary_report(results))

        # Export results
        if args.output_json:
            analyzer.export_to_json(results, args.output_json)
            print(f"\n📁 JSON results exported to: {args.output_json}")

        if args.output_csv:
            analyzer.create_csv_report(results, args.output_csv)
            print(f"📁 CSV results exported to: {args.output_csv}")

        # Print basic stats
        print(f"\n📊 Analysis completed in {results.execution_time:.2f} seconds")
        print(f"   Found {results.num_targets_found} targets above threshold")

        if results.targets:
            top_target = results.targets[0]
            print(
                f"   Top target: {top_target.protein_name} (similarity: {top_target.similarity_score:.3f})"
            )

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
