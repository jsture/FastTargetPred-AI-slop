#!/usr/bin/env python3
"""
Example usage of FastTargetPred v2.0 with SMILES input.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_smiles_conversion():
    """Test SMILES to SDF conversion."""
    try:
        from src.arg_parsing import (
            UserArguments,
            SMILES,
            SDFile,
            DATABASE,
            FINGERPRINT,
            TANIMOTO_COEF_THRESHOLD,
            ZSCORE_THRESHOLD,
            REPORTED_TARGET_NUMBER,
            OUTPUT,
            OUTPUT_FORMAT,
            NUM_CORE,
            FILTER_BEST_POSE_PER_TARGET,
            NO_INFO,
        )
        from src.config import DEFAULT_TC, DEFAULT_OUTPUT

        # Create a mock arguments dictionary with SMILES input
        test_args = {
            SMILES: [
                "aspirin:CC(=O)OC1=CC=CC=C1C(=O)O",
                "caffeine:CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
            ],
            SDFile: [],
            DATABASE: "db/chembl25_active",
            FINGERPRINT: ["ECFP4"],
            TANIMOTO_COEF_THRESHOLD: DEFAULT_TC,
            ZSCORE_THRESHOLD: 0.8,
            REPORTED_TARGET_NUMBER: 100,
            OUTPUT: DEFAULT_OUTPUT,
            OUTPUT_FORMAT: "txt",
            NUM_CORE: 4,
            FILTER_BEST_POSE_PER_TARGET: False,
            NO_INFO: False,
        }

        # Create UserArguments instance
        user_args = UserArguments(test_args)

        # Test validation
        if user_args.are_ok():
            print("✅ SMILES input validation passed")

            # Test SDF path generation (this will attempt SMILES conversion)
            try:
                sdf_path = user_args.sdf_path
                print(f"✅ SMILES conversion successful: {sdf_path}")

                # Check if file exists and has content
                if sdf_path.exists():
                    content = sdf_path.read_text()
                    if content:
                        print(
                            f"✅ Generated SDF file has content ({len(content)} characters)"
                        )
                        print("First 200 characters:")
                        print(content[:200] + "..." if len(content) > 200 else content)
                    else:
                        print("❌ Generated SDF file is empty")
                else:
                    print("❌ SDF file was not created")

            except ImportError as e:
                print(f"⚠️  RDKit not available for SMILES conversion: {e}")
            except Exception as e:
                print(f"❌ SMILES conversion failed: {e}")
        else:
            print(f"❌ Validation failed: {user_args.errormsg}")

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True


def test_bundled_maya():
    """Test bundled MayaChemTools detection."""
    try:
        from src.misc import get_bundled_maya_path, _is_maya_path_fine

        maya_path = get_bundled_maya_path()
        print(f"Bundled Maya path: {maya_path}")

        if _is_maya_path_fine(maya_path):
            print("✅ Bundled MayaChemTools found and valid")

            # List some tools
            tools = list(maya_path.glob("*.pl"))[:5]  # First 5 Perl scripts
            if tools:
                print("Available tools (sample):")
                for tool in tools:
                    print(f"  - {tool.name}")
            else:
                print("No Perl scripts found in Maya bin directory")
        else:
            print("❌ Bundled MayaChemTools not found or invalid")
            print("This is expected if mayachemtools directory doesn't exist")

    except Exception as e:
        print(f"❌ Maya test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("FastTargetPred v2.0 - Testing New Features")
    print("=" * 50)

    print("\n1. Testing bundled MayaChemTools detection:")
    test_bundled_maya()

    print("\n2. Testing SMILES input support:")
    test_smiles_conversion()

    print("\n3. Testing modern Python features:")
    # Test f-strings and type annotations work
    version = "2.0.0"
    message = f"FastTargetPred version {version} is ready!"
    print(f"✅ {message}")

    print("\nAll tests completed!")
    print("\nNext steps:")
    print("1. Install RDKit: pip install rdkit")
    print(
        "2. Run with SMILES: python src/main.py -smiles 'aspirin:CC(=O)OC1=CC=CC=C1C(=O)O'"
    )
    print("3. Or run with SDF: python src/main.py input.sdf")
