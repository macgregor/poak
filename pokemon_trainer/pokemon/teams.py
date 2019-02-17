# -*- coding: utf-8 -*-

from enum import Enum
from .types import TypeCoverage
from .pokedex import Pokemon


class TeamPosition(Enum):
    first = 1
    second = 2
    third = 3
    fourth = 4
    fifth = 5
    sixth = 6


class Team(object):

    def __init__(self, id, name, first=None, second=None, third=None, fourth=None, fifth=None, sixth=None):
        self.id = id
        self.name = name
        self._team = {
            TeamPosition.first: first,
            TeamPosition.second: second,
            TeamPosition.third: third,
            TeamPosition.fourth: fourth,
            TeamPosition.fifth: fifth,
            TeamPosition.sixth: sixth
        }

    def get_position(self, position_num):
        if isinstance(position_num, TeamPosition):
            return self._team[position_num]
        elif isinstance(position_num, int):
            return self._team[TeamPosition(position_num)]
        else:
            raise ValueError('Parameter \'position_num\' should be type TeamPosition or int, got %s' % (type(position_num)))

    def set_position(self, position_num, pokemon):
        if isinstance(position_num, TeamPosition):
            self._team[position_num] = pokemon
        elif isinstance(position_num, int):
            self._team[TeamPosition(position_num)] = pokemon
        else:
            raise ValueError('Parameter \'position_num\' should be type TeamPosition or int, got %s' % (type(position_num)))

    def is_full(self):
        for pos in TeamPosition:
            if self._team[pos] is None:
                return False
        return True

    def team(self, ordered=True):
        if ordered:
            return [self._team[pos] for pos in TeamPosition]
        else:
            return [val for val in self._team.values() if val is not None]

    def position_on_team(self, pokemon):
        if pokemon is not None and pokemon in self.team():
            return TeamPosition(self.team().index(pokemon)+1)
        return None

    def type_coverage(self):
        coverage = TypeCoverage()
        for pokemon in self.team():
            coverage += pokemon.type_coverage()
        return coverage

    @classmethod
    def from_dict(cls, data, pokemon_list=[]):
        existing_pokemon = {}
        if pokemon_list is not None:
            for p in pokemon_list:
                existing_pokemon[p.id] = p

        for pos, pokemon_id in data['team'].items():
            if pokemon_id is not None:
                if pokemon_id in existing_pokemon:
                    data[pos] = existing_pokemon[pokemon_id]
                else:
                    raise ValueError('Unknown pokemon id %d in team %s, position %s' % (pokemon_id, data['name'], pos))

        del data['team']
        return cls(**data)

    def to_dict(self):
        data = {'id': self.id, 'name': self.name}
        team = {}
        for pos in TeamPosition:
            team[pos.name.lower()] = self._team[pos].id if self._team[pos] is not None else None
        data['team'] = team
        return data

    def __eq__(self, other):
        if type(other) is not Team:
            return False

        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __str__(self):
        coverage = self.type_coverage().effective_coverage()
        team = ''
        for pos in TeamPosition:
            if self._team[pos] is not None:
                name = self._team[pos].name
                species_types = '/'.join([t.name for t in self._team[pos].species.types])
                move_types = 'None'
                if self._team[pos].move_set is not None:
                    move_types = ', '.join([m.type_.name for m in self._team[pos].move_set.moves()])
                team += '\n%d: %s (%s; moves: %s)' %(pos.value, name, species_types, move_types)
            else:
                team += '\n%d: Empty' % pos.value

        return 'Team - %-10s %s\n\nEffective Coverage\n%s' % (self.name, team, coverage)


class Roster(object):

    def __init__(self, pokemon=[], teams=[], active_team_id=None):
        self.pokemon = {}
        for p in pokemon:
            self.pokemon[p.id] = p

        self.teams = {}
        for t in teams:
            self.teams[t.id] = t
        self._active_team = active_team_id

    def active_team(self):
        if self._active_team is None:
            return None
        return self.teams[self._active_team]

    def set_active_team(self, team_id):
        if team_id is not None and team_id not in self.teams:
            raise ValueError('Unknown team %d' % (team_id))
        self._active_team = team_id

    def remove_team(self, team):
        if team is not None and team.id in self.teams:
            del self.teams[team.id]
            if self._active_team == team.id:
                self._active_team = None

    def add_team(self, team, active=False):
        self.teams[team.id] = team
        if active:
            self._active_team = team.id

    def get_team(self, team_id):
        return self.teams[team_id]

    def add_pokemon(self, pokemon):
        self.pokemon[pokemon.id] = pokemon

    def remove_pokemon(self, pokemon):
        if pokemon is not None and pokemon.id in self.pokemon:
            del self.pokemon[pokemon.id]
        for t in self.teams.values():
            if t.position_on_team(pokemon) is not None:
                t.set_position(t.position_on_team(pokemon), None)

    def get_pokemon(self, pokemon_id):
        return self.pokemon[pokemon_id]

    @classmethod
    def from_dict(cls, data):
        pokemon = []
        if 'pokemon' in data and data['pokemon'] is not None:
            pokemon = [Pokemon.from_dict(p) for p in data['pokemon']]

        teams = []
        if 'teams' in data and data['teams'] is not None:
            teams = [Team.from_dict(t, pokemon) for t in data['teams']]

        active_team = data['active_team'] if 'active_team' in data else None

        return cls(pokemon, teams, active_team)

    def to_dict(self):
        data = {
            'pokemon': [p.to_dict() for p in self.pokemon.values()],
            'teams': [t.to_dict() for t in self.teams.values()],
            'active_team': self._active_team
        }
        return data

    def __eq__(self, other):
        if type(other) is not Roster:
            return False

        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(str(self.to_dict()))
