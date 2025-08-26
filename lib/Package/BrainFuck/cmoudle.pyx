
cdef extern from "BfHandler.h":
    void init_bf()
    void interpret_bf(const char* code)
    const  int* get_memory()
    int  DATA

# Python 包装类
cdef class BrainFuck:
    cdef public object memory_view
    
    def __cinit__(self):
        init_bf()
    
    def execute(self, code):
        # 将Python字符串转换为C字符串
        cdef bytes code_bytes = code.encode('utf-8')
        cdef char* c_code = code_bytes
        interpret_bf(c_code)
    
    def get_memory(self):
        # 获取内存指针并转换为Python列表
        cdef const int* mem_ptr = get_memory()
        return [mem_ptr[i] for i in range(256)]
    
    def get_data_pointer(self):
        return DATA
    
    def reset(self):
        init_bf()