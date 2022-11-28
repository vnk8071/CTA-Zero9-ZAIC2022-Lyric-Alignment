"""Command line functions for aligning corpora"""
from __future__ import annotations

import os
import argparse
import sys
import time
from typing import TYPE_CHECKING, List, Optional

import yaml

from montreal_forced_aligner.alignment import PretrainedAligner
from montreal_forced_aligner.command_line.utils import validate_model_arg
from montreal_forced_aligner.exceptions import ArgumentError
from montreal_forced_aligner.helper import mfa_open
from montreal_forced_aligner.command_line.align import run_align_corpus

from montreal_forced_aligner.config import (
    load_command_history,
    load_global_config,
)
from montreal_forced_aligner.exceptions import MFAError
from montreal_forced_aligner.models import MODEL_TYPES
from montreal_forced_aligner.utils import check_third_party

if TYPE_CHECKING:
    from argparse import Namespace, ArgumentParser


__all__ = ["align_corpus", "validate_args", "run_align_corpus"]

def create_parser() -> ArgumentParser:
    """
    Constructs the MFA argument parser
    Returns
    -------
    :class:`~argparse.ArgumentParser`
        MFA argument parser
    """
    GLOBAL_CONFIG = load_global_config()

    def add_global_options(subparser: argparse.ArgumentParser, textgrid_output: bool = False):
        """
        Add a set of global options to a subparser
        Parameters
        ----------
        subparser: :class:`~argparse.ArgumentParser`
            Subparser to augment
        textgrid_output: bool
            Flag for whether the subparser is used for a command that generates TextGrids
        """
        subparser.add_argument(
            "-t",
            "--temp_directory",
            "--temporary_directory",
            dest="temporary_directory",
            type=str,
            default=GLOBAL_CONFIG["temporary_directory"],
            help=f"Temporary directory root to store MFA created files, default is {GLOBAL_CONFIG['temporary_directory']}",
        )
        subparser.add_argument(
            "--disable_mp",
            help=f"Disable any multiprocessing during alignment (not recommended), default is {not GLOBAL_CONFIG['use_mp']}",
            action="store_true",
            default=not GLOBAL_CONFIG["use_mp"],
        )
        subparser.add_argument(
            "-j",
            "--num_jobs",
            type=int,
            default=GLOBAL_CONFIG["num_jobs"],
            help=f"Number of data splits (and cores to use if multiprocessing is enabled), defaults "
            f"is {GLOBAL_CONFIG['num_jobs']}",
        )
        subparser.add_argument(
            "-v",
            "--verbose",
            help=f"Output debug messages, default is {GLOBAL_CONFIG['verbose']}",
            action="store_true",
            default=GLOBAL_CONFIG["verbose"],
        )
        subparser.add_argument(
            "-q",
            "--quiet",
            help=f"Suppress all output messages (overrides verbose), default is {GLOBAL_CONFIG['quiet']}",
            action="store_true",
            default=GLOBAL_CONFIG["quiet"],
        )
        subparser.add_argument(
            "--clean",
            help=f"Remove files from previous runs, default is {GLOBAL_CONFIG['clean']}",
            action="store_false",
            default=True,
        )
        subparser.add_argument(
            "--overwrite",
            help=f"Overwrite output files when they exist, default is {GLOBAL_CONFIG['overwrite']}",
            action="store_false",
            default=True,
        )
        subparser.add_argument(
            "--debug",
            help=f"Run extra steps for debugging issues, default is {GLOBAL_CONFIG['debug']}",
            action="store_true",
            default=GLOBAL_CONFIG["debug"],
        )
        if textgrid_output:
            subparser.add_argument(
                "--disable_textgrid_cleanup",
                help=f"Disable extra clean up steps on TextGrid output, default is {not GLOBAL_CONFIG['cleanup_textgrids']}",
                action="store_true",
                default=not GLOBAL_CONFIG["cleanup_textgrids"],
            )

    pretrained_acoustic = ", ".join(MODEL_TYPES["acoustic"].get_available_models())
    if not pretrained_acoustic:
        pretrained_acoustic = (
            "you can use ``mfa model download acoustic`` to get pretrained MFA models"
        )

    pretrained_ivector = ", ".join(MODEL_TYPES["ivector"].get_available_models())
    if not pretrained_ivector:
        pretrained_ivector = (
            "you can use ``mfa model download ivector`` to get pretrained MFA models"
        )

    pretrained_g2p = ", ".join(MODEL_TYPES["g2p"].get_available_models())
    if not pretrained_g2p:
        pretrained_g2p = "you can use ``mfa model download g2p`` to get pretrained MFA models"

    pretrained_lm = ", ".join(MODEL_TYPES["language_model"].get_available_models())
    if not pretrained_lm:
        pretrained_lm = (
            "you can use ``mfa model download language_model`` to get pretrained MFA models"
        )

    pretrained_dictionary = ", ".join(MODEL_TYPES["dictionary"].get_available_models())
    if not pretrained_dictionary:
        pretrained_dictionary = (
            "you can use ``mfa model download dictionary`` to get MFA dictionaries"
        )

    dictionary_path_help = f"Full path to pronunciation dictionary, or saved dictionary name ({pretrained_dictionary})"

    acoustic_model_path_help = (
        f"Full path to pre-trained acoustic model, or saved model name ({pretrained_acoustic})"
    )
    language_model_path_help = (
        f"Full path to pre-trained language model, or saved model name ({pretrained_lm})"
    )
    ivector_model_path_help = f"Full path to pre-trained ivector extractor model, or saved model name ({pretrained_ivector})"
    g2p_model_path_help = (
        f"Full path to pre-trained G2P model, or saved model name ({pretrained_g2p}). "
        "If not specified, then orthographic transcription is split into pronunciations."
    )

    parser = argparse.ArgumentParser()
    
    subparsers = parser.add_subparsers(dest="subcommand")

    _ = subparsers.add_parser("version")

    align_parser = subparsers.add_parser(
        "align", 
        help="Align a corpus with a pretrained acoustic model",
    )
    align_parser.add_argument(
        "--corpus_directory", 
        help="Full path to the directory to align",
        )
    align_parser.add_argument(
        "--dictionary_path",
        help=dictionary_path_help,
        type=str,
    )
    align_parser.add_argument(
        "--acoustic_model_path",
        type=str,
        help=acoustic_model_path_help,
    )
    align_parser.add_argument(
        "--output_directory",
        type=str,
        help="Full path to output directory, will be created if it doesn't exist",
    )
    align_parser.add_argument(
        "--config_path", 
        type=str, 
        default="mfa/config/align_config.yaml", 
        help="Path to config file to use for alignment"
    )
    align_parser.add_argument(
        "-s",
        "--speaker_characters",
        type=str,
        default="0",
        help="Number of characters of file names to use for determining speaker, "
        "default is to use directory names",
    )
    align_parser.add_argument(
        "-a",
        "--audio_directory",
        type=str,
        default="",
        help="Audio directory root to use for finding audio files",
    )
    align_parser.add_argument(
        "--reference_directory",
        type=str,
        default="",
        help="Directory containing gold standard alignments to evaluate",
    )
    align_parser.add_argument(
        "--custom_mapping_path",
        type=str,
        default="",
        help="YAML file for mapping phones across phone sets in evaluations",
    )
    align_parser.add_argument(
        "--output_format",
        type=str,
        default="csv",
        choices=["long_textgrid", "short_textgrid", "json", "csv"],
        help="Format for aligned output files (default is long_textgrid)",
    )
    align_parser.add_argument(
        "--include_original_text",
        help="Flag to include original utterance text in the output",
        action="store_true",
    )
    add_global_options(align_parser, textgrid_output=True)

    help_message = "Inspect, download, and save pretrained MFA models"
    model_parser = subparsers.add_parser(
        "model", aliases=["models"], description=help_message, help=help_message
    )

    model_subparsers = model_parser.add_subparsers(dest="action")
    model_subparsers.required = True
    help_message = "Download a pretrained model from the MFA repository"
    model_download_parser = model_subparsers.add_parser(
        "download", description=help_message, help=help_message
    )
    model_download_parser.add_argument(
        "model_type", choices=sorted(MODEL_TYPES), help="Type of model to download"
    )
    model_download_parser.add_argument(
        "name",
        help="Name of language code to download, if not specified, "
        "will list all available languages",
        type=str,
        nargs="?",
    )
    model_download_parser.add_argument(
        "--github_token",
        type=str,
        default="",
        help="Personal access token to use for requests to GitHub to increase rate limit",
    )
    model_download_parser.add_argument(
        "--ignore_cache",
        action="store_true",
        help="Flag to ignore existing downloaded models and force a re-download",
    )
    help_message = "List of saved models"
    model_list_parser = model_subparsers.add_parser(
        "list", description=help_message, help=help_message
    )
    model_list_parser.add_argument(
        "model_type",
        choices=sorted(MODEL_TYPES),
        type=str,
        nargs="?",
        help="Type of model to list",
    )
    model_list_parser.add_argument(
        "--github_token",
        type=str,
        default="",
        help="Personal access token to use for requests to GitHub to increase rate limit",
    )

    help_message = "Inspect a model and output its metadata"
    model_inspect_parser = model_subparsers.add_parser(
        "inspect", description=help_message, help=help_message
    )
    model_inspect_parser.add_argument(
        "model_type",
        choices=sorted(MODEL_TYPES),
        type=str,
        nargs="?",
        help="Type of model to inspect",
    )
    model_inspect_parser.add_argument(
        "name", type=str, help="Name of pretrained model or path to MFA model to inspect"
    )

    help_message = "Save a MFA model to the pretrained directory for name-based referencing"
    model_save_parser = model_subparsers.add_parser(
        "save", description=help_message, help=help_message
    )
    model_save_parser.add_argument(
        "model_type", type=str, choices=sorted(MODEL_TYPES), help="Type of MFA model"
    )
    model_save_parser.add_argument(
        "path", help="Path to MFA model to save for invoking with just its name"
    )
    model_save_parser.add_argument(
        "--name",
        help="Name to use as reference (defaults to the name of the zip file",
        type=str,
        default="",
    )
    model_save_parser.add_argument(
        "--overwrite",
        help="Flag to overwrite existing pretrained models with the same name (and model type)",
        action="store_false",
    )

    config_parser = subparsers.add_parser(
        "configure",
        help="The configure command is used to set global defaults for MFA so "
        "you don't have to set them every time you call an MFA command.",
    )
    config_parser.add_argument(
        "-t",
        "--temp_directory",
        "--temporary_directory",
        dest="temporary_directory",
        type=str,
        default="",
        help=f"Set the default temporary directory, default is {GLOBAL_CONFIG['temporary_directory']}",
    )
    config_parser.add_argument(
        "-j",
        "--num_jobs",
        type=int,
        default=100,
        help=f"Set the number of processes to use by default, defaults to {GLOBAL_CONFIG['num_jobs']}",
    )
    config_parser.add_argument(
        "--always_clean",
        help="Always remove files from previous runs by default",
        action="store_true",
    )
    config_parser.add_argument(
        "--never_clean",
        help="Don't remove files from previous runs by default",
        action="store_true",
    )
    config_parser.add_argument(
        "--always_verbose", help="Default to verbose output", action="store_true"
    )
    config_parser.add_argument(
        "--never_verbose", help="Default to non-verbose output", action="store_true"
    )
    config_parser.add_argument("--always_quiet", help="Default to no output", action="store_true")
    config_parser.add_argument(
        "--never_quiet", help="Default to printing output", action="store_true"
    )
    config_parser.add_argument(
        "--always_debug", help="Default to running debugging steps", action="store_true"
    )
    config_parser.add_argument(
        "--never_debug", help="Default to not running debugging steps", action="store_true"
    )
    config_parser.add_argument(
        "--always_overwrite", help="Always overwrite output files", action="store_true"
    )
    config_parser.add_argument(
        "--never_overwrite",
        help="Never overwrite output files (if file already exists, "
        "the output will be saved in the temp directory)",
        action="store_true",
    )
    config_parser.add_argument(
        "--disable_mp",
        help="Disable all multiprocessing (not recommended as it will usually "
        "increase processing times)",
        action="store_true",
    )
    config_parser.add_argument(
        "--enable_mp",
        help="Enable multiprocessing (recommended and enabled by default)",
        action="store_true",
    )
    config_parser.add_argument(
        "--disable_textgrid_cleanup",
        help="Disable postprocessing of TextGrids that cleans up "
        "silences and recombines compound words and clitics",
        action="store_true",
    )
    config_parser.add_argument(
        "--enable_textgrid_cleanup",
        help="Enable postprocessing of TextGrids that cleans up "
        "silences and recombines compound words and clitics",
        action="store_true",
    )
    config_parser.add_argument(
        "--disable_detect_phone_set",
        help="Disable auto-detecting phone sets from the dictionary during training",
        action="store_true",
    )
    config_parser.add_argument(
        "--enable_detect_phone_set",
        help="Enable auto-detecting phone sets from the dictionary during training",
        action="store_true",
    )
    config_parser.add_argument(
        "--disable_terminal_colors", help="Turn off colored text in output", action="store_true"
    )
    config_parser.add_argument(
        "--enable_terminal_colors", help="Turn on colored text in output", action="store_true"
    )
    config_parser.add_argument(
        "--terminal_width",
        help=f"Set width of terminal output, "
        f"currently set to {GLOBAL_CONFIG['terminal_width']}",
        default=GLOBAL_CONFIG["terminal_width"],
        type=int,
    )
    config_parser.add_argument(
        "--blas_num_threads",
        help=f"Number of threads to use for BLAS libraries, 1 is recommended "
        f"due to how much MFA relies on multiprocessing. "
        f"Currently set to {GLOBAL_CONFIG['blas_num_threads']}",
        default=GLOBAL_CONFIG["blas_num_threads"],
        type=int,
    )

    history_parser = subparsers.add_parser("history", help="Show previously run mfa commands")
    _ = subparsers.add_parser("thirdparty", help="DEPRECATED: Please install Kaldi via conda.")
    _ = subparsers.add_parser(
        "download", help="DEPRECATED: Please use mfa model download instead."
    )

    history_parser.add_argument(
        "depth", type=int, help="Number of commands to list", nargs="?", default=10
    )
    history_parser.add_argument(
        "-v",
        "--verbose",
        help=f"Output debug messages, default is {GLOBAL_CONFIG['verbose']}",
        action="store_true",
    )

    _ = subparsers.add_parser(
        "anchor", aliases=["annotator"], help="Launch Anchor Annotator (if installed)"
    )

    return parser


def print_history(args: argparse.Namespace) -> None:
    """
    Print the history of MFA commands
    Parameters
    ----------
    args: argparse.Namespace
        Parsed args
    """
    depth = args.depth
    history = load_command_history()[-depth:]
    if args.verbose:
        print("command\tDate\tExecution time\tVersion\tExit code\tException")
        for h in history:
            execution_time = time.strftime("%H:%M:%S", time.gmtime(h["execution_time"]))
            d = h["date"].isoformat()
            print(
                f"{h['command']}\t{d}\t{execution_time}\t{h['version']}\t{h['exit_code']}\t{h['exception']}"
            )
        pass
    else:
        for h in history:
            print(h["command"])

def align_corpus(args: Namespace, unknown_args: Optional[List[str]] = None) -> None:
    """
    Run the alignment
    Parameters
    ----------
    args: :class:`~argparse.Namespace`
        Command line arguments
    unknown_args: list[str]
        Optional arguments that will be passed to configuration objects
    """
    aligner = PretrainedAligner(
        acoustic_model_path=args.acoustic_model_path,
        corpus_directory=args.corpus_directory,
        dictionary_path=args.dictionary_path,
        temporary_directory=args.temporary_directory,
        **PretrainedAligner.parse_parameters(args.config_path, args, unknown_args),
    )
    try:
        aligner.align()
        output_format = getattr(args, "output_format", None)
        aligner.export_files(
            args.output_directory,
            output_format=output_format,
            include_original_text=getattr(args, "include_original_text", False),
        )
        if getattr(args, "reference_directory", ""):
            mapping = None
            if getattr(args, "custom_mapping_path", ""):
                with mfa_open(args.custom_mapping_path, "r") as f:
                    mapping = yaml.safe_load(f)
            aligner.load_reference_alignments(args.reference_directory)
            aligner.evaluate_alignments(mapping, output_directory=args.output_directory)
    except Exception:
        aligner.dirty = True
        raise
    finally:
        aligner.cleanup()


def validate_args(args: Namespace) -> None:
    """
    Validate the command line arguments
    Parameters
    ----------
    args: :class:`~argparse.Namespace`
        Parsed command line arguments
    Raises
    ------
    :class:`~montreal_forced_aligner.exceptions.ArgumentError`
        If there is a problem with any arguments
    """
    try:
        args.speaker_characters = int(args.speaker_characters)
    except ValueError:
        pass
    args.output_directory = args.output_directory.rstrip("/").rstrip("\\")
    args.corpus_directory = args.corpus_directory.rstrip("/").rstrip("\\")
    if not os.path.exists(args.corpus_directory):
        raise ArgumentError(f"Could not find the corpus directory {args.corpus_directory}.")
    if not os.path.isdir(args.corpus_directory):
        raise ArgumentError(
            f"The specified corpus directory ({args.corpus_directory}) is not a directory."
        )

    if args.corpus_directory == args.output_directory:
        raise ArgumentError("Corpus directory and output directory cannot be the same folder.")

    args.dictionary_path = validate_model_arg(args.dictionary_path, "dictionary")
    args.acoustic_model_path = validate_model_arg(args.acoustic_model_path, "acoustic")


def run_align_corpus(args: Namespace, unknown_args: Optional[List[str]] = None) -> None:
    """
    Wrapper function for running alignment
    Parameters
    ----------
    args: :class:`~argparse.Namespace`
        Parsed command line arguments
    unknown_args: list[str]
        Parsed command line arguments to be passed to the configuration objects
    """
    validate_args(args)
    align_corpus(args, unknown_args)

if __name__ == '__main__':
    """
    Main function for the MFA command line interface
    """
    
    parser = create_parser()
    try:
        args, unknown = parser.parse_known_args()
        print(f"A: {args}")
        run_align_corpus(args, unknown)
    except MFAError as e:
        if getattr(args, "debug", False):
            raise
        print(e, file=sys.stderr)
        sys.exit(1)