#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pokemon_trainer` package."""


import unittest
from click.testing import CliRunner

from pokemon_trainer import cli


class TestPokemonTrainerCli(unittest.TestCase):
    """Tests for `pokemon_trainer` cli."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_cli_help(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--help'])
        assert result.exit_code == 0
        assert 'Usage' in result.output
