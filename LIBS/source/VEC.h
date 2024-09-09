#ifndef VEC_H
#define VEC_H

typedef struct Vec2 {
    int x, y;
} Vec2;

int VEC_edge_cross(Vec2 *a, Vec2 *b, Vec2 *p);
int VEC_is_top_left(Vec2 *start, Vec2 *end);

#endif