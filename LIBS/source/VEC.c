#include "VEC.h"

int VEC_edge_cross(Vec2 *a, Vec2 *b, Vec2 *p){
    Vec2 ab = { b->x - a->x, b->y - a->y };
    Vec2 ap = { p->x - a->x, p->y - a->y };
    return ab.x * ap.y - ab.y * ap.x;
}

int VEC_is_top_left(Vec2 *start, Vec2 *end){

    Vec2 edge = {end->x - start->x, end->y - start->y};
    int is_top_edge = edge.y == 0 && edge.x > 0;
    int is_left_edge = edge.y < 0;
    return is_top_edge || is_left_edge;
}