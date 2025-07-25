#!/usr/bin/env python3
"""
Command-line interface wrappers for FastTargetPred
"""


def fasttargetpred_main():
    """Entry point for fasttargetpred command"""
    import sys
    import os

    # Find the FastTargetPred project root directory
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))

    # Change to project root directory so relative paths work correctly
    original_cwd = os.getcwd()
    os.chdir(project_root)

    # Add project root to path to find FastTargetPred module
    sys.path.insert(0, project_root)

    try:
        from FastTargetPred import main

        main()
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def fasttargetpred_workup_main():
    """Entry point for fasttargetpred-workup command"""
    import sys
    import os

    # Find the FastTargetPred project root directory
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))

    # Change to project root directory so relative paths work correctly
    original_cwd = os.getcwd()
    os.chdir(project_root)

    # Add project root to path to find FastTargetPred_workup module
    sys.path.insert(0, project_root)

    try:
        import FastTargetPred_workup

        # Run the workup script's main logic
        import argparse
        from FastTargetPred_workup import ARGUMENTS

        parser = argparse.ArgumentParser(
            description=f"Script version {FastTargetPred_workup.__version__}. Will process csv output from FastTargetPred to build a single html file."
        )
        mandatory_arguments = parser.add_argument_group(title="Mandatory arguments")
        mandatory_arguments.add_argument(
            f"-{ARGUMENTS.CSV_INPUT}",
            help="Path to the output csv file of FastTargetPred.",
        )
        mandatory_arguments.add_argument(
            f"-{ARGUMENTS.HTML_OUTPUT}",
            help="Path to the html file output (including the file name + extension).",
        )

        optional_arguments = parser.add_argument_group(title="Optional arguments")
        optional_arguments.add_argument(
            f"-{ARGUMENTS.SDF_INPUT}",
            help="Path to the sdf file used as input for FastTargetPred. The html file will include the 2D structure of the compounds when using this argument.",
        )
        optional_arguments.add_argument(
            f"-{ARGUMENTS.SCORE_FILTER}",
            help="When provided, will only keep the targets that match the minimum score threshold. Score ranges from 0 to 1.",
            type=float,
        )
        optional_arguments.add_argument(
            f"-{ARGUMENTS.PLOT_STATS}",
            help="When provided, will plot some basic statistics.",
            action="store_true",
        )

        arguments = vars(parser.parse_args())
        FastTargetPred_workup.main(arguments)
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    # This allows the module to be run directly
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "workup":
        fasttargetpred_workup_main()
    else:
        fasttargetpred_main()
