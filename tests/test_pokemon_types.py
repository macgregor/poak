#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os
from httpretty import httprettified
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

from pokemon_trainer.pokemon.types import *
from utils import *


class TestPokemonTypeCoverage(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_init_no_args(self):
        type_coverage = TypeCoverage()
        expected = {
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
        self.assertDictEqual(type_coverage._coverage, expected)

    def test_init_with_dict(self):
        types = [Type(1, 'normal')]
        expected = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        type_coverage = TypeCoverage(expected)
        self.assertDictEqual(type_coverage._coverage, expected)

    def test_setitem_empty(self):
        type_coverage = TypeCoverage()
        type_list = []
        for damage_relation in DamageRelation:
            type_coverage[damage_relation] = type_list
            self.assertEqual(type_coverage._coverage[damage_relation], type_list)

    def test_setitem_list(self):
        type_coverage = TypeCoverage()
        type_list = [Type(1, 'normal')]
        for damage_relation in DamageRelation:
            type_coverage[damage_relation] = [Type(1, 'normal')]
            self.assertEqual(type_coverage._coverage[damage_relation], type_list)

    def test_setitem_validates_key_is_damagerelation_type(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.__setitem__, 'foo', [])

    def test_setitem_validates_value_is_not_none(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.__setitem__, DamageRelation.NO_DAMAGE_TO, None)

    def test_setitem_validates_value_is_list(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.__setitem__, DamageRelation.NO_DAMAGE_TO, set())

    def test_setitem_validates_value_only_contains_types(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.__setitem__, DamageRelation.NO_DAMAGE_TO, [Type(1, 'normal'), 'foo'])

    def test_getitem(self):
        type_coverage = TypeCoverage()
        type_list = [Type(1, 'normal')]
        for damage_relation in DamageRelation:
            type_coverage[damage_relation] = [Type(1, 'normal')]
            self.assertEqual(type_coverage[damage_relation], type_list)

    def test_getitem_validates_key_is_damagerelation_type(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.__getitem__, 'foo')

    def test_delitem_resets_to_empty_list(self):
        types = [Type(1, 'normal')]
        expected = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        type_coverage = TypeCoverage(expected)
        for damage_relation in DamageRelation:
            del type_coverage[damage_relation]
            self.assertEqual(type_coverage[damage_relation], [])

    def test_delitem_validates_key_is_damagerelation_type(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.__delitem__, 'foo')

    def test_len(self):
        self.assertEqual(len(TypeCoverage()), len(DamageRelation))

    def test_repr(self):
        type_coverage = TypeCoverage()
        expected = {
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
        self.assertEqual(repr(type_coverage), repr(expected))

    def test_str(self):
        coverage = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal')]
        }
        type_coverage = TypeCoverage(coverage)
        expected = """
Offensive
-----  ------
Power  Types 
-----  ------
0x     normal
-----  ------

Defensive
-----  ------
Power  Types 
-----  ------
0x     normal
-----  ------
"""

        self.assertEqual(expected, str(type_coverage))


    def test_clear(self):
        types = [Type(1, 'normal')]
        expected = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        type_coverage = TypeCoverage(expected)
        type_coverage.clear()
        for damage_relation in DamageRelation:
            self.assertEqual(type_coverage[damage_relation], [])

    def test_copy(self):
        types = [Type(1, 'normal')]
        expected = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        original = TypeCoverage(expected)
        copy = original.copy()
        self.assertEqual(copy, original)
        assert copy is not original
        assert copy._coverage is not original._coverage

    def test_has_key(self):
        type_coverage = TypeCoverage()
        for damage_relation in DamageRelation:
            self.assertTrue(type_coverage.has_key(damage_relation))
        self.assertFalse(type_coverage.has_key('_coverage'))

    def test_update(self):
        types = [Type(1, 'normal')]
        expected = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        type_coverage = TypeCoverage()
        type_coverage.update(expected)
        self.assertEqual(type_coverage._coverage, expected)

    def test_update_validates_key(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.update, {'foo': 'bar'})

    def test_update_validates_value_is_not_none(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.update, {DamageRelation.NO_DAMAGE_TO: None})

    def test_update_validates_value_is_list(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.update, {DamageRelation.NO_DAMAGE_TO: set()})

    def test_update_validates_value_only_contains_types(self):
        type_coverage = TypeCoverage()
        self.assertRaises(TypeError, type_coverage.update, {DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal'), 'foo']})

    def test_keys(self):
        self.assertEqual(sorted(list(TypeCoverage().keys())), sorted(list(DamageRelation)))

    def test_values(self):
        expected = [[] for d in DamageRelation]
        self.assertEqual(list(TypeCoverage().values()), expected)

    def test_items(self):
        type_coverage = TypeCoverage()
        for k, v in type_coverage.items():
            assert k in list(DamageRelation)
            self.assertEqual(v, [])

    def test_iterator(self):
        type_coverage = TypeCoverage()
        for k, v in type_coverage:
            assert k in list(DamageRelation)
            self.assertEqual(v, [])

    def test_pop_raises_error(self):
        type_coverage = TypeCoverage()
        self.assertRaises(NotImplementedError, type_coverage.pop)

    def test_contains(self):
        type_coverage = TypeCoverage()
        for damage_relation in DamageRelation:
            self.assertTrue(type_coverage.__contains__(damage_relation))
        self.assertFalse(type_coverage.__contains__('_coverage'))

    def test_iadd(self):
        types = [Type(1, 'normal')]
        coverage = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        expected_types = [Type(1, 'normal'), Type(1, 'normal')]
        expected_coverage = {
            DamageRelation.NO_DAMAGE_TO: expected_types,
            DamageRelation.QUARTER_DAMAGE_TO: expected_types,
            DamageRelation.HALF_DAMAGE_TO: expected_types,
            DamageRelation.NORMAL_DAMAGE_TO: expected_types,
            DamageRelation.DOUBLE_DAMAGE_TO: expected_types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: expected_types,
            DamageRelation.NO_DAMAGE_FROM: expected_types,
            DamageRelation.QUARTER_DAMAGE_FROM: expected_types,
            DamageRelation.HALF_DAMAGE_FROM: expected_types,
            DamageRelation.NORMAL_DAMAGE_FROM: expected_types,
            DamageRelation.DOUBLE_DAMAGE_FROM: expected_types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: expected_types
        }
        type_coverage = TypeCoverage(coverage)
        other = TypeCoverage(coverage)
        original_ref = type_coverage
        type_coverage += other
        self.assertEqual(TypeCoverage(expected_coverage), type_coverage)
        assert type_coverage is original_ref

    def test_iadd_with_interface_class(self):
        type_coverage = TypeCoverage()
        types = [Type(1, 'normal')]
        expected = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        other = TypeCoverage(expected)
        original_ref = type_coverage
        type_coverage += MockTestCoverage(other)
        self.assertEqual(type_coverage, other)
        assert type_coverage is original_ref

    def test_add(self):
        types = [Type(1, 'normal')]
        coverage = {
            DamageRelation.NO_DAMAGE_TO: types,
            DamageRelation.QUARTER_DAMAGE_TO: types,
            DamageRelation.HALF_DAMAGE_TO: types,
            DamageRelation.NORMAL_DAMAGE_TO: types,
            DamageRelation.DOUBLE_DAMAGE_TO: types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: types,
            DamageRelation.NO_DAMAGE_FROM: types,
            DamageRelation.QUARTER_DAMAGE_FROM: types,
            DamageRelation.HALF_DAMAGE_FROM: types,
            DamageRelation.NORMAL_DAMAGE_FROM: types,
            DamageRelation.DOUBLE_DAMAGE_FROM: types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: types
        }
        expected_types = [Type(1, 'normal'), Type(1, 'normal')]
        expected_coverage = {
            DamageRelation.NO_DAMAGE_TO: expected_types,
            DamageRelation.QUARTER_DAMAGE_TO: expected_types,
            DamageRelation.HALF_DAMAGE_TO: expected_types,
            DamageRelation.NORMAL_DAMAGE_TO: expected_types,
            DamageRelation.DOUBLE_DAMAGE_TO: expected_types,
            DamageRelation.QUADRUPLE_DAMAGE_TO: expected_types,
            DamageRelation.NO_DAMAGE_FROM: expected_types,
            DamageRelation.QUARTER_DAMAGE_FROM: expected_types,
            DamageRelation.HALF_DAMAGE_FROM: expected_types,
            DamageRelation.NORMAL_DAMAGE_FROM: expected_types,
            DamageRelation.DOUBLE_DAMAGE_FROM: expected_types,
            DamageRelation.QUADRUPLE_DAMAGE_FROM: expected_types
        }
        type_coverage = TypeCoverage(coverage)
        other = TypeCoverage(coverage)
        original_ref = type_coverage
        original_other_ref = other

        new_type_coverage = type_coverage + other
        self.assertEqual(type_coverage, original_ref)
        self.assertEqual(original_other_ref, other)
        self.assertEqual(TypeCoverage(expected_coverage), new_type_coverage)
        self.assertTrue(type_coverage is original_ref)
        self.assertTrue(other is original_other_ref)
        self.assertTrue(new_type_coverage is not original_ref)
        self.assertTrue(new_type_coverage is not original_other_ref)

    def test_type_coverage_conversion_raises_error(self):
        self.assertRaises(TypeError, TypeCoverage._type_coverage, 'foo')

    def test_type_coverage_conversion_with_inteface_class_without_return_annotation(self):
        other = MockTestCoverageNoReturnAnnotation()
        self.assertRaises(TypeError, TypeCoverage._type_coverage, other)

    def test_type_coverage_conversion_with_inteface_class_with_wrong_method_signature(self):
        other = MockTestCoverageImproperMethodSignature()
        self.assertRaises(TypeError, TypeCoverage._type_coverage, other)

    def test_type_coverage_conversion_with_inteface_class_with_wrong_method_name(self):
        other = MockTestCoverageImproperMethodName()
        self.assertRaises(TypeError, TypeCoverage._type_coverage, other)

    def test_sub(self):
        expected = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal')],
            DamageRelation.QUARTER_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        original_ref = type_coverage
        other = type_coverage.copy()
        original_other_ref = other
        new_type_coverage = type_coverage - other
        self.assertEqual(new_type_coverage, TypeCoverage())
        self.assertTrue(original_ref is type_coverage)
        self.assertTrue(original_other_ref is other)
        self.assertTrue(new_type_coverage is not type_coverage)
        self.assertTrue(new_type_coverage is not other)

    def test_sub_only_removes_first(self):
        dupes = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.QUARTER_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon')],
        }
        no_dupes = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal')],
            DamageRelation.QUARTER_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(dupes)
        original_ref = type_coverage
        other = TypeCoverage(no_dupes)
        original_other_ref = other
        new_type_coverage = type_coverage - other
        self.assertEqual(new_type_coverage, TypeCoverage(no_dupes))
        self.assertTrue(original_ref is type_coverage)
        self.assertTrue(original_other_ref is other)
        self.assertTrue(new_type_coverage is not type_coverage)
        self.assertTrue(new_type_coverage is not other)

    def test_isub(self):
        expected = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal')],
            DamageRelation.QUARTER_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        original_ref = type_coverage
        other = type_coverage.copy()
        original_other_ref = other
        type_coverage -= other
        self.assertEqual(type_coverage, TypeCoverage())
        self.assertTrue(original_ref is type_coverage)
        self.assertTrue(original_other_ref is other)

    def test_isub_only_removes_first(self):
        dupes = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.QUARTER_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon')],
        }
        no_dupes = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal')],
            DamageRelation.QUARTER_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(dupes)
        original_ref = type_coverage
        other = TypeCoverage(no_dupes)
        original_other_ref = other
        type_coverage -= other
        self.assertEqual(type_coverage, TypeCoverage(no_dupes))
        self.assertTrue(original_ref is type_coverage)
        self.assertTrue(original_other_ref is other)

    def test_offensive_types(self):
        expected = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_FROM: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        self.assertEqual(type_coverage.offensive_types(), [Type(1, 'normal')])

    def test_offensive_types_dedupes(self):
        expected = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal'), Type(3, 'fire'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_FROM: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        self.assertEqual(type_coverage.offensive_types(), [Type(1, 'normal'), Type(3, 'fire')])
        self.assertEqual(type_coverage.offensive_types(unique=True), [Type(3, 'fire'), Type(1, 'normal')])

    def test_offensive_types_with_doesnt_dedupes(self):
        expected = {
            DamageRelation.NO_DAMAGE_TO: [Type(1, 'normal'), Type(3, 'fire'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_FROM: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        self.assertEqual(type_coverage.offensive_types(unique=False), [Type(3, 'fire'), Type(1, 'normal'), Type(1, 'normal')])

    def test_defensive_types(self):
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        self.assertTrue(type_coverage.defensive_types() == [Type(1, 'normal')])

    def test_defensive_types_dedupes(self):
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(3, 'fire'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        self.assertEqual(type_coverage.defensive_types(), [Type(1, 'normal'), Type(3, 'fire')])
        self.assertEqual(type_coverage.defensive_types(unique=True), [Type(3, 'fire'), Type(1, 'normal')])

    def test_defensive_types_with_doesnt_dedupe(self):
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(3, 'fire'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        type_coverage = TypeCoverage(expected)
        self.assertEqual(type_coverage.defensive_types(unique=False), [Type(3, 'fire'), Type(1, 'normal'), Type(1, 'normal')])

    def test_unique(self):
        starting = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon')],
        }
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        self.assertEqual(TypeCoverage(starting).unique(), TypeCoverage(expected))

    def test_overlap_no_overlap(self):
        starting = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        self.assertEqual(TypeCoverage(starting).overlap(), TypeCoverage())

    def test_overlap_doubles(self):
        starting = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon')],
        }
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        self.assertEqual(TypeCoverage(starting).overlap(), TypeCoverage(expected))

    def test_overlap_triples(self):
        starting = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon'), Type(2, 'dragon')],
        }
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon')],
        }
        self.assertEqual(TypeCoverage(starting).overlap(), TypeCoverage(expected))

    def test_overlap_triples_doesnt_dedupe(self):
        starting = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon'), Type(2, 'dragon')],
        }
        expected = {
            DamageRelation.NO_DAMAGE_FROM: [Type(1, 'normal'), Type(1, 'normal')],
            DamageRelation.NO_DAMAGE_TO: [Type(2, 'dragon'), Type(2, 'dragon')],
        }
        self.assertEqual(TypeCoverage(starting).overlap(unique=False), TypeCoverage(expected))


class TestPokemonType(unittest.TestCase):
    """Tests for `pokemon_trainer` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        setup_cache()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_type_minimal(self):
        type_ = Type(1, 'normal')
        assert type_.id == 1
        assert type_.name == 'normal'

        expected = {
            DamageRelation.NO_DAMAGE_TO: [],
            DamageRelation.HALF_DAMAGE_TO: [],
            DamageRelation.DOUBLE_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_FROM: [],
            DamageRelation.HALF_DAMAGE_FROM: [],
            DamageRelation.DOUBLE_DAMAGE_FROM: []
        }
        assert type_.damage_relations == expected

    def test_001_set_damage_relation(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.NO_DAMAGE_TO, type_)
        assert type_.damage_relations[DamageRelation.NO_DAMAGE_TO] == [type_]

    def test_002_set_damage_relation_doesnt_dupe(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.NO_DAMAGE_TO, type_)
        type_.set_damage_relation(DamageRelation.NO_DAMAGE_TO, type_)
        assert type_.damage_relations[DamageRelation.NO_DAMAGE_TO] == [type_]

    def test_003_damage_relation_to_type_exists(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.NO_DAMAGE_TO, type_)
        assert type_.damage_relation_to_type(type_) == DamageRelation.NO_DAMAGE_TO

    def test_004_damage_relation_to_type_doesnt_exists(self):
        type_ = Type(1, 'normal')
        assert type_.damage_relation_to_type(type_) == DamageRelation.NORMAL_DAMAGE_TO

    def test_005_damage_relation_from_type_exists(self):
        type_ = Type(1, 'normal')
        type_.set_damage_relation(DamageRelation.NORMAL_DAMAGE_FROM, type_)
        assert type_.damage_relation_from_type(type_) == DamageRelation.NORMAL_DAMAGE_FROM

    def test_006_damage_relation_from_type_doesnt_exists(self):
        type_ = Type(1, 'normal')
        assert type_.damage_relation_from_type(type_) == DamageRelation.NORMAL_DAMAGE_FROM

    def test_007_to_dict(self):
        type_ = Type(1, 'normal')
        assert type_.to_dict() == {'id': type_.id, 'name': type_.name}

    def test_008_equals(self):
        type1 = Type(1, 'normal')
        type2 = Type(1, 'normal')
        assert type1 == type2
        assert [type1] == [type2]
        assert type1 in [type2]
        assert type2 in [type1]

    def test_009_not_equals(self):
        type1 = Type(1, 'normal')
        type2 = Type(2, 'not normal')
        assert type1 != type2
        assert [type1] != [type2]
        assert type1 not in [type2]
        assert type2 not in [type1]

    @httprettified(allow_net_connect=False)
    def test_010_type_search(self):
        mock_pokeapi_calls()
        fighting = Type(2, 'fighting')
        rock = Type(6, 'rock')
        steel = Type(9, 'steel')
        ghost = Type(8, 'ghost')

        expected_damage_relations = {
            DamageRelation.NO_DAMAGE_TO: [ghost],
            DamageRelation.HALF_DAMAGE_TO: [rock, steel],
            DamageRelation.DOUBLE_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_FROM: [ghost],
            DamageRelation.HALF_DAMAGE_FROM: [],
            DamageRelation.DOUBLE_DAMAGE_FROM: [fighting]
        }

        type_ = Type.search(1)
        for key, val in expected_damage_relations.items():
            assert key in type_.damage_relations
            assert val == type_.damage_relations[key]

    @httprettified(allow_net_connect=False)
    def test_011_from_dict(self):
        mock_pokeapi_calls()
        fighting = Type(2, 'fighting')
        rock = Type(6, 'rock')
        steel = Type(9, 'steel')
        ghost = Type(8, 'ghost')

        expected_damage_relations = {
            DamageRelation.NO_DAMAGE_TO: [ghost],
            DamageRelation.HALF_DAMAGE_TO: [rock, steel],
            DamageRelation.DOUBLE_DAMAGE_TO: [],
            DamageRelation.NO_DAMAGE_FROM: [ghost],
            DamageRelation.HALF_DAMAGE_FROM: [],
            DamageRelation.DOUBLE_DAMAGE_FROM: [fighting]
        }

        type_ = Type.from_dict({'id': 1, 'name': 'normal'})
        for key, val in expected_damage_relations.items():
            assert key in type_.damage_relations
            assert val == type_.damage_relations[key]

    @httprettified(allow_net_connect=False)
    def test_012_type_search_not_found(self):
        mock_pokeapi_calls()
        self.assertRaises(ValueError, pokemon.Species.search, 999)


class MockTestCoverage(object):
    def __init__(self, coverage=None):
        self.coverage = TypeCoverage() if coverage is None else coverage

    def type_coverage(self) -> TypeCoverage:
        return self.coverage


class MockTestCoverageNoReturnAnnotation(object):
    def __init__(self, coverage=None):
        self.coverage = TypeCoverage() if coverage is None else coverage

    def type_coverage(self):
        return self.coverage


class MockTestCoverageImproperMethodSignature(object):
    def __init__(self, coverage=None):
        self.coverage = TypeCoverage() if coverage is None else coverage

    def type_coverage(self, foo):
        return self.coverage


class MockTestCoverageImproperMethodName(object):
    def __init__(self, coverage=None):
        self.coverage = TypeCoverage() if coverage is None else coverage

    def typo_coverage(self) -> TypeCoverage:
        return self.coverage