"""Unit tests for selectors.

"""

import broom
import unittest

class SelectorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        fields = {
                'a': broom.types.SelectorField(name='a', weight=0),
                'b': broom.types.SelectorField(name='b', weight=1),
                'c': broom.types.SelectorField(name='c', weight=1),
                'd': broom.types.SelectorField(name='d', weight=2)
                }

        u = broom.types.SelectorUnion
        i = broom.types.SelectorIntersect
        e = broom.types.SelectorEquals

        selectors = {
            broom.types.Selector(
                name='a',
                root_node=e(selector_field=fields['a'], value='a')
                ),
            broom.types.Selector(
                name='a_b',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['b'], value='b')
                        ]
                    )
                ),
            broom.types.Selector(
                name='a_c',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['c'], value='c'),
                        ]
                    )
                ),
            broom.types.Selector(
                name='a_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='a_b_c',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['b'], value='b'),
                        e(selector_field=fields['c'], value='c')
                        ]
                    )
                ),
            broom.types.Selector(
                name='a_b_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['b'], value='b'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='a_c_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['c'], value='c'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='a_b_c_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['a'], value='a'),
                        e(selector_field=fields['b'], value='b'),
                        e(selector_field=fields['c'], value='c'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='b',
                root_node=e(selector_field=fields['b'], value='b')
                ),
            broom.types.Selector(
                name='b_c',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['b'], value='b'),
                        e(selector_field=fields['c'], value='c')
                        ]
                    )
                ),
            broom.types.Selector(
                name='b_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['b'], value='b'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='b_c_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['b'], value='b'),
                        e(selector_field=fields['c'], value='c'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='c',
                root_node=e(selector_field=fields['c'], value='c')
                ),
            broom.types.Selector(
                name='c_d',
                root_node=i(
                    child_nodes=[
                        e(selector_field=fields['c'], value='c'),
                        e(selector_field=fields['d'], value='d')
                        ]
                    )
                ),
            broom.types.Selector(
                name='d',
                root_node=e(selector_field=fields['d'], value='d')
                )
            }

        cls.fields = fields
        cls.selectors = selectors
        cls.selector_set = broom.types.SelectorSet(SelectorObjects=selectors)

        cls.union = u
        cls.intersect = i
        cls.equals = e

    def assertSelectorsEqual(self, matches, expected):
        attractions = [m[1] for m in matches]
        self._assertSelectorsEqual(attractions, expected)

    def _assertSelectorsEqual(self, attractions, expected):
        attractions = reversed(
                sorted(attractions, key=lambda i: (i.Strength(), i.SelectorObject().Name()))
                )
        self.assertSequenceEqual(
                [a.SelectorObject().Name() for a in attractions],
                expected
                )

    def test_selectors(self):
        obj = {}
        v = self.selector_set.evaluate([obj])
        self.assertSequenceEqual(v, [])

        obj = {'a': 'a'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['a'])

        v = self.selector_set.evaluateOne(obj)
        self._assertSelectorsEqual(v, ['a'])

        obj = {'a': 'a', 'b': 'b'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['a_b', 'b', 'a'])

        v = self.selector_set.evaluateOne(obj)
        self._assertSelectorsEqual(v, ['a_b', 'b', 'a'])

        obj = {'a': 'x', 'b': 'b'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['b'])

        obj = {'a': 'a', 'b': 'b', 'c': 'c'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['a_b_c', 'b_c', 'a_c', 'a_b', 'c', 'b', 'a'])

        obj = {'b': 'b', 'c': 'c'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['b_c', 'c', 'b'])

        obj = {'d': 'd'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['d'])

        obj = {'a': 'a', 'd': 'd'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['a_d', 'd', 'a'])

        obj = {'a': 'a', 'd': 'x'}
        v = self.selector_set.evaluate([obj])
        self.assertSelectorsEqual(v, ['a'])


if __name__ == '__main__':
    unittest.main()
