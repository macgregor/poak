#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

from pokemon_trainer.pokemon.types import *
from pokemon_trainer.pokemon.moves import *
from pokemon_trainer.pokemon.versions import *
from pokemon_trainer.pokemon.teams import *
from pokemon_trainer.pokemon.pokedex import *
from httpretty import httprettified


class TestPokemonMove(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_move_minimal(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.special
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        assert move.id == 1
        assert move.name == 'pound'
        assert move.damage_class == damage_class
        assert move.generation == generation

    def test_001_move_equals(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.special
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(1, 'pound', damage_class, type_, generation)
        assert move1 == move2
        assert [move1] == [move2]
        assert move1 in [move2]
        assert move2 in [move1]

    def test_002_move_not_equals(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.special
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'another move', damage_class, type_, generation)
        assert move1 != move2
        assert [move1] != [move2]
        assert move1 not in [move2]
        assert move2 not in [move1]

    def test_003_move_to_dict(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.special
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        expected = {
            'id': 1,
            'name': 'pound',
            'damage_class': 'special',
            'type': 'normal'
        }
        assert move.to_dict() == expected

    def test_004_move_to_string(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.special
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        assert 'pound (special, normal)' in str(move)

    @httprettified(allow_net_connect=False)
    def test_005_move_search(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        meta = {
            'accuracy': 100,
            'effect_chance': None,
            'effect_entries': ['Inflicts regular damage.'],
            'crit_rate': 0,
            'drain': 0,
            'flinch_chance': 0,
            'healing': 0,
            'max_hits': None,
            'max_turns': None,
            'min_hits': None,
            'min_turns': None,
            'stat_chance': 0,
            'power': 40,
            'pp': 35
        }
        expected = Move(1, 'pound', damage_class, type_, generation, **meta)

        mock_pokeapi_calls()
        move = Move.search(1)
        assert move == expected
        for k, v in meta.items():
            assert k in move.__dict__
            assert v == move.__dict__[k]

    @httprettified(allow_net_connect=False)
    def test_006_move_from_dict(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        meta = {
            'accuracy': 100,
            'effect_chance': None,
            'effect_entries': ['Inflicts regular damage.'],
            'crit_rate': 0,
            'drain': 0,
            'flinch_chance': 0,
            'healing': 0,
            'max_hits': None,
            'max_turns': None,
            'min_hits': None,
            'min_turns': None,
            'stat_chance': 0,
            'power': 40,
            'pp': 35
        }
        expected = Move(1, 'pound', damage_class, type_, generation, **meta)

        mock_pokeapi_calls()
        move = Move.from_dict(expected.to_dict())
        assert move == expected
        for k, v in meta.items():
            assert k in move.__dict__
            assert v == move.__dict__[k]


class TestPokemonMoveSet(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_moveset_minimal(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move)
        assert moveset.first == move

    def test_001_moveset_moves(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move)
        assert moveset.moves() == [move]

    def test_002_moveset_damage_classes(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move)
        print(moveset.damage_classes())
        assert moveset.damage_classes() == [damage_class]

    def test_003_moveset_damage_classes_dedupes(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move1, second=move2)
        assert moveset.damage_classes() == [damage_class]

    def test_004_moveset_damage_types(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move)
        assert moveset.damage_types() == [type_]

    def test_005_moveset_damage_types_dedupes(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move1, second=move2)
        assert moveset.damage_types() == [type_]

    def test_006_moveset_to_dict(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move1, second=move2)

        expected = {
            'first': move1.to_dict(),
            'second': move2.to_dict(),
            'third': None,
            'fourth': None
        }

        assert moveset.to_dict() == expected

    def test_007_moveset_equals(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset1 = MoveSet(move)
        moveset2 = MoveSet(move)
        assert moveset1 == moveset2
        assert [moveset1] == [moveset2]
        assert moveset1 in [moveset2]
        assert moveset2 in [moveset1]

    def test_008_moveset_not_equals(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'another move', damage_class, type_, generation)
        moveset1 = MoveSet(move1)
        moveset2 = MoveSet(move2)
        assert moveset1 != moveset2
        assert [moveset1] != [moveset2]
        assert moveset1 not in [moveset2]
        assert moveset2 not in [moveset1]

    @httprettified(allow_net_connect=False)
    def test_009_moveset_from_dict(self):
        mock_pokeapi_calls()
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move1 = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move1, second=move2)

        reloaded = MoveSet.from_dict(moveset.to_dict())
        assert reloaded == moveset

    def test_010_moveset_to_string(self):
        type_ = Type(1, 'normal')
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move, second=move)
        assert '1. pound' in str(moveset)
        assert '2. pound' in str(moveset)
        assert '3. Empty' in str(moveset)
        assert '4. Empty' in str(moveset)

    def test_011_moveset_type_coverage_simple(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.DOUBLE_DAMAGE_TO, type_)
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move)
        expected = {
            DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_012_moveset_type_coverage_simple_dedupe(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.DOUBLE_DAMAGE_TO, type_)
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        moveset = MoveSet(move, second=move)
        expected = {
            DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_012_moveset_type_coverage_simple_ignore_half_if_double(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.DOUBLE_DAMAGE_TO, type_)
        type2 = Type(2, 'not normal')
        type2.set_damage_relation(DamageRelation.HALF_DAMAGE_TO, type_)
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'not pound', damage_class, type2, generation)
        moveset = MoveSet(move, second=move2)
        expected = {
            DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_013_moveset_type_coverage_simple_ignore_no_damage_if_double(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.DOUBLE_DAMAGE_TO, type_)
        type2 = Type(2, 'not normal')
        type2.set_damage_relation(DamageRelation.NO_DAMAGE_TO, type_)
        damage_class = DamageClass.physical
        generation = Generation.generation_i
        move = Move(1, 'pound', damage_class, type_, generation)
        move2 = Move(2, 'not pound', damage_class, type2, generation)
        moveset = MoveSet(move, second=move2)
        expected = {
            DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_014_moveset_type_coverage_complex(self):
        normal = Type(1, 'normal')
        ghost = Type(2, 'ghost')
        rock = Type(3, 'rock')
        steel = Type(4, 'steel')
        dark = Type(4, 'dark')
        psychic = Type(4, 'psychic')

        normal.set_damage_relation(DamageRelation.NO_DAMAGE_TO, ghost)
        normal.set_damage_relation(DamageRelation.HALF_DAMAGE_TO, rock)
        normal.set_damage_relation(DamageRelation.HALF_DAMAGE_TO, steel)

        ghost.set_damage_relation(DamageRelation.NO_DAMAGE_TO, normal)
        ghost.set_damage_relation(DamageRelation.HALF_DAMAGE_TO, dark)
        ghost.set_damage_relation(DamageRelation.DOUBLE_DAMAGE_TO, ghost)
        ghost.set_damage_relation(DamageRelation.DOUBLE_DAMAGE_TO, psychic)

        generation = Generation.generation_i
        pound = Move(1, 'pound', DamageClass.physical, normal, generation)
        night_shade = Move(2, 'night_shade', DamageClass.special, ghost, generation)
        moveset = MoveSet(pound, second=night_shade)
        expected = {
            DamageRelation.DOUBLE_DAMAGE_TO: [ghost, psychic],
            DamageRelation.HALF_DAMAGE_TO: [dark, rock, steel],
            DamageRelation.NO_DAMAGE_TO: [normal]
        }
        assert moveset.type_coverage() == expected