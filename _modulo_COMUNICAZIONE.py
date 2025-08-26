import numpy as np

class Converter:
    def __init__(self):
        
        self.dad_vertices = np.array([[0.,0.,0.],
                                [0.,0.,3.],
                                [0.5,2.,3.],
                                [0.5,-1.,3.]])
        self.dad_links = np.array([[0, 1],
                            [1, 2],
                            [1, 3]])
        
        self.dad_spessori = np.array([0.1, 0.2, 0.2])

        self.vertices_prism = np.array([
            [1, 0, 0],
            [-0.5, -0.87, 0.0],
            [-0.5, 0.87, 0.0],
            [1, 0, 1],
            [-0.5, -0.87, 1],
            [-0.5, 0.87, 1]
        ])

        self.lookup_table = np.array([
            # [0, 1, 2],
            # [3, 5, 4],
            [3, 1, 0],
            [1, 3, 4],
            [1, 4, 2],
            [2, 4, 5],
            [5, 0, 2],
            [5, 3, 0]
        ])


    def new_values(self, vertices, links, spessori):
        self.dad_vertices = vertices
        self.dad_links = links[:, :2]
        self.dad_spessori = spessori


    def rotate_prisms(self):
        points, vertices, links = self.vertices_prism, self.dad_vertices, self.dad_links
        # links: (L,2) -> indices of vertex pairs, each defines a segment (axis of prism)
        # vertices: (N,3) -> 3D coordinates of vertices
        # points: (V,3) -> template coordinates of prism vertices, centered around z-axis

        # 1. Extract the endpoints of each link
        P1 = vertices[links[:,0].astype(int)]     # (L,3) starting points of axes
        P2 = vertices[links[:,1].astype(int)]     # (L,3) ending points of axes
        widths = self.dad_spessori

        # 2. Compute the axis vectors of each link
        axis = P2 - P1                # (L,3) vector along each link
        magnitudos = np.linalg.norm(axis, axis=1)[:,None]  # (L,1) length of each axis
        u = axis / magnitudos         # (L,3) normalized unit axis vectors

        # 3. Set reference vector (global z-axis)
        z = np.array([0,0,1.0])  

        # 4. Compute cosine of angle between z and each axis
        c = np.einsum('ij,j->i', u, z)  # dot(u,z) → (L,) scalar cosines

        # 5. Compute rotation axis = cross product of z with u
        v = np.cross(z, u)              # (L,3) perpendicular vector to rotate around

        # 6. Compute sine magnitude (||v|| = sinθ)
        s = np.linalg.norm(v, axis=1)   # (L,) magnitudes

        # 7. Build skew-symmetric matrices for each v
        vx = np.zeros((len(u),3,3))
        vx[:,0,1] = -v[:,2]; vx[:,0,2] = v[:,1]
        vx[:,1,0] = v[:,2];  vx[:,1,2] = -v[:,0]
        vx[:,2,0] = -v[:,1]; vx[:,2,1] = v[:,0]
        # vx[i] = [[  0   -vz   vy ],
        #           [ vz    0  -vx ],
        #           [-vy   vx    0 ]]

        # 8. Identity matrix, broadcast for each rotation
        eye = np.eye(3)[None,:,:]  # (1,3,3)

        # 9. Rodrigues' rotation formula for each link
        # R = I + [v]× + (1-c)/s² [v]×²
        R = eye + vx + np.einsum('i,ijk->ijk',(1-c)/(s**2+1e-12), vx@vx)  # (L,3,3)

        # 10. Handle degenerate special cases
        mask_pos = np.allclose(u, z, atol=1e-8)     # axis == +z → no rotation
        mask_neg = np.allclose(u, -z, atol=1e-8)    # axis == -z → 180° rotation
        if np.ndim(mask_pos)==0:  # single link
            if mask_pos: R = eye
            if mask_neg: R = np.diag([1,-1,-1])[None,:,:]  # reflect x,y
        else:  # multiple links
            R[mask_pos] = eye
            R[mask_neg] = np.diag([1,-1,-1])

        # 11. Apply scaling along Z scale and width
        points_expanded = points[None, :, :]       # (1,V,3)
        array_of_points_expanded = np.broadcast_to(points_expanded, (len(magnitudos), *points_expanded.shape[1:])).copy()

        array_of_points_expanded[:, :, 2] *= magnitudos[:]
        array_of_points_expanded[:, :, :2] *= widths[:, None, None]

        # 12. Apply rotations to the template points
        rotated = np.einsum('ijk,ivk->ivj', R, array_of_points_expanded)   # (L,V,3) rotate each prism template
        
        # 13. Apply traslations
        rotated += P1[:,None,:]                         # translate to start point of axis  
        
        # 14. Flatten all prisms into one array
        return rotated.reshape(-1, 3)


    def stack_links(self):

        offsets = 6 * np.arange(len(self.dad_links))[:, None, None]   # (L,1,1)
        stacked = self.lookup_table[None, :, :] + offsets          # (L,8,3)
        return stacked.reshape(-1, 3)
