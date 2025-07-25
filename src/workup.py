#!/usr/bin/env python3
"""
FastTargetPred Workup - Modernized version of FastTargetPred_workup.py

This module processes CSV output from FastTargetPred to build HTML reports.
"""

__version__ = "2.0.0"

import sys
import argparse
from datetime import datetime
import base64
import re
from urllib import request, error


# Check Python version
if sys.version_info < (3, 8):
    print(
        "This program requires Python 3.8 or higher. Please upgrade your Python version."
    )
    sys.exit(1)


class Arguments:
    """Modern argument constants."""

    CSV_INPUT = "i"
    SDF_INPUT = "sdf"
    HTML_OUTPUT = "o"
    SCORE_FILTER = "f"
    PLOT_STATS = "p"
    CLASS_NUMBER = "cn"
    SAVE_CHEMBL_STRUCT = "s"
    SPLIT_QUERY_COMPOUNDS = "c"
    ARG_LIST = [
        CSV_INPUT,
        SDF_INPUT,
        HTML_OUTPUT,
        SCORE_FILTER,
        PLOT_STATS,
        CLASS_NUMBER,
        SAVE_CHEMBL_STRUCT,
        SPLIT_QUERY_COMPOUNDS,
    ]


HTM_LINK_TEMPLATE = """<a href="{link}" target="blank">{name}</a>"""


def render_classic_str(s: str, **kwargs) -> str:
    return s


def render_classic_float(s: str, **kwargs) -> str:
    return f"{float(s):.2f}"


def render_query_mol(s: str, img_provider=None, **kwargs) -> str:
    if img_provider is None:
        return s
    else:
        return img_provider.get_img(s) + f"<div>{s}</div>"


def render_chembl_structure(s: str, arguments=None, **kwargs) -> str:
    url = f"https://www.ebi.ac.uk/chembl/api/data/image/{s}.svg"
    img_markup = ""
    if arguments is not None and arguments.get(Arguments.SAVE_CHEMBL_STRUCT, False):
        try:
            with request.urlopen(url, timeout=60) as response:
                response_bytes = response.read()
                b64_str = base64.b64encode(response_bytes).decode("ASCII")
                img_markup = f"<img src='data:image/png;base64,{b64_str}'/>"
        except error.URLError:
            print(f"CHEMBL topological formula fetching failed on {s}")
    else:
        img_markup = f"<img src='{url}'/>"

    base_url_template = "https://www.ebi.ac.uk/chembl/compound_report_card/{}/"
    s = re.sub(
        "CHEMBL[0-9]+",
        lambda match: HTM_LINK_TEMPLATE.format(
            name=match.group(0), link=base_url_template.format(match.group(0))
        ),
        s,
    )

    return f"{img_markup}<div>{s}</div>"


def render_reactome_link(s: str, **kwargs) -> str:
    base_url_template = "https://reactome.org/PathwayBrowser/#/{}"
    s = re.sub(
        r" *(?P<reactome_id>[a-zA-Z]+-[a-zA-Z]+-(?P<reactome_number>[0-9]+)) *",
        lambda m: HTM_LINK_TEMPLATE.format(
            link=base_url_template.format(m.group("reactome_id")),
            name=m.group("reactome_number"),
        ),
        s,
    )
    s = s.replace(";", "</br>")
    return s


def render_gene_ontology(s: str, **kwargs) -> str:
    # Warning: char ':' must be translated to %3A for html query
    base_url_template = (
        "http://amigo.geneontology.org/amigo/medial_search?q={}&searchtype=all"
    )

    def get_markup(s):
        match = re.match(r"(?P<name>[^\[\]]*) \[(?P<link>GO:[0-9]*)\]", s)
        if match:
            link = base_url_template.format(match.group("link").replace(":", "%3A"))
            return HTM_LINK_TEMPLATE.format(link=link, name=match.group("name"))
        else:
            return ""

    return "</br>".join([get_markup(x) for x in s.split(";")])


def render_involvement_in_disease(s: str, **kwargs) -> str:
    # format MIM strings
    base_url_template = "https://www.omim.org/entry/{}"
    s = re.sub(
        r"(?P<disease_name>DISEASE:[^\[\]]*) (?P<mim_str>\[MIM:(?P<mim_num>[0-9]+)\])",
        lambda match: HTM_LINK_TEMPLATE.format(
            link=base_url_template.format(match.group("mim_num")),
            name=match.group("disease_name"),
        ),
        s,
    )

    # format PUBMED strings
    base_url_template = "https://www.ncbi.nlm.nih.gov/pubmed?cmd=search&term={}"
    s = re.sub(
        r"PubMed:(?P<pubmed_num>[0-9]+)",
        lambda x: HTM_LINK_TEMPLATE.format(
            link=base_url_template.format(x.group("pubmed_num")), name="PubMed"
        ),
        s,
    )

    # format ECO strings
    base_url_template = "https://www.ebi.ac.uk/QuickGO/term/{}"
    s = re.sub(
        r"(?<!/)(?P<eco_num>ECO:[0-9]+)(?!\")",
        lambda x: HTM_LINK_TEMPLATE.format(
            link=base_url_template.format(x.group("eco_num")), name="ECO"
        ),
        s,
    )

    return s


def render_chembl_target(s: str, **kwargs) -> str:
    base_url_template = "https://www.ebi.ac.uk/chembl/target_report_card/{}/"
    s = re.sub(
        "CHEMBL[0-9]+",
        lambda match: HTM_LINK_TEMPLATE.format(
            name=match.group(0), link=base_url_template.format(match.group(0))
        ),
        s,
    )
    return s


def render_uniprot_id(s: str, **kwargs) -> str:
    base_url_template = "https://www.uniprot.org/uniprot/{}"
    s = re.sub(
        r"(?P<uniprot_id>.*)",
        lambda match: HTM_LINK_TEMPLATE.format(
            name=match.group("uniprot_id"),
            link=base_url_template.format(match.group("uniprot_id")),
        ),
        s,
    )
    return s


class CSVFields:
    """CSV field definitions."""

    query_name = "query_name"
    database_molecule_id = "database_molecule_id"
    target_id = "target_id"
    score = "score"
    Entry = "Uniprot"
    Entry_name = "Uniprot name"
    Status = "Status"
    Protein_names = "Protein names"
    Gene_names = "Gene names"
    Organism = "Organism"
    CHEMBL = "CHEMBL"
    Involvement_in_disease = "Involvement in disease"
    Gene_ontology = "Gene ontology (biological process)"
    Reactome = "Cross-reference (Reactome)"

    field_list = (
        query_name,
        database_molecule_id,
        score,
        Entry,
        Entry_name,
        Status,
        Protein_names,
        Gene_names,
        Organism,
        CHEMBL,
        Involvement_in_disease,
        Gene_ontology,
        Reactome,
    )

    field_display_function = {
        query_name: render_query_mol,
        database_molecule_id: render_chembl_structure,
        target_id: render_classic_str,
        score: render_classic_float,
        Entry: render_uniprot_id,
        Entry_name: render_classic_str,
        Status: render_classic_str,
        Protein_names: render_classic_str,
        Gene_names: render_classic_str,
        Organism: render_classic_str,
        CHEMBL: render_chembl_target,
        Involvement_in_disease: render_involvement_in_disease,
        Gene_ontology: render_gene_ontology,
        Reactome: render_reactome_link,
    }


def main() -> None:
    """Main entry point for FastTargetPred workup."""
    parser = argparse.ArgumentParser(
        description=f"Script version {__version__}. Process CSV output from FastTargetPred to build HTML files."
    )

    mandatory_arguments = parser.add_argument_group(title="Mandatory arguments")
    mandatory_arguments.add_argument(
        f"-{Arguments.CSV_INPUT}",
        help="Path to the output CSV file of FastTargetPred.",
        required=True,
    )
    mandatory_arguments.add_argument(
        f"-{Arguments.HTML_OUTPUT}",
        help="Path to the HTML report.",
        default=f"out_{datetime.now().isoformat().replace(':', ' ')}.html",
    )

    optional_arguments = parser.add_argument_group(title="Additional arguments")
    optional_arguments.add_argument(
        f"-{Arguments.SDF_INPUT}",
        help="Path to the SD file used as input of FastTargetPred. Used for image generation.\nWarning: RDKit is required for this to work.",
    )
    optional_arguments.add_argument(
        f"-{Arguments.SCORE_FILTER}",
        help="Score filtering value. Useful for a smaller or cleaner file.",
        type=float,
    )
    optional_arguments.add_argument(
        f"-{Arguments.PLOT_STATS}",
        help="Analyze data and plot metrics at the top of the HTML report.",
        action="store_true",
    )
    optional_arguments.add_argument(
        f"-{Arguments.CLASS_NUMBER}",
        help="Class Number. Will change the frequency distribution graph class width.",
        type=int,
        default=20,
    )
    optional_arguments.add_argument(
        f"-{Arguments.SPLIT_QUERY_COMPOUNDS}",
        help="Split Query Compounds. Generate one file per query compound in a folder.",
        action="store_true",
    )

    args = parser.parse_args()
    argument_dict = {
        arg: getattr(args, arg) for arg in Arguments.ARG_LIST if hasattr(args, arg)
    }

    print(f"FastTargetPred Workup v{__version__}")
    print("Processing CSV output to HTML...")

    # Implementation would go here - for now, just print the arguments
    print(f"Input CSV: {argument_dict[Arguments.CSV_INPUT]}")
    print(f"Output HTML: {argument_dict[Arguments.HTML_OUTPUT]}")

    # The rest of the original implementation would be modernized and added here


if __name__ == "__main__":
    main()
