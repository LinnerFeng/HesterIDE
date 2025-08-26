//This is handle that Bf language


#include <stdio.h>
#include <stdint.h>

//The brainfuck is a 8 bits langugage so we must create a array which is 256*256

int MAP[256];

int DATA;

void MOVE(uint32_t start){
    
    start+=1;
    DATA=start;//To set the now place is in this var
    
}

void ADD(){
    
    MAP[DATA]++;
}

void DEL(){

    MAP[DATA]--;
}

void OUT(){

    putchar(MAP[DATA]);
}

void IN(){

    MAP[DATA]=getchar();
}

void interpret_bf(const char* code) {
    int loop_level;
    const char* loop_start;
    
    for (const char* ptr = code; *ptr; ptr++) {
        switch (*ptr) {
            case '>': MOVE(1); break;
            case '<': MOVE(-1); break;
            case '+': ADD(); break;
            case '-': DEL(); break;
            case '.': OUT(); break;
            case ',': IN(); break;
            case '[':
                if (MAP[DATA] == 0) {
                    loop_level = 1;
                    while (loop_level > 0) {
                        ptr++;
                        if (*ptr == '[') loop_level++;
                        else if (*ptr == ']') loop_level--;
                    }
                } else {
                    loop_start = ptr;
                }
                break;
            case ']':
                if (MAP[DATA] != 0) {
                    ptr = loop_start;
                }
                break;
        }
    }
}

const int* get_memory() {
    return MAP;
}

static char (*input_callback)() = NULL;
static void (*output_callback)(char) = NULL;

// 设置回调函数
void set_input_callback(char (*cb)()) {
    input_callback = cb;
}

void set_output_callback(void (*cb)(char)) {
    output_callback = cb;
}

// 修改输入输出函数以使用回调
void input_cell() {
    if (input_callback) {
        MAP[DATA] = input_callback();
    } else {
        MAP[DATA] = getchar();
    }
}

void output_cell() {
    if (output_callback) {
        output_callback((char)MAP[DATA]);
    } else {
        putchar(MAP[DATA]);
    }
}
