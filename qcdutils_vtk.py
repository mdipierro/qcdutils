#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# create by: Massimo Di Pierro<mdipierro@cs.depaul.edu>
# license: GPL2.0 + BSD
# includes processing.min.js created by John Resig

import os, sys, glob

__all__ = ['P3D', 'read_vtk', 'make_points']

class Iso:
    class GridCell:
        def __init__(self):
            self.position = [(0.0,0.0,0.0) for i in range(8)]
            self.value = [0.0]*8

    def __init__(self,point,level=0.0):
        self.point = point
        self.level = float(level)
        self.triangles = []

    def vertexInterp(self,p1,p2,valp1,valp2):
        if abs(self.level-valp1) < 0.000000000001: return p1
        if abs(self.level-valp2) < 0.000000000001: return p2
        if abs(valp1-valp2) < 0.0000000001: return p1
        mu = (self.level-valp1)/(valp2-valp1)
        p = (p1[0] + mu * (p2[0] - p1[0]),
             p1[1] + mu * (p2[1] - p1[1]),
             p1[2] + mu * (p2[2] - p1[2]))
        return p

    def cube(self,cell):
        cubeIndex = 0
        value = cell.value
        position = cell.position
        level = self.level
        
        vertexList = [[0.0,0.0,0.0] for i in range(12)]
        if value[0] < level: cubeIndex|=1
        if value[1] < level: cubeIndex|=2
        if value[2] < level: cubeIndex|=4
        if value[3] < level: cubeIndex|=8
        if value[4] < level: cubeIndex|=16
        if value[5] < level: cubeIndex|=32
        if value[6] < level: cubeIndex|=64
        if value[7] < level: cubeIndex|=128 
        
        et = edgeTable[cubeIndex]
        vi = self.vertexInterp

        if et==0: return 0
        if et&1: vertexList[0] = vi(position[0],position[1],value[0],value[1])
        if et&2: vertexList[1] = vi(position[1],position[2],value[1],value[2])
        if et&4: vertexList[2] = vi(position[2],position[3],value[2],value[3])
        if et&8: vertexList[3] = vi(position[3],position[0],value[3],value[0])
        if et&16: vertexList[4] = vi(position[4],position[5],value[4],value[5])
        if et&32: vertexList[5] = vi(position[5],position[6],value[5],value[6])
        if et&64: vertexList[6] = vi(position[6],position[7],value[6],value[7])
        if et&128: vertexList[7] = vi(position[7],position[4],value[7],value[4])
        if et&256: vertexList[8] = vi(position[0],position[4],value[0],value[4])
        if et&512: vertexList[9] = vi(position[1],position[5],value[1],value[5])
        if et&1024: vertexList[10] = vi(position[2],position[6],value[2],value[6])
        if et&2048: vertexList[11] = vi(position[3],position[7],value[3],value[7])

        ntriangle = 0
        tt = triTable[cubeIndex]
        for i in range(0,16,3):
            if tt[i]!= -1:
                self.triangles.append((vertexList[tt[i]],
                                       vertexList[tt[i+1]],
                                       vertexList[tt[i+2]]))
                ntriangle+=1
        return ntriangle

    def grid(self):
        ni = len(self.point)-1
        nj = len(self.point[0])-1
        nk = len(self.point[0][0])-1
        #triangles = []
        point = self.point
        for i in xrange(0,ni):
            for j in xrange(0,nj):
                for k in xrange(0,nk):
                    p = self.GridCell()
                    position = p.position
                    (x,y,z)=(float(i),float(j),float(k))
                    position[0] = (x,y,z)
                    position[1] = (x+1,y,z)
                    position[2] = (x+1,y+1,z)
                    position[3] = (x,y+1,z)
                    position[4] = (x,y,z+1)
                    position[5] = (x+1,y,z+1)
                    position[6] = (x+1,y+1,z+1)
                    position[7] = (x,y+1,z+1)
                    p.value = (point[i][j][k], point[i+1][j][k],
                               point[i+1][j+1][k], point[i][j+1][k],
                               point[i][j][k+1], point[i+1][j][k+1],
                               point[i+1][j+1][k+1], point[i][j+1][k+1])
                    n = self.cube(p)
        return (ni,nj,nk)

edgeTable = [0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c,
0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
0x190, 0x99 , 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c,
0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
0x230, 0x339, 0x33 , 0x13a, 0x636, 0x73f, 0x435, 0x53c,
0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
0x3a0, 0x2a9, 0x1a3, 0xaa , 0x7a6, 0x6af, 0x5a5, 0x4ac,
0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
0x460, 0x569, 0x663, 0x76a, 0x66 , 0x16f, 0x265, 0x36c,
0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff , 0x3f5, 0x2fc,
0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55 , 0x15c,
0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc ,
0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc,
0xcc , 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c,
0x15c, 0x55 , 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc,
0x2fc, 0x3f5, 0xff , 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c,
0x36c, 0x265, 0x16f, 0x66 , 0x76a, 0x663, 0x569, 0x460,
0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac,
0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa , 0x1a3, 0x2a9, 0x3a0,
0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c,
0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33 , 0x339, 0x230,
0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c,
0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99 , 0x190,
0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c,
0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0]

triTable = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[9, 2, 10, 0, 2, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[2, 8, 3, 2, 10, 8, 10, 9, 8, -1, -1, -1, -1, -1, -1, -1],
[3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 11, 2, 8, 11, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 9, 0, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 11, 2, 1, 9, 11, 9, 8, 11, -1, -1, -1, -1, -1, -1, -1],
[3, 10, 1, 11, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 10, 1, 0, 8, 10, 8, 11, 10, -1, -1, -1, -1, -1, -1, -1],
[3, 9, 0, 3, 11, 9, 11, 10, 9, -1, -1, -1, -1, -1, -1, -1],
[9, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 3, 0, 7, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 10, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[3, 4, 7, 3, 0, 4, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1],
[9, 2, 10, 9, 0, 2, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
[2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1, -1, -1, -1],
[8, 4, 7, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[11, 4, 7, 11, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, -1],
[9, 0, 1, 8, 4, 7, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
[4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1, -1, -1, -1],
[3, 10, 1, 3, 11, 10, 7, 8, 4, -1, -1, -1, -1, -1, -1, -1],
[1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1, -1, -1, -1],
[4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1, -1, -1, -1],
[4, 7, 11, 4, 11, 9, 9, 11, 10, -1, -1, -1, -1, -1, -1, -1],
[9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[8, 5, 4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 10, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[3, 0, 8, 1, 2, 10, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
[5, 2, 10, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1, -1],
[2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, -1],
[9, 5, 4, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 11, 2, 0, 8, 11, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
[0, 5, 4, 0, 1, 5, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
[2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1, -1, -1, -1],
[10, 3, 11, 10, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1],
[4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1, -1, -1, -1],
[5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1, -1, -1, -1],
[5, 4, 8, 5, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1],
[9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[9, 3, 0, 9, 5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, -1],
[0, 7, 8, 0, 1, 7, 1, 5, 7, -1, -1, -1, -1, -1, -1, -1],
[1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[9, 7, 8, 9, 5, 7, 10, 1, 2, -1, -1, -1, -1, -1, -1, -1],
[10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, -1],
[8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1, -1, -1, -1],
[2, 10, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1],
[7, 9, 5, 7, 8, 9, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1],
[9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1, -1, -1, -1],
[2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1, -1, -1, -1],
[11, 2, 1, 11, 1, 7, 7, 1, 5, -1, -1, -1, -1, -1, -1, -1],
[9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1, -1, -1, -1],
[5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1],
[11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1],
[11, 10, 5, 7, 11, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 3, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[9, 0, 1, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 8, 3, 1, 9, 8, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
[1, 6, 5, 2, 6, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1, -1, -1, -1, -1],
[9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, -1],
[5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, -1],
[2, 3, 11, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[11, 0, 8, 11, 2, 0, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
[0, 1, 9, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
[5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1, -1, -1, -1],
[6, 3, 11, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1, -1, -1, -1],
[3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1, -1, -1, -1],
[6, 5, 9, 6, 9, 11, 11, 9, 8, -1, -1, -1, -1, -1, -1, -1],
[5, 10, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 3, 0, 4, 7, 3, 6, 5, 10, -1, -1, -1, -1, -1, -1, -1],
[1, 9, 0, 5, 10, 6, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
[10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1, -1, -1, -1],
[6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, -1],
[8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1, -1, -1, -1],
[7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1],
[3, 11, 2, 7, 8, 4, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
[5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1, -1, -1, -1],
[0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1],
[9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1],
[8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1, -1, -1, -1],
[5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1],
[0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1],
[6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1, -1, -1, -1],
[10, 4, 9, 6, 4, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 10, 6, 4, 9, 10, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1],
[10, 0, 1, 10, 6, 0, 6, 4, 0, -1, -1, -1, -1, -1, -1, -1],
[8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1, -1, -1, -1],
[1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, -1],
[3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, -1],
[0, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1],
[10, 4, 9, 10, 6, 4, 11, 2, 3, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1, -1, -1, -1],
[3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1, -1, -1, -1],
[6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1],
[9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1, -1, -1, -1],
[8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1],
[3, 11, 6, 3, 6, 0, 0, 6, 4, -1, -1, -1, -1, -1, -1, -1],
[6, 4, 8, 11, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[7, 10, 6, 7, 8, 10, 8, 9, 10, -1, -1, -1, -1, -1, -1, -1],
[0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1, -1, -1, -1],
[10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, -1],
[10, 6, 7, 10, 7, 1, 1, 7, 3, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1, -1, -1, -1],
[2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1],
[7, 8, 0, 7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, -1],
[7, 3, 2, 6, 7, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1, -1, -1, -1],
[2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1],
[1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1],
[11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1, -1, -1, -1],
[8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1],
[0, 9, 1, 11, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1, -1, -1, -1],
[7, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[3, 0, 8, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 1, 9, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[8, 1, 9, 8, 3, 1, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
[10, 1, 2, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 10, 3, 0, 8, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
[2, 9, 0, 2, 10, 9, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
[6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1, -1, -1, -1],
[7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[7, 0, 8, 7, 6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, -1],
[2, 7, 6, 2, 3, 7, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1],
[1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1, -1, -1],
[10, 7, 6, 10, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, -1],
[10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1, -1, -1, -1],
[0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1, -1, -1, -1],
[7, 6, 10, 7, 10, 8, 8, 10, 9, -1, -1, -1, -1, -1, -1, -1],
[6, 8, 4, 11, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[3, 6, 11, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, -1],
[8, 6, 11, 8, 4, 6, 9, 0, 1, -1, -1, -1, -1, -1, -1, -1],
[9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1, -1, -1, -1],
[6, 8, 4, 6, 11, 8, 2, 10, 1, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1, -1, -1, -1],
[4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1, -1, -1, -1],
[10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1],
[8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1],
[0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, -1],
[1, 9, 4, 1, 4, 2, 2, 4, 6, -1, -1, -1, -1, -1, -1, -1],
[8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1, -1, -1, -1],
[10, 1, 0, 10, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, -1],
[4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1],
[10, 9, 4, 6, 10, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 9, 5, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 3, 4, 9, 5, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
[5, 0, 1, 5, 4, 0, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
[11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, -1],
[9, 5, 4, 10, 1, 2, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
[6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1, -1, -1, -1],
[7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1, -1, -1, -1],
[3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1],
[7, 2, 3, 7, 6, 2, 5, 4, 9, -1, -1, -1, -1, -1, -1, -1],
[9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1, -1, -1],
[3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, -1],
[6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1],
[9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1, -1, -1, -1],
[1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1],
[4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1],
[7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1, -1, -1, -1],
[6, 9, 5, 6, 11, 9, 11, 8, 9, -1, -1, -1, -1, -1, -1, -1],
[3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, -1],
[0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1, -1, -1, -1],
[6, 11, 3, 6, 3, 5, 5, 3, 1, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1, -1, -1, -1],
[0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1],
[11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1],
[6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1, -1, -1, -1],
[5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1, -1, -1, -1],
[9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, -1],
[1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1],
[1, 5, 6, 2, 1, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1],
[10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, -1],
[0, 3, 8, 5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[10, 5, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[11, 5, 10, 7, 5, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[11, 5, 10, 11, 7, 5, 8, 3, 0, -1, -1, -1, -1, -1, -1, -1],
[5, 11, 7, 5, 10, 11, 1, 9, 0, -1, -1, -1, -1, -1, -1, -1],
[10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, -1],
[11, 1, 2, 11, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1, -1, -1, -1],
[9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1, -1, -1, -1],
[7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1],
[2, 5, 10, 2, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1],
[8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1, -1, -1, -1],
[9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1, -1, -1, -1],
[9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1],
[1, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 7, 0, 7, 1, 1, 7, 5, -1, -1, -1, -1, -1, -1, -1],
[9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1, -1, -1],
[9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[5, 8, 4, 5, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1],
[5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1, -1, -1, -1],
[0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1, -1, -1, -1],
[10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1],
[2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1, -1, -1, -1],
[0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1],
[0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1],
[9, 4, 5, 2, 11, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, -1],
[5, 10, 2, 5, 2, 4, 4, 2, 0, -1, -1, -1, -1, -1, -1, -1],
[3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1],
[5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, -1],
[8, 4, 5, 8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, -1],
[0, 4, 5, 1, 0, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1, -1, -1, -1],
[9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 11, 7, 4, 9, 11, 9, 10, 11, -1, -1, -1, -1, -1, -1, -1],
[0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1, -1, -1, -1],
[1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1, -1, -1, -1],
[3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1],
[4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1, -1, -1, -1],
[9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1],
[11, 7, 4, 11, 4, 2, 2, 4, 0, -1, -1, -1, -1, -1, -1, -1],
[11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1, -1, -1, -1],
[2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, -1],
[9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1],
[3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1],
[1, 10, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, -1],
[4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, -1],
[4, 0, 3, 7, 4, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[4, 8, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[9, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[3, 0, 9, 3, 9, 11, 11, 9, 10, -1, -1, -1, -1, -1, -1, -1],
[0, 1, 10, 0, 10, 8, 8, 10, 11, -1, -1, -1, -1, -1, -1, -1],
[3, 1, 10, 11, 3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 2, 11, 1, 11, 9, 9, 11, 8, -1, -1, -1, -1, -1, -1, -1],
[3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1, -1, -1, -1],
[0, 2, 11, 8, 0, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[3, 2, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[2, 3, 8, 2, 8, 10, 10, 8, 9, -1, -1, -1, -1, -1, -1, -1],
[9, 10, 2, 0, 9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1, -1, -1, -1],
[1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[0, 3, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]


def read_vtk(filename):
    import struct, re
    data = open(filename,'rb').read()
    i = data.find('LOOKUP_TABLE default\n')
    data2 = data[i+len('LOOKUP_TABLE default\n'):]
    k = len(data2)/4
    v = struct.unpack('>%sf' %k,data2)
    match = re.compile('DIMENSIONS\s+(?P<nx>\d*)\s+(?P<ny>\d*)\s+(?P<nz>\d*)',re.MULTILINE).search(data) 
    nx, ny, nz = int(match.group('nx')), int(match.group('ny')), int(match.group('nz'))
    points = [[[0.0 for k in range(nz)] for i in range(ny)] for m in range(nx)] 
    for z in range(0,nz):
        for y in range(0,ny):
            for x in range(0,nx):
                points[x][y][z] = v[int(x+nx*(y+ny*z))]
    return points
    
def make_points(f, rx, ry, rz):
    (min_x, max_x, dx) = rx
    (min_y, max_y, dy) = ry
    (min_z, max_z, dz) = rz
    nx = int(float(max_x-min_x)/dx+1)
    ny = int(float(max_y-min_y)/dy+1)
    nz = int(float(max_z-min_z)/dz+1)
    points = [[[0.0 for i in range(nx)] for j in range(ny)] for k in range(nz)]
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                x = float(dx)*i + min_x
                y = float(dy)*j + min_y
                z = float(dz)*k + min_z
                #print i,j,k,x,y,z,f(x,y,z)
                points[k][j][i] = f(x,y,z)
    return points
    
class P3D:

    def __init__(self, width=400, onrotate=None):
        self.lines = []
        self.spheres = []
        self.triangles = []
        self.width = width
        self.height = width
        self.onrotate = onrotate
        self.scale=float(width)/400

    def line(self,x0,y0,z0,x1,y1,z1,stroke = 1,red = 255,green = 255,blue = 255):
        self.lines.append((self.scale*x0,self.scale*y0,self.scale*z0,
                           self.scale*x1,self.scale*y1,self.scale*z1,
                           stroke,red,green,blue))
        
    def sphere(self,x0,y0,z0,radius = 5,red = 255,green = 255,blue = 255):
        self.spheres.append((self.scale*x0,self.scale*y0,self.scale*z0,
                             radius,red,green,blue))

    def triangle(self,x0,y0,z0,x1,y1,z1,x2,y2,z2,red = 255,green = 255,blue = 255):
        self.triangles.append((self.scale*x0,self.scale*y0,self.scale*z0,
                               self.scale*x1,self.scale*y1,self.scale*z1,
                               self.scale*x2,self.scale*y2,self.scale*z2,
                               red,green,blue))

    def test_cube(self):
        for x in xrange(-100,200,200):
            for y in xrange(-100,200,200):
                for z in xrange(-100,200,200):
                    if x>0: self.line(x,y,z,-x,y,z)
                    if y>0: self.line(x,y,z,x,-y,z)
                    if z>0: self.line(x,y,z,x,y,-z)
                    #self.sphere(x,y,z,radius = 10,green = 0)
                    #self.triangle(0,0,0,0,y,z,x,y,z,red = 0)

    def isosurface(self, points, alpha = 0.7, red = 250, green = 0, blue = 0):
        self.test_cube()
        (maximum, minimum) = (-1e100, 1e100)
        for p in points:
            for q in p:
                for r in q:
                    maximum = max(r,r,maximum)
                    minimum = min(r,r,minimum)
        draw = Iso(points, alpha*maximum + (1.0-alpha)*minimum)
        pixel = draw.grid()
        relaPos = draw.triangles
        for t in relaPos:
            self.triangle((t[0][0]/pixel[0])*200.0-100,
                          (t[0][1]/pixel[1])*200.0-100,
                          (t[0][2]/pixel[2])*200.0-100,
                          (t[1][0]/pixel[0])*200.0-100,
                          (t[1][1]/pixel[1])*200.0-100,
                          (t[1][2]/pixel[2])*200.0-100,
                          (t[2][0]/pixel[0])*200.0-100,
                          (t[2][1]/pixel[1])*200.0-100,
                          (t[2][2]/pixel[2])*200.0-100,
                          red=red, green=green, blue=blue)
        return points

    def test_random_event(self,q1 = None):

        import random, copy
        def r():
            return 100.0*random.random()-50
        p = copy.copy(q1) or [(0,0,0,r()*2,r(),r()) for k in range(50)]
        q = []
                
        while p:
            (x,y,z,x1,y1,z1) = p.pop()
            q.append((x,y,z,x1,y1,z1))
            self.line(x,y,z,x1,y1,z1)
            if x1*x1+y1*y1*z1*z1<200*100:
                if not q1:
                    p.append((x1,y1,z1,x1*2-x+r()/5,y1*2-y+r()/5,z1*2-z+r()/5))
                    p.append((x1,y1,z1,x1*2-x+r()/5,y1*2-y+r()/5,z1*2-z+r()/5))
                    p.append((x1,y1,z1,x1*2-x+r()/5,y1*2-y+r()/5,z1*2-z+r()/5))
            self.sphere(x1,y1,z1,random.randint(5,10),
                        red = random.randint(0,255),
                        green = random.randint(0,255),
                        blue = random.randint(0,255))

    def lin(self,v):
        return ','.join([str(int(x)) for x in v])

    def xml(self):
        lines = ','.join([self.lin(x) for x in self.lines])
        spheres = ','.join([self.lin(x) for x in self.spheres])
        triangles = ','.join([self.lin(x) for x in self.triangles])
        if self.onrotate:
            rotate_call = "jQuery.get('%s?alpha='+alpha+'&beta='+beta);" % self.onrotate
        else:
            rotate_call = ''
        return """
<script type="application/processing">
float dx = %s;
floay dy = %s;
float dc = 1000;
float alpha = 0.3;
float beta = 0.2;
float bx;
float by;
float bdifx = 0.0; 
float bdify = 0.0; 
float cos_alpha = cos(alpha);
float sin_alpha = sin(alpha);
float cos_beta = cos(beta);
float sin_beta = sin(beta);

float[] lines = { %s };
float[] spheres = { %s };
float[] triangles = { %s };

void rot(x,y,z,p) {
   float x1=cos_alpha*x-sin_alpha*z;
   float y1=y;
   float z1=sin_alpha*x+cos_alpha*z;
   float x2=x1;
   float y2=cos_beta*y1-sin_beta*z1;
   float z2=sin_beta*y1+cos_beta*z1;
   p[0]=x2/(1.0+z2/dc)+dx;
   p[1]=y2/(1.0+z2/dc)+dy;
}

void setup() {
  size(%s, %s);
  stroke(255);
  smooth();
  noLoop();
  drawnow();
}

void drawnow() {
  float[] pa={0,0};
  float[] pb={0,0};
  float[] pc={0,0};
  background(0);
  fill(80);
  noStroke();
  for(var i=0; i<lines.length; i+=10) {
     rot(lines[i+0],lines[i+1],lines[i+2],pa);
     rot(lines[i+3],lines[i+4],lines[i+5],pb);
     strokeWeight(lines[i+6]);
     fill(lines[i+7],lines[i+8],lines[i+9]);
     line(pa[0],pa[1],pb[0],pb[1]); 
  }
  for(var i=0; i<spheres.length; i+=7) {
     fill(spheres[i+4],spheres[i+5],spheres[i+6],90);
     rot(spheres[i+0],spheres[i+1],spheres[i+2],pa);
     ellipse(pa[0],pa[1],spheres[i+3],spheres[i+3]);
  }
  for(var i=0; i<triangles.length; i+=12) {
     fill(triangles[i+9],triangles[i+10],triangles[i+11],90);
     rot(triangles[i+0],triangles[i+1],triangles[i+2],pa);
     rot(triangles[i+3],triangles[i+4],triangles[i+5],pb);
     rot(triangles[i+6],triangles[i+7],triangles[i+8],pc);
     beginShape();
     vertex(pa[0], pa[1]);
     vertex(pb[0], pb[1]);
     vertex(pc[0], pc[1]);
     endShape();
  }
}

void mousePressed() {
  bdifx = mouseX-bx; 
  bdify = mouseY-by;
}

void mouseDragged() {
  bx = mouseX-bdifx; 
  by = mouseY-bdify; 
  alpha = 0.01*bx;
  beta = 0.01*by;   
  %s           
  cos_alpha=cos(alpha);
  sin_alpha=sin(alpha);
  cos_beta=cos(beta);
  sin_beta=sin(beta);      
  drawnow()      
}


</script><canvas width="%spx" height="%spx"></canvas>
""" % (self.width/2,self.height/2,lines, spheres, triangles, self.width, self.height, rotate_call, self.width, self.height)


HTML = r"""
<html>
  <title>
    {{=title}}
  </title>
  <head>
    <script>
(function(){this.Processing=function Processing(aElement,aCode){if(typeof aElement=="string")
aElement=document.getElementById(aElement);var p=buildProcessing(aElement);if(aCode)
p.init(aCode);return p;};function log(){try{console.log.apply(console,arguments);}catch(e){try{opera.postError.apply(opera,arguments);}catch(e){}}}
var parse=Processing.parse=function parse(aCode,p){aCode=aCode.replace(/\/\/ .*\n/g,"\n");aCode=aCode.replace(/([^\s])%([^\s])/g,"$1 % $2");aCode=aCode.replace(/(?:static )?(\w+ )(\w+)\s*(\([^\)]*\)\s*{)/g,function(all,type,name,args){if(name=="if"||name=="for"||name=="while"){return all;}else{return"Processing."+name+" = function "+name+args;}});aCode=aCode.replace(/import \(|import\(/g,"p.Import(");aCode=aCode.replace(/\.length\(\)/g,".length");aCode=aCode.replace(/([\(,]\s*)(\w+)((?:\[\])+| )\s*(\w+\s*[\),])/g,"$1$4");aCode=aCode.replace(/([\(,]\s*)(\w+)((?:\[\])+| )\s*(\w+\s*[\),])/g,"$1$4");aCode=aCode.replace(/new (\w+)((?:\[([^\]]*)\])+)/g,function(all,name,args){return"new ArrayList("+args.slice(1,-1).split("][").join(", ")+")";});aCode=aCode.replace(/(?:static )?\w+\[\]\s*(\w+)\[?\]?\s*=\s*{.*?};/g,function(all){return all.replace(/{/g,"[").replace(/}/g,"]");});var intFloat=/(\n\s*(?:int|float)(?:\[\])?(?:\s*|[^\(]*?,\s*))([a-z]\w*)(;|,)/i;while(intFloat.test(aCode)){aCode=aCode.replace(new RegExp(intFloat),function(all,type,name,sep){return type+" "+name+" = 0"+sep;});}
aCode=aCode.replace(/(?:static )?(\w+)((?:\[\])+| ) *(\w+)\[?\]?(\s*[=,;])/g,function(all,type,arr,name,sep){if(type=="return")
return all;else
return"var "+name+sep;});aCode=aCode.replace(/=\s*{((.|\s)*?)};/g,function(all,data){return"= ["+data.replace(/{/g,"[").replace(/}/g,"]")+"]";});aCode=aCode.replace(/static\s*{((.|\n)*?)}/g,function(all,init){return init;});aCode=aCode.replace(/super\(/g,"superMethod(");var classes=["int","float","boolean","string"];function ClassReplace(all,name,extend,vars,last){classes.push(name);var static="";vars=vars.replace(/final\s+var\s+(\w+\s*=\s*.*?;)/g,function(all,set){static+=" "+name+"."+set;return"";});return"function "+name+"() {with(this){\n  "+
(extend?"var __self=this;function superMethod(){extendClass(__self,arguments,"+extend+");}\n":"")+
vars.replace(/,\s?/g,";\n  this.").replace(/\b(var |final |public )+\s*/g,"this.").replace(/\b(var |final |public )+\s*/g,"this.").replace(/this.(\w+);/g,"this.$1 = null;")+
(extend?"extendClass(this, "+extend+");\n":"")+"<CLASS "+name+" "+static+">"+(typeof last=="string"?last:name+"(");}
var matchClasses=/(?:public |abstract |static )*class (\w+)\s*(?:extends\s*(\w+)\s*)?{\s*((?:.|\n)*?)\b\1\s*\(/g;var matchNoCon=/(?:public |abstract |static )*class (\w+)\s*(?:extends\s*(\w+)\s*)?{\s*((?:.|\n)*?)(Processing)/g;aCode=aCode.replace(matchClasses,ClassReplace);aCode=aCode.replace(matchNoCon,ClassReplace);var matchClass=/<CLASS (\w+) (.*?)>/,m;while((m=aCode.match(matchClass))){var left=RegExp.leftContext,allRest=RegExp.rightContext,rest=nextBrace(allRest),className=m[1],staticVars=m[2]||"";allRest=allRest.slice(rest.length+1);rest=rest.replace(new RegExp("\\b"+className+"\\(([^\\)]*?)\\)\\s*{","g"),function(all,args){args=args.split(/,\s*?/);if(args[0].match(/^\s*$/))
args.shift();var fn="if ( arguments.length == "+args.length+" ) {\n";for(var i=0;i<args.length;i++){fn+="    var "+args[i]+" = arguments["+i+"];\n";}
return fn;});rest=rest.replace(/(?:public )?Processing.\w+ = function (\w+)\((.*?)\)/g,function(all,name,args){return"ADDMETHOD(this, '"+name+"', function("+args+")";});var matchMethod=/ADDMETHOD([\s\S]*?{)/,mc;var methods="";while((mc=rest.match(matchMethod))){var prev=RegExp.leftContext,allNext=RegExp.rightContext,next=nextBrace(allNext);methods+="addMethod"+mc[1]+next+"});"
rest=prev+allNext.slice(next.length+1);}
rest=methods+rest;aCode=left+rest+"\n}}"+staticVars+allRest;}
aCode=aCode.replace(/Processing.\w+ = function addMethod/g,"addMethod");function nextBrace(right){var rest=right;var position=0;var leftCount=1,rightCount=0;while(leftCount!=rightCount){var nextLeft=rest.indexOf("{");var nextRight=rest.indexOf("}");if(nextLeft<nextRight&&nextLeft!=-1){leftCount++;rest=rest.slice(nextLeft+1);position+=nextLeft+1;}else{rightCount++;rest=rest.slice(nextRight+1);position+=nextRight+1;}}
return right.slice(0,position-1);}
aCode=aCode.replace(/\(int\)/g,"0|");aCode=aCode.replace(new RegExp("\\(("+classes.join("|")+")(\\[\\])?\\)","g"),"");aCode=aCode.replace(/(\d+)f[^a-zA-Z0-9]/g,"$1");aCode=aCode.replace(/('[a-zA-Z0-9]')/g,"$1.charCodeAt(0)");aCode=aCode.replace(/#([a-f0-9]{6})/ig,function(m,hex){var num=toNumbers(hex);return"DefaultColor("+num[0]+","+num[1]+","+num[2]+")";});function toNumbers(str){var ret=[];str.replace(/(..)/g,function(str){ret.push(parseInt(str,16));});return ret;}
return aCode;};function buildProcessing(curElement){var p={};p.PI=Math.PI;p.TWO_PI=2*p.PI;p.HALF_PI=p.PI/2;p.P3D=3;p.CORNER=0;p.RADIUS=1;p.CENTER_RADIUS=1;p.CENTER=2;p.POLYGON=2;p.QUADS=5;p.TRIANGLES=6;p.POINTS=7;p.LINES=8;p.TRIANGLE_STRIP=9;p.TRIANGLE_FAN=4;p.QUAD_STRIP=3;p.CORNERS=10;p.CLOSE=true;p.RGB=1;p.HSB=2;p.CENTER=88888880;p.CODED=88888888;p.UP=88888870;p.RIGHT=88888871;p.DOWN=88888872;p.LEFT=88888869;p.codedKeys=[69,70,71,72];var curContext=curElement.getContext("2d");var doFill=true;var doStroke=true;var loopStarted=false;var hasBackground=false;var doLoop=true;var looping=0;var curRectMode=p.CORNER;var curEllipseMode=p.CENTER;var inSetup=false;var inDraw=false;var curBackground="rgba(204,204,204,1)";var curFrameRate=1000;var curShape=p.POLYGON;var curShapeCount=0;var curvePoints=[];var curTightness=0;var opacityRange=255;var redRange=255;var greenRange=255;var blueRange=255;var pathOpen=false;var mousePressed=false;var keyPressed=false;var firstX,firstY,secondX,secondY,prevX,prevY;var curColorMode=p.RGB;var curTint=-1;var curTextSize=12;var curTextFont="Arial";var getLoaded=false;var start=(new Date).getTime();p.ln="";p.glyphTable={};p.pmouseX=0;p.pmouseY=0;p.mouseX=0;p.mouseY=0;p.mouseButton=0;p.mouseDown=false;p.mouseClicked=undefined;p.mouseDragged=undefined;p.mouseMoved=undefined;p.mousePressed=undefined;p.mouseReleased=undefined;p.keyPressed=undefined;p.keyReleased=undefined;p.draw=undefined;p.setup=undefined;p.width=curElement.width-0;p.height=curElement.height-0;p.frameCount=0;p.DefaultColor=function(aValue1,aValue2,aValue3){var tmpColorMode=curColorMode;curColorMode=p.RGB;var c=p.color(((aValue1/255)*redRange),((aValue2/255)*greenRange),((aValue3/255)*blueRange));curColorMode=tmpColorMode;return c;}
p.ajax=function(url){if(window.XMLHttpRequest){AJAX=new XMLHttpRequest();}
else{AJAX=new ActiveXObject("Microsoft.XMLHTTP");}
if(AJAX){AJAX.open("GET",url,false);AJAX.send(null);return AJAX.responseText;}else{return false;}}
p.Import=function Import(lib){eval(p.ajax(lib));}
p.loadStrings=function loadStrings(url){return p.ajax(url).split("\n");};p.color=function color(aValue1,aValue2,aValue3,aValue4){var aColor="";if(arguments.length==3){aColor=p.color(aValue1,aValue2,aValue3,opacityRange);}else if(arguments.length==4){var a=aValue4/opacityRange;a=isNaN(a)?1:a;if(curColorMode==p.HSB){var rgb=HSBtoRGB(aValue1,aValue2,aValue3);var r=rgb[0],g=rgb[1],b=rgb[2];}else{var r=getColor(aValue1,redRange);var g=getColor(aValue2,greenRange);var b=getColor(aValue3,blueRange);}
aColor="rgba("+r+","+g+","+b+","+a+")";}else if(typeof aValue1=="string"){aColor=aValue1;if(arguments.length==2){var c=aColor.split(",");c[3]=(aValue2/opacityRange)+")";aColor=c.join(",");}}else if(arguments.length==2){aColor=p.color(aValue1,aValue1,aValue1,aValue2);}else if(typeof aValue1=="number"){aColor=p.color(aValue1,aValue1,aValue1,opacityRange);}else{aColor=p.color(redRange,greenRange,blueRange,opacityRange);}
function HSBtoRGB(h,s,b){h=(h/redRange)*360;s=(s/greenRange)*100;b=(b/blueRange)*100;var br=Math.round(b/100*255);if(s==0){return[br,br,br];}else{var hue=h%360;var f=hue%60;var p=Math.round((b*(100-s))/10000*255);var q=Math.round((b*(6000-s*f))/600000*255);var t=Math.round((b*(6000-s*(60-f)))/600000*255);switch(Math.floor(hue/60)){case 0:return[br,t,p];case 1:return[q,br,p];case 2:return[p,br,t];case 3:return[p,q,br];case 4:return[t,p,br];case 5:return[br,p,q];}}}
function getColor(aValue,range){return Math.round(255*(aValue/range));}
return aColor;}
p.red=function(aColor){return parseInt(verifyChannel(aColor).slice(5));};p.green=function(aColor){return parseInt(verifyChannel(aColor).split(",")[1]);};p.blue=function(aColor){return parseInt(verifyChannel(aColor).split(",")[2]);};p.alpha=function(aColor){return parseInt(parseFloat(verifyChannel(aColor).split(",")[3])*255);};function verifyChannel(aColor){if(aColor.constructor==Array){return aColor;}else{return p.color(aColor);}}
p.lerpColor=function lerpColor(c1,c2,amt){var colors1=p.color(c1).split(",");var r1=parseInt(colors1[0].split("(")[1]);var g1=parseInt(colors1[1]);var b1=parseInt(colors1[2]);var a1=parseFloat(colors1[3].split(")")[0]);var colors2=p.color(c2).split(",");var r2=parseInt(colors2[0].split("(")[1]);var g2=parseInt(colors2[1]);var b2=parseInt(colors2[2]);var a2=parseFloat(colors2[3].split(")")[0]);var r=parseInt(p.lerp(r1,r2,amt));var g=parseInt(p.lerp(g1,g2,amt));var b=parseInt(p.lerp(b1,b2,amt));var a=parseFloat(p.lerp(a1,a2,amt));aColor="rgba("+r+","+g+","+b+","+a+")";return aColor;}
p.nf=function(num,pad){var str=""+num;while(pad-str.length)
str="0"+str;return str;};p.AniSprite=function(prefix,frames){this.images=[];this.pos=0;for(var i=0;i<frames;i++){this.images.push(prefix+p.nf(i,(""+frames).length)+".gif");}
this.display=function(x,y){p.image(this.images[this.pos],x,y);if(++this.pos>=frames)
this.pos=0;};this.getWidth=function(){return getImage(this.images[0]).width;};this.getHeight=function(){return getImage(this.images[0]).height;};};function buildImageObject(obj){var pixels=obj.data;var data=p.createImage(obj.width,obj.height);if(data.__defineGetter__&&data.__lookupGetter__&&!data.__lookupGetter__("pixels")){var pixelsDone;data.__defineGetter__("pixels",function(){if(pixelsDone)
return pixelsDone;pixelsDone=[];for(var i=0;i<pixels.length;i+=4){pixelsDone.push(p.color(pixels[i],pixels[i+1],pixels[i+2],pixels[i+3]));}
return pixelsDone;});}else{data.pixels=[];for(var i=0;i<pixels.length;i+=4){data.pixels.push(p.color(pixels[i],pixels[i+1],pixels[i+2],pixels[i+3]));}}
return data;}
p.createImage=function createImage(w,h,mode){var data={};data.width=w;data.height=h;data.data=[];if(curContext.createImageData){data=curContext.createImageData(w,h);}
data.pixels=new Array(w*h);data.get=function(x,y){return this.pixels[w*y+x];};data._mask=null;data.mask=function(img){this._mask=img;};data.loadPixels=function(){};data.updatePixels=function(){};return data;};p.createGraphics=function createGraphics(w,h){var canvas=document.createElement("canvas");var ret=buildProcessing(canvas);ret.size(w,h);ret.canvas=canvas;return ret;};p.beginDraw=function beginDraw(){};p.endDraw=function endDraw(){};p.tint=function tint(rgb,a){curTint=a;};function getImage(img){if(typeof img=="string"){return document.getElementById(img);}
if(img.img||img.canvas){return img.img||img.canvas;}
for(var i=0,l=img.pixels.length;i<l;i++){var pos=i*4;var c=(img.pixels[i]||"rgba(0,0,0,1)").slice(5,-1).split(",");img.data[pos]=parseInt(c[0]);img.data[pos+1]=parseInt(c[1]);img.data[pos+2]=parseInt(c[2]);img.data[pos+3]=parseFloat(c[3])*100;}
var canvas=document.createElement("canvas")
canvas.width=img.width;canvas.height=img.height;var context=canvas.getContext("2d");context.putImageData(img,0,0);img.canvas=canvas;return canvas;}
p.image=function image(img,x,y,w,h){x=x||0;y=y||0;var obj=getImage(img);if(curTint>=0){var oldAlpha=curContext.globalAlpha;curContext.globalAlpha=curTint/opacityRange;}
if(arguments.length==3){curContext.drawImage(obj,x,y);}else{curContext.drawImage(obj,x,y,w,h);}
if(curTint>=0){curContext.globalAlpha=oldAlpha;}
if(img._mask){var oldComposite=curContext.globalCompositeOperation;curContext.globalCompositeOperation="darker";p.image(img._mask,x,y);curContext.globalCompositeOperation=oldComposite;}};p.exit=function exit(){clearInterval(looping);};p.save=function save(file){};p.loadImage=function loadImage(file){var img=document.getElementById(file);if(!img)
return;var h=img.height,w=img.width;var canvas=document.createElement("canvas");canvas.width=w;canvas.height=h;var context=canvas.getContext("2d");context.drawImage(img,0,0);var data=buildImageObject(context.getImageData(0,0,w,h));data.img=img;return data;};p.loadFont=function loadFont(name){if(name.indexOf(".svg")==-1){return{name:name,width:function(str){if(curContext.mozMeasureText)
return curContext.mozMeasureText(typeof str=="number"?String.fromCharCode(str):str)/curTextSize;else
return 0;}};}else{var font=p.loadGlyphs(name);return{name:name,glyph:true,units_per_em:font.units_per_em,horiz_adv_x:1/font.units_per_em*font.horiz_adv_x,ascent:font.ascent,descent:font.descent,width:function(str){var width=0;var len=str.length;for(var i=0;i<len;i++){try{width+=parseFloat(p.glyphLook(p.glyphTable[name],str[i]).horiz_adv_x);}
catch(e){;}}
return width/p.glyphTable[name].units_per_em;}}}};p.textFont=function textFont(name,size){curTextFont=name;p.textSize(size);};p.textSize=function textSize(size){if(size){curTextSize=size;}};p.textAlign=function textAlign(){};p.glyphLook=function glyphLook(font,chr){try{switch(chr){case"1":return font["one"];break;case"2":return font["two"];break;case"3":return font["three"];break;case"4":return font["four"];break;case"5":return font["five"];break;case"6":return font["six"];break;case"7":return font["seven"];break;case"8":return font["eight"];break;case"9":return font["nine"];break;case"0":return font["zero"];break;case" ":return font["space"];break;case"$":return font["dollar"];break;case"!":return font["exclam"];break;case'"':return font["quotedbl"];break;case"#":return font["numbersign"];break;case"%":return font["percent"];break;case"&":return font["ampersand"];break;case"'":return font["quotesingle"];break;case"(":return font["parenleft"];break;case")":return font["parenright"];break;case"*":return font["asterisk"];break;case"+":return font["plus"];break;case",":return font["comma"];break;case"-":return font["hyphen"];break;case".":return font["period"];break;case"/":return font["slash"];break;case"_":return font["underscore"];break;case":":return font["colon"];break;case";":return font["semicolon"];break;case"<":return font["less"];break;case"=":return font["equal"];break;case">":return font["greater"];break;case"?":return font["question"];break;case"@":return font["at"];break;case"[":return font["bracketleft"];break;case"\\":return font["backslash"];break;case"]":return font["bracketright"];break;case"^":return font["asciicircum"];break;case"`":return font["grave"];break;case"{":return font["braceleft"];break;case"|":return font["bar"];break;case"}":return font["braceright"];break;case"~":return font["asciitilde"];break;default:return font[chr];break;}}catch(e){;}}
p.text=function text(str,x,y){if(!curTextFont.glyph){if(str&&curContext.mozDrawText){curContext.save();curContext.mozTextStyle=curTextSize+"px "+curTextFont.name;curContext.translate(x,y);curContext.mozDrawText(typeof str=="number"?String.fromCharCode(str):str);curContext.restore();}}else{var font=p.glyphTable[curTextFont.name];curContext.save();curContext.translate(x,y+curTextSize);var upem=font["units_per_em"];var newScale=1/upem*curTextSize;curContext.scale(newScale,newScale);var len=str.length;for(var i=0;i<len;i++){try{p.glyphLook(font,str[i]).draw();}
catch(e){;}}
curContext.restore();}};p.loadGlyphs=function loadGlyph(url){var loadXML=function loadXML(){try{var xmlDoc=new ActiveXObject("Microsoft.XMLDOM");}
catch(e){try{xmlDoc=document.implementation.createDocument("","",null);}
catch(e){p.println(e.message);return;}}
try{xmlDoc.async=false;xmlDoc.load(url);parse(xmlDoc.getElementsByTagName("svg")[0]);}
catch(e){try{try{console.log(e)}catch(e){alert(e);}
var xmlhttp=new window.XMLHttpRequest();xmlhttp.open("GET",url,false);xmlhttp.send(null);parse(xmlhttp.responseXML.documentElement);}catch(e){}}}
var regex=function regex(needle,hay){var regexp=new RegExp(needle,"g");var i=0;var results=[];while(results[i]=regexp.exec(hay)){i++;}
return results;}
var parse=function parse(svg){var font=svg.getElementsByTagName("font");p.glyphTable[url]["horiz_adv_x"]=font[0].getAttribute("horiz-adv-x");var font_face=svg.getElementsByTagName("font-face")[0];p.glyphTable[url]["units_per_em"]=parseFloat(font_face.getAttribute("units-per-em"));p.glyphTable[url]["ascent"]=parseFloat(font_face.getAttribute("ascent"));p.glyphTable[url]["descent"]=parseFloat(font_face.getAttribute("descent"));var getXY="[0-9\-]+";var glyph=svg.getElementsByTagName("glyph");var len=glyph.length;for(var i=0;i<len;i++){var unicode=glyph[i].getAttribute("unicode");var name=glyph[i].getAttribute("glyph-name");var horiz_adv_x=glyph[i].getAttribute("horiz-adv-x");if(horiz_adv_x==null){var horiz_adv_x=p.glyphTable[url]['horiz_adv_x'];}
var buildPath=function buildPath(d){var c=regex("[A-Za-z][0-9\- ]+|Z",d);var path="var path={draw:function(){curContext.beginPath();";var x=0,y=0,cx=0,cy=0,nx=0,ny=0,d=0,a=0,lastCom="";var lenC=c.length-1;for(var j=0;j<lenC;j++){var com=c[j][0];var xy=regex(getXY,com);switch(com[0]){case"M":x=parseFloat(xy[0][0]);y=parseFloat(xy[1][0]);path+="curContext.moveTo("+(x)+","+(-y)+");";break;case"L":x=parseFloat(xy[0][0]);y=parseFloat(xy[1][0]);path+="curContext.lineTo("+(x)+","+(-y)+");";break;case"H":x=parseFloat(xy[0][0]);path+="curContext.lineTo("+(x)+","+(-y)+");";break;case"V":y=parseFloat(xy[0][0]);path+="curContext.lineTo("+(x)+","+(-y)+");";break;case"T":nx=parseFloat(xy[0][0]);ny=parseFloat(xy[1][0]);if(lastCom=="Q"||lastCom=="T"){d=Math.sqrt(Math.pow(x-cx,2)+Math.pow(cy-y,2));a=Math.PI+Math.atan2(cx-x,cy-y);cx=x+(Math.sin(a)*(d));cy=y+(Math.cos(a)*(d));}else{cx=x;cy=y;}
path+="curContext.quadraticCurveTo("+(cx)+","+(-cy)+","+(nx)+","+(-ny)+");";x=nx;y=ny;break;case"Q":cx=parseFloat(xy[0][0]);cy=parseFloat(xy[1][0]);nx=parseFloat(xy[2][0]);ny=parseFloat(xy[3][0]);path+="curContext.quadraticCurveTo("+(cx)+","+(-cy)+","+(nx)+","+(-ny)+");";x=nx;y=ny;break;case"Z":path+="curContext.closePath();";break;}
lastCom=com[0];}
path+="curContext.translate("+(horiz_adv_x)+",0);";path+="doStroke?curContext.stroke():0;";path+="doFill?curContext.fill():0;";path+="}}";return path;}
var d=glyph[i].getAttribute("d");if(d!==undefined){var path=buildPath(d);eval(path);p.glyphTable[url][name]={name:name,unicode:unicode,horiz_adv_x:horiz_adv_x,draw:path.draw}}}}
p.glyphTable[url]={};loadXML(url);return p.glyphTable[url];}
p.lnPrinted=function lnPrinted(){};p.printed=function printed(){};p.println=function println(){var Caller=arguments.callee.caller.name.toString();if(arguments.length>1){Caller!="print"?p.ln=arguments:p.ln=arguments[0];}else{p.ln=arguments[0];}
Caller=="print"?p.printed(arguments):p.lnPrinted();};p.print=function print(){p.println(arguments[0])};p.char=function char(key){return key;};p.map=function map(value,istart,istop,ostart,ostop){return ostart+(ostop-ostart)*((value-istart)/(istop-istart));};String.prototype.replaceAll=function(re,replace){return this.replace(new RegExp(re,"g"),replace);};p.Point=function Point(x,y){this.x=x;this.y=y;this.copy=function(){return new Point(x,y);}};p.Random=function(){var haveNextNextGaussian=false;var nextNextGaussian;this.nextGaussian=function(){if(haveNextNextGaussian){haveNextNextGaussian=false;return nextNextGaussian;}else{var v1,v2,s;do{v1=2*p.random(1)-1;v2=2*p.random(1)-1;s=v1*v1+v2*v2;}while(s>=1||s==0);var multiplier=Math.sqrt(-2*Math.log(s)/s);nextNextGaussian=v2*multiplier;haveNextNextGaussian=true;return v1*multiplier;}};};p.ArrayList=function ArrayList(size,size2,size3){var array=new Array(0|size);if(size2){for(var i=0;i<size;i++){array[i]=[];for(var j=0;j<size2;j++){var a=array[i][j]=size3?new Array(size3):0;for(var k=0;k<size3;k++){a[k]=0;}}}}else{for(var i=0;i<size;i++){array[i]=0;}}
array.size=function(){return this.length;};array.get=function(i){return this[i];};array.remove=function(i){return this.splice(i,1);};array.add=function(item){return this.push(item);};array.clone=function(){var a=new ArrayList(size);for(var i=0;i<size;i++){a[i]=this[i];}
return a;};array.isEmpty=function(){return!this.length;};array.clear=function(){this.length=0;};return array;};p.colorMode=function colorMode(mode,range1,range2,range3,range4){curColorMode=mode;if(arguments.length>=4){redRange=range1;greenRange=range2;blueRange=range3;}
if(arguments.length==5){opacityRange=range4;}
if(arguments.length==2){p.colorMode(mode,range1,range1,range1,range1);}};p.beginShape=function beginShape(type){curShape=type;curShapeCount=0;curvePoints=[];};p.endShape=function endShape(close){if(curShapeCount!=0){if(close||doFill)
curContext.lineTo(firstX,firstY);if(doFill)
curContext.fill();if(doStroke)
curContext.stroke();curContext.closePath();curShapeCount=0;pathOpen=false;}
if(pathOpen){if(doFill)
curContext.fill();if(doStroke)
curContext.stroke();curContext.closePath();curShapeCount=0;pathOpen=false;}};p.vertex=function vertex(x,y,x2,y2,x3,y3){if(curShapeCount==0&&curShape!=p.POINTS){pathOpen=true;curContext.beginPath();curContext.moveTo(x,y);firstX=x;firstY=y;}else{if(curShape==p.POINTS){p.point(x,y);}else if(arguments.length==2){if(curShape!=p.QUAD_STRIP||curShapeCount!=2)
curContext.lineTo(x,y);if(curShape==p.TRIANGLE_STRIP){if(curShapeCount==2){p.endShape(p.CLOSE);pathOpen=true;curContext.beginPath();curContext.moveTo(prevX,prevY);curContext.lineTo(x,y);curShapeCount=1;}
firstX=prevX;firstY=prevY;}
if(curShape==p.TRIANGLE_FAN&&curShapeCount==2){p.endShape(p.CLOSE);pathOpen=true;curContext.beginPath();curContext.moveTo(firstX,firstY);curContext.lineTo(x,y);curShapeCount=1;}
if(curShape==p.QUAD_STRIP&&curShapeCount==3){curContext.lineTo(prevX,prevY);p.endShape(p.CLOSE);pathOpen=true;curContext.beginPath();curContext.moveTo(prevX,prevY);curContext.lineTo(x,y);curShapeCount=1;}
if(curShape==p.QUAD_STRIP){firstX=secondX;firstY=secondY;secondX=prevX;secondY=prevY;}}else if(arguments.length==4){if(curShapeCount>1){curContext.moveTo(prevX,prevY);curContext.quadraticCurveTo(firstX,firstY,x,y);curShapeCount=1;}}else if(arguments.length==6){curContext.bezierCurveTo(x,y,x2,y2,x3,y3);}}
prevX=x;prevY=y;curShapeCount++;if(curShape==p.LINES&&curShapeCount==2||(curShape==p.TRIANGLES)&&curShapeCount==3||(curShape==p.QUADS)&&curShapeCount==4){p.endShape(p.CLOSE);}};p.curveVertex=function(x,y,x2,y2){if(curvePoints.length<3){curvePoints.push([x,y]);}else{var b=[],s=1-curTightness;curvePoints.push([x,y]);b[0]=[curvePoints[1][0],curvePoints[1][1]];b[1]=[curvePoints[1][0]+(s*curvePoints[2][0]-s*curvePoints[0][0])/6,curvePoints[1][1]+(s*curvePoints[2][1]-s*curvePoints[0][1])/6];b[2]=[curvePoints[2][0]+(s*curvePoints[1][0]-s*curvePoints[3][0])/6,curvePoints[2][1]+(s*curvePoints[1][1]-s*curvePoints[3][1])/6];b[3]=[curvePoints[2][0],curvePoints[2][1]];if(!pathOpen){p.vertex(b[0][0],b[0][1]);}else{curShapeCount=1;}
p.vertex(b[1][0],b[1][1],b[2][0],b[2][1],b[3][0],b[3][1]);curvePoints.shift();}};p.curveTightness=function(tightness){curTightness=tightness;};p.bezierVertex=p.vertex;p.rectMode=function rectMode(aRectMode){curRectMode=aRectMode;};p.imageMode=function(){};p.ellipseMode=function ellipseMode(aEllipseMode){curEllipseMode=aEllipseMode;};p.dist=function dist(x1,y1,x2,y2){return Math.sqrt(Math.pow(x2-x1,2)+Math.pow(y2-y1,2));};p.year=function year(){return(new Date).getYear()+1900;};p.month=function month(){return(new Date).getMonth();};p.day=function day(){return(new Date).getDay();};p.hour=function hour(){return(new Date).getHours();};p.minute=function minute(){return(new Date).getMinutes();};p.second=function second(){return(new Date).getSeconds();};p.millis=function millis(){return(new Date).getTime()-start;};p.ortho=function ortho(){};p.translate=function translate(x,y){curContext.translate(x,y);};p.scale=function scale(x,y){curContext.scale(x,y||x);};p.rotate=function rotate(aAngle){curContext.rotate(aAngle);};p.pushMatrix=function pushMatrix(){curContext.save();};p.popMatrix=function popMatrix(){curContext.restore();};p.redraw=function redraw(){if(hasBackground){p.background();}
p.frameCount++;inDraw=true;p.pushMatrix();p.draw();p.popMatrix();inDraw=false;};p.loop=function loop(){if(loopStarted)
return;looping=setInterval(function(){try{p.redraw();}
catch(e){clearInterval(looping);throw e;}},1000/curFrameRate);loopStarted=true;};p.frameRate=function frameRate(aRate){curFrameRate=aRate;};p.background=function background(img){if(arguments.length){if(img&&img.img){curBackground=img;}else{curBackground=p.color.apply(this,arguments);}}
if(curBackground.img){p.image(curBackground,0,0);}else{var oldFill=curContext.fillStyle;curContext.fillStyle=curBackground+"";curContext.fillRect(0,0,p.width,p.height);curContext.fillStyle=oldFill;}};p.clear=function clear(x,y,width,height){arguments.length==0?curContext.clearRect(0,0,p.width,p.height):curContext.clearRect(x,y,width,height);}
p.str=function str(aNumber){return aNumber+'';}
p.sq=function sq(aNumber){return aNumber*aNumber;};p.sqrt=function sqrt(aNumber){return Math.sqrt(aNumber);};p.ngsqrt=function ngsqrt(aNumber){if(aNumber<=0){return Math.sqrt(-aNumber);}else{return Math.sqrt(aNumber);}};p.int=function int(aNumber){return Math.floor(aNumber);};p.min=function min(aNumber,aNumber2){return Math.min(aNumber,aNumber2);};p.max=function max(aNumber,aNumber2){return Math.max(aNumber,aNumber2);};p.ceil=function ceil(aNumber){return Math.ceil(aNumber);};p.round=function round(aNumber){return Math.round(aNumber);};p.norm=function norm(aNumber,low,high){var range=high-low;return((1/range)*aNumber)-((1/range)*low);};p.lerp=function lerp(value1,value2,amt){var range=value2-value1;return(range*amt)+value1;}
p.floor=function floor(aNumber){return Math.floor(aNumber);};p.float=function float(aNumber){return parseFloat(aNumber);};p.byte=function byte(aNumber){return aNumber||0;};p.random=function random(aMin,aMax){return arguments.length==2?aMin+(Math.random()*(aMax-aMin)):Math.random()*aMin;};p.noise=function(x,y,z){return arguments.length>=2?PerlinNoise_2D(x,y):PerlinNoise_2D(x,x);};function Noise(x,y){var n=x+y*57;n=(n<<13)^n;return Math.abs(1.0-(((n*((n*n*15731)+789221)+1376312589)&0x7fffffff)/1073741824.0));};function SmoothedNoise(x,y){var corners=(Noise(x-1,y-1)+Noise(x+1,y-1)+Noise(x-1,y+1)+Noise(x+1,y+1))/16;var sides=(Noise(x-1,y)+Noise(x+1,y)+Noise(x,y-1)+Noise(x,y+1))/8;var center=Noise(x,y)/4;return corners+sides+center;};function InterpolatedNoise(x,y){var integer_X=Math.floor(x);var fractional_X=x-integer_X;var integer_Y=Math.floor(y);var fractional_Y=y-integer_Y;var v1=SmoothedNoise(integer_X,integer_Y);var v2=SmoothedNoise(integer_X+1,integer_Y);var v3=SmoothedNoise(integer_X,integer_Y+1);var v4=SmoothedNoise(integer_X+1,integer_Y+1);var i1=Interpolate(v1,v2,fractional_X);var i2=Interpolate(v3,v4,fractional_X);return Interpolate(i1,i2,fractional_Y);}
function PerlinNoise_2D(x,y){var total=0;var p=0.25;var n=3;for(var i=0;i<=n;i++){var frequency=Math.pow(2,i);var amplitude=Math.pow(p,i);total=total+InterpolatedNoise(x*frequency,y*frequency)*amplitude;}
return total;}
function Interpolate(a,b,x){var ft=x*p.PI;var f=(1-p.cos(ft))*.5;return a*(1-f)+b*f;}
p.abs=function abs(aNumber){return Math.abs(aNumber);};p.cos=function cos(aNumber){return Math.cos(aNumber);};p.sin=function sin(aNumber){return Math.sin(aNumber);};p.pow=function pow(aNumber,aExponent){return Math.pow(aNumber,aExponent);};p.constrain=function constrain(aNumber,aMin,aMax){return Math.min(Math.max(aNumber,aMin),aMax);};p.sqrt=function sqrt(aNumber){return Math.sqrt(aNumber);};p.atan2=function atan2(aNumber,aNumber2){return Math.atan2(aNumber,aNumber2);};p.radians=function radians(aAngle){return(aAngle/180)*p.PI;};p.degrees=function degrees(aAngle){aAngle=(aAngle*180)/p.PI;if(aAngle<0){aAngle=360+aAngle}
return aAngle;};p.size=function size(aWidth,aHeight){var fillStyle=curContext.fillStyle;var strokeStyle=curContext.strokeStyle;curElement.width=p.width=aWidth;curElement.height=p.height=aHeight;curContext.fillStyle=fillStyle;curContext.strokeStyle=strokeStyle;};p.noStroke=function noStroke(){doStroke=false;};p.noFill=function noFill(){doFill=false;};p.smooth=function smooth(){};p.noSmooth=function noSmooth(){};p.noLoop=function noLoop(){doLoop=false;};p.fill=function fill(){doFill=true;curContext.fillStyle=p.color.apply(this,arguments);};p.stroke=function stroke(){doStroke=true;curContext.strokeStyle=p.color.apply(this,arguments);};p.strokeWeight=function strokeWeight(w){curContext.lineWidth=w;};p.point=function point(x,y){var oldFill=curContext.fillStyle;curContext.fillStyle=curContext.strokeStyle;curContext.fillRect(Math.round(x),Math.round(y),1,1);curContext.fillStyle=oldFill;};p.get=function get(x,y){if(arguments.length==0){var c=p.createGraphics(p.width,p.height);c.image(curContext,0,0);return c;}
if(!getLoaded){getLoaded=buildImageObject(curContext.getImageData(0,0,p.width,p.height));}
return getLoaded.get(x,y);};p.set=function set(x,y,obj){if(obj&&obj.img){p.image(obj,x,y);}else{var oldFill=curContext.fillStyle;var color=obj;curContext.fillStyle=color;curContext.fillRect(Math.round(x),Math.round(y),1,1);curContext.fillStyle=oldFill;}};p.arc=function arc(x,y,width,height,start,stop){if(width<=0)
return;if(curEllipseMode==p.CORNER){x+=width/2;y+=height/2;}
curContext.moveTo(x,y);curContext.beginPath();curContext.arc(x,y,curEllipseMode==p.CENTER_RADIUS?width:width/2,start,stop,false);if(doStroke)
curContext.stroke();curContext.lineTo(x,y);if(doFill)
curContext.fill();curContext.closePath();};p.line=function line(x1,y1,x2,y2){curContext.lineCap="round";curContext.beginPath();curContext.moveTo(x1||0,y1||0);curContext.lineTo(x2||0,y2||0);curContext.stroke();curContext.closePath();};p.bezier=function bezier(x1,y1,x2,y2,x3,y3,x4,y4){curContext.lineCap="butt";curContext.beginPath();curContext.moveTo(x1,y1);curContext.bezierCurveTo(x2,y2,x3,y3,x4,y4);curContext.stroke();curContext.closePath();};p.triangle=function triangle(x1,y1,x2,y2,x3,y3){p.beginShape();p.vertex(x1,y1);p.vertex(x2,y2);p.vertex(x3,y3);p.endShape();};p.quad=function quad(x1,y1,x2,y2,x3,y3,x4,y4){curContext.lineCap="square";p.beginShape();p.vertex(x1,y1);p.vertex(x2,y2);p.vertex(x3,y3);p.vertex(x4,y4);p.endShape();};p.rect=function rect(x,y,width,height){if(width==0&&height==0)
return;curContext.beginPath();var offsetStart=0;var offsetEnd=0;if(curRectMode==p.CORNERS){width-=x;height-=y;}
if(curRectMode==p.RADIUS){width*=2;height*=2;}
if(curRectMode==p.CENTER||curRectMode==p.RADIUS){x-=width/2;y-=height/2;}
curContext.rect(Math.round(x)-offsetStart,Math.round(y)-offsetStart,Math.round(width)+offsetEnd,Math.round(height)+offsetEnd);if(doFill)
curContext.fill();if(doStroke)
curContext.stroke();curContext.closePath();};p.ellipse=function ellipse(x,y,width,height){x=x||0;y=y||0;if(width<=0&&height<=0)
return;curContext.beginPath();if(curEllipseMode==p.RADIUS){width*=2;height*=2;}
var offsetStart=0;if(width==height){curContext.arc(x-offsetStart,y-offsetStart,width/2,0,Math.PI*2,false);}else{var w=width/2;var h=height/2;var C=0.5522847498307933;var c_x=C*w;var c_y=C*h;curContext.moveTo(x+w,y);curContext.bezierCurveTo(x+w,y-c_y,x+c_x,y-h,x,y-h);curContext.bezierCurveTo(x-c_x,y-h,x-w,y-c_y,x-w,y);curContext.bezierCurveTo(x-w,y+c_y,x-c_x,y+h,x,y+h);curContext.bezierCurveTo(x+c_x,y+h,x+w,y+c_y,x+w,y);}
if(doFill)
curContext.fill();if(doStroke)
curContext.stroke();curContext.closePath();};p.cursor=function(mode){document.body.style.cursor=mode;}
p.link=function(href,target){window.location=href;};p.loadPixels=function(){p.pixels=buildImageObject(curContext.getImageData(0,0,p.width,p.height)).pixels;};p.updatePixels=function(){var colors=/(\d+),(\d+),(\d+),(\d+)/;var pixels={};pixels.width=p.width;pixels.height=p.height;pixels.data=[];if(curContext.createImageData){pixels=curContext.createImageData(p.width,p.height);}
var data=pixels.data;var pos=0;for(var i=0,l=p.pixels.length;i<l;i++){var c=(p.pixels[i]||"rgba(0,0,0,1)").match(colors);data[pos]=parseInt(c[1]);data[pos+1]=parseInt(c[2]);data[pos+2]=parseInt(c[3]);data[pos+3]=parseFloat(c[4])*255;pos+=4;}
curContext.putImageData(pixels,0,0);};p.extendClass=function extendClass(obj,args,fn){if(arguments.length==3){fn.apply(obj,args);}else{args.call(obj);}};p.addMethod=function addMethod(object,name,fn){if(object[name]){var args=fn.length;var oldfn=object[name];object[name]=function(){if(arguments.length==args)
return fn.apply(this,arguments);else
return oldfn.apply(this,arguments);};}else{object[name]=fn;}};p.init=function init(code){p.stroke(0);p.fill(255);curContext.translate(0.5,0.5);if(code){(function(Processing){with(p){eval(parse(code,p));}})(p);}
if(p.setup){inSetup=true;p.setup();}
inSetup=false;if(p.draw){if(!doLoop){p.redraw();}else{p.loop();}}
attach(curElement,"mousemove",function(e){var scrollX=window.scrollX!=null?window.scrollX:window.pageXOffset;var scrollY=window.scrollY!=null?window.scrollY:window.pageYOffset;p.pmouseX=p.mouseX;p.pmouseY=p.mouseY;p.mouseX=e.clientX-curElement.offsetLeft+scrollX;p.mouseY=e.clientY-curElement.offsetTop+scrollY;if(p.mouseMoved){p.mouseMoved();}
if(mousePressed&&p.mouseDragged){p.mouseDragged();}});attach(curElement,"mouseout",function(e){p.cursor("auto");});attach(curElement,"mousedown",function(e){mousePressed=true;switch(e.which){case 1:p.mouseButton=p.LEFT;break;case 2:p.mouseButton=p.CENTER;break;case 3:p.mouseButton=p.RIGHT;break;}
p.mouseDown=true;if(typeof p.mousePressed=="function"){p.mousePressed();}else{p.mousePressed=true;}});attach(curElement,"contextmenu",function(e){e.preventDefault();e.stopPropagation();});attach(curElement,"mouseup",function(e){mousePressed=false;if(p.mouseClicked){p.mouseClicked();}
if(typeof p.mousePressed!="function"){p.mousePressed=false;}
if(p.mouseReleased){p.mouseReleased();}});attach(document,"keydown",function(e){keyPressed=true;p.key=e.keyCode+32;var i;for(i=0;i<p.codedKeys.length;i++){if(p.key==p.codedKeys[i]){switch(p.key){case 70:p.keyCode=p.UP;break;case 71:p.keyCode=p.RIGHT;break;case 72:p.keyCode=p.DOWN;break;case 69:p.keyCode=p.LEFT;break;}
p.key=p.CODED;}}
if(e.shiftKey){p.key=String.fromCharCode(p.key).toUpperCase().charCodeAt(0);}
if(typeof p.keyPressed=="function"){p.keyPressed();}else{p.keyPressed=true;}});attach(document,"keyup",function(e){keyPressed=false;if(typeof p.keyPressed!="function"){p.keyPressed=false;}
if(p.keyReleased){p.keyReleased();}});function attach(elem,type,fn){if(elem.addEventListener)
elem.addEventListener(type,fn,false);else
elem.attachEvent("on"+type,fn);}};return p;}})();
    </script>
    <script>
/*
 * This code searches for all the <script type="application/processing" target="canvasid">
 * in your page and loads each script in the target canvas with the proper id.
 * It is useful to smooth the process of adding Processing code in your page and starting
 * the Processing.js engine.
 */

if ( window.addEventListener ) {
	window.addEventListener("load", function() {
		var scripts = document.getElementsByTagName("script");
		
		for ( var i = 0; i < scripts.length; i++ ) {
			if ( scripts[i].type == "application/processing" ) {
				var src = scripts[i].src, canvas = scripts[i].nextSibling;
	
				if ( src && src.indexOf("#") ) {
					canvas = document.getElementById( src.substr( src.indexOf("#") + 1 ) );
				} else {
					while ( canvas && canvas.nodeName.toUpperCase() != "CANVAS" )
						canvas = canvas.nextSibling;
				}

				if ( canvas ) {
					Processing(canvas, scripts[i].text);
				}
			}
		}
	}, false);
}

    </script>
  </head>
  <body bgcolor="black">
    <center>
      {{=obj}}
    </center>
  </body>
</html>
"""

def process(path,options):
    if not os.path.exists(path):
        print 'file %s does not exist' % path
        sys.exit(0)
    filename = os.path.basename(path)
    points = read_vtk(path)
    p.isosurface(points,alpha=float(options.upper),
                 red = int(options.upper_red),
                 green = int(options.upper_green),
                 blue = int(options.upper_blue))
    p.isosurface(points,alpha=float(options.lower),
                 red = int(options.lower_red),
                 green = int(options.lower_green),
                 blue = int(options.lower_blue))
    output = path+'.html'
    html = HTML.replace('{{=title}}',filename).replace('{{=obj}}',p.xml())
    open(output,'wb').write(html)
    print 'file %s written' % output

if __name__=='__main__':
    import optparse
    usage = 'usage: qcdutils_vtk.py filename.vtk'
    version= ""
    parser = optparse.OptionParser(usage, None, optparse.Option, version)
    parser.add_option('-u',
                      '--upper-threshold',
                      default='0.7',
                      dest='upper',
                      help='treshold for isosurface')
    parser.add_option('-l',
                      '--lower-threshold',
                      default='0.3',
                      dest='lower',
                      help='treshold for isosurface')
    parser.add_option('-R',
                      '--upper-red',
                      default='255',
                      dest='upper_red',
                      help='color component for upper isosurface')
    parser.add_option('-G',
                      '--upper-green',
                      default='0',
                      dest='upper_green',
                      help='color component for upper isosurface')
    parser.add_option('-B',
                      '--upper-blue',
                      default='0',
                      dest='upper_blue',
                      help='color component for upper isosurface')
    parser.add_option('-r',
                      '--lower-red',
                      default='0',
                      dest='lower_red',
                      help='color component for lower isosurface')
    parser.add_option('-g',
                      '--lower-green',
                      default='0',
                      dest='lower_green',
                      help='color component for lower isosurface')
    parser.add_option('-b',
                      '--lower-blue',
                      default='255',
                      dest='lower_blue',
                      help='color component for lower isosurface')
    (options, args) = parser.parse_args()
    p = P3D(width=800)
    if args:
        for path in glob.glob(args[0]):
            print path
            try:
                process(path,options)
                print 'SUCCESS'
            except:
                print 'FAIL'
    else:
        print usage
