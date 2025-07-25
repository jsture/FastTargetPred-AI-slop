#!/usr/bin/env python3
"""
Demo script for the FastTargetPred Results Analyzer

This script demonstrates how to use the results analyzer to extract
and format FastTargetPred results for any compound.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from results_analyzer import FastTargetPredAnalyzer, quick_analysis


def demo_caffeine():
    """Demo analysis of caffeine."""
    print("🔬 Analyzing Caffeine...")
    print("=" * 50)

    analyzer = FastTargetPredAnalyzer()

    # Analyze caffeine
    results = analyzer.analyze_compound(
        "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        fingerprint="ECFP4",
        threshold=0.7,
        max_targets=5,
    )

    # Print summary report
    print(analyzer.create_summary_report(results))

    # Export to files
    analyzer.export_to_json(results, "results/caffeine_results.json")
    analyzer.create_csv_report(results, "results/caffeine_results.csv")

    print(
        "\n📁 Results exported to results/caffeine_results.json and results/caffeine_results.csv"
    )


def demo_tetrapeptide():
    """Demo analysis of a tetrapeptide."""
    print("\n\n🧬 Analyzing Tetrapeptide LAAA...")
    print("=" * 50)

    # Use the quick analysis function
    report = quick_analysis(
        "LAAA:[H]N[C@@H](CC(C)C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(=O)N[C@@H](C)C(O)=O",
        fingerprint="ECFP4",
        threshold=0.5,
        max_targets=3,
    )

    print(report)


def demo_multiple_compounds():
    """Demo analysis of multiple compounds."""
    print("\n\n🧪 Analyzing Multiple Compounds...")
    print("=" * 50)

    compounds = [
        ("aspirin", "aspirin:CC(=O)OC1=CC=CC=C1C(O)=O"),
        ("ibuprofen", "ibuprofen:CC(C)CC1=CC=C(C=C1)C(C)C(O)=O"),
    ]

    analyzer = FastTargetPredAnalyzer()

    for name, smiles in compounds:
        print(f"\n--- {name.upper()} ---")
        try:
            results = analyzer.analyze_compound(
                smiles, fingerprint="ECFP4", threshold=0.6, max_targets=3
            )

            # Print just the top target
            if results.targets:
                top_target = results.targets[0]
                print(f"Top Target: {top_target.protein_name}")
                print(f"Similarity: {top_target.similarity_score:.3f}")
                print(f"Gene: {top_target.gene_name}")
            else:
                print("No targets found above threshold")
        except Exception as e:
            print(f"Error analyzing {name}: {e}")


def interactive_mode():
    """Interactive mode for user input."""
    print("\n\n💻 Interactive Mode")
    print("=" * 50)
    print("Enter SMILES strings to analyze (or 'quit' to exit)")
    print("Format: name:SMILES (e.g., 'aspirin:CC(=O)OC1=CC=CC=C1C(O)=O')")

    analyzer = FastTargetPredAnalyzer()

    while True:
        user_input = input("\n🔍 Enter compound: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            break

        if not user_input:
            continue

        try:
            results = analyzer.analyze_compound(
                user_input, fingerprint="ECFP4", threshold=0.6, max_targets=5
            )

            print("\n" + analyzer.create_summary_report(results))

            # Ask if user wants to export
            export = input("\n💾 Export results? (y/n): ").strip().lower()
            if export in ["y", "yes"]:
                compound_name = results.compound_name.replace(" ", "_")
                json_file = f"results/{compound_name}_results.json"
                csv_file = f"results/{compound_name}_results.csv"

                analyzer.export_to_json(results, json_file)
                analyzer.create_csv_report(results, csv_file)

                print(f"📁 Results exported to {json_file} and {csv_file}")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main demo function."""
    print("🎯 FastTargetPred Results Analyzer Demo")
    print("=" * 60)

    # Create results directory
    Path("results").mkdir(exist_ok=True)

    print("\nThis demo shows how to extract and analyze FastTargetPred results")
    print("for any compound in a clean, structured format.\n")

    # Run demos
    demo_caffeine()
    demo_tetrapeptide()
    demo_multiple_compounds()

    # Interactive mode
    try:
        interactive_mode()
    except KeyboardInterrupt:
        pass

    print("\n\n✨ Demo completed! Check the results/ directory for exported files.")
    print("\nTo use the analyzer in your own code:")
    print("  from src.results_analyzer import FastTargetPredAnalyzer")
    print("  analyzer = FastTargetPredAnalyzer()")
    print("  results = analyzer.analyze_compound('name:SMILES')")
    print("  print(analyzer.create_summary_report(results))")


if __name__ == "__main__":
    main()
