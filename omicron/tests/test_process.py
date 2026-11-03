from pathlib import Path

import pytest

from ..cli.process import (
    create_parser,
    post_process_output_names,
    write_post_process_submit_file,
)


def test_post_process_template_option_is_available():
    args = create_parser().parse_args([
        "SIM",
        "--post-process-template",
        "/tmp/post-processing.sub",
    ])

    assert args.post_process_template == Path("/tmp/post-processing.sub")


def test_post_process_output_names_merges_contiguous_files():
    inputs = [
        "/tmp/H1-TEST_OMICRON-100000000-60.root",
        "/tmp/H1-TEST_OMICRON-100000060-60.root",
        "/tmp/H1-TEST_OMICRON-100000200-60.root",
    ]

    assert post_process_output_names(inputs) == [
        "H1-TEST_OMICRON-100000000-120.root",
        "H1-TEST_OMICRON-100000200-60.root",
    ]


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({}, "H1-TEST_OMICRON-100000000-60.xml.gz"),
        ({"no_gzip": True}, "H1-TEST_OMICRON-100000000-60.xml"),
        ({"no_merge": True}, "H1-TEST_OMICRON-100000000-60.xml"),
    ],
)
def test_post_process_output_names_respects_xml_options(kwargs, expected):
    inputs = ["/tmp/H1-TEST_OMICRON-100000000-60.xml"]

    assert post_process_output_names(inputs, **kwargs) == [expected]


def test_write_post_process_submit_file_replaces_template_fields(tmp_path):
    template = (
        Path(__file__).parents[2]
        / "templates"
        / "ligo_omicron_post_process.sub"
    )
    outfile = tmp_path / "post-processing.sub"

    write_post_process_submit_file(
        template,
        outfile,
        tmp_path / "logs",
        "SIM",
        "ligo.dev.test",
        "tester",
    )

    contents = outfile.read_text()
    assert "@LOG_DIR@" not in contents
    assert "@POST_PROCESS_GROUP@" not in contents
    assert "@CONDOR_ACCOUNTING_GROUP@" not in contents
    assert "@CONDOR_ACCOUNTING_GROUP_USER@" not in contents
    assert "$(macroargument4)" in contents
    assert "queue 1" in contents
