# -*- coding: utf-8 -*-
import os
import shutil
import httpretty

from pokebase import api

import logging
logging.basicConfig(level=logging.DEBUG)


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