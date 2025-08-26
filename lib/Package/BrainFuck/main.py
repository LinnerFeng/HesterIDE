#This is a compiler for BrainFuck language
import ctypes
import platform
import os
class BrainFuck:
    def __init__(self, lib_path=None):
        # 确定库文件路径
        if lib_path is None:
            if platform.system() == "Windows":
                lib_name = "bfhandler.dll"
            else:
                lib_name = "libbfhandler.so"
            lib_path = os.path.join(os.path.dirname(__file__), lib_name)
        
        # 加载共享库
        try:
            self.lib = ctypes.CDLL(lib_path)
        except OSError as e:
            raise Exception(f"无法加载共享库 {lib_path}: {e}. 请确保已编译共享库。")
        
        # 设置函数参数和返回类型
        self._setup_function_prototypes()
        
        # 初始化
        self.init()
    
    def _setup_function_prototypes(self):
        """设置C函数的参数和返回类型"""
        # init_bf: 无参数，无返回值
        self.lib.init_bf.restype = None
        
        # interpret_bf: 接受字符串参数，无返回值
        self.lib.interpret_bf.argtypes = [ctypes.c_char_p]
        self.lib.interpret_bf.restype = None
        
        # get_memory: 无参数，返回指向uint32数组的指针
        self.lib.get_memory.restype = ctypes.POINTER(ctypes.c_uint32)
        
        # get_data_ptr: 无参数，返回uint32
        self.lib.get_data_ptr.restype = ctypes.c_uint32
        
        # 如果实现了自定义输入输出，设置回调函数
        try:
            # set_input_callback: 接受函数指针参数，无返回值
            self.lib.set_input_callback.argtypes = [ctypes.CFUNCTYPE(ctypes.c_char)]
            self.lib.set_input_callback.restype = None
            
            # set_output_callback: 接受函数指针参数，无返回值
            self.lib.set_output_callback.argtypes = [ctypes.CFUNCTYPE(None, ctypes.c_char)]
            self.lib.set_output_callback.restype = None
        except AttributeError:
            # 如果共享库没有这些函数，忽略错误
            pass
    
    def init(self):
        """初始化 BrainFuck 环境"""
        self.lib.init_bf()
    
    def execute(self, code):
        """执行 BrainFuck 代码"""
        # 将字符串转换为字节
        code_bytes = code.encode('utf-8')
        self.lib.interpret_bf(code_bytes)
    
    def get_memory(self):
        """获取内存状态"""
        mem_ptr = self.lib.get_memory()
        # 将C数组转换为Python列表
        return [mem_ptr[i] for i in range(256)]
    
    def get_data_pointer(self):
        """获取数据指针位置"""
        return self.lib.get_data_ptr()
    
    def reset(self):
        """重置 BrainFuck 环境"""
        self.init()
    
    def set_input_handler(self, callback):
        """设置自定义输入处理器"""
        # 定义C回调函数类型
        input_func_type = ctypes.CFUNCTYPE(ctypes.c_char)
        
        # 包装Python回调函数
        def input_wrapper():
            result = callback()
            return ord(result) if isinstance(result, str) and len(result) > 0 else 0
        
        # 保存引用以避免垃圾回收
        self._input_callback = input_func_type(input_wrapper)
        self.lib.set_input_callback(self._input_callback)
    
    def set_output_handler(self, callback):
        """设置自定义输出处理器"""
        # 定义C回调函数类型
        output_func_type = ctypes.CFUNCTYPE(None, ctypes.c_char)
        
        # 包装Python回调函数
        def output_wrapper(c):
            callback(chr(c))
        
        # 保存引用以避免垃圾回收
        self._output_callback = output_func_type(output_wrapper)
        self.lib.set_output_callback(self._output_callback)

def main(code):
    #using the script to run of it
    bf=BrainFuck()
    bf.init()
    bf.execute(code)