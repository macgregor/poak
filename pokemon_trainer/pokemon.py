# -*- coding: utf-8 -*-

from enum import Enum
from .util import *
import pokebase as pb
import math
import textwrap


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


class DamageRelation(Enum):
    NO_DAMAGE_TO = 0
    NO_DAMAGE_FROM = 1
    QUARTER_DAMAGE_TO = 2
    QUARTER_DAMAGE_FROM = 3
    HALF_DAMAGE_TO = 4
    HALF_DAMAGE_FROM = 5
    NORMAL_DAMAGE_TO = 6
    NORMAL_DAMAGE_FROM = 7
    DOUBLE_DAMAGE_TO = 8
    DOUBLE_DAMAGE_FROM = 9
    QUADRUPLE_DAMAGE_FROM = 10
    QUADRUPLE_DAMAGE_TO = 11

    def readable_name(self):
        return self.name.lower().replace('_', ' ').title()

    def multiplier(self):
        if 'NO' in self.name:
            return '0x'
        elif 'QUARTER' in self.name:
            return '1/4x'
        elif 'HALF' in self.name:
            return '1/2x'
        elif 'DOUBLE' in self.name:
            return '2x'
        elif 'QUADRUPLE' in self.name:
            return '4x'
        else:
            return '1x'

    @staticmethod
    def damage_to():
        return [DamageRelation.NO_DAMAGE_TO, DamageRelation.QUARTER_DAMAGE_TO, DamageRelation.HALF_DAMAGE_TO,
                DamageRelation.NORMAL_DAMAGE_TO, DamageRelation.DOUBLE_DAMAGE_TO, DamageRelation.QUADRUPLE_DAMAGE_TO]

    @staticmethod
    def damage_from():
        return [DamageRelation.NO_DAMAGE_FROM, DamageRelation.QUARTER_DAMAGE_FROM, DamageRelation.HALF_DAMAGE_FROM,
                DamageRelation.NORMAL_DAMAGE_FROM, DamageRelation.DOUBLE_DAMAGE_FROM, DamageRelation.QUADRUPLE_DAMAGE_FROM]


class TypeCoverage(dict):

    def __init__(self, **kwargs):
        self._coverage = {}
        self.clear()
        for relation in DamageRelation:
            if relation in kwargs:
                self._coverage[relation] += kwargs[relation]

    def clear(self):
        self._coverage = {
            DamageRelation.NO_DAMAGE_TO: [],
            DamageRelation.QUARTER_DAMAGE_TO: [],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.DOUBLE_DAMAGE_TO: [],
            DamageRelation.QUADRUPLE_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_FROM: [],
            DamageRelation.QUARTER_DAMAGE_FROM: [],
            DamageRelation.HALF_DAMAGE_FROM: [],
            DamageRelation.DOUBLE_DAMAGE_FROM: [],
            DamageRelation.QUADRUPLE_DAMAGE_FROM: []
        }

    def __setitem__(self, key, val):
        if not isinstance(key, DamageRelation):
            raise KeyError('TypeCoverage key must be of type DamageRelation, got \'%s\'' % type(key))
        if not isinstance(val, list):
            raise ValueError('TypeCoverage values must be empty list or list of Type, got \'%s\'' % type(val))
        if len(val) > 0:
            for i in val:
                if not isinstance(i, Type):
                    raise ValueError('TypeCoverage values must be empty list or list of Type, found type \'%s\' in list'
                                     % type(i))
        self._coverage[key] = val

    def __getitem__(self, key):
        if not isinstance(key, DamageRelation):
            raise KeyError('TypeCoverage key must be of type DamageRelation, got \'%s\'' % type(key))
        return self._coverage[key]

    def __delitem__(self, key):
        if not isinstance(key, DamageRelation):
            raise KeyError('TypeCoverage key must be of type DamageRelation, got \'%s\'' % type(key))
        self._coverage[key] = []

    def _add_type(self, type_):
        pass

    def _add_move(self, move):
        pass

    def _add_move_set(self, move_set):
        pass

    def _add_team(self, team):
        pass

    def _add_type_coverage(self, type_coverage):
        for relation in DamageRelation:
            if relation in type_coverage._

        pass

    def __iadd__(self, other):
        for stat in StatSet.STATS:
            self.__dict__[stat] += other.__dict__[stat]
        return self

    def __add__(self, other):
        type_coverage = TypeCoverage()
        if isinstance(other, Type):
            type_coverage._coverage = self._add_team(other)
        elif isinstance(other, Move):
            type_coverage._coverage = self._add_move(other)
        elif isinstance(other, MoveSet):
            type_coverage._coverage = self._add_move_set(other)
        elif isinstance(other, Team):
            type_coverage._coverage = self._add_team(other)
        elif isinstance(other, TypeCoverage):
            type_coverage._coverage = self._add_type_coverage(other)
        else:
            raise ValueError('Cannot add object of type \'%s\' to TypeCoverage. \
            Expected one of: Move, MoveSet, Type, Team, TypeCoverage' % type(other))
        return type_coverage


class Type(object):

    def __init__(self, id, name, type_coverage=None):
        self.id = id
        self.name = name
        self._type_coverage = type_coverage if type_coverage is not None else TypeCoverage()

    def reset_damage_relations(self):
        self._type_coverage.clear()

    def set_damage_relation(self, relation, type_):
        if type(relation) is not DamageRelation:
            raise ValueError('Expected \'relation\' to be of type DamageRelation, got %s' % (type(relation)))

        if relation not in self.damage_relations:
            self.damage_relations[relation] = []
        if type_ not in self.damage_relations[relation]:
            self.damage_relations[relation].append(type_)

    def damage_relation_to_type(self, other):
        for relation in DamageRelation.damage_to():
            if relation in self.damage_relations and other in self.damage_relations[relation]:
                return relation

        return DamageRelation.NORMAL_DAMAGE_TO

    def damage_relation_from_type(self, other):
        for relation in DamageRelation.damage_from():
            if relation in self.damage_relations and other in self.damage_relations[relation]:
                return relation

        return DamageRelation.NORMAL_DAMAGE_FROM

    def type_coverage(self):
        return self._type_coverage

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data):
        return Type.search(data['id'])

    @classmethod
    def search(cls, id_or_name):
        pb_type_ = pb.type_(id_or_name)
        type_ = cls(pb_type_.id, pb_type_.name)

        for relation in DamageRelation:
            if relation.name.lower() in pb_type_.damage_relations.__dict__:
                for t in pb_type_.damage_relations.__dict__[relation.name.lower()]:
                    name = t['name']
                    id = extract_id_or_name(t['url'])
                    type_.set_damage_relation(relation, Type(id, name))
        return type_

    def __eq__(self, other):
        if type(other) is not Type:
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __cmp__(self, other):
        return self.name.__cmp__(other.name)

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        dmg = ''
        relations = DamageRelation.damage_to() + DamageRelation.damage_from()
        for relation in relations:
            if relation in self.damage_relations and len(self.damage_relations[relation]):
                types = sorted([t.name for t in self.damage_relations[relation]])
                dmg += '\n{0: <18} ({1: <4}): {2}'.format(relation.readable_name(), relation.multiplier(), ', '.join(types))
        return '%-10s %s' % (self.name, dmg)


class DamageClass(Enum):
    status = 1
    physical = 2
    special = 3


class Generation(Enum):
    generation_i = 1
    generation_ii = 2
    generation_iii = 3
    generation_iv = 4
    generation_v = 5
    generation_vi = 6
    generation_vii = 7


class Move(object):

    FIELDS = ["accuracy", "effect_chance", "effect_entries", "crit_rate", "drain", "flinch_chance", "healing", "max_hits", "max_turns",
              "min_hits", "min_turns", "stat_chance", "power", "pp"]

    def __init__(self, id, name, damage_class, type_, generation, **kwargs):
        self.id = id
        self.name = name
        self.damage_class = damage_class
        self.type_ = type_
        self.generation = generation
        self.__dict__.update(kwargs)

    @classmethod
    def search(cls, id_or_name):
        move = pb.move(id_or_name)
        damage_class = DamageClass[move.damage_class.name]
        type_ = Type.search(move.type.name)
        generation = Generation[move.generation.name.replace('-', '_')]

        data = {}
        for field in Move.FIELDS:
            if field in move.__dict__:
                if field == 'effect_entries':
                    data[field] = [e.effect for e in move.__dict__[field]]
                else:
                    data[field] = move.__dict__[field]
            elif field in move.meta.__dict__:
                data[field] = move.meta.__dict__[field]
        return cls(move.id, move.name, damage_class, type_, generation, **data)

    @classmethod
    def from_dict(cls, data):
        return Move.search(data['id'])

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'damage_class': self.damage_class.name, 'type': self.type_.name}

    def __eq__(self, other):
        if type(other) is not Move:
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __cmp__(self, other):
        return self.name.__cmp__(other.name)

    def __str__(self):
        double_damage = sorted([t.name for t in self.type_.damage_relations[DamageRelation.DOUBLE_DAMAGE_TO]])
        half_damage = sorted([t.name for t in self.type_.damage_relations[DamageRelation.HALF_DAMAGE_TO]])
        no_damage = sorted([t.name for t in self.type_.damage_relations[DamageRelation.NO_DAMAGE_TO]])
        meta_fields = ["effect_chance", "crit_rate", "drain", "flinch_chance", "healing", "max_hits", "max_turns",
                       "min_hits", "min_turns", "stat_chance"]
        meta = [(f, self.__dict__[f]) for f in meta_fields if self.__dict__[f] is not None]
        args = {
            'name': self.name,
            'damage_class': self.damage_class.name,
            'type_name': self.type_.name,
            'description': '. '.join(self.effect_entries),
            'no_damage': ', '.join(no_damage),
            'half_damage': ', '.join(half_damage),
            'double_damage': ', '.join(double_damage),
            'accuracy': self.accuracy,
            'power': self.power,
            'pp': self.pp
        }
        return textwrap.dedent("""\
        {name} ({damage_class}, {type_name})
        power:    {power} 
        accuracy: {accuracy}
        pp:       {pp}
        
        {description}
        
        No Damage To     (0x  ): {no_damage}
        Half Damage To   (1/2x): {half_damage}
        Double Damage To (2x  ): {no_damage}
        
        Meta
        \
        """.format(**args))+tabulate(meta)


class MoveSet(object):

    def __init__(self, first, second=None, third=None, fourth=None):
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth

    def moves(self):
        tmp = [self.first, self.second, self.third, self.fourth]
        return [m for m in tmp if m is not None]

    def damage_classes(self):
        return list(set([m.damage_class for m in self.moves()]))

    def damage_types(self):
        return list(set([m.type_ for m in self.moves()]))

    def _name_or_empty(self, move):
        return move.name if move is not None else 'Empty'

    def to_dict(self):
        return {
            'first': self.first.to_dict(),
            'second': self.second.to_dict() if self.second is not None else None,
            'third': self.third.to_dict() if self.third is not None else None,
            'fourth': self.fourth.to_dict() if self.fourth is not None else None
        }

    @classmethod
    def from_dict(cls, data):
        moves = {
            'first': Move.from_dict(data['first']),
            'second': Move.from_dict(data['second']) if data['second'] is not None else None,
            'third': Move.from_dict(data['third']) if data['third'] is not None else None,
            'fourth': Move.from_dict(data['fourth']) if data['fourth'] is not None else None
        }
        return cls(**moves)

    def type_coverage(self):
        double_damage = []
        half_damage = []
        no_damage = []
        for t in self.damage_types():
            double_damage += t.damage_relations[DamageRelation.DOUBLE_DAMAGE_TO]
            half_damage += t.damage_relations[DamageRelation.HALF_DAMAGE_TO]
            no_damage += t.damage_relations[DamageRelation.NO_DAMAGE_TO]

        no_damage = [t for t in no_damage if t not in double_damage and t not in half_damage]
        half_damage = [t for t in half_damage if t not in double_damage and t not in no_damage]

        return {
            DamageRelation.DOUBLE_DAMAGE_TO: sorted(list(set(double_damage))),
            DamageRelation.HALF_DAMAGE_TO: sorted(list(set(half_damage))),
            DamageRelation.NO_DAMAGE_TO: sorted(list(set(no_damage)))
        }

    def __eq__(self, other):
        if type(other) is not MoveSet:
            return False
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __str__(self):
        return '1. {0: <16} 2. {1}\n3. {2: <16} 4. {3}'.format(self.first.name, self._name_or_empty(self.second),
                                                               self._name_or_empty(self.third), self._name_or_empty(self.fourth))


class Species(object):

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

    def _combined_damage_relations(self, damage_relation):
        damage_relations = []
        for species_t in self.types:
            for damage_t in species_t.damage_relations[damage_relation]:
                damage_relations.append(damage_t)
        return damage_relations

    def damage_relation_from_type(self, move_type):
        no_damage = self._combined_damage_relations(DamageRelation.NO_DAMAGE_FROM)
        half_damage = self._combined_damage_relations(DamageRelation.HALF_DAMAGE_FROM)
        double_damage = self._combined_damage_relations(DamageRelation.DOUBLE_DAMAGE_FROM)

        # If the type of move is completely ineffective against one of the opponent's types,
        # then the move does no damage, even if the opponent has a second type that would be vulnerable to it
        if move_type in no_damage:
            return DamageRelation.NO_DAMAGE_FROM

        # If the type of a move is super effective against both of the opponent's types,
        # then the move does 4 times the damage
        if double_damage.count(move_type) == 2:
            return DamageRelation.QUADRUPLE_DAMAGE_FROM

        # If the type of a move is super effective against one of the opponent's types
        # but not very effective against the other, then the move deals normal damage
        if move_type in double_damage and move_type in half_damage:
            return DamageRelation.NORMAL_DAMAGE_FROM

        # If the type of a move is not very effective against both of the opponent's types,
        # then the move only does 1/4 of the damage;
        if half_damage.count(move_type) == 2:
            return DamageRelation.QUARTER_DAMAGE_FROM

        # special cases weeded out, at this point we either have a single type with half, normal or double
        # damage, or dual types where at least one of the types is normal damage
        if move_type in double_damage:
            return DamageRelation.DOUBLE_DAMAGE_FROM
        elif move_type in half_damage:
            return DamageRelation.HALF_DAMAGE_FROM
        else:
            return DamageRelation.NORMAL_DAMAGE_FROM

    def vulnerabilities(self):
        vulnerable_relations = [DamageRelation.DOUBLE_DAMAGE_FROM, DamageRelation.QUADRUPLE_DAMAGE_FROM]
        double_damage = self._combined_damage_relations(DamageRelation.DOUBLE_DAMAGE_FROM)
        vulnerable_to_types = []
        for t in double_damage:
            if t not in vulnerable_to_types and self.damage_relation_from_type(t) in vulnerable_relations:
                vulnerable_to_types.append(t)

        return vulnerable_to_types

    def is_vulnerable_to(self, type_):
        vulnerable_relations = [DamageRelation.DOUBLE_DAMAGE_FROM, DamageRelation.QUADRUPLE_DAMAGE_FROM]
        return self.damage_relation_from_type(type_) in vulnerable_relations

    def immunities(self):
        return list(set(self._combined_damage_relations(DamageRelation.NO_DAMAGE_FROM)))

    def is_immune_to(self, type_):
        return type_ in self._combined_damage_relations(DamageRelation.NO_DAMAGE_FROM)

    def resistances(self):
        resistance_relations = [DamageRelation.HALF_DAMAGE_FROM, DamageRelation.QUARTER_DAMAGE_FROM]
        half_damage = self._combined_damage_relations(DamageRelation.HALF_DAMAGE_FROM)
        resistant_to_types = []
        for t in half_damage:
            if t not in resistant_to_types and self.damage_relation_from_type(t) in resistance_relations:
                resistant_to_types.append(t)

        return resistant_to_types

    def is_resistant_to(self, type_):
        resistance_relations = [DamageRelation.HALF_DAMAGE_FROM, DamageRelation.QUARTER_DAMAGE_FROM]
        return self.damage_relation_from_type(type_) in resistance_relations

    def type_coverage(self):
        return {
            DamageRelation.NO_DAMAGE_FROM: self.immunities(),
            DamageRelation.QUARTER_DAMAGE_FROM: [t for t in self.resistances() if self.damage_relation_from_type(t) == DamageRelation.QUARTER_DAMAGE_FROM],
            DamageRelation.HALF_DAMAGE_FROM: [t for t in self.resistances() if self.damage_relation_from_type(t) == DamageRelation.HALF_DAMAGE_FROM],
            DamageRelation.DOUBLE_DAMAGE_FROM: [t for t in self.vulnerabilities() if self.damage_relation_from_type(t) == DamageRelation.DOUBLE_DAMAGE_FROM],
            DamageRelation.QUADRUPLE_DAMAGE_FROM: [t for t in self.vulnerabilities() if self.damage_relation_from_type(t) == DamageRelation.QUADRUPLE_DAMAGE_FROM]
        }

    def __str__(self):
        type_ = ', '.join([t.name for t in self.types])
        vulnerable_to = ['%s (%s)' % (t.name, self.damage_relation_from_type(t).multiplier()) for t in self.vulnerabilities()]
        vulnerable_to = ', '.join(sorted(vulnerable_to))
        immune_to = ['%s (%s)' % (t.name, self.damage_relation_from_type(t).multiplier()) for t in self.immunities()]
        immune_to = ', '.join(sorted(immune_to))
        resistance_to = ['%s (%s)' % (t.name, self.damage_relation_from_type(t).multiplier()) for t in self.resistances()]
        resistance_to = ', '.join(sorted(resistance_to))
        return '#%03d %-10s (%s)\nVulnerable To: %s\nImmune To: %s\nResistance To: %s' \
               % (self.id, self.name, type_, vulnerable_to, immune_to, resistance_to)

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
        coverage = {
            DamageRelation.NO_DAMAGE_TO: [],
            DamageRelation.QUARTER_DAMAGE_TO: [],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.DOUBLE_DAMAGE_TO: [],
            DamageRelation.QUADRUPLE_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_FROM: [],
            DamageRelation.QUARTER_DAMAGE_FROM: [],
            DamageRelation.HALF_DAMAGE_FROM: [],
            DamageRelation.DOUBLE_DAMAGE_FROM: [],
            DamageRelation.QUADRUPLE_DAMAGE_FROM: []
        }
        for p in self.team(ordered=False):
            coverage = merge_dict_lists(coverage, p.species.type_coverage())
            if p.move_set:
                coverage = merge_dict_lists(coverage, p.move_set.type_coverage())

        # ignore quarter/half/no damage to if we have an effective moves (double/quadruple damage)
        coverage[DamageRelation.HALF_DAMAGE_TO] = [t for t in coverage[DamageRelation.HALF_DAMAGE_TO]
                                                   if t not in coverage[DamageRelation.DOUBLE_DAMAGE_TO] or
                                                   t not in coverage[DamageRelation.QUADRUPLE_DAMAGE_TO]]
        coverage[DamageRelation.QUARTER_DAMAGE_TO] = [t for t in coverage[DamageRelation.QUARTER_DAMAGE_TO]
                                                      if t not in coverage[DamageRelation.DOUBLE_DAMAGE_TO] or
                                                      t not in coverage[DamageRelation.QUADRUPLE_DAMAGE_TO]]
        coverage[DamageRelation.NO_DAMAGE_TO] = [t for t in coverage[DamageRelation.NO_DAMAGE_TO]
                                                 if t not in coverage[DamageRelation.DOUBLE_DAMAGE_TO] or
                                                 t not in coverage[DamageRelation.QUADRUPLE_DAMAGE_TO]]

        # prefer quadruple damage to double damage if in both
        coverage[DamageRelation.HALF_DAMAGE_TO] = [t for t in coverage[DamageRelation.HALF_DAMAGE_TO]
                                                   if t not in coverage[DamageRelation.QUARTER_DAMAGE_TO]]
        coverage[DamageRelation.DOUBLE_DAMAGE_TO] = [t for t in coverage[DamageRelation.DOUBLE_DAMAGE_TO]
                                                     if t not in coverage[DamageRelation.QUADRUPLE_DAMAGE_TO]]

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
        team = ''
        for pos in TeamPosition:
            team += '\n%d: %s' %(pos.value, self._team[pos].name if self._team[pos] is not None else 'Empty')
        return 'Team - %-10s %s' % (self.name, team)


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
