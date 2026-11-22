import unittest
import numpy as np
import pandas as pd
from affine import Affine
from recover_cell_grid import recover
from diagnose_grid_spectra import overlap_cells

class GridTests(unittest.TestCase):
    def test_recover_non_native_spacing_and_reject_corruption(self):
        cell=np.array([1,2,3,5,6,8,9,12,13])
        d=pd.DataFrame(dict(cell=cell,easting=100+(cell-1)%4*29.93,
                            northing=200-(cell-1)//4*30.14))
        fits,status=recover(d)
        self.assertEqual(status,'UNIQUE_LATTICE');self.assertEqual(fits[0]['ncols'],4)
        d.loc[2,'easting']+=1
        self.assertNotEqual(recover(d)[1],'UNIQUE_LATTICE')

    def test_native_center_has_one_cell(self):
        cells=overlap_cells(15,-15,30,30,Affine(30,0,0,0,-30,0))
        self.assertEqual(cells,[(0,0,900)])

    def test_boundary_has_four_quarters(self):
        cells=overlap_cells(30,-30,30,30,Affine(30,0,0,0,-30,0))
        self.assertEqual(cells,[(0,0,225),(0,1,225),(1,0,225),(1,1,225)])

    def test_fractional_footprint_conserves_area(self):
        cells=overlap_cells(31.7,-29.2,29.93,30.14,Affine(30,0,0,0,-30,0))
        self.assertAlmostEqual(sum(a for r,c,a in cells),29.93*30.14)
        self.assertTrue(all(a>0 for r,c,a in cells))

if __name__=='__main__':unittest.main()
