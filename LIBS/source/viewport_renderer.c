#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "math_tools.h"
#include "VEC.h"

#ifdef _WIN32 // Only use __declspec(dllexport) on Windows
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT 
#endif

DLLEXPORT void debugger(int *array, int w, int h, int t) {
    
    float converted = (float)t;
    float divided = converted / 20.0;
    float sin_divider = sin(divided);
    float cos_divider = cos(divided);
    float final_conversion1 = (sin_divider + 1.0) / 2.0;
    float final_conversion2 = (cos_divider + 1.0) / 2.0;

    for (int i = 0; i < w; i++){
        for (int j = 0; j < h; j++){
            array[(i * w + j) * 3 + 1] = (int)(255 * j * final_conversion1 / h); 
            array[(i * w + j) * 3 + 0] = (int)(255 * i * final_conversion2 / w); 
            array[(i * w + j) * 3 + 2] = 255;
        }
    }
}


DLLEXPORT void reset_canvas(int *array, int w, int h) {
    for (int i = 0; i < w; i++){
        for (int j = 0; j < h; j++){
            array[(i * w + j) * 3 + 0] = 30;
            array[(i * w + j) * 3 + 1] = 30;
            array[(i * w + j) * 3 + 2] = 30;
        }
    }
}



DLLEXPORT void main_loop(int *array, int *coords, int *links, int *triangoli, int n_punti, int n_links, int n_triangoli, int w, int h, int FLAG_points, int FLAG_lines, int FLAG_polygons) {

    if (FLAG_polygons){

        for (int i = 0; i < n_triangoli; i++) {
            
            Vec2 vertices[3] = {
                {.x = coords[triangoli[i * 3 + 0] * 2 + 0], .y = coords[triangoli[i * 3 + 0] * 2 + 1]},
                {.x = coords[triangoli[i * 3 + 1] * 2 + 0], .y = coords[triangoli[i * 3 + 1] * 2 + 1]},
                {.x = coords[triangoli[i * 3 + 2] * 2 + 0], .y = coords[triangoli[i * 3 + 2] * 2 + 1]},
            };


            int x_min = min(vertices[0].x, vertices[1].x, vertices[2].x);
            int y_min = min(vertices[0].y, vertices[1].y, vertices[2].y);
            int x_max = max(vertices[0].x, vertices[1].x, vertices[2].x);
            int y_max = max(vertices[0].y, vertices[1].y, vertices[2].y); 

            int delta_w0_col = (vertices[1].y - vertices[2].y);
            int delta_w1_col = (vertices[2].y - vertices[0].y);
            int delta_w2_col = (vertices[0].y - vertices[1].y);

            int delta_w0_row = (vertices[2].x - vertices[1].x);
            int delta_w1_row = (vertices[0].x - vertices[2].x);
            int delta_w2_row = (vertices[1].x - vertices[0].x);

            int bias0 = VEC_is_top_left(&vertices[1], &vertices[2]) ? 0 : -1;
            int bias1 = VEC_is_top_left(&vertices[2], &vertices[0]) ? 0 : -1;
            int bias2 = VEC_is_top_left(&vertices[0], &vertices[1]) ? 0 : -1;

            float area = VEC_edge_cross(&vertices[0], &vertices[1], &vertices[2]);

            Vec2 p0 = {x_min, y_min}; 
            int w0_row = VEC_edge_cross(&vertices[1], &vertices[2], &p0) + bias0; 
            int w1_row = VEC_edge_cross(&vertices[2], &vertices[0], &p0) + bias1; 
            int w2_row = VEC_edge_cross(&vertices[0], &vertices[1], &p0) + bias2; 

            for (int y = y_min; y <= y_max; y++){

                float w0 = w0_row; 
                float w1 = w1_row; 
                float w2 = w2_row; 

                for (int x = x_min; x <= x_max; x++){
                    
                    if (w0 >= 0 && w1 >= 0 && w2 >= 0) {

                        float alpha = w0 / area;
                        float beta = w1 / area;
                        float gamma = w2 / area;

                        array[(x * w + y) * 3 + 0] = 255 * alpha;
                        array[(x * w + y) * 3 + 1] = 255 * beta;
                        array[(x * w + y) * 3 + 2] = 255 * gamma;

                    }

                    w0 += delta_w0_col; 
                    w1 += delta_w1_col; 
                    w2 += delta_w2_col; 

                }

                w0_row += delta_w0_row;
                w1_row += delta_w1_row;
                w2_row += delta_w2_row;

            }

        }
    }


    if (FLAG_lines){

        int temp;

        for (int i = 0; i < n_links; i++) {

            int indice_1 = links[i * 2 + 0];
            int indice_2 = links[i * 2 + 1];

            int x0 = coords[indice_1 * 2 + 0];
            int y0 = coords[indice_1 * 2 + 1];
            
            int x1 = coords[indice_2 * 2 + 0];
            int y1 = coords[indice_2 * 2 + 1];

            if (x0 != w * 1.5 && y0 != h * 1.5 && x1 != w * 1.5 && y1 != h * 1.5)  {          

                if (abs(x1 - x0) > abs(y1 - y0)){

                    if (x0 > x1){
                        temp = x0;
                        x0 = x1;
                        x1 = temp;

                        temp = y0;
                        y0 = y1;
                        y1 = temp;
                    }

                    int dx = x1 - x0;
                    int dy = y1 - y0;

                    int dir = dy < 0 ? -1 : 1;
                    dy *= dir;

                    if (dx != 0){
                        int y = y0;
                        int p = 2 * dy - dx;

                        for (int j = 0; j < dx + 1; j++){

                            if (x0 + j < h && x0 + j > 0 && y < w && y > 0){
                                array[((x0 + j) * w + y) * 3 + 0] = 100;
                                array[((x0 + j) * w + y) * 3 + 1] = 100;
                                array[((x0 + j) * w + y) * 3 + 2] = 100;
                            }

                            if (p >= 0){
                                y += dir;
                                p = p - 2 * dx;
                            }

                            p = p + 2 * dy;

                        }
                    }

                } else {

                    if (y0 > y1){
                        temp = x0;
                        x0 = x1;
                        x1 = temp;

                        temp = y0;
                        y0 = y1;
                        y1 = temp;
                    }

                    int dx = x1 - x0;
                    int dy = y1 - y0;

                    int dir = dx < 0 ? -1 : 1;
                    dx *= dir;

                    if (dy != 0){
                        int x = x0;
                        int p = 2 * dx - dy;

                        for (int j = 0; j < dy + 1; j++){
                            if (x < h && x > 0 && y0 + j < w && y0 + j > 0){
                                array[(x * w + (y0 + j)) * 3 + 1] = 100;
                                array[(x * w + (y0 + j)) * 3 + 0] = 100;
                                array[(x * w + (y0 + j)) * 3 + 2] = 100;
                            }

                            if (p >= 0){
                                x += dir;
                                p = p - 2 * dy;
                            }

                            p = p + 2 * dx;

                        }
                    }           
                }
            }
        }
    }

    if (FLAG_points){
        for (int i = 0; i < n_punti; i++){

            int int_coords_x = coords[i * 2 + 0];
            int int_coords_y = coords[i * 2 + 1];

            if (int_coords_x < h && int_coords_x > 0 && int_coords_y < w && int_coords_y > 0){
                if (int_coords_x != w * 1.5 && int_coords_y != h * 1.5)  {
                    
                    for (int j = -1; j < 2; j++){
                        for (int k = -1; k < 2; k++){
                            array[((int_coords_x + j) * w + (int_coords_y + k)) * 3 + 0] = 255;
                            array[((int_coords_x + j) * w + (int_coords_y + k)) * 3 + 1] = 100;
                            array[((int_coords_x + j) * w + (int_coords_y + k)) * 3 + 2] = 100;
                        }
                    }
                }
            }
        }
    }

}


DLLEXPORT int* create_array(int w, int h) {
    int *array = (int*)malloc(w * h * 3 * sizeof(int));
    return array;
}


DLLEXPORT void free_array(int *ptr) {
    free(ptr);
    ptr = NULL;
}