# -*- coding: utf-8 -*-

import pokebase as pb
import math
from .types import *
from .moves import MoveSet


class StatSet(object):

    STATS = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
    LABELS = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']

    MAX_STAT = 255
    MAX_EV = 510

    @staticmethod
    def label(stat):
        return StatSet.LABELS[StatSet.STATS.index(stat)]

    def __init__(self, hp=0, attack=0, defense=0, special_attack=0,
                 special_defense=0, speed=0):
        self.hp = int(hp)
        self.attack = int(attack)
        self.defense = int(defense)
        self.special_attack = int(special_attack)
        self.special_defense = int(special_defense)
        self.speed = int(speed)

    def __iadd__(self, other):
        for stat in StatSet.STATS:
            self.__dict__[stat] += other.__dict__[stat]
        return self

    def __add__(self, other):
        evs = self.clone()
        evs += other
        return evs

    def __imul__(self, integer):
        for stat in StatSet.STATS:
            self.__dict__[stat] *= integer
        return self

    def __mul__(self, integer):
        evs = self.clone()
        for stat in StatSet.STATS:
            evs.__dict__[stat] *= integer
        return evs

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        stats = ''
        for i in range(len(StatSet.STATS)):
            if i % math.floor(len(StatSet.STATS)/2) == 0:
                stats += '\n'
            stats += '{}. {0: <8}'.format(StatSet.LABELS[i], self.__dict__[StatSet.STATS[i]])
        return stats

    def clone(self):
        return StatSet(**self.to_dict())

    def to_dict(self):
        dict = {}
        for stat in StatSet.STATS:
            dict[stat] = self.__dict__[stat]
        return dict


class Species(object):

    @staticmethod
    def resource_list():
        return pb.APIResourceList('pokemon')

    @classmethod
    def search(cls, id_or_name):
        pokemon = pb.pokemon(id_or_name)

        battle_evs = {}
        for stat in pokemon.stats:
            cleaned_name = stat.stat.name.replace('-', '_')
            battle_evs[cleaned_name] = stat.effort

        types = []
        for t in pokemon.types:
            types.append(Type.search(t.type.name))

        return cls(pokemon.id, pokemon.name, types=types, evs=StatSet(**battle_evs))

    def __init__(self, id, name, types=[], evs=None):
        self.id = int(id)
        self.name = name
        self.types = types
        self.evs = StatSet() if evs is None else evs

    def weak_to_types(self):
        coverage = self.type_coverage().effective_defensive_coverage()
        return coverage[DamageRelation.DOUBLE_DAMAGE_FROM] + coverage[DamageRelation.QUADRUPLE_DAMAGE_FROM]

    def is_weak_to(self, type_):
        return type_ in self.weak_to_types()

    def immune_to_types(self):
        coverage = self.type_coverage().effective_defensive_coverage()
        return coverage[DamageRelation.NO_DAMAGE_FROM]

    def is_immune_to(self, type_):
        return type_ in self.immune_to_types()

    def resistant_to_types(self):
        coverage = self.type_coverage().effective_defensive_coverage()
        return coverage[DamageRelation.HALF_DAMAGE_FROM] + coverage[DamageRelation.QUARTER_DAMAGE_FROM]

    def is_resistant_to(self, type_):
        return type_ in self.resistant_to_types()

    def type_coverage(self):
        coverage = TypeCoverage()
        for species_t in self.types:
            coverage += species_t.type_coverage()
        return coverage

    def __str__(self):
        type_ = ', '.join([t.name for t in self.types])
        return '#%03d %-10s (%s)\n%s' \
               % (self.id, self.name, type_, self.type_coverage().effective_defensive_coverage())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __cmp__(self, other):
        return self.name.__cmp__(other.name)


class Pokemon(object):

    def __init__(self, id, species, nick_name=None, pokerus=False, item=None, evs=None, stats=None, move_set=None):
        self.id = id
        self.species = species
        self.nick_name = nick_name
        self.pokerus = pokerus
        self.item = item
        self.evs = StatSet() if evs is None else evs
        self.stats = StatSet() if stats is None else stats
        self.move_set = move_set

    name = property(lambda self: self.get_name(),
                    lambda self, name: self.set_name(name))

    def __eq__(self, other):
        if type(other) is not Pokemon:
            return False

        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __cmp__(self, other):
        return self.get_name().__cmp__(other.get_name())

    def __str__(self):
        s = '%s\n%s' % (self.get_name(), self.species)
        if self.item is not None:
            s += '\nItem Held: %s' % self.item
        if self.pokerus:
            s += '\nPokerus'
        s += '\n\nStats\n%s' % self.stats
        s += '\n\nEVs\n%s' % self.evs
        if self.move_set is not None:
            s += '\n\nMoves\n%s' % self.move_set

        return s

    @classmethod
    def from_dict(cls, data):
        data['species'] = Species.search(data['species'])
        data['evs'] = StatSet(**data['evs'])
        data['stats'] = StatSet(**data['stats'])

        if 'move_set' in data and data['move_set'] is not None:
            data['move_set'] = MoveSet.from_dict(**data['move_set'])
        return cls(**data)

    def to_dict(self):
        return {
            'id': self.id, 'species': self.species.id, 'nick_name': self.nick_name,
            'pokerus': self.pokerus, 'item': self.item, 'evs': self.evs.to_dict(),
            'stats': self.stats.to_dict(),
            'move_set': self.move_set.to_dict() if self.move_set is not None else None
        }

    def get_name(self):
        return self.species.name if self.nick_name is None else self.nick_name

    def set_name(self, name):
        if name is not None and len(name.strip()) > 0:
            self.nick_name = name.strip()

    def type_coverage(self):
        coverage = TypeCoverage()
        coverage += self.species.type_coverage()
        if self.move_set is not None:
            coverage += self.move_set.type_coverage()
        return coverage

    def status(self):
        status = [str(self)]
        if self.pokerus:
            status.append('Pokerus')
        if self.item:
            status.append(self.item)
        status.append(self.evs.verbose())
        return '\n'.join(status)

    def listing(self, active):
        padding = '* ' if self is active else '  '
        return '%s%s' % (padding, self)
