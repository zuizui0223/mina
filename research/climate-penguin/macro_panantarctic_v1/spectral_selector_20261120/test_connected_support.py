import unittest
from connected_label_support import interior_cells

class ConnectedTests(unittest.TestCase):
    def test_three_by_three_has_one_interior(self):
        cells={r*10+c+1 for r in range(3) for c in range(3)}
        self.assertEqual(interior_cells(cells,10,1),{12})
        self.assertEqual(interior_cells(cells,10,2),set())

    def test_missing_neighbor_is_not_filled(self):
        cells={r*10+c+1 for r in range(3) for c in range(3)}-{1}
        self.assertEqual(interior_cells(cells,10,1),set())

    def test_row_wrap_does_not_create_neighbor(self):
        self.assertEqual(interior_cells(range(8,17),10,1),set())

    def test_five_by_five_nesting(self):
        cells={r*10+c+1 for r in range(5) for c in range(5)}
        self.assertEqual(len(interior_cells(cells,10,1)),9)
        self.assertEqual(interior_cells(cells,10,2),{23})

if __name__=='__main__':unittest.main()
