# -*- coding: utf-8 -*-

from enum import Enum
import pokebase as pb
import textwrap


class DamageClass(Enum):
    status = 1
    physical = 2
    special = 3


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
