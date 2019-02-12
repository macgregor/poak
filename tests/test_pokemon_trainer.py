#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pokemon_trainer` package."""


import unittest
import httpretty
from httpretty import httprettified
import os
import shutil

from pokemon_trainer import ev_trainer
from pokebase import api


class TestPokemonTrainerTrainer(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

        api.set_cache(os.path.join(os.path.sep, 'tmp', 'pokemon-trainer', 'testing'))

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(os.path.join(os.path.sep, 'tmp', 'pokemon-trainer', 'testing'))

    def test_000_trainer_has_active(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        t.active = p
        assert t.has_active()

    def test_001_trainer_no_active(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        assert not t.has_active()

    def test_002_trainer_get_active(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        t.active = p
        assert t.active == [p]
        assert t.get_active() == [p]

    def test_003_trainer_no_active_raises_error(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        self.assertRaises(pokemon_trainer.NoActivePokemon, t.get_active)

    def test_004_trainer_add_active(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        p2 = pokemon_trainer.Pokemon(2, s)
        t = pokemon_trainer.Trainer()
        t.add_active(p)
        t.add_active(p2)
        assert t.active == [p, p2]
        assert t.get_active() == [p, p2]

    def test_005_trainer_track_pokemon(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        t.track(p)
        assert t.get_position(p.id) == p

    def test_006_trainer_untrack_pokemon(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        t.track(p)
        assert t.get_position(p.id) == p
        t.untrack(p)
        self.assertRaises(pokemon_trainer.NoTrackedPokemon, t.get_position, p.id)

    def test_007_trainer_untrack_pokemon_removes_active(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        t.track(p)
        t.active = p
        assert p in t.active
        t.untrack(p)
        self.assertRaises(pokemon_trainer.NoActivePokemon, t.get_active)

    def test_008_trainer_unique_id(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        t = pokemon_trainer.Trainer()
        t.track(p)
        assert t.unique_id() == p.id+1

    def test_009_trainer_to_dict_blank(self):
        t = pokemon_trainer.Trainer()
        d = t.to_dict()
        assert d == {'pokemon': []}

    def test_010_trainer_to_dict_with_tracked(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        p2 = pokemon_trainer.Pokemon(2, s)
        t = pokemon_trainer.Trainer()
        t.track(p)
        t.track(p2)
        d = t.to_dict()
        expected = {'pokemon': [p.to_dict(), p2.to_dict()]}
        assert d == expected

    def test_011_trainer_to_dict_with_active(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        p2 = pokemon_trainer.Pokemon(2, s)
        t = pokemon_trainer.Trainer()
        t.track(p)
        t.track(p2)
        t.add_active(p)
        t.add_active(p2)
        d = t.to_dict()
        expected = {'pokemon': [p.to_dict(), p2.to_dict()], 'active': [p.id, p2.id]}
        assert d == expected

    def test_012_trainer_from_dict_blank(self):
        t = pokemon_trainer.Trainer.from_dict({'pokemon': []})
        assert t == pokemon_trainer.Trainer()

    @httprettified(allow_net_connect=False)
    def test_013_trainer_from_dict_with_tracked(self):
        mock_bulbasaur_calls()
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        p2 = pokemon_trainer.Pokemon(2, s)
        data = {'pokemon': [p.to_dict(), p2.to_dict()]}

        expected = pokemon_trainer.Trainer()
        expected.track(p)
        expected.track(p2)
        expected.counter = 3

        actual = pokemon_trainer.Trainer.from_dict(data)
        print(actual)
        assert actual == expected

    @httprettified(allow_net_connect=False)
    def test_014_trainer_from_dict_with_active(self):
        mock_bulbasaur_calls()
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        p2 = pokemon_trainer.Pokemon(2, s)
        data = {'pokemon': [p.to_dict(), p2.to_dict()], 'active': [p.id, p2.id]}

        expected = pokemon_trainer.Trainer()
        expected.track(p)
        expected.track(p2)
        expected.add_active(p)
        expected.add_active(p2)
        expected.counter = 3

        actual = pokemon_trainer.Trainer.from_dict(data)
        assert actual == expected

    def test_006_pokemon_battle(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == s.evs

    def test_007_pokemon_battle_pokerus(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, pokerus=True)
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs*2)

    def test_008_pokemon_battle_macho_brace(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Macho Brace')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs*2)

    def test_009_pokemon_battle_power_weight(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Power Weight')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs + pokemon_trainer.StatSet(hp=4))

    def test_010_pokemon_battle_power_bracers(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Power Bracer')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs + pokemon_trainer.StatSet(attack=4))

    def test_011_pokemon_battle_power_belt(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Power Belt')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs + pokemon_trainer.StatSet(defense=4))

    def test_012_pokemon_battle_power_lens(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Power Lens')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs + pokemon_trainer.StatSet(special_attack=4))

    def test_013_pokemon_battle_power_band(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Power Band')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs + pokemon_trainer.StatSet(special_defense=4))

    def test_014_pokemon_battle_power_anklet(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, item='Power Anklet')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == (s.evs + pokemon_trainer.StatSet(speed=4))

    def test_015_pokemon_battle_pokerus_and_item(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s, pokerus=True, item='Power Anklet')
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s)
        assert p.evs == ((s.evs + pokemon_trainer.StatSet(speed=4)) * 2)

    def test_016_pokemon_battle_multi(self):
        s = pokemon_trainer.Species(1, 'bulbasaur')
        p = pokemon_trainer.Pokemon(1, s)
        assert p.evs == pokemon_trainer.StatSet()
        p.battle(s, 2)
        assert p.evs == (s.evs*2)


def mock_bulbasaur_calls():
    https_redirect('http://pokeapi.co/api/v2/pokemon', 200, 'tests/resources/pokemon.json')
    https_redirect('http://pokeapi.co/api/v2/pokemon/?limit=964', 200, 'tests/resources/pokemon_limit.json')
    https_redirect('http://pokeapi.co/api/v2/pokemon/bulbasaur', 200, 'tests/resources/bulbasaur.json')
    https_redirect('http://pokeapi.co/api/v2/ability', 200, 'tests/resources/ability.json')
    https_redirect('http://pokeapi.co/api/v2/ability/?limit=293', 200, 'tests/resources/ability_limit.json')
    https_redirect('http://pokeapi.co/api/v2/pokemon-form', 200, 'tests/resources/pokemon-form.json')
    https_redirect('http://pokeapi.co/api/v2/pokemon-form/?limit=1123', 200, 'tests/resources/pokemon-form_limit.json')
    https_redirect('http://pokeapi.co/api/v2/version', 200, 'tests/resources/version.json')
    https_redirect('http://pokeapi.co/api/v2/version/?limit=30', 200, 'tests/resources/version_limit.json')
    https_redirect('http://pokeapi.co/api/v2/move', 200, 'tests/resources/move.json')
    https_redirect('http://pokeapi.co/api/v2/move/?limit=746', 200, 'tests/resources/move_limit.json')
    https_redirect('http://pokeapi.co/api/v2/pokemon-species', 200, 'tests/resources/pokemon-species.json')
    https_redirect('http://pokeapi.co/api/v2/pokemon-species/?limit=807', 200, 'tests/resources/pokemon-species_limit.json')
    https_redirect('http://pokeapi.co/api/v2/stat', 200, 'tests/resources/stat.json')
    https_redirect('http://pokeapi.co/api/v2/type', 200, 'tests/resources/type.json')
    https_redirect('http://pokeapi.co/api/v2/stat/speed', 200, 'tests/resources/speed.json')
    https_redirect('http://pokeapi.co/api/v2/characteristic', 200, 'tests/resources/characteristic.json')
    https_redirect('http://pokeapi.co/api/v2/characteristic/?limit=30', 200, 'tests/resources/characteristic_limit.json')
    https_redirect('http://pokeapi.co/api/v2/language', 200, 'tests/resources/language.json')
    https_redirect('http://pokeapi.co/api/v2/stat/special-defense', 200, 'tests/resources/special-defense.json')
    https_redirect('http://pokeapi.co/api/v2/move-damage-class', 200, 'tests/resources/move-damage-class.json')
    https_redirect('http://pokeapi.co/api/v2/stat/special-attack', 200, 'tests/resources/special-attack.json')
    https_redirect('http://pokeapi.co/api/v2/stat/defense', 200, 'tests/resources/defense.json')
    https_redirect('http://pokeapi.co/api/v2/stat/attack', 200, 'tests/resources/attack.json')
    https_redirect('http://pokeapi.co/api/v2/stat/hp', 200, 'tests/resources/hp.json')


def https_redirect(url, status, body):
    target = url.replace('http://', 'https://')
    httpretty.register_uri(httpretty.GET, url, match_querystring=True, status=301, location=target)

    with open(body) as f:
        httpretty.register_uri(httpretty.GET, target, match_querystring=True, status=status, body=f.read())