# -*- coding: utf-8 -*-

from enum import Enum
from typing import List
from .util import *
import pokebase as pb
from inspect import Signature


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

    def __eq__(self, other):
        maybe_relation = other
        if type(maybe_relation) is str:
            maybe_relation = DamageRelation[other]
        elif type(maybe_relation) is int:
            maybe_relation = DamageRelation(other)

        if type(maybe_relation) is DamageRelation:
            return self.name == maybe_relation.name and self.value == maybe_relation.value
        return False

    def __hash__(self):
        return hash(self.name+str(self.value))

    def __lt__(self, other):
        return self.value < other.value

    def readable_name(self):
        return self.name.lower().replace('_', ' ').title()

    def multiplier(self, colorize=False):
        multiplier = '1x'
        if 'NO_DAMAGE' in self.name:
            multiplier = '0x'
            if colorize:
                multiplier = '{0x:256_bright_red}' if '_TO' in self.name else '{0x:256_bright_green}'
        elif 'QUARTER' in self.name:
            multiplier = '1/4x'
            if colorize:
                multiplier = '{1/4x:256_red}' if '_TO' in self.name else '{1/4x:256_green}'
        elif 'HALF' in self.name:
            multiplier = '1/2x'
            if colorize:
                multiplier = '{1/2x:256_light_red}' if '_TO' in self.name else '{1/2x:256_light_green}'
        elif 'DOUBLE' in self.name:
            multiplier = '2x'
            if colorize:
                multiplier = '{2x:256_light_red}' if '_FROM' in self.name else '{2x:256_light_green}'
        elif 'QUADRUPLE' in self.name:
            multiplier = '4x'
            if colorize:
                multiplier = '{4x:256_red}' if '_FROM' in self.name else '{4x:256_green}'
        return multiplier

    @staticmethod
    def damage_to():
        return [DamageRelation.NO_DAMAGE_TO, DamageRelation.QUARTER_DAMAGE_TO, DamageRelation.HALF_DAMAGE_TO,
                DamageRelation.NORMAL_DAMAGE_TO, DamageRelation.DOUBLE_DAMAGE_TO, DamageRelation.QUADRUPLE_DAMAGE_TO]

    @staticmethod
    def damage_from():
        return [DamageRelation.NO_DAMAGE_FROM, DamageRelation.QUARTER_DAMAGE_FROM, DamageRelation.HALF_DAMAGE_FROM,
                DamageRelation.NORMAL_DAMAGE_FROM, DamageRelation.DOUBLE_DAMAGE_FROM, DamageRelation.QUADRUPLE_DAMAGE_FROM]


class Type(object):

    def __init__(self, id, name, type_coverage=None):
        self.id = id
        self.name = name
        self._type_coverage = type_coverage if type_coverage is not None else TypeCoverage()

    def type_coverage(self):
        return self._type_coverage

    def set_damage_relation(self, relation, type_):
        self._type_coverage[relation].append(type_)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data):
        return Type.search(data['id'])

    @staticmethod
    def resource_list():
        return pb.APIResourceList('type')

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
        return self.id == other.id and self.name == other.name

    def __hash__(self):
        return hash(str(self.to_dict()))

    def __cmp__(self, other):
        return self.name.__cmp__(other.name)

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        coverage = self._type_coverage.unique()
        offensive_table = [('{Power:bold}', '{Types:bold}')]
        defensive_table = [('{Power:bold}', '{Types:bold}')]
        for damage_relation in DamageRelation.damage_to():
            if len(coverage[damage_relation]) > 0:
                multiplier = damage_relation.multiplier(colorize=True)
                row = (multiplier, ', '.join([t.name for t in sorted(coverage[damage_relation])]))
                offensive_table.append(row)

        for damage_relation in DamageRelation.damage_from():
            if len(coverage[damage_relation]) > 0:
                multiplier = damage_relation.multiplier(colorize=True)
                row = (multiplier, ', '.join([t.name for t in sorted(coverage[damage_relation])]))
                defensive_table.append(row)

        template_data = {
            'name': self.name,
            'offense': offensive_table,
            'defense': defensive_table
        }
        template = """
        {name:bold}
        
        Offensive Type Effectiveness
        {offense:table}
        
        Defensive Type Effectiveness
        {defense:table}
        """

        return CliFormatter().format(template, **template_data)


class TypeCoverage(dict):

    def __init__(self, coverage=None):
        self._coverage = {}
        self.clear()
        if coverage is not None:
            self.update(coverage)

    def offensive_types(self, unique=True) -> List[Type]:
        """
        Get a list of offensive types in the coverage map
        :param unique: If true (default), removes overlapping types from the list
        :return: List[Type]
        """
        types = []
        for damage_relation in DamageRelation.damage_to():
            types += self[damage_relation]
        return list(set(types)) if unique else types

    def defensive_types(self, unique=True) -> List[Type]:
        """
        Get a list of defensive types in the coverage map
        :param unique: If true (default), removes overlapping types from the list
        :return: List[Type]
        """
        types = []
        for damage_relation in DamageRelation.damage_from():
            types += self[damage_relation]
        return list(set(types)) if unique else types

    def types(self, unique=True) -> List[Type]:
        types = []
        for types_list in self.values():
            types += types_list

        return list(set(types)) if unique else types

    def unique(self) -> 'TypeCoverage':
        """
        Make a copy of the TypeCoverage with duplicate Type removed from the coverage map.
        :return: new TypeCoverage object
        """
        copy = self.copy()
        for k, v in copy:
            copy[k] = list(set(v))
        return copy

    def overlap(self, unique=True) -> 'TypeCoverage':
        """
        Make a copy of the TypeCoverage with only types that have duplicates. If unique=False
        then only 1 instance of a duplicate type will be removed from the coverage map, allowing
        the caller to tell how many times a type is duplicated (n+1).
        :param unique: If true (default), removes overlapping types from the list
        :return: new TypeCoverage object
        """
        copy = self.copy()
        copy -= self.unique()
        return copy.unique() if unique else copy

    def damage_effectiveness_from_type(self, move_type):
        no_damage = self[DamageRelation.NO_DAMAGE_FROM]
        half_damage = self[DamageRelation.HALF_DAMAGE_FROM]
        double_damage = self[DamageRelation.DOUBLE_DAMAGE_FROM]

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

    def effective_coverage(self):
        coverage = TypeCoverage()
        for damage_relation, types in self:
            if damage_relation in DamageRelation.damage_from():
                for type_ in types:
                    effectiveness = self.damage_effectiveness_from_type(type_)
                    if type_ not in coverage[effectiveness]:
                        coverage[effectiveness].append(type_)
            else:
                coverage[damage_relation] = list(set(types))
        return coverage.sorted()

    def effective_offensive_coverage(self):
        coverage = self.effective_coverage()
        for damage_relation in DamageRelation.damage_from():
            del coverage[damage_relation]
        return coverage

    def effective_defensive_coverage(self):
        coverage = self.effective_coverage()
        for damage_relation in DamageRelation.damage_to():
            del coverage[damage_relation]
        return coverage

    def sorted(self):
        for k, v in self:
            self[k] = sorted(v)
        return self

    def clear(self):
        self._coverage = {
            DamageRelation.NO_DAMAGE_TO: [],
            DamageRelation.QUARTER_DAMAGE_TO: [],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.NORMAL_DAMAGE_TO: [],
            DamageRelation.DOUBLE_DAMAGE_TO: [],
            DamageRelation.QUADRUPLE_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_FROM: [],
            DamageRelation.QUARTER_DAMAGE_FROM: [],
            DamageRelation.HALF_DAMAGE_FROM: [],
            DamageRelation.NORMAL_DAMAGE_FROM: [],
            DamageRelation.DOUBLE_DAMAGE_FROM: [],
            DamageRelation.QUADRUPLE_DAMAGE_FROM: []
        }

    def copy(self) -> 'TypeCoverage':
        coverage = self._coverage.copy()
        return TypeCoverage(coverage)

    def has_key(self, k):
        return k in self._coverage

    def update(self, *args, **kwargs) -> 'TypeCoverage':
        """
        Update underlying type coverage map with the provided args. Keys and arguments will
        be type checked, throwing TypeError if the key is not a DamageRelation or the values
        arent List[Type] (or empty list)
        :param args:
        :param kwargs:
        :return: self
        """
        tmp = self._coverage.copy()
        tmp.update(*args, **kwargs)
        for k, v in tmp.items():
            TypeCoverage._sanity_check_key(k)
            TypeCoverage._sanity_check_value(v)

        self._coverage.update(*args, **kwargs)
        return self.sorted()

    def keys(self):
        return self._coverage.keys()

    def values(self):
        return self._coverage.values()

    def items(self):
        return self._coverage.items()

    def pop(self, *args):
        raise NotImplementedError('TypeCoverage doesnt support this operation.')

    def __cmp__(self, dict_):
        raise NotImplementedError('TypeCoverage doesnt support this operation.')

    def __setitem__(self, key, val):
        TypeCoverage._sanity_check_key(key)
        TypeCoverage._sanity_check_value(val)
        self._coverage[key] = val

    def __getitem__(self, key):
        TypeCoverage._sanity_check_key(key)
        return self._coverage[key]

    def __delitem__(self, key):
        TypeCoverage._sanity_check_key(key)
        self._coverage[key] = []

    def __str__(self):
        offensive_table = [('{Power:bold}', '{Types:bold}')]
        defensive_table = [('{Power:bold}', '{Types:bold}')]
        for damage_relation in DamageRelation.damage_to():
            if len(self[damage_relation]) > 0:
                multiplier = damage_relation.multiplier(colorize=True)
                row = (multiplier, ', '.join([t.name for t in sorted(self[damage_relation])]))
                offensive_table.append(row)

        for damage_relation in DamageRelation.damage_from():
            if len(self[damage_relation]) > 0:
                multiplier = damage_relation.multiplier(colorize=True)
                row = (multiplier, ', '.join([t.name for t in sorted(self[damage_relation])]))
                defensive_table.append(row)

        template = ''
        template_data = {}
        if len(offensive_table) > 1:
            template += '''
            Offensive Type Effectiveness
            {offense:table}
            '''
            template_data['offense'] = offensive_table
        if len(defensive_table) > 1:
            template += '''
            Defensive Type Effectiveness
            {defense:table}
            '''
            template_data['defense'] = defensive_table

        return CliFormatter().format(template, **template_data)

        str_ = ''
        offensive_table = [('Power', 'Types')]
        defensive_table = [('Power', 'Types')]
        for damage_relation in DamageRelation.damage_to():
            if len(self[damage_relation]) > 0:
                multiplier = damage_relation.multiplier(colorize=True)
                row = (multiplier, ', '.join([t.name for t in sorted(coverage[damage_relation])]))
                row = (damage_relation.multiplier(), ', '.join([t.name for t in sorted(self[damage_relation])]))
                offensive_table.append(row)
        if len(offensive_table) > 1:
            str_ += '\nOffensive\n%s' % tabulate(offensive_table, first_row_header=True)

        for damage_relation in DamageRelation.damage_from():
            if len(self[damage_relation]) > 0:
                multiplier = damage_relation.multiplier(colorize=True)
                row = (damage_relation.multiplier(), ', '.join([t.name for t in sorted(self[damage_relation])]))
                defensive_table.append(row)
        if len(defensive_table) > 1:
            str_ += '\nDefensive\n%s' % tabulate(defensive_table, first_row_header=True)

        return str_

    def __repr__(self):
        return repr(self._coverage)

    def __len__(self):
        return len(self._coverage)

    def __contains__(self, item):
        return item in self._coverage

    def __iter__(self):
        return iter(self._coverage.items())

    def __unicode__(self):
        return repr(self._coverage)

    def __iadd__(self, other):
        other_type_coverage = TypeCoverage._type_coverage(other)
        combined = merge_dict_lists(self._coverage, other_type_coverage._coverage, dedupe=False)
        self.update(combined)
        return self

    def __add__(self, other):
        other_type_coverage = TypeCoverage._type_coverage(other)
        combined = merge_dict_lists(self._coverage, other_type_coverage._coverage, dedupe=False)
        return TypeCoverage(combined)

    def __isub__(self, other):
        other_type_coverage = TypeCoverage._type_coverage(other)
        for damage_relation, types in other_type_coverage:
            for t in types:
                self[damage_relation].remove(t)
        return self.sorted()

    def __sub__(self, other):
        type_coverage = self.copy()
        type_coverage.__isub__(other)
        return type_coverage.sorted()

    def __eq__(self, other):
        if type(other) is TypeCoverage:
            return self._coverage == other._coverage
        return False

    @staticmethod
    def _sanity_check_key(key):
        if not isinstance(key, DamageRelation):
            raise TypeError('TypeCoverage key must be of type DamageRelation, got \'%s\'' % type(key))

    @staticmethod
    def _sanity_check_value(val):
        if not isinstance(val, list):
            raise TypeError('TypeCoverage values must be empty list or list of Type, got \'%s\'' % type(val))
        if len(val) > 0:
            for i in val:
                if not isinstance(i, Type):
                    raise TypeError('TypeCoverage values must be empty list or list of Type, found type \'%s\' in list'
                                    % type(i))

    @staticmethod
    def _type_coverage(other):
        if isinstance(other, TypeCoverage):
            return other
        elif has_method(other, 'type_coverage', signature=Signature(return_annotation=TypeCoverage)):
            return other.type_coverage()
        else:
            raise TypeError('Cannot add object of type \'%s\' to TypeCoverage. Expected either a TypeCoverage or an \
            object that has a method signture of `type_coverage() -> TypeCoverage`' % type(other))
