from ppcurses.state import State, link
import unittest


class Tracker:
    def __init__(self, retval):
        self.count = 0
        self.retval = retval

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.retval


class MockWindow:
    def draw(self):
        pass


class TestState(unittest.TestCase):
    def setUp(self):
        data = [
                {'id': 1, 'name': 'first'},
                {'id': 2, 'name': 'second'},
                {'id': 3, 'name': 'third'},
                {'id': 4, 'name': 'fourth'},
                {'id': 5, 'name': 'fifth'}
                ]
        self.state = State(lambda *args, **kwargs: data)
        self.state.update()
        link(self.state)

    def test_next(self):
        self.state.attach_window(MockWindow())
        self.state.next()
        self.assertEqual(self.state.index, 1)
        self.assertEqual(self.state.current_id, 2)
        self.assertEqual(self.state.current_item, {'id': 2, 'name': 'second'})

    def test_next_at_end(self):
        self.state.current_id = 5
        self.state.next()
        self.assertEqual(self.state.index, 4)
        self.assertEqual(self.state.current_id, 5)
        self.assertEqual(self.state.current_item, {'id': 5, 'name': 'fifth'})

    def test_prev(self):
        self.state.current_id = 2
        self.state.attach_window(MockWindow())
        self.state.prev()
        self.assertEqual(self.state.index, 0)
        self.assertEqual(self.state.current_id, 1)
        self.assertEqual(self.state.current_item, {'id': 1, 'name': 'first'})

    def test_prev_at_start(self):
        self.state.prev()
        self.assertEqual(self.state.index, 0)
        self.assertEqual(self.state.current_id, 1)
        self.assertEqual(self.state.current_item, {'id': 1, 'name': 'first'})


class TestEmptyState(unittest.TestCase):
    def setUp(self):
        data = [
                ]
        self.state = State(lambda *args, **kwargs: data)
        self.state.update()
        link(self.state)

    def test_current_with_no_data(self):
        self.assertEqual(self.state.index, 0)
        self.assertEqual(self.state.current_id, State.zerostate[0]['id'])
        self.assertEqual(self.state.current_item, State.zerostate[0])

    def test_next_with_no_data(self):
        self.state.next()
        self.assertEqual(self.state.index, 0)
        self.assertEqual(self.state.current_id, State.zerostate[0]['id'])
        self.assertEqual(self.state.current_item, State.zerostate[0])

    def test_prev_with_no_data(self):
        self.state.prev()
        self.assertEqual(self.state.index, 0)
        self.assertEqual(self.state.current_id, State.zerostate[0]['id'])
        self.assertEqual(self.state.current_item, State.zerostate[0])


class TestStateLink(unittest.TestCase):
    def setUp(self):
        data = [
                {'id': 1, 'name': 'first'},
                {'id': 2, 'name': 'second'},
                {'id': 3, 'name': 'third'},
                {'id': 4, 'name': 'fourth'},
                {'id': 5, 'name': 'fifth'}
                ]
        self.state1 = State(Tracker(data))
        self.state2 = State(Tracker(data))
        self.state3 = State(Tracker(data))
        self.state1.update()
        self.state2.update()
        self.state3.update()
        link(self.state1, self.state2, self.state3)

    def test_linking(self):
        self.assertEqual(self.state1.nstate, self.state2)
        self.assertEqual(self.state2.nstate, self.state3)

        self.assertEqual(self.state2.pstate, self.state1)
        self.assertEqual(self.state3.pstate, self.state2)

        self.assertFalse(hasattr(self.state1, 'pstate'))
        self.assertFalse(hasattr(self.state3, 'nstate'))

    def test_update_triggers_descendents(self):
        self.state1.update()
        self.assertEqual(self.state1.updatef.count, 2)
        self.assertEqual(self.state2.updatef.count, 2)
        self.assertEqual(self.state3.updatef.count, 2)

    def test_middle_update_skips_parents(self):
        self.state2.update()
        self.assertEqual(self.state1.updatef.count, 1)
        self.assertEqual(self.state2.updatef.count, 2)
        self.assertEqual(self.state3.updatef.count, 2)


class TestSurroundings(unittest.TestCase):
    def setUp(self):
        data = [
                {'id': 1, 'name': 'first'},
                {'id': 2, 'name': 'second'},
                {'id': 3, 'name': 'third'},
                {'id': 4, 'name': 'fourth'},
                {'id': 5, 'name': 'fifth'},
                {'id': 6, 'name': 'sixth'},
                {'id': 7, 'name': 'seventh'},
                {'id': 8, 'name': 'eighth'}
                ]
        self.state = State(lambda *args, **kwargs: data)
        self.state.update()

    def test_even_surrounding_items(self):
        self.state.current_id = 5
        items, highlight_index, _, _ = self.state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [3, 4, 5, 6, 7])
        self.assertEqual(len(items), 5)
        self.assertEqual(highlight_index, 2)

    def test_even_surrounding_items_at_start(self):
        items, highlight_index, _, _ = self.state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [1, 2, 3, 4, 5])
        self.assertEqual(len(items), 5)
        self.assertEqual(highlight_index, 0)

    def test_even_surrounding_items_near_start(self):
        self.state.current_id = 2
        items, highlight_index, _, _ = self.state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [1, 2, 3, 4, 5])
        self.assertEqual(len(items), 5)
        self.assertEqual(highlight_index, 1)

    def test_even_surrounding_items_near_end(self):
        self.state.current_id = 7
        items, highlight_index, _, _ = self.state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [4, 5, 6, 7, 8])
        self.assertEqual(len(items), 5)
        self.assertEqual(highlight_index, 3)

    def test_even_surrounding_items_at_end(self):
        self.state.current_id = 8
        items, highlight_index, _, _ = self.state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [4, 5, 6, 7, 8])
        self.assertEqual(len(items), 5)
        self.assertEqual(highlight_index, 4)

    def test_single_element(self):
        data = [
                {'id': 1, 'name': 'first'}
                ]
        state = State(lambda *args, **kwargs: data)
        state.update()
        items, highlight_index, _, _ = state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [1])
        self.assertEqual(highlight_index, 0)

    def test_few_elements(self):
        data = [
                {'id': 1, 'name': 'first'},
                {'id': 2, 'name': 'second'}
                ]

        state = State(lambda *args, **kwargs: data)
        state.update()
        items, highlight_index, _, _ = state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [1, 2])
        self.assertEqual(highlight_index, 0)

    def test_few_elements_reverse(self):
        data = [
                {'id': 1, 'name': 'first'},
                {'id': 2, 'name': 'second'}
                ]

        state = State(lambda *args, **kwargs: data)
        state.update()
        state.current_id = 2
        items, highlight_index, _, _ = state.surrounding(4)
        self.assertEqual([each['id'] for each in items], [1, 2])
        self.assertEqual(highlight_index, 1)

    def test_massive_surrounding_items(self):
        self.state.current_id = 4
        items, highlight_index, _, _ = self.state.surrounding(99)
        self.assertEqual([each['id'] for each in items], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(highlight_index, 3)


if __name__ == '__main__':
    unittest.main()
