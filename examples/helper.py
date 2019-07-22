"""Helper functions."""

from matplotlib import pyplot
import numpy
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import eigsh

import pyibm


def is_symmetric(Op, tol=1e-12):
    A = Op - Op.T
    A = A.multiply(abs(A) > tol)
    return A.nnz == 0


def condition_number(Op):
    evals_large, _ = eigsh(Op, 1, which='LM')
    evals_small, _ = eigsh(Op, 1, sigma=0, which='LM')
    lambda_min, lambda_max = evals_small[0], evals_large[0]
    cond = lambda_max / lambda_min
    return lambda_min, lambda_max, cond


def print_matrix_info(Op):
    """Print information of a given sparse matrix."""
    print('Type: ', type(Op))
    print('Shape: ', Op.shape)
    print('Size: ', Op.data.size)
    if Op.data.size > 0:
        print('Min/Max: ', Op.data.min(), Op.data.max())


def plot_matrix(M, figsize=(6.0, 6.0), axis_scaled=True,
                markersize=1, color='red', cmap=None,
                limits=[None, None, None, None]):
    """Plot non-zero structure of an operator."""
    if not isinstance(M, coo_matrix):
        M = coo_matrix(M)
    pyplot.rc('font', family='serif', size=16)
    fig, ax = pyplot.subplots(figsize=figsize)
    if cmap is None:
        ax.scatter(M.col, M.row, c=color, s=markersize, marker='s')
    else:
        sc = ax.scatter(M.col, M.row, c=M.data, s=markersize, cmap=cmap)
        fig.colorbar(sc)
    if axis_scaled:
        ax.axis('scaled', adjustable='box')
    default_limits = [0, M.shape[0] - 1, 0, M.shape[1] - 1]
    for i, lim in enumerate(limits):
        if lim is None:
            limits[i] = default_limits[i]
    ax.set_xlim(limits[2:])
    ax.set_ylim(limits[:2])
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def plot_contourf(field, grid, body=None,
                  levels=None,
                  axis_lim=(None, None, None, None),
                  show_grid=False):
    """Plot the filled contour of the 2D field."""
    pyplot.rc('font', family='serif', size=16)
    fig, ax = pyplot.subplots(figsize=(8.0, 8.0))
    X, Y = numpy.meshgrid(grid.x.vertices, grid.y.vertices)
    if show_grid:
        xmin, xmax = grid.x.start, grid.x.end
        ymin, ymax = grid.y.start, grid.y.end
        for xi in grid.x.vertices:
            ax.axvline(xi, ymin=ymin, ymax=ymax, color='grey')
        for yi in grid.y.vertices:
            ax.axhline(yi, xmin=xmin, xmax=xmax, color='grey')
        ax.scatter(X, Y, marker='x')
    if body is not None:
        ax.scatter(body.x, body.y, color='C3')
    if levels is None:
        levels = numpy.linspace(numpy.min(field), numpy.max(field), num=51)
    contf = ax.contourf(X, Y, field,
                        levels=levels, extend='both', zorder=0)
    fig.colorbar(contf)
    ax.axis('scaled', adjustable='box')
    ax.axis(axis_lim)
    return fig, ax


def plot_grids(grid, body=None, Op=None,
               axis_lim=(None, None, None, None)):
    """Plot the 2D grid."""
    pyplot.rc('font', family='serif', size=16)
    fig, ax = pyplot.subplots(figsize=(8.0, 8.0))
    xmin, xmax = grid.x.start, grid.x.end
    ymin, ymax = grid.y.start, grid.y.end
    for xi in grid.x.vertices:
        ax.axvline(xi, ymin=ymin, ymax=ymax, color='grey')
    for yi in grid.y.vertices:
        ax.axhline(yi, xmin=xmin, xmax=xmax, color='grey')
    gridc = pyibm.GridCellCentered(grid=grid)
    X, Y = numpy.meshgrid(gridc.x.vertices, gridc.y.vertices)
    ax.scatter(X, Y, label='cell-centered', marker='o', s=20)
    gridx = pyibm.GridFaceX(grid=grid)
    X, Y = numpy.meshgrid(gridx.x.vertices, gridx.y.vertices)
    ax.scatter(X, Y, label='x-face', marker='x', s=20)
    gridy = pyibm.GridFaceY(grid=grid)
    X, Y = numpy.meshgrid(gridy.x.vertices, gridy.y.vertices)
    ax.scatter(X, Y, label='y-face', marker='x', s=20)
    if body is not None:
        ax.scatter(body.x, body.y, label='body', s=40)
        neighbors = body.get_neighbors(gridc)
        xn, yn = [], []
        for xb, yb, neighbor in zip(body.x, body.y, neighbors):
            i, j, _ = gridc.ijk(neighbor)
            xi, yj = gridc.x.vertices[i], gridc.y.vertices[j]
            xn.append(xi)
            yn.append(yj)
            ax.plot([xb, xi], [yb, yj], color='black')
        ax.scatter(xn, yn, label='neighbors',
                   marker='*', s=40, color='black')
    if Op is not None:
        Op = coo_matrix(Op)
        rows = Op.row
        cols = Op.col
        for row, col in zip(rows, cols):
            if row % body.ndim == 0:
                i, j, _ = gridx.ijk(col)
                xi, yj = gridx.x.vertices[i], gridx.y.vertices[j]
                ax.scatter(xi, yj, marker='s', s=40, color='navy')
    ax.axis('scaled', adjustable='box')
    ax.axis(axis_lim)
    return fig, ax
