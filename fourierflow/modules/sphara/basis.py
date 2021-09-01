import torch
from torch import linalg as LA

from .trimesh import TriMesh


class SpharaBasis:
    def __init__(self, mesh: TriMesh, mode: str = 'fem', largest: bool = False):
        self.mesh = mesh
        self.mode = mode
        self._largest = largest
        self._basis = None
        self._frequencies = None
        self._mass_matrix = None

    def basis(self):
        r"""Return the SPHARA basis for the triangulated sample points.

        The method determines a SPHARA basis for spatially distributed
        sampling points described by a triangular mesh. A discrete
        Laplace-Beltrami operator in matrix form is determined for the
        given triangular grid. The discretization methods for
        determining the Laplace-Beltrami operator is specified in the
        attribute `mode`. The eigenvectors :math:`\vec{x}` and the
        eigenvalues :math:`\lambda` of the matrix :math:`L`
        containing the discrete Laplace-Beltrami operator are the
        SPHARA basis vectors and the natural frequencies,
        respectively, :math:`L \vec{x} = \lambda \vec{x}`.

        Returns
        -------
        frequencies : tensor, shape (k)
            The top k natural frequencies associated to the SPHARA basis
            functions.
        basis : tensor, shape (n_points, k)
            Matrix, which contains the SPHARA basis functions column by column.
            The number of vertices of the triangular mesh is n_points.

        Examples
        --------
        >>> mesh = TriMesh([[0, 1, 2]], [[1., 0., 0.], [0., 2., 0.], [0., 0., 3.]])
        >>> sb_fem = SpharaBasis(mesh, mode='fem')
        >>> frequencies, basis = sb_fem.basis()
        >>> frequencies
        tensor([5.1429])
        >>> basis
        tensor([[ 1.4286],
                [-1.1429],
                [-0.2857]])

        """
        if self._basis is None or self._frequencies is None:
            self._construct_basis()
        return self._frequencies, self._basis

    def _construct_basis(self):
        if self.mode == 'fem':
            self._construct_fem_basis()
        elif self.mode in ['unit', 'inv_euclidean']:
            raise NotImplementedError
        else:
            raise ValueError(f'Unrecognized mode: {self.mode}')

    def _construct_fem_basis(self, k=1):
        self._mass_matrix = self.mesh.get_mass_matrix(mode='normal')
        stiffness = self.mesh.get_stiffness_matrix()
        self._frequencies, self._basis = torch.lobpcg(
            -stiffness.to_dense(), k, self._mass_matrix.to_dense(),
            largest=self._largest)
