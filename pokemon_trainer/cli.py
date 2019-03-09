# -*- coding: utf-8 -*-

"""Console script for pokemon_trainer."""
import os
import click
import click_completion
import yaml
from shutil import copyfile
from .pokemon.moves import Move
from .pokemon.teams import Roster
from .pokemon.pokedex import Species
from .pokemon.types import Type

TRAINER_FILENAME = '.pokemon-trainer'
TRAINER_PATH = os.path.expanduser(os.path.join('~', TRAINER_FILENAME))
COMPLETION_DATA_FILENAME = '.pokemon-trainer-complete'
COMPLETION_DATA_PATH = os.path.expanduser(os.path.join('~', COMPLETION_DATA_FILENAME))

click_completion.init()
moves_argument_type = click.STRING
species_argument_type = click.STRING
types_argument_type = click.STRING


class TabCompleteChoice(click.Choice):
    def __init__(self, choices, case_sensitive=False, truncate_at=5):
        super(TabCompleteChoice, self).__init__(choices, case_sensitive)
        self.truncate_at = truncate_at

    def get_metavar(self, param):
        if len(self.choices) > self.truncate_at:
            return '[{} ...]'.format('|'.join(self.choices[:self.truncate_at]))
        else:
            return '[%s]'.format('|'.join(self.choices))

    def convert(self, value, param, ctx):
        try:
            return super(TabCompleteChoice, self).convert(value, param, ctx)
        except click.BadParameter:
            return value


if os.path.exists(COMPLETION_DATA_PATH):
    try:
        with open(COMPLETION_DATA_PATH) as f:
            data = yaml.safe_load(f)
            moves_argument_type = TabCompleteChoice(data['moves'])
            species_argument_type = TabCompleteChoice(data['species'])
            types_argument_type = TabCompleteChoice(data['types'])
    except IOError:
        pass


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
@click.option('--rebuild', is_flag=True, default=False,
              help="Force a rebuild of the tab completion cache (e.g. pokemon names)")
def install_completion(rebuild):
    """Setup tab completion for pokemon-trainer commands and arguments.
    Supports fish, Zsh, Bash and PowerShell.

    :param rebuild: Force the pokemon api cache of names, types, etc to refresh
    :return:
    """
    if not os.path.exists(COMPLETION_DATA_PATH) or rebuild:
        data = {
            'moves': [l['name'] for l in Move.resource_list()],
            'species': [l['name'] for l in Species.resource_list()],
            'types': [l['name'] for l in Type.resource_list()],
        }
        with open(COMPLETION_DATA_PATH, 'w') as f:
            yaml.dump(data, f)
        click.echo('pokemon completion data cached in {}'.format(COMPLETION_DATA_PATH))
    else:
        click.echo('pokemon completion data cached already exists in {}, force a rebuild with --rebuild'.format(COMPLETION_DATA_PATH))
    shell, path = click_completion.core.install()
    click.echo('{} completion installed in {}'.format(shell, path))
    return 0


@main.command()
@click.pass_context
@click.argument('id_or_name', type=species_argument_type, nargs=-1)
def species(ctx, id_or_name):
    """List details for a Pokemon species, where id_or_name is
    the pokedex name or ID of the Pokemon (e.g. 1 or 'bulbasaur'
    to lookup bulbasaur). Names support tab completion.
    \f

    :param ctx:
    :param id_or_name:
    :return:
    """
    for id in id_or_name:
        try:
            click.echo(Species.search(id))
        except ValueError as e:
            click.echo("{} failed: {}".format(id, e))
    return 0


@main.command()
@click.pass_context
@click.argument('id_or_name', type=types_argument_type, nargs=-1)
def type(ctx, id_or_name):
    """List details for a Pokemon/Move Type, where id_or_name is
    the name or ID of the type (e.g. 16 or \'dragon\' to
    lookup the dragon type). Names support tab completion.
    \f

    :param ctx:
    :param id_or_name:
    :return:
    """
    for id in id_or_name:
        try:
            click.echo(Type.search(id))
        except ValueError as e:
            click.echo("{} failed: {}".format(id, e))
    return 0

@main.command()
@click.pass_context
@click.argument('id_or_name', type=moves_argument_type, nargs=-1)
def move(ctx, id_or_name):
    """List details for a Move, where id_or_name is
    the name or ID of the move (e.g. 15 or \'cut\' to
    lookup the cut move). Names support tab completion.
    \f

    :param ctx:
    :param id_or_name:
    :return:
    """
    for id in id_or_name:
        try:
            click.echo(Move.search(id))
        except ValueError as e:
            click.echo("{} failed: {}".format(id, e))
    return 0


@main.command()
@click.pass_context
@click.option('--id', help='ID or name of the team')
def team(ctx, id_or_name, active):
    pass
