#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import shutil
import httpretty

from pokemon_trainer import pokemon
from pokebase import api
from httpretty import httprettified

import logging
logging.basicConfig(level=logging.DEBUG)


class TestPokemonStatSet(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_stat_set_label(self):
        for i in range(0, len(pokemon.StatSet.STATS)):
            stat = pokemon.StatSet.STATS[i]
            label = pokemon.StatSet.LABELS[i]
            assert pokemon.StatSet.label(stat) == label

    def test_001_stat_set_plus_equal(self):
        ev1 = pokemon.StatSet(hp=1)
        ev2 = pokemon.StatSet(hp=2)
        ev1 += ev2
        assert ev1.hp == 3

    def test_002_stat_set_plus(self):
        ev1 = pokemon.StatSet(hp=1)
        ev2 = pokemon.StatSet(hp=2)
        ev3 = ev1 + ev2
        assert ev1.hp == 1
        assert ev2.hp == 2
        assert ev3.hp == 3

    def test_003_stat_set_times_equal(self):
        ev1 = pokemon.StatSet(hp=2)
        ev1 *= 3
        assert ev1.hp == 6

    def test_004_stat_set_times(self):
        ev1 = pokemon.StatSet(hp=2)
        ev2 = ev1 * 3
        assert ev1.hp == 2
        assert ev2.hp == 6

    def test_005_stat_set_equals(self):
        ev1 = pokemon.StatSet(hp=2)
        ev2 = pokemon.StatSet(hp=2)
        assert ev1 == ev2

    def test_006_stat_set_not_equals(self):
        ev1 = pokemon.StatSet(hp=1)
        ev2 = pokemon.StatSet(hp=2)
        assert ev1 != ev2

    def test_007_stat_set_clone(self):
        ev1 = pokemon.StatSet(hp=2)
        ev2 = ev1.clone()
        assert ev1 == ev2
        assert ev1 is not ev2

    def test__008_stat_set_to_dict(self):
        ev1 = pokemon.StatSet(hp=2)
        ev_dict = ev1.to_dict()
        excepted_dict = {
            'hp': 2,
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0
        }
        assert ev_dict == excepted_dict


class TestPokemonType(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_type_minimal(self):
        type_ = pokemon.Type(1, 'normal')
        assert type_.id == 1
        assert type_.name == 'normal'

        expected = {
            pokemon.DamageRelation.NO_DAMAGE_TO: [],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [],
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_FROM: [],
            pokemon.DamageRelation.HALF_DAMAGE_FROM: [],
            pokemon.DamageRelation.DOUBLE_DAMAGE_FROM: []
        }
        assert type_.damage_relations == expected

    def test_001_set_damage_relation(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, type_)
        assert type_.damage_relations[pokemon.DamageRelation.NO_DAMAGE_TO] == [type_]

    def test_002_set_damage_relation_doesnt_dupe(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, type_)
        type_.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, type_)
        assert type_.damage_relations[pokemon.DamageRelation.NO_DAMAGE_TO] == [type_]

    def test_003_damage_relation_to_type_exists(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, type_)
        assert type_.damage_relation_to_type(type_) == pokemon.DamageRelation.NO_DAMAGE_TO

    def test_004_damage_relation_to_type_doesnt_exists(self):
        type_ = pokemon.Type(1, 'normal')
        assert type_.damage_relation_to_type(type_) == pokemon.DamageRelation.NORMAL_DAMAGE_TO

    def test_005_damage_relation_from_type_exists(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.NORMAL_DAMAGE_FROM, type_)
        assert type_.damage_relation_from_type(type_) == pokemon.DamageRelation.NORMAL_DAMAGE_FROM

    def test_006_damage_relation_from_type_doesnt_exists(self):
        type_ = pokemon.Type(1, 'normal')
        assert type_.damage_relation_from_type(type_) == pokemon.DamageRelation.NORMAL_DAMAGE_FROM

    def test_007_to_dict(self):
        type_ = pokemon.Type(1, 'normal')
        assert type_.to_dict() == {'id': type_.id, 'name': type_.name}

    def test_008_equals(self):
        type1 = pokemon.Type(1, 'normal')
        type2 = pokemon.Type(1, 'normal')
        assert type1 == type2
        assert [type1] == [type2]
        assert type1 in [type2]
        assert type2 in [type1]

    def test_009_not_equals(self):
        type1 = pokemon.Type(1, 'normal')
        type2 = pokemon.Type(2, 'not normal')
        assert type1 != type2
        assert [type1] != [type2]
        assert type1 not in [type2]
        assert type2 not in [type1]

    @httprettified(allow_net_connect=False)
    def test_010_type_search(self):
        mock_pokeapi_calls()
        fighting = pokemon.Type(2, 'fighting')
        rock = pokemon.Type(6, 'rock')
        steel = pokemon.Type(9, 'steel')
        ghost = pokemon.Type(8, 'ghost')

        expected_damage_relations = {
            pokemon.DamageRelation.NO_DAMAGE_TO: [ghost],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [rock, steel],
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_FROM: [ghost],
            pokemon.DamageRelation.HALF_DAMAGE_FROM: [],
            pokemon.DamageRelation.DOUBLE_DAMAGE_FROM: [fighting]
        }

        type_ = pokemon.Type.search(1)
        for key, val in expected_damage_relations.items():
            assert key in type_.damage_relations
            assert val == type_.damage_relations[key]

    @httprettified(allow_net_connect=False)
    def test_011_from_dict(self):
        mock_pokeapi_calls()
        fighting = pokemon.Type(2, 'fighting')
        rock = pokemon.Type(6, 'rock')
        steel = pokemon.Type(9, 'steel')
        ghost = pokemon.Type(8, 'ghost')

        expected_damage_relations = {
            pokemon.DamageRelation.NO_DAMAGE_TO: [ghost],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [rock, steel],
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_FROM: [ghost],
            pokemon.DamageRelation.HALF_DAMAGE_FROM: [],
            pokemon.DamageRelation.DOUBLE_DAMAGE_FROM: [fighting]
        }

        type_ = pokemon.Type.from_dict({'id': 1, 'name': 'normal'})
        for key, val in expected_damage_relations.items():
            assert key in type_.damage_relations
            assert val == type_.damage_relations[key]

    @httprettified(allow_net_connect=False)
    def test_012_type_search_not_found(self):
        mock_pokeapi_calls()
        self.assertRaises(ValueError, pokemon.Species.search, 999)


class TestPokemonSpecies(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    @httprettified(allow_net_connect=False)
    def test_000_species_search(self):
        mock_pokeapi_calls()

        species = pokemon.Species.search(1)
        assert species.name == 'bulbasaur'
        assert species.id == 1
        assert species.evs == pokemon.StatSet(special_attack=1)
        assert species.types == [pokemon.Type(4, 'poison'), pokemon.Type(12, 'grass')]

    @httprettified(allow_net_connect=False)
    def test_001_species_search_not_found(self):
        mock_pokeapi_calls()
        self.assertRaises(ValueError, pokemon.Species.search, 999)

    def test_002_species_equals(self):
        s1 = pokemon.Species(1, 'bulbasaur')
        s2 = pokemon.Species(1, 'bulbasaur')
        assert s1 == s2
        assert [s1] == [s2]
        assert s1 in [s2]
        assert s2 in [s1]

    def test_003_species_not_equals(self):
        s1 = pokemon.Species(1, 'bulbasaur')
        s2 = pokemon.Species(2, 'ivysaur')
        assert s1 != s2
        assert [s1] != [s2]
        assert s1 not in [s2]
        assert s2 not in [s1]

    def test_004_species_damage_relation_single_type(self):
        for damage_relation in [pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM,
                                pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM]:
            t = pokemon.Type(1, damage_relation.name)
            t.set_damage_relation(damage_relation, t)
            s = pokemon.Species(1, 'bulbasaur', types=[t])
            assert s.damage_relation_from_type(t) == damage_relation

    def test_005_species_damage_relation_dual_type_no_damage(self):
        t1 = pokemon.Type(1, 'normal')
        t1.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_FROM, t1)

        for damage_relation in [pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM,
                                pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM]:
            t2 = pokemon.Type(2, 'flying')
            t2.set_damage_relation(damage_relation, t1)
            s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])
            assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.NO_DAMAGE_FROM

    def test_006_species_damage_relation_dual_type_quadruple_damage(self):
        t1 = pokemon.Type(1, 'normal')
        t1.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, t1)
        t2 = pokemon.Type(2, 'flying')
        t2.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, t1)
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])
        assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.QUADRUPLE_DAMAGE_FROM

    def test_007_species_damage_relation_dual_type_quarter_damage(self):
        t1 = pokemon.Type(1, 'normal')
        t1.set_damage_relation(pokemon.DamageRelation.HALF_DAMAGE_FROM, t1)
        t2 = pokemon.Type(2, 'flying')
        t2.set_damage_relation(pokemon.DamageRelation.HALF_DAMAGE_FROM, t1)
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])
        assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.QUARTER_DAMAGE_FROM

    def test_008_species_damage_relation_dual_type_normal_damage(self):
        permutations = [(pokemon.DamageRelation.HALF_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM),
                        (pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM),
                        (pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.NORMAL_DAMAGE_FROM

    def test_009_species_damage_relation_dual_type_double_damage(self):
        permutations = [(pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM),
                        (pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.DOUBLE_DAMAGE_FROM

    def test_010_species_damage_relation_dual_type_half_damage(self):
        permutations = [(pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM),
                        (pokemon.DamageRelation.HALF_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.HALF_DAMAGE_FROM

    def test_011_species_damage_relation_dual_type_no_damage(self):
        permutations = [(pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM),
                        (pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM),
                        (pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM),
                        (pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM),
                        (pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM),
                        (pokemon.DamageRelation.HALF_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM),
                        (pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert s.damage_relation_from_type(t1) == pokemon.DamageRelation.NO_DAMAGE_FROM

    def test_012_species_damage_relation_vulnerability(self):
        permutations = [(pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM),
                        (pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert t1 in s.vulnerabilities()
            assert s.is_vulnerable_to(t1)
            assert t1 not in s.resistances()
            assert not s.is_resistant_to(t1)
            assert t1 not in s.immunities()
            assert not s.is_immune_to(t1)

    def test_013_species_damage_relation_immunities(self):
        permutations = [(pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM),
                        (pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM),
                        (pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.DOUBLE_DAMAGE_FROM),
                        (pokemon.DamageRelation.NO_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM),
                        (pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM),
                        (pokemon.DamageRelation.HALF_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM),
                        (pokemon.DamageRelation.DOUBLE_DAMAGE_FROM, pokemon.DamageRelation.NO_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert t1 not in s.vulnerabilities()
            assert not s.is_vulnerable_to(t1)
            assert t1 not in s.resistances()
            assert not s.is_resistant_to(t1)
            assert t1 in s.immunities()
            assert s.is_immune_to(t1)

    def test_014_species_damage_relation_resistances(self):
        permutations = [(pokemon.DamageRelation.NORMAL_DAMAGE_FROM, pokemon.DamageRelation.HALF_DAMAGE_FROM),
                        (pokemon.DamageRelation.HALF_DAMAGE_FROM, pokemon.DamageRelation.NORMAL_DAMAGE_FROM)]

        t1 = pokemon.Type(1, 'normal')
        t2 = pokemon.Type(2, 'flying')
        s = pokemon.Species(1, 'bulbasaur', types=[t1, t2])

        for damage_relations in permutations:
            t1.reset_damage_relations()
            t1.set_damage_relation(damage_relations[0], t1)
            t2.reset_damage_relations()
            t2.set_damage_relation(damage_relations[1], t1)
            assert t1 not in s.vulnerabilities()
            assert not s.is_vulnerable_to(t1)
            assert t1 in s.resistances()
            assert s.is_resistant_to(t1)
            assert t1 not in s.immunities()
            assert not s.is_immune_to(t1)


class TestPokemonPokemon(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_pokemon_name_none_uses_species_name(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        assert p.name == 'bulbasaur'

    def test_001_pokemon_name_overrides_species_name(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s, nick_name='Boots')
        assert p.name == 'Boots'

    def test_002_pokemon_status_pokerus(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        assert 'Pokerus' not in p.status()
        p = pokemon.Pokemon(1, s, pokerus=True)
        assert 'Pokerus' in p.status()

    def test_003_pokemon_status_item(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s, item='Macho Brace')
        assert 'Macho Brace' in p.status()

    def test_004_pokemon_to_dict(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        d = p.to_dict()
        expected = {
            'id': 1,
            'species': 1,
            'nick_name': None,
            'pokerus': False,
            'item': None,
            'evs': pokemon.StatSet().to_dict(),
            'stats': pokemon.StatSet().to_dict(),
            'move_set': None
        }
        assert d == expected

    @httprettified(allow_net_connect=False)
    def test_005_pokemon_from_dict(self):
        mock_pokeapi_calls()

        expected = {
            'id': 1,
            'species': 1,
            'nick_name': 'Boots',
            'pokerus': False,
            'item': 'Macho Brace',
            'evs': pokemon.StatSet().to_dict(),
            'stats': pokemon.StatSet().to_dict(),
            'move_set': None
        }
        p = pokemon.Pokemon.from_dict(expected)
        assert p.name == 'Boots'
        assert p.item == 'Macho Brace'
        assert p.evs == pokemon.StatSet()
        assert p.stats == pokemon.StatSet()
        assert p.species.name == 'bulbasaur'
        assert p.species.id == 1
        assert p.species.evs == pokemon.StatSet(special_attack=1)

    def test_006_pokemon_to_string(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        assert '1' in str(p)
        assert 'bulbasaur' in str(p)

    def test_007_pokemon_to_string_nickname(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s, nick_name='Boots')
        assert 'Boots (bulbasaur)' in str(p)


class TestPokemonTeam(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_team_minimal(self):
        t = pokemon.Team(1, 'basic team')
        assert t.id == 1
        assert t.name == 'basic team'
        for pos in pokemon.TeamPosition:
            assert t.get_position(pos) is None

    def teast_001_team_with_pokemon(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        assert t.get_position(pokemon.TeamPosition.first) == p

    def test_002_team_not_full(self):
        t = pokemon.Team(1, 'basic team')
        assert not t.is_full()

    def test_003_team_full(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p, second=p, third=p, fourth=p, fifth=p, sixth=p)
        assert t.is_full()

    def test_004_set_position(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team')
        t.set_position(pokemon.TeamPosition.first, p)
        assert t.get_position(pokemon.TeamPosition.first) == p

    def test_005_team_ordered(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        assert t.team() == [p, None, None, None, None, None]

    def test_006_team_unordered(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        assert t.team(ordered=False) == [p]

    def test_006_team_get_position_type_checks(self):
        t = pokemon.Team(1, 'basic team')
        self.assertRaises(ValueError, t.get_position, 'foo')

    def test_007_team_get_position_accepts_ints(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        assert t.get_position(1) == p
        self.assertRaises(ValueError, t.get_position, -1)

    def test_008_team_set_position_type_checks(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team')
        self.assertRaises(ValueError, t.set_position, 'foo', p)

    def test_009_team_set_position_accepts_ints(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team')
        t.set_position(1, p)
        assert t.get_position(1) == p
        self.assertRaises(ValueError, t.set_position, -1, p)

    def test_010_team_to_dict(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        expected = {
            'id': 1,
            'name': 'basic team',
            'team': {
                'first': p.id,
                'second': None,
                'third': None,
                'fourth': None,
                'fifth': None,
                'sixth': None
            }
        }
        assert t.to_dict() == expected

    @httprettified(allow_net_connect=False)
    def test_011_team_from_dict(self):
        mock_pokeapi_calls()
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        data = t.to_dict()
        assert pokemon.Team.from_dict(data, [p]) == t

    def test_012_team_to_string(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        assert 'basic team' in str(t)
        assert '1: bulbasaur' in str(t)
        assert '2: Empty' in str(t)
        assert '3: Empty' in str(t)
        assert '4: Empty' in str(t)
        assert '5: Empty' in str(t)
        assert '6: Empty' in str(t)

    @httprettified(allow_net_connect=False)
    def test_013_team_from_dict_with_pokemon_list(self):
        mock_pokeapi_calls()
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t = pokemon.Team(1, 'basic team', first=p)
        data = t.to_dict()
        reloaded = pokemon.Team.from_dict(data, [p])
        reloaded.get_position(1).id = 2
        assert reloaded.get_position(1) is p
        assert reloaded.get_position(1).id == 2
        assert p.id == 2


class TestPokemonRoster(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_roster_minimal(self):
        r = pokemon.Roster()
        assert r.active_team() is None
        assert r.pokemon == {}
        assert r.teams == {}

    def test_001_roster_active_team(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t1 = pokemon.Team(1, 'basic team', first=p)
        t2 = pokemon.Team(2, 'another team', first=p)
        r = pokemon.Roster(pokemon=[p], teams=[t1, t2], active_team_id=1)
        assert r.active_team() == t1
        r.set_active_team(2)
        assert r.active_team() == t2
        r.set_active_team(None)
        assert r.active_team() is None

    def test_002_roster_add_team(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t1 = pokemon.Team(1, 'basic team', first=p)
        t2 = pokemon.Team(2, 'another team', first=p)
        r = pokemon.Roster(pokemon=[p], teams=[t1], active_team_id=1)
        r.add_team(t2)
        assert r.get_team(2) == t2

    def test_003_roster_remove_team(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t1 = pokemon.Team(1, 'basic team', first=p)
        t2 = pokemon.Team(2, 'another team', first=p)
        r = pokemon.Roster(pokemon=[p], teams=[t1, t2], active_team_id=1)
        r.remove_team(t2)
        assert r.active_team() is t1
        self.assertRaises(KeyError, r.get_team, 2)

    def test_004_roster_remove_team_resets_active_team_id(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t1 = pokemon.Team(1, 'basic team', first=p)
        t2 = pokemon.Team(2, 'another team', first=p)
        r = pokemon.Roster(pokemon=[p], teams=[t1, t2], active_team_id=2)
        r.remove_team(t2)
        assert r.active_team() is None
        self.assertRaises(KeyError, r.get_team, 2)

    def test_005_roster_add_pokemon(self):
        s = pokemon.Species(1, 'bulbasaur')
        p1 = pokemon.Pokemon(1, s)
        p2 = pokemon.Pokemon(2, s)
        t = pokemon.Team(1, 'basic team', first=p1)
        r = pokemon.Roster(pokemon=[p1], teams=[t], active_team_id=1)
        r.add_pokemon(p2)
        assert r.get_pokemon(2) == p2

    def test_006_roster_remove_pokemon(self):
        s = pokemon.Species(1, 'bulbasaur')
        p1 = pokemon.Pokemon(1, s)
        p2 = pokemon.Pokemon(2, s)
        t = pokemon.Team(1, 'basic team', first=p1, second=p2)
        r = pokemon.Roster(pokemon=[p1, p2], teams=[t], active_team_id=1)
        r.remove_pokemon(p2)
        self.assertRaises(KeyError, r.get_pokemon, 2)
        assert t.get_position(2) is None

    def test_007_roster_to_dict(self):
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t1 = pokemon.Team(1, 'basic team', first=p)
        r = pokemon.Roster(pokemon=[p], teams=[t1], active_team_id=1)
        expected = {
            'pokemon': [p.to_dict()],
            'teams': [t1.to_dict()],
            'active_team': 1
        }
        assert r.to_dict() == expected

    def test_008_roster_from_dict_empty(self):
        r = pokemon.Roster.from_dict({})
        assert r.active_team() is None
        assert r.pokemon == {}
        assert r.teams == {}

    @httprettified(allow_net_connect=False)
    def test_009_roster_from_dict(self):
        mock_pokeapi_calls()
        s = pokemon.Species(1, 'bulbasaur')
        p = pokemon.Pokemon(1, s)
        t1 = pokemon.Team(1, 'basic team', first=p)
        t2 = pokemon.Team(2, 'another team', first=p)
        r = pokemon.Roster(pokemon=[p], teams=[t1, t2], active_team_id=2)
        reloaded = pokemon.Roster.from_dict(r.to_dict())
        p_reloaded = reloaded.get_pokemon(1)

        assert r == reloaded
        assert reloaded.teams[1].get_position(1) is p_reloaded
        assert reloaded.teams[2].get_position(1) is p_reloaded


class TestPokemonMove(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_move_minimal(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.special
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        assert move.id == 1
        assert move.name == 'pound'
        assert move.damage_class == damage_class
        assert move.generation == generation

    def test_001_move_equals(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.special
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        assert move1 == move2
        assert [move1] == [move2]
        assert move1 in [move2]
        assert move2 in [move1]

    def test_002_move_not_equals(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.special
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'another move', damage_class, type_, generation)
        assert move1 != move2
        assert [move1] != [move2]
        assert move1 not in [move2]
        assert move2 not in [move1]

    def test_003_move_to_dict(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.special
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        expected = {
            'id': 1,
            'name': 'pound',
            'damage_class': 'special',
            'type': 'normal'
        }
        assert move.to_dict() == expected

    def test_004_move_to_string(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.special
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        assert 'pound (special, normal)' in str(move)

    @httprettified(allow_net_connect=False)
    def test_005_move_search(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
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
        expected = pokemon.Move(1, 'pound', damage_class, type_, generation, **meta)

        mock_pokeapi_calls()
        move = pokemon.Move.search(1)
        assert move == expected
        for k, v in meta.items():
            assert k in move.__dict__
            assert v == move.__dict__[k]

    @httprettified(allow_net_connect=False)
    def test_006_move_from_dict(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
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
        expected = pokemon.Move(1, 'pound', damage_class, type_, generation, **meta)

        mock_pokeapi_calls()
        move = pokemon.Move.from_dict(expected.to_dict())
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
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move)
        assert moveset.first == move

    def test_001_moveset_moves(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move)
        assert moveset.moves() == [move]

    def test_002_moveset_damage_classes(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move)
        print(moveset.damage_classes())
        assert moveset.damage_classes() == [damage_class]

    def test_003_moveset_damage_classes_dedupes(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move1, second=move2)
        assert moveset.damage_classes() == [damage_class]

    def test_004_moveset_damage_types(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move)
        assert moveset.damage_types() == [type_]

    def test_005_moveset_damage_types_dedupes(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move1, second=move2)
        assert moveset.damage_types() == [type_]

    def test_006_moveset_to_dict(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move1, second=move2)

        expected = {
            'first': move1.to_dict(),
            'second': move2.to_dict(),
            'third': None,
            'fourth': None
        }

        assert moveset.to_dict() == expected

    def test_007_moveset_equals(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset1 = pokemon.MoveSet(move)
        moveset2 = pokemon.MoveSet(move)
        assert moveset1 == moveset2
        assert [moveset1] == [moveset2]
        assert moveset1 in [moveset2]
        assert moveset2 in [moveset1]

    def test_008_moveset_not_equals(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'another move', damage_class, type_, generation)
        moveset1 = pokemon.MoveSet(move1)
        moveset2 = pokemon.MoveSet(move2)
        assert moveset1 != moveset2
        assert [moveset1] != [moveset2]
        assert moveset1 not in [moveset2]
        assert moveset2 not in [moveset1]

    @httprettified(allow_net_connect=False)
    def test_009_moveset_from_dict(self):
        mock_pokeapi_calls()
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move1 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move1, second=move2)

        reloaded = pokemon.MoveSet.from_dict(moveset.to_dict())
        assert reloaded == moveset

    def test_010_moveset_to_string(self):
        type_ = pokemon.Type(1, 'normal')
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move, second=move)
        assert '1. pound' in str(moveset)
        assert '2. pound' in str(moveset)
        assert '3. Empty' in str(moveset)
        assert '4. Empty' in str(moveset)

    def test_011_moveset_type_coverage_simple(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_TO, type_)
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move)
        expected = {
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_012_moveset_type_coverage_simple_dedupe(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_TO, type_)
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        moveset = pokemon.MoveSet(move, second=move)
        expected = {
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_012_moveset_type_coverage_simple_ignore_half_if_double(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_TO, type_)
        type2 = pokemon.Type(2, 'not normal')
        type2.set_damage_relation(pokemon.DamageRelation.HALF_DAMAGE_TO, type_)
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'not pound', damage_class, type2, generation)
        moveset = pokemon.MoveSet(move, second=move2)
        expected = {
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_013_moveset_type_coverage_simple_ignore_no_damage_if_double(self):
        type_ = pokemon.Type(1, 'normal')
        type_.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_TO, type_)
        type2 = pokemon.Type(2, 'not normal')
        type2.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, type_)
        damage_class = pokemon.DamageClass.physical
        generation = pokemon.Generation.generation_i
        move = pokemon.Move(1, 'pound', damage_class, type_, generation)
        move2 = pokemon.Move(2, 'not pound', damage_class, type2, generation)
        moveset = pokemon.MoveSet(move, second=move2)
        expected = {
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [type_],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [],
            pokemon.DamageRelation.NO_DAMAGE_TO: []
        }
        assert moveset.type_coverage() == expected

    def test_014_moveset_type_coverage_complex(self):
        normal = pokemon.Type(1, 'normal')
        ghost = pokemon.Type(2, 'ghost')
        rock = pokemon.Type(3, 'rock')
        steel = pokemon.Type(4, 'steel')
        dark = pokemon.Type(4, 'dark')
        psychic = pokemon.Type(4, 'psychic')

        normal.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, ghost)
        normal.set_damage_relation(pokemon.DamageRelation.HALF_DAMAGE_TO, rock)
        normal.set_damage_relation(pokemon.DamageRelation.HALF_DAMAGE_TO, steel)

        ghost.set_damage_relation(pokemon.DamageRelation.NO_DAMAGE_TO, normal)
        ghost.set_damage_relation(pokemon.DamageRelation.HALF_DAMAGE_TO, dark)
        ghost.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_TO, ghost)
        ghost.set_damage_relation(pokemon.DamageRelation.DOUBLE_DAMAGE_TO, psychic)

        generation = pokemon.Generation.generation_i
        pound = pokemon.Move(1, 'pound', pokemon.DamageClass.physical, normal, generation)
        night_shade = pokemon.Move(2, 'night_shade', pokemon.DamageClass.special, ghost, generation)
        moveset = pokemon.MoveSet(pound, second=night_shade)
        expected = {
            pokemon.DamageRelation.DOUBLE_DAMAGE_TO: [ghost, psychic],
            pokemon.DamageRelation.HALF_DAMAGE_TO: [dark, rock, steel],
            pokemon.DamageRelation.NO_DAMAGE_TO: [normal]
        }
        assert moveset.type_coverage() == expected



def setup_cache():
    try:
        shutil.rmtree(os.path.join(os.path.sep, 'tmp', 'pokemon-trainer', 'testing'))
    except FileNotFoundError:
        pass
    api.set_cache(os.path.join(os.path.sep, 'tmp', 'pokemon-trainer', 'testing'))


def test_resource(filename):
    return os.path.join(os.path.dirname(__file__), 'resources', filename)


def mock_pokeapi_calls():
    https_redirect('http://pokeapi.co/api/v2/pokemon', 200, test_resource('pokemon.json'))
    https_redirect('http://pokeapi.co/api/v2/pokemon/?limit=964', 200, test_resource('pokemon_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/ability', 200, test_resource('ability.json'))
    https_redirect('http://pokeapi.co/api/v2/ability/?limit=293', 200, test_resource('ability_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/pokemon-form', 200, test_resource('pokemon-form.json'))
    https_redirect('http://pokeapi.co/api/v2/pokemon-form/?limit=1123', 200, test_resource('pokemon-form_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/version', 200, test_resource('version.json'))
    https_redirect('http://pokeapi.co/api/v2/version/?limit=30', 200, test_resource('version_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/move', 200, test_resource('move.json'))
    https_redirect('http://pokeapi.co/api/v2/move/?limit=746', 200, test_resource('move_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/pokemon-species', 200, test_resource('pokemon-species.json'))
    https_redirect('http://pokeapi.co/api/v2/pokemon-species/?limit=807', 200, test_resource('pokemon-species_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/stat', 200, test_resource('stat.json'))
    https_redirect('http://pokeapi.co/api/v2/type', 200, test_resource('type.json'))
    https_redirect('http://pokeapi.co/api/v2/stat/speed', 200, test_resource('speed.json'))
    https_redirect('http://pokeapi.co/api/v2/characteristic', 200, test_resource('characteristic.json'))
    https_redirect('http://pokeapi.co/api/v2/characteristic/?limit=30', 200, test_resource('characteristic_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/language', 200, test_resource('language.json'))
    https_redirect('http://pokeapi.co/api/v2/stat/special-defense', 200, test_resource('special-defense.json'))
    https_redirect('http://pokeapi.co/api/v2/move-damage-class', 200, test_resource('move-damage-class.json'))
    https_redirect('http://pokeapi.co/api/v2/stat/special-attack', 200, test_resource('special-attack.json'))
    https_redirect('http://pokeapi.co/api/v2/stat/defense', 200, test_resource('defense.json'))
    https_redirect('http://pokeapi.co/api/v2/stat/attack', 200, test_resource('attack.json'))
    https_redirect('http://pokeapi.co/api/v2/stat/hp', 200, test_resource('hp.json'))
    https_redirect('http://pokeapi.co/api/v2/generation', 200, test_resource('generation.json'))
    https_redirect('http://pokeapi.co/api/v2/move/pound', 200, test_resource('pound.json'))
    https_redirect('http://pokeapi.co/api/v2/contest-effect', 200, test_resource('contest-effect.json'))
    https_redirect('http://pokeapi.co/api/v2/contest-effect/?limit=33', 200, test_resource('contest-effect_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/contest-type', 200, test_resource('contest-type.json'))
    https_redirect('http://pokeapi.co/api/v2/version-group', 200, test_resource('version-group.json'))
    https_redirect('http://pokeapi.co/api/v2/move-ailment', 200, test_resource('move-ailment.json'))
    https_redirect('http://pokeapi.co/api/v2/move-ailment/?limit=21', 200, test_resource('move-ailment_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/move-category', 200, test_resource('move-category.json'))
    https_redirect('http://pokeapi.co/api/v2/super-contest-effect', 200, test_resource('super-contest-effect.json'))
    https_redirect('http://pokeapi.co/api/v2/super-contest-effect/?limit=22', 200, test_resource('super-contest-effect_limit.json'))
    https_redirect('http://pokeapi.co/api/v2/move-target', 200, test_resource('move-target.json'))
    https_redirect('http://pokeapi.co/api/v2/move-damage-class/physical', 200, test_resource('physical.json'))
    https_redirect('http://pokeapi.co/api/v2/generation/generation-i', 200, test_resource('generation-i.json'))
    https_redirect('http://pokeapi.co/api/v2/region', 200, test_resource('region.json'))
    https_redirect('http://pokeapi.co/api/v2/type/grass', 200, test_resource('grass.json'))
    https_redirect('http://pokeapi.co/api/v2/type/poison', 200, test_resource('poison.json'))
    https_redirect('http://pokeapi.co/api/v2/type/normal', 200, test_resource('normal.json'))
    https_redirect('http://pokeapi.co/api/v2/pokemon/bulbasaur', 200, test_resource('bulbasaur.json'))
    https_redirect('http://pokeapi.co/api/v2/contest-effect/1', 200, test_resource('contest-effect-1.json'))
    https_redirect('http://pokeapi.co/api/v2/super-contest-effect/5', 200, test_resource('super-contest-effect-5.json'))
    https_redirect('http://pokeapi.co/api/v2/contest-type/tough', 200, test_resource('contest-type_tough.json'))
    https_redirect('http://pokeapi.co/api/v2/berry-flavor', 200, test_resource('berry-flavor.json'))
    https_redirect('http://pokeapi.co/api/v2/move-target/selected-pokemon', 200, test_resource('move-target-selected-pokemon.json'))


def https_redirect(url, status, body):
    target = url.replace('http://', 'https://')
    httpretty.register_uri(httpretty.GET, url, match_querystring=True, status=301, location=target)

    with open(body, encoding='utf8') as f:
        httpretty.register_uri(httpretty.GET, target, match_querystring=True, status=status, body=f.read())
