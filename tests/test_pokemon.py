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



