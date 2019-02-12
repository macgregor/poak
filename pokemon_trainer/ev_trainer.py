# -*- coding: utf-8 -*-
# This file taken almost entirely from https://github.com/mathewbyrne/ev-tracker

import pokebase as pb

from .pokemon import *

EV_ITEMS = {
    'Macho Brace': lambda evs: evs * 2,
    'Power Weight': lambda evs: evs + StatSet(hp=4),
    'Power Bracer': lambda evs: evs + StatSet(attack=4),
    'Power Belt': lambda evs: evs + StatSet(defense=4),
    'Power Lens': lambda evs: evs + StatSet(special_attack=4),
    'Power Band': lambda evs: evs + StatSet(special_defense=4),
    'Power Anklet': lambda evs: evs + StatSet(speed=4)
}


class Pokemon(object):

    @classmethod
    def from_dict(cls, dict):
        dict['species'] = Species.search(dict['species'])
        dict['evs'] = StatSet(**dict['evs'])
        return cls(**dict)

    def to_dict(self):
        return {'species': self.species.id, 'name': self._name,
                'pokerus': self.pokerus, 'item': self.item,
                'evs': self.evs.to_dict(), 'id': self.id}

    def __init__(self, id, species, name=None, pokerus=False, item=None, evs=None):
        self.id = id
        self.species = species
        self._name = None
        self.name = name
        self.pokerus = pokerus
        self._item = None
        self.item = item
        self.evs = StatSet() if evs is None else evs

    name = property(lambda self: self.get_name(),
                    lambda self, name: self.set_name(name))

    item = property(lambda self: self._item,
                    lambda self, item: self.set_item(item))

    def __eq__(self, other):
        if type(other) is not Pokemon:
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_name(self):
        return self.species.name if self._name is None else self._name

    def set_name(self, name):
        if name is not None and len(name.strip()) > 0:
            self._name = name.strip()

    def set_item(self, item):
        if item is not None and item not in ITEMS:
            raise ValueError("Invalid item '%s'" % item)
        self._item = item if item is not None else None

    def __str__(self):
        name = self.name
        if self._name is not None:
            name = '%s (%s)' % (name, self.species.name)
        if self.id is None:
            return name
        else:
            return '%d %s' % (self.id, name)

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

    def battle(self, species, number=1):
        '''
        Alter's a tracked Pokemons EVs to simulate having battled a Species.
        These values are altered by pokerus and any item held. The EV
        increment can be multiplied by number to simulate multiple battles.
        '''
        evs = species.evs.clone()
        if self.item is not None:
            evs = ITEMS[self.item](evs)
        if self.pokerus:
            evs *= 2
        self.evs += evs * number


class EvTrainer(object):

    @classmethod
    def from_dict(cls, data):
        trainer = cls()
        for p in data['pokemon']:
            pokemon = Pokemon.from_dict(p)
            trainer.track(pokemon)
            if 'active' in data and pokemon.id in data['active']:
                trainer.add_active(pokemon)
        trainer.unique_id()

        return trainer

    def to_dict(self):
        data = {}
        if self.has_active():
            data['active'] = [p.id for p in self.active]
        data['pokemon'] = [pokemon.to_dict() for pokemon in self.pokemon.values()]
        return data

    def __init__(self):
        self._active = []
        self.counter = 1
        self.pokemon = {}

    active = property(lambda self: self.get_active(),
                      lambda self, pokemon: self.set_active(pokemon))

    def __eq__(self, other):
        if type(other) is not Trainer:
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def has_active(self):
        return self._active is not None and len(self._active) > 0

    def get_active(self):
        if self._active is None or len(self._active) < 1:
            raise NoActivePokemon()
        return self._active

    def set_active(self, pokemon):
        self._active = [pokemon]

    def add_active(self, pokemon):
        self._active.append(pokemon)

    def remove_active(self, pokemon):
        if pokemon in self._active:
            self._active.remove(pokemon)

    def get_pokemon(self, id):
        if id not in self.pokemon:
            raise NoTrackedPokemon(id)
        return self.pokemon[id]

    def unique_id(self):
        while self.counter in self.pokemon:
            self.counter += 1
        return self.counter

    def track(self, pokemon):
        self.pokemon[pokemon.id] = pokemon

    def untrack(self, pokemon):
        del self.pokemon[pokemon.id]
        pokemon.id = None
        self.remove_active(pokemon)

    def __str__(self):
        if len(self.pokemon):
            return '\n'.join([pokemon.listing(self._active) for pokemon in self.pokemon.values()])
        else:
            return 'No tracked Pokemon'

class NoActivePokemon(Exception):
    """
    Raised when an operation that assumes the existence of an active Pokemon
    is carried out.
    """
    pass


class NoTrackedPokemon(Exception):
    """
    Raised when an id is requested from a Tracker but the Tracker does not
    have a Pokemon with the provided id.
    """
    def __init__(self, id):
        super(NoTrackedPokemon, self).__init__()
        self.id = id
