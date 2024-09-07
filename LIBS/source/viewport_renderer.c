#include <stdio.h>
#include <stdlib.h>
#include <math.h>

__declspec(dllexport) void debugger(int *array, int w, int h, int t) {
    
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


__declspec(dllexport) void reset_canvas(int *array, int w, int h) {
    for (int i = 0; i < w; i++){
        for (int j = 0; j < h; j++){
            array[(i * w + j) * 3 + 1] = 30;
            array[(i * w + j) * 3 + 0] = 30;
            array[(i * w + j) * 3 + 2] = 30;
        }
    }
}



__declspec(dllexport) void main_loop(int *array, float *coords, int *links, int n_punti, int n_links, int w, int h, int FLAG_points, int FLAG_lines, int FLAG_polygons) {

    if (FLAG_lines){

        int temp;

        for (int i = 0; i < n_links; i++) {

            int indice_1 = links[i * 2 + 0];
            int indice_2 = links[i * 2 + 1];

            int x0 = (int)(coords[indice_1 * 2 + 0]);
            int y0 = (int)(coords[indice_1 * 2 + 1]);
            
            int x1 = (int)(coords[indice_2 * 2 + 0]);
            int y1 = (int)(coords[indice_2 * 2 + 1]);

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

            int int_coords_x = (int)(coords[i * 2 + 0]);
            int int_coords_y = (int)(coords[i * 2 + 1]);

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


__declspec(dllexport) int* create_array(int w, int h) {
    int *array = (int*)malloc(w * h * 3 * sizeof(int));
    return array;
}


__declspec(dllexport) void free_array(int *ptr) {
    free(ptr);
    ptr = NULL;
}