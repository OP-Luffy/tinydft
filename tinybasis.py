#!/usr/bin/env python3
# Tiny DFT is a minimalistic atomic DFT implementation.
# Copyright (C) 2019 The Tiny DFT Development Team
#
# This file is part of Tiny DFT.
#
# Tiny DFT is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Tiny DFT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Radial orbital basis of Gaussian primitives and their integrals for TinyDFT."""


import numpy as np
from numpy.testing import assert_allclose


class Basis:
    """Gaussian radial orbital basis set, precomputed integrals and integral evaluation.

    Attributes
    ----------
    grid
        The radial numerical integration grid.
    alphas
        Gaussian exponents.
    fns
        Normalized basis functions evaluated on the grid.
    normalizations
        Vector with normalization constants for the Gaussians.
    olp
        Overlap matrix
    kin_rad
        Radial kinetic energy operator.
    kin_ang
        Angular kinetic energy operator for l=1.
    ext
        Operator for the interaction with a proton, i.e. the external field.

    """

    def __init__(self, grid, alphamin=1e-6, alphamax=1e8, nbasis=96):
        """Initialize a basis.

        Parameters
        ----------
        grid
            The radial integration grid.
        alphamin
            The lowest Gaussian exponent.
        alphamax
            The highest Gaussian exponent.
        nbasis
            The number of basis functions.

        """
        self.grid = grid
        self.alphas = 10**np.linspace(np.log10(alphamin), np.log10(alphamax), nbasis)
        self.fns = np.exp(-np.outer(self.alphas, grid.points**2)) * grid.points
        self.normalizations = np.sqrt((2 * self.alphas / np.pi)**1.5 * 4 * np.pi)
        self.fns *= self.normalizations[:, np.newaxis]
        assert_allclose(np.sqrt(grid.integrate(self.fns**2)), 1.0, atol=1e-13, rtol=0)

        # Precompute some integrals
        self.olp = self.grid.integrate(self.fns, self.fns)
        fns_d = self.grid.derivative(self.fns)
        # return self.grid.integrate(fns_d, fns_d) / 2
        fns_dd = self.grid.derivative(fns_d)
        self.kin_rad = self.grid.integrate(self.fns, -fns_dd) / 2
        self.kin_ang = self.grid.integrate(self.fns, self.fns, self.grid.points**-2)
        self.ext = self.grid.integrate(self.fns, self.fns, -self.grid.points**-1)

    @property
    def nbasis(self):
        """Return the number of basis functions."""
        return self.fns.shape[0]

    def pot(self, pot):
        """Return the operator for the interaction with a potential on a grid."""
        return self.grid.integrate(self.fns, self.fns, pot)