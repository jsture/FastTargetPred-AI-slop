#!/usr/bin/env python3
"""
Simple Example: FastTargetPred Results Analyzer

This script shows how to easily extract and analyze FastTargetPred results
for any compound (drug, tetrapeptide, or any molecule).

Usage:
    python simple_example.py
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from results_analyzer import FastTargetPredAnalyzer


def analyze_compounds():
    """Analyze several example compounds."""

    # Initialize the analyzer
    analyzer = FastTargetPredAnalyzer()

    # List of compounds to analyze
    compounds = [
        # Drug examples
        ("caffeine", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"),
        ("aspirin", "CC(=O)OC1=CC=CC=C1C(O)=O"),
        # Tetrapeptide example from the research dataset
        (
            "LAAA",
            "[H]N[C@@H](CC(C)C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(O)=O",
        ),
    ]

    print("🧬 FastTargetPred Results Analyzer Example")
    print("=" * 60)
    print()

    for name, smiles in compounds:
        print(f"🔬 Analyzing: {name}")
        print("-" * 30)

        try:
            # Analyze the compound
            results = analyzer.analyze_compound(
                f"{name}:{smiles}", fingerprint="ECFP4", threshold=0.6, max_targets=3
            )

            # Print basic information
            print(f"Compound: {results.compound_name}")
            print(f"Targets found: {results.num_targets_found}")
            print(f"Analysis time: {results.execution_time:.1f}s")

            # Show top targets
            if results.targets:
                print("\nTop Targets:")
                for i, target in enumerate(results.targets[:2], 1):
                    print(f"  {i}. {target.protein_name}")
                    print(f"     Similarity: {target.similarity_score:.3f}")
                    print(f"     ChEMBL: {target.target_chembl_id}")
                    print(f"     UniProt: {target.uniprot_id}")

                    # Show biological processes if available
                    if target.biological_processes:
                        print(
                            f"     Key process: {target.biological_processes[0][:80]}..."
                        )
                    print()
            else:
                print("No targets found above threshold.")

            # Export results
            output_dir = Path("results")
            output_dir.mkdir(exist_ok=True)

            # Export to JSON and CSV
            json_file = output_dir / f"{name}_analysis.json"
            csv_file = output_dir / f"{name}_analysis.csv"

            analyzer.export_to_json(results, str(json_file))
            analyzer.create_csv_report(results, str(csv_file))

            print("📁 Results exported to:")
            print(f"   JSON: {json_file}")
            print(f"   CSV: {csv_file}")

        except Exception as e:
            print(f"❌ Error analyzing {name}: {e}")

        print("\n" + "=" * 60 + "\n")


def create_detailed_report_example():
    """Example of creating a detailed report for a single compound."""

    print("📋 Detailed Report Example")
    print("=" * 60)

    # Analyze caffeine in detail
    analyzer = FastTargetPredAnalyzer()

    results = analyzer.analyze_compound(
        "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        fingerprint="ECFP4",
        threshold=0.7,
        max_targets=10,
    )

    # Create and display the full report
    detailed_report = analyzer.create_summary_report(results)
    print(detailed_report)

    # Save detailed report to file
    report_file = Path("results") / "caffeine_detailed_report.txt"
    report_file.write_text(detailed_report)
    print(f"\n📄 Detailed report saved to: {report_file}")


def quick_analysis_example():
    """Example using the quick analysis function."""

    print("⚡ Quick Analysis Example")
    print("=" * 60)

    from results_analyzer import quick_analysis  # type: ignore

    # Quick analysis of ibuprofen
    report = quick_analysis(
        "ibuprofen:CC(C)CC1=CC=C(C=C1)C(C)C(O)=O", threshold=0.6, max_targets=5
    )

    print(report)


if __name__ == "__main__":
    print("🎯 FastTargetPred Results Analyzer - Simple Examples")
    print("=" * 70)
    print()
    print("This script demonstrates how to use the results analyzer to:")
    print("• Extract FastTargetPred results for any compound")
    print("• Create clean, structured reports")
    print("• Export data to JSON and CSV formats")
    print("• Analyze drugs, peptides, and other molecules")
    print()

    # Create results directory
    Path("results").mkdir(exist_ok=True)

    # Run examples
    analyze_compounds()
    create_detailed_report_example()
    quick_analysis_example()

    print("\n✨ All examples completed!")
    print("Check the 'results/' directory for exported files.")

    print("\n💡 To use this in your own code:")
    print("   from src.results_analyzer import FastTargetPredAnalyzer")
    print("   analyzer = FastTargetPredAnalyzer()")
    print("   results = analyzer.analyze_compound('name:SMILES')")
    print("   print(analyzer.create_summary_report(results))")
