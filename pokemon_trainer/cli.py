# -*- coding: utf-8 -*-

"""Console script for pokemon_trainer."""
import os
import click
import threading
import sys
import time
import yaml
from shutil import copyfile
from .pokemon import *

TRAINER_FILENAME = '.pokemon-trainer'
TRAINER_PATH = os.path.expanduser(os.path.join('~', TRAINER_FILENAME))


def load(filename):
    try:
        with open(filename) as f:
            return Roster.from_dict(yaml.safe_load(f))
    except IOError:
        pass  # Ignore missing tracking file.

    return Roster()


def save(roster, filename):
    if os.path.exists(roster.filename):
        copyfile(roster.filename,  roster.filename + '.bak')  # Create backup

    with open(filename, "w") as f:
        yaml.dump(roster.to_dict(), f)


@click.group()
@click.option('-f', '--file', type=click.Path(dir_okay=False, writable=True, resolve_path=True), default=TRAINER_PATH,
              show_default=True, help='File path to save/load trainer data from. Will be created if it does not exist.')
@click.pass_context
def main(ctx, file):
    ctx.ensure_object(dict)
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['filename'] = file
    ctx.obj['roster'] = load(file)


@main.command()
@click.pass_context
@click.argument('id_or_name')
def species(ctx, id_or_name):
    """List details for a Pokemon species, where id_or_name is
    the pokedex name or ID of the Pokemon (e.g. 1 or 'bulbasaur'
    to lookup bulbasaur).
    \f

    :param ctx:
    :param id_or_name:
    :return:
    """
    try:
        click.echo(Species.search(id_or_name))
    except ValueError as e:
        click.echo(e)
        return 1
    return 0


@main.command()
@click.pass_context
@click.argument('id_or_name')
def type(ctx, id_or_name):
    """List details for a Pokemon/Move Type, where id_or_name is
    the name or ID of the type (e.g. 16 or \'dragon\' to
    lookup the dragon type).
    \f

    :param ctx:
    :param id_or_name:
    :return:
    """
    try:
        click.echo(Type.search(id_or_name))
    except ValueError as e:
        click.echo(e)
        return 1
    return 0

@main.command()
@click.pass_context
@click.argument('id_or_name')
def move(ctx, id_or_name):
    """List details for a Move, where id_or_name is
    the name or ID of the move (e.g. 15 or \'cut\' to
    lookup the cut move).
    \f

    :param ctx:
    :param id_or_name:
    :return:
    """
    try:
        click.echo(Move.search(id_or_name))
    except ValueError as e:
        click.echo(e)
        return 1
    return 0


@main.command()
@click.pass_context
@click.option('--id', help='ID or name of the team')
def team(ctx, id_or_name, active):
    pass
