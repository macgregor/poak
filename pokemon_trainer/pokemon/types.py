# -*- coding: utf-8 -*-

from enum import Enum
from unicodedata import
import pokebase as pb

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
        self.update(**kwargs)

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

    def __repr__(self):
        return repr(self._coverage)

    def __len__(self):
        return len(self._coverage)

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

    def copy(self):
        coverage = self._coverage.copy()
        return TypeCoverage(**coverage)

    def has_key(self, k):
        return k in self._coverage

    def update(self, *args, **kwargs):
        tmp = self._coverage.copy()
        tmp.update(*args, **kwargs)
        for k, v in tmp:
            TypeCoverage._sanity_check_key(k)
            TypeCoverage._sanity_check_value(v)

        return self._coverage.update(*args, **kwargs)

    def keys(self):
        return self._coverage.keys()

    def values(self):
        return self._coverage.values()

    def items(self):
        return self._coverage.items()

    def pop(self, *args):
        raise NotImplementedError('TypeCoverage doesnt support this operation.')

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self._coverage

    def __iter__(self):
        return iter(self._coverage)

    def __unicode__(self):
        return repr(self._coverage)

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

    def __iadd__(self, other):
        if isinstance(other, TypeCoverage):
            self.update(other._coverage)
        elif type(other) in [Type, Move, MoveSet, Team]:
            self.update(other.type_coverage()._coverage)
        else:
            raise TypeError('Cannot add object of type \'%s\' to TypeCoverage. \
            Expected one of: Move, MoveSet, Type, Team, TypeCoverage' % type(other))
        return self

    def __add__(self, other):
        type_coverage = self.copy()
        if isinstance(other, TypeCoverage):
            type_coverage.update(other._coverage)
        elif type(other) in [Type, Move, MoveSet, Team]:
            type_coverage.update(other.type_coverage()._coverage)
        else:
            raise TypeError('Cannot add object of type \'%s\' to TypeCoverage. \
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
