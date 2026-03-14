#!/usr/bin/env python3
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from files2db.cli import app

runner = CliRunner()


class TestCLI(unittest.TestCase):
    def test_version(self):
        result = runner.invoke(app, ["--version"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("files2db version", result.stdout)

    def test_license(self):
        result = runner.invoke(app, ["--license"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("license", result.stdout.lower())

    def test_warranty(self):
        result = runner.invoke(app, ["--warranty"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("warranty", result.stdout.lower())

    def test_missing_path(self):
        result = runner.invoke(app, [])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing argument", result.stdout)

    @patch("files2db.cli.main")
    def test_main_called(self, mock_main):

        result = runner.invoke(
            app,
            [
                "input.txt",
                "--normalize",
                "--output",
                "outdir",
                "--prefix",
                "testprefix",
            ],
        )

        self.assertEqual(result.exit_code, 0)

        mock_main.assert_called_once_with(
            path="input.txt",
            normalize=True,
            output_folder="outdir",
            output_files_prefix="testprefix",
        )
