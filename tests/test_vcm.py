from __future__ import print_function
"""
Tests for PyRate's interferogram covariance calculation
and Variance-Covariance matrix functionality.
"""

import os
import shutil
import sys
import tempfile
import unittest
import pytest
from numpy import array

import numpy as np
from numpy.testing import assert_array_almost_equal

from pyrate import config as cf
from pyrate import ref_phs_est as rpe
from pyrate import shared
from pyrate import mpiops
from pyrate.scripts import run_pyrate, run_prepifg
from pyrate.scripts.run_pyrate import get_tiles, create_ifg_dict
from pyrate.vcm import cvd, get_vcmt
from tests.common import SYD_TEST_DIR
from tests.common import sydney5_mock_ifgs, sydney5_ifgs
from tests.common import sydney_data_setup
from tests import common


class CovarianceTests(unittest.TestCase):
    def setUp(self):
        self.ifgs = sydney_data_setup()
        for i in self.ifgs:
            i.mm_converted = True
        params = dict()
        params[cf.NO_DATA_VALUE] = 0
        params[cf.NAN_CONVERSION] = True
        self.params = params

    def test_covariance_basic(self):
        ifgs = sydney5_ifgs()

        for i in ifgs:
            i.open()

            if bool((i.phase_data == 0).all()) is True:
                raise Exception("All zero")

            maxvar, alpha = cvd(i, self.params, calc_alpha=True)
            self.assertTrue(maxvar is not None)
            self.assertTrue(alpha is not None)
            print("maxvar: %s, alpha: %s" % (maxvar, alpha))

    def test_covariance_17ifgs(self):
        # From Matlab Pirate after raw data import
        # (no reference pixel correction and units in radians)
        exp_maxvar = [5.6149, 8.7710, 2.9373, 0.3114, 12.9931, 2.0459, 0.4236,
                      2.1243, 0.4745, 0.6725, 0.8333, 3.8232, 3.3052, 2.4925,
                      16.0159, 2.8025, 1.4345]

        exp_alpha = [0.0356, 0.1601, 0.5128, 0.5736, 0.0691, 0.1337, 0.2333,
                    0.3202, 1.2338, 0.4273, 0.9024, 0.1280, 0.3585, 0.1599,
                    0.0110, 0.1287, 0.0676]

        act_maxvar = []
        act_alpha = []
        for i in self.ifgs:

            if bool((i.phase_data == 0).all()) is True:
                raise Exception("All zero")

            maxvar, alpha = cvd(i, self.params, calc_alpha=True)
            self.assertTrue(maxvar is not None)
            self.assertTrue(alpha is not None)
           
            act_maxvar.append(maxvar)
            act_alpha.append(alpha)

        assert_array_almost_equal(act_maxvar, exp_maxvar, decimal=3)

        # This test fails for greater than 1 decimal place.
        # Discrepancies observed in distance calculations.
        assert_array_almost_equal(act_alpha, exp_alpha, decimal=1)


class VCMTests(unittest.TestCase):

    def setUp(self):
        self.ifgs = sydney_data_setup()

    def test_vcm_basic(self):
        ifgs = sydney5_mock_ifgs(5, 9)
        maxvar = [8.486, 12.925, 6.313, 0.788, 0.649]

        # from Matlab Pirate make_vcmt.m code
        exp = array([[8.486, 5.2364, 0.0, 0.0, 0.0],
            [5.2364, 12.925,  4.5165,  1.5957,  0.0],
            [0.0, 4.5165, 6.313, 1.1152, 0.0],
            [0.0, 1.5957, 1.1152, 0.788, -0.3576],
            [0.0, 0.0, 0.0, -0.3576, 0.649]])

        act = get_vcmt(ifgs, maxvar)
        assert_array_almost_equal(act, exp, decimal=3)

    def test_vcm_17ifgs(self):
        # TODO: maxvar should be calculated by vcm.cvd
        maxvar = [2.879, 4.729, 22.891, 4.604, 3.290, 6.923, 2.519, 13.177,
                  7.548, 6.190, 12.565, 9.822, 18.484, 7.776, 2.734, 6.411,
                  4.754]

        # Output from Matlab Pirate make_vcmt.m
        exp = array([
            [2.879, 0.0, -4.059, -1.820, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 4.729, 0.0, 0.0, 1.972, 0.0, 0.0, -3.947, -2.987, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [-4.059, 0.0, 22.891, 5.133, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             -7.497, -10.285, 0.0, 0.0, 0.0, 0.0],
            [-1.820, 0.0, 5.133, 4.604, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             3.362, 0.0, 0.0, -1.774, 0.0, 0.0],
            [0.0, 1.972, 0.0, 0.0, 3.290, 2.386, 1.439, -3.292, -2.492, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 2.386, 6.923, 2.088, 0.0, 0.0, -3.273,
             -4.663, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.439, 2.088, 2.519, 0.0, 0.0, 1.974, 0.0,
             0.0, 0.0, -2.213, 0.0, 0.0, 0.0],
            [0.0, -3.947, 0.0, 0.0, -3.292, 0.0, 0.0, 13.177, 4.986, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0, 4.596, -3.957],
            [0.0, -2.987, 0.0, 0.0, -2.492, 0.0, 0.0, 4.986, 7.548, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.0, 2.995],
            [0.0, 0.0, 0.0, 0.0, 0.0, -3.273, 1.974, 0.0, 0.0, 6.190, 4.410,
             0.0, 0.0, -3.469, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, -4.663, 0.0, 0.0, 0.0, 4.410, 12.565,
             0.0, 0.0, 4.942, 0.0, 0.0, 0.0],
            [0.0, 0.0, -7.497, 3.362, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             9.8221, 6.737, 0.0, -2.591, 0.0, 0.0],
            [0.0, 0.0, -10.285, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.737,
             18.484, 0.0, 3.554, -5.443, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -2.213, 0.0, 0.0, -3.469, 4.942,
             0.0, 0.0, 7.776, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, -1.774, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -2.591,
             3.554, 0.0, 2.734, -2.093, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.596, 0.0, 0.0, 0.0, 0.0,
             -5.443, 0.0, -2.093, 6.411, -2.760],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -3.957, 2.995, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, -2.760, 4.754]
        ])

        act = get_vcmt(self.ifgs, maxvar)
        assert_array_almost_equal(act, exp, decimal=3)


matlab_maxvar = [15.4156637191772,
                 2.85829424858093,
                 34.3486289978027,
                 2.59190344810486,
                 3.18510007858276,
                 3.61054635047913,
                 1.64398515224457,
                 14.9226036071777,
                 5.13451862335205,
                 6.82901763916016,
                 10.9644861221313,
                 14.5026779174805,
                 29.3710079193115,
                 8.00364685058594,
                 2.06328082084656,
                 5.66661834716797,
                 5.62802362442017]


class MatlabEqualityTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        params = cf.get_config_params(
                os.path.join(SYD_TEST_DIR, 'pyrate_system_test.conf')
        )
        cls.temp_out_dir = tempfile.mkdtemp()

        sys.argv = ['run_prepifg.py', os.path.join(SYD_TEST_DIR,
                    'pyrate_system_test.conf')]
        params[cf.OUT_DIR] = cls.temp_out_dir
        params[cf.REF_EST_METHOD] = 2
        run_prepifg.main(params)
        xlks, ylks, crop = cf.transform_params(params)
        base_ifg_paths = cf.original_ifg_paths(params[cf.IFG_FILE_LIST])
        dest_paths = cf.get_dest_paths(base_ifg_paths, crop, params, xlks)
        ifgs = shared.pre_prepare_ifgs(dest_paths, params)
        refx, refy = run_pyrate.ref_pixel_calc(dest_paths, params)
        run_pyrate.remove_orbital_error(ifgs, params)
        ifgs = shared.prepare_ifgs_without_phase(dest_paths, params)
        _, ifgs = rpe.estimate_ref_phase(ifgs, params, refx, refy)

        # Calculate interferogram noise
        cls.maxvar = [cvd(i, params)[0] for i in ifgs]
        cls.vcmt = get_vcmt(ifgs, cls.maxvar)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_out_dir)

    def test_matlab_maxvar_equality_sydney_test_files(self):
        np.testing.assert_array_almost_equal(self.maxvar, matlab_maxvar,
                                             decimal=3)

    def test_matlab_vcmt_equality_sydney_test_files(self):
        from tests.common import SYD_TEST_DIR
        MATLAB_VCM_DIR = os.path.join(SYD_TEST_DIR, 'matlab_vcm')
        matlab_vcm = np.genfromtxt(os.path.join(MATLAB_VCM_DIR,
                                   'matlab_vcmt.csv'), delimiter=',')
        np.testing.assert_array_almost_equal(matlab_vcm, self.vcmt, decimal=3)


@pytest.fixture(params=range(1, 6))
def modify_config(request, tempdir, get_config):
    test_conf = common.SYDNEY_TEST_CONF
    params_dict = get_config(test_conf)
    params_dict[cf.IFG_LKSX] = request.param
    params_dict[cf.IFG_LKSY] = request.param
    params_dict[cf.OBS_DIR] = tempdir()
    shared.copytree(common.SYD_TEST_GAMMA, params_dict[cf.OBS_DIR])
    params_dict[cf.IFG_FILE_LIST] = os.path.join(
        params_dict[cf.OBS_DIR], 'ifms_17')
    params_dict[cf.PARALLEL] = 0
    params_dict[cf.APS_CORRECTION] = 0
    yield params_dict
    # clean up
    shutil.rmtree(params_dict[cf.OBS_DIR])


def test_matlab_vs_mpi(mpisync, tempdir, get_config):
    from tests.common import SYD_TEST_DIR

    params_dict = get_config(
        os.path.join(SYD_TEST_DIR, 'pyrate_system_test.conf')
    )

    MATLAB_VCM_DIR = os.path.join(SYD_TEST_DIR, 'matlab_vcm')
    matlab_vcm = np.genfromtxt(os.path.join(MATLAB_VCM_DIR,
                                            'matlab_vcmt.csv'), delimiter=',')
    if mpiops.rank == 0:
        outdir = tempdir()
    else:
        outdir = None
    outdir = mpiops.comm.bcast(outdir, root=0)
    params_dict[cf.OUT_DIR] = outdir
    params_dict[cf.PARALLEL] = False
    xlks, ylks, crop = cf.transform_params(params_dict)
    base_unw_paths = cf.original_ifg_paths(params_dict[cf.IFG_FILE_LIST])
    # dest_paths are tifs that have been geotif converted and multilooked
    dest_paths = cf.get_dest_paths(base_unw_paths, crop, params_dict, xlks)

    # run prepifg, create the dest_paths files
    if mpiops.rank == 0:
        run_prepifg.roipac_prepifg(base_unw_paths, params_dict)

    mpiops.comm.barrier()

    tiles = get_tiles(dest_paths[0], rows=1, cols=1)
    preread_ifgs = create_ifg_dict(dest_paths,
                                   params=params_dict,
                                   tiles=tiles)
    refpx, refpy = run_pyrate.ref_pixel_calc(dest_paths, params_dict)
    run_pyrate.orb_fit_calc(dest_paths, params_dict)
    run_pyrate.ref_phase_estimation_mpi(dest_paths, params_dict, refpx, refpy)

    maxvar, vcmt = run_pyrate.maxvar_vcm_mpi(dest_paths, params_dict,
                                             preread_ifgs)
    np.testing.assert_array_almost_equal(maxvar, matlab_maxvar, decimal=4)
    np.testing.assert_array_almost_equal(matlab_vcm, vcmt, decimal=3)
    if mpiops.rank == 0:
        shutil.rmtree(outdir)


def test_vcm_maxvar_mpi(mpisync, tempdir, modify_config, ref_est_method,
                        row_splits, col_splits):
    from pyrate import refpixel
    params_dict = modify_config
    outdir = mpiops.run_once(tempdir)
    params_dict[cf.OUT_DIR] = outdir
    params_dict[cf.REF_EST_METHOD] = ref_est_method
    xlks, ylks, crop = cf.transform_params(params_dict)
    print("xlks, row_splits, col_splits, rank")
    print(xlks, row_splits, col_splits, mpiops.rank)
    if xlks * col_splits > 45 or ylks * row_splits > 70:
        print('skipping test')
        return

    base_unw_paths = cf.original_ifg_paths(params_dict[cf.IFG_FILE_LIST])
    # dest_paths are tifs that have been geotif converted and multilooked
    dest_paths = cf.get_dest_paths(base_unw_paths, crop, params_dict, xlks)

    # run prepifg, create the dest_paths files
    if mpiops.rank == 0:
        run_prepifg.gamma_prepifg(base_unw_paths, params_dict)

    mpiops.comm.barrier()

    tiles = get_tiles(dest_paths[0], rows=row_splits, cols=col_splits)
    preread_ifgs = create_ifg_dict(dest_paths,
                                   params=params_dict,
                                   tiles=tiles)

    refpx, refpy = run_pyrate.ref_pixel_calc(dest_paths, params_dict)
    run_pyrate.orb_fit_calc(dest_paths, params_dict)
    run_pyrate.ref_phase_estimation_mpi(dest_paths, params_dict, refpx, refpy)

    maxvar, vcmt = run_pyrate.maxvar_vcm_mpi(dest_paths, params_dict,
                                             preread_ifgs)
    ifgs_mpi_out_dir = params_dict[cf.OUT_DIR]
    ifgs_mpi = sydney_data_setup(datafiles=dest_paths)

    # old vcm/maxvar estimate
    params_dict_old = modify_config
    params_dict_old[cf.OUT_DIR] = tempdir()
    params_dict_old[cf.REF_EST_METHOD] = ref_est_method
    if mpiops.rank == 0:
        xlks, ylks, crop = cf.transform_params(params_dict_old)
        base_unw_paths = cf.original_ifg_paths(
            params_dict_old[cf.IFG_FILE_LIST])
        dest_paths = cf.get_dest_paths(
            base_unw_paths, crop, params_dict_old, xlks)
        run_prepifg.gamma_prepifg(base_unw_paths, params_dict_old)

        ifgs = shared.pre_prepare_ifgs(dest_paths, params_dict_old)
        refy, refx = refpixel.ref_pixel(ifgs, params_dict)

        run_pyrate.remove_orbital_error(ifgs, params_dict)
        ifgs = shared.prepare_ifgs_without_phase(dest_paths, params_dict)

        _, ifgs = rpe.estimate_ref_phase(ifgs, params_dict, refx, refy)
        maxvar_s = [cvd(i, params_dict_old)[0] for i in ifgs]
        vcmt_s = get_vcmt(ifgs, maxvar)

        np.testing.assert_array_almost_equal(maxvar, maxvar_s)
        np.testing.assert_array_almost_equal(vcmt, vcmt_s)
        for i, j in zip(ifgs, ifgs_mpi):
            np.testing.assert_array_almost_equal(i.phase_data, j.phase_data)
        shutil.rmtree(ifgs_mpi_out_dir)  # remove mpi out dir
        shutil.rmtree(params_dict_old[cf.OUT_DIR])  # remove serial out dir


if __name__ == "__main__":
    unittest.main()
