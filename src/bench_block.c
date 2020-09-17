#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>

#include "matrix.h"

int main(int argc, char**argv) {

    if (argc < 4) {
        printf("usage ./bench_block matrix_size block_size repeats");
        return 1;
    }

    int n = atoi(argv[1]);
    int block_size = atoi(argv[2]);
    int repeats = atoi(argv[3]);

    double *a = random_matrix(n);
    double *b = random_matrix(n); 
    
    double *res = alloc_matrix(n);
    struct timespec start, stop;

    clock_gettime( CLOCK_REALTIME, &start);

    for (int i = 0; i < repeats; i++) {
        matrix_mul_blocked(res, a, b, n, block_size);
    }

    clock_gettime( CLOCK_REALTIME, &stop);
    double blocked = seconds(start, stop);

    printf("%f\n", blocked);

    free(res);
    free(a);
    free(b);

    return 0;
}