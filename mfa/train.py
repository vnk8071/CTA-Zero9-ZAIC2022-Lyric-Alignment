"""Command line functions for training new acoustic models"""
from __future__ import annotations

import os
import sys
import argparse
from typing import TYPE_CHECKING, List, Optional

from montreal_forced_aligner.acoustic_modeling import TrainableAligner
from montreal_forced_aligner.command_line.utils import validate_model_arg
from montreal_forced_aligner.exceptions import ArgumentError
from montreal_forced_aligner.exceptions import MFAError
from montreal_forced_aligner.models import MODEL_TYPES
from montreal_forced_aligner.config import (
    load_command_history,
    load_global_config,
    update_command_history,
    update_global_config,
)

if TYPE_CHECKING:
    from argparse import Namespace, ArgumentParser

__all__ = ["train_acoustic_model", "validate_args", "run_train_acoustic_model"]

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
            action="store_true",
            default=GLOBAL_CONFIG["clean"],
        )
        subparser.add_argument(
            "--overwrite",
            help=f"Overwrite output files when they exist, default is {GLOBAL_CONFIG['overwrite']}",
            action="store_true",
            default=GLOBAL_CONFIG["overwrite"],
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
    subparsers.required = True

    _ = subparsers.add_parser("version")

    train_parser = subparsers.add_parser(
        "train", help="Train a new acoustic model on a corpus and optionally export alignments"
    )
    train_parser.add_argument(
        "corpus_directory", type=str, help="Full path to the source directory to align"
    )
    train_parser.add_argument("dictionary_path", type=str, help=dictionary_path_help, default="")
    train_parser.add_argument(
        "output_paths",
        type=str,
        nargs="+",
        help="Path to save the new acoustic model, path to export aligned TextGrids, or both",
    )
    train_parser.add_argument(
        "--config_path",
        type=str,
        default="",
        help="Path to config file to use for training and alignment",
    )
    train_parser.add_argument(
        "-o",
        "--output_model_path",
        type=str,
        default="",
        help="Full path to save resulting acoustic model",
    )
    train_parser.add_argument(
        "-s",
        "--speaker_characters",
        type=str,
        default="0",
        help="Number of characters of filenames to use for determining speaker, "
        "default is to use directory names",
    )
    train_parser.add_argument(
        "-a",
        "--audio_directory",
        type=str,
        default="",
        help="Audio directory root to use for finding audio files",
    )
    train_parser.add_argument(
        "--phone_set",
        dest="phone_set_type",
        type=str,
        help="Enable extra decision tree modeling based on the phone set",
        default="UNKNOWN",
        choices=["AUTO", "IPA", "ARPA", "PINYIN"],
    )
    train_parser.add_argument(
        "--output_format",
        type=str,
        default="long_textgrid",
        choices=["short_textgrid", "long_textgrid", "json"],
        help="Format for aligned output files",
    )
    train_parser.add_argument(
        "--include_original_text",
        help="Flag to include original utterance text in the output",
        action="store_true",
    )
    add_global_options(train_parser, textgrid_output=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a corpus for use in MFA")
    validate_parser.add_argument(
        "corpus_directory", type=str, help="Full path to the source directory to align"
    )
    validate_parser.add_argument(
        "dictionary_path", type=str, help=dictionary_path_help, default=""
    )
    validate_parser.add_argument(
        "acoustic_model_path",
        type=str,
        nargs="?",
        default="",
        help=acoustic_model_path_help,
    )
    validate_parser.add_argument(
        "-s",
        "--speaker_characters",
        type=str,
        default="0",
        help="Number of characters of file names to use for determining speaker, "
        "default is to use directory names",
    )
    validate_parser.add_argument(
        "--config_path",
        type=str,
        default="",
        help="Path to config file to use for training and alignment",
    )
    validate_parser.add_argument(
        "--test_transcriptions", help="Test accuracy of transcriptions", action="store_true"
    )
    validate_parser.add_argument(
        "--ignore_acoustics",
        "--skip_acoustics",
        dest="ignore_acoustics",
        help="Skip acoustic feature generation and associated validation",
        action="store_true",
    )
    validate_parser.add_argument(
        "-a",
        "--audio_directory",
        type=str,
        default="",
        help="Audio directory root to use for finding audio files",
    )
    validate_parser.add_argument(
        "--phone_set",
        dest="phone_set_type",
        type=str,
        help="Enable extra decision tree modeling based on the phone set",
        default="UNKNOWN",
        choices=["AUTO", "IPA", "ARPA", "PINYIN"],
    )
    add_global_options(validate_parser)

    validate_dictionary_parser = subparsers.add_parser(
        "validate_dictionary",
        help="Validate a dictionary using a G2P model to detect unlikely pronunciations",
    )

    validate_dictionary_parser.add_argument(
        "dictionary_path", type=str, help=dictionary_path_help, default=""
    )
    validate_dictionary_parser.add_argument(
        "output_path",
        type=str,
        nargs="?",
        help="Path to save the CSV file with the scored pronunciations",
    )
    validate_dictionary_parser.add_argument(
        "--g2p_model_path",
        type=str,
        help="Pretrained G2P model path",
    )
    validate_dictionary_parser.add_argument(
        "--g2p_threshold",
        type=float,
        default=1.5,
        help="Threshold to use when running G2P. Paths with costs less than the best path times the threshold value will be included.",
    )
    validate_dictionary_parser.add_argument(
        "--config_path",
        type=str,
        default="",
        help="Path to config file to use for validation",
    )
    add_global_options(validate_dictionary_parser)

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
        action="store_true",
    )

    train_lm_parser = subparsers.add_parser(
        "train_lm", help="Train a language model from a corpus"
    )
    train_lm_parser.add_argument(
        "source_path",
        type=str,
        help="Full path to the source directory to train from, alternatively "
        "an ARPA format language model to convert for MFA use",
    )
    train_lm_parser.add_argument(
        "output_model_path", type=str, help="Full path to save resulting language model"
    )
    train_lm_parser.add_argument(
        "-m",
        "--model_path",
        type=str,
        help="Full path to existing language model to merge probabilities",
    )
    train_lm_parser.add_argument(
        "-w",
        "--model_weight",
        type=float,
        default=1.0,
        help="Weight factor for supplemental language model, defaults to 1.0",
    )
    train_lm_parser.add_argument(
        "--dictionary_path", type=str, help=dictionary_path_help, default=""
    )
    train_lm_parser.add_argument(
        "--config_path",
        type=str,
        default="",
        help="Path to config file to use for training and alignment",
    )
    add_global_options(train_lm_parser)

    train_dictionary_parser = subparsers.add_parser(
        "train_dictionary",
        help="Calculate pronunciation probabilities for a dictionary based on alignment results in a corpus",
    )
    train_dictionary_parser.add_argument(
        "corpus_directory", help="Full path to the directory to align"
    )
    train_dictionary_parser.add_argument("dictionary_path", type=str, help=dictionary_path_help)
    train_dictionary_parser.add_argument(
        "acoustic_model_path",
        type=str,
        help=acoustic_model_path_help,
    )
    train_dictionary_parser.add_argument(
        "output_directory",
        type=str,
        help="Full path to output directory, will be created if it doesn't exist",
    )
    train_dictionary_parser.add_argument(
        "--config_path", type=str, default="", help="Path to config file to use for alignment"
    )
    train_dictionary_parser.add_argument(
        "--silence_probabilities",
        action="store_true",
        help="Flag for saving silence information for pronunciations",
    )
    train_dictionary_parser.add_argument(
        "-s",
        "--speaker_characters",
        type=str,
        default="0",
        help="Number of characters of file names to use for determining speaker, "
        "default is to use directory names",
    )
    add_global_options(train_dictionary_parser)

    train_ivector_parser = subparsers.add_parser(
        "train_ivector",
        help="Train an ivector extractor from a corpus and pretrained acoustic model",
    )
    train_ivector_parser.add_argument(
        "corpus_directory",
        type=str,
        help="Full path to the source directory to train the ivector extractor",
    )
    train_ivector_parser.add_argument(
        "output_model_path",
        type=str,
        help="Full path to save resulting ivector extractor",
    )
    train_ivector_parser.add_argument(
        "-s",
        "--speaker_characters",
        type=str,
        default="0",
        help="Number of characters of filenames to use for determining speaker, "
        "default is to use directory names",
    )
    train_ivector_parser.add_argument(
        "--config_path", type=str, default="", help="Path to config file to use for training"
    )
    add_global_options(train_ivector_parser)

    classify_speakers_parser = subparsers.add_parser(
        "classify_speakers", help="Use an ivector extractor to cluster utterances into speakers"
    )
    classify_speakers_parser.add_argument(
        "corpus_directory",
        type=str,
        help="Full path to the source directory to run speaker classification",
    )
    classify_speakers_parser.add_argument(
        "ivector_extractor_path", type=str, default="", help=ivector_model_path_help
    )
    classify_speakers_parser.add_argument(
        "output_directory",
        type=str,
        help="Full path to output directory, will be created if it doesn't exist",
    )

    classify_speakers_parser.add_argument(
        "-s", "--num_speakers", type=int, default=0, help="Number of speakers if known"
    )
    classify_speakers_parser.add_argument(
        "--cluster", help="Using clustering instead of classification", action="store_true"
    )
    classify_speakers_parser.add_argument(
        "--config_path",
        type=str,
        default="",
        help="Path to config file to use for ivector extraction",
    )
    add_global_options(classify_speakers_parser)

    create_segments_parser = subparsers.add_parser(
        "create_segments", help="Create segments based on voice activity dectection (VAD)"
    )
    create_segments_parser.add_argument(
        "corpus_directory", help="Full path to the source directory to run VAD segmentation"
    )
    create_segments_parser.add_argument(
        "output_directory",
        type=str,
        help="Full path to output directory, will be created if it doesn't exist",
    )
    create_segments_parser.add_argument(
        "--config_path", type=str, default="", help="Path to config file to use for segmentation"
    )
    add_global_options(create_segments_parser)

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

def train_acoustic_model(args: Namespace, unknown_args: Optional[List[str]] = None) -> None:
    """
    Run the acoustic model training
    Parameters
    ----------
    args: :class:`~argparse.Namespace`
        Command line arguments
    unknown_args: list[str]
        Optional arguments that will be passed to configuration objects
    """
    trainer = TrainableAligner(
        corpus_directory=args.corpus_directory,
        dictionary_path=args.dictionary_path,
        temporary_directory=args.temporary_directory,
        **TrainableAligner.parse_parameters(args.config_path, args, unknown_args),
    )
    try:
        trainer.train()
        if args.output_model_path is not None:
            trainer.export_model(args.output_model_path)

        if args.output_directory is not None:
            output_format = getattr(args, "output_format", None)
            trainer.export_files(
                args.output_directory,
                output_format,
                include_original_text=getattr(args, "include_original_text", False),
            )
    except Exception:
        trainer.dirty = True
        raise
    finally:
        trainer.cleanup()


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

    args.output_directory = None
    if not args.output_model_path:
        args.output_model_path = None
    output_paths = args.output_paths
    if len(output_paths) > 2:
        raise ArgumentError(f"Got more arguments for output_paths than 2: {output_paths}")
    for path in output_paths:
        if path.endswith(".zip"):
            args.output_model_path = path
        else:
            args.output_directory = path.rstrip("/").rstrip("\\")

    args.corpus_directory = args.corpus_directory.rstrip("/").rstrip("\\")
    if args.corpus_directory == args.output_directory:
        raise ArgumentError("Corpus directory and output directory cannot be the same folder.")
    if not os.path.exists(args.corpus_directory):
        raise (ArgumentError(f'Could not find the corpus directory "{args.corpus_directory}".'))
    if not os.path.isdir(args.corpus_directory):
        raise (
            ArgumentError(
                f'The specified corpus directory "{args.corpus_directory}" is not a directory.'
            )
        )

    args.dictionary_path = validate_model_arg(args.dictionary_path, "dictionary")


def run_train_acoustic_model(args: Namespace, unknown_args: Optional[List[str]] = None) -> None:
    """
    Wrapper function for running acoustic model training
    Parameters
    ----------
    args: :class:`~argparse.Namespace`
        Parsed command line arguments
    unknown_args: list[str]
        Parsed command line arguments to be passed to the configuration objects
    """
    validate_args(args)
    train_acoustic_model(args, unknown_args)

if __name__ == '__main__':
    """
    Main function for the MFA command line interface
    """
    
    parser = create_parser()
    try:
        args, unknown = parser.parse_known_args()
        run_train_acoustic_model(args, unknown)
    except MFAError as e:
        if getattr(args, "debug", False):
            raise
        print(e, file=sys.stderr)
        sys.exit(1)
