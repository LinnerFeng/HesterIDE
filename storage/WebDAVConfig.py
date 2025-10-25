import requests
import base64
import os
from xml.etree import ElementTree as ET
from typing import List, Dict, Optional, Callable
from cloud_service import CloudService, CloudFile, SyncStatus

class WebDAVService(CloudService):
    """WebDAV 云服务实现"""
    
    def __init__(self):
        self.base_url = ""
        self.username = ""
        self.password = ""
        self.session = requests.Session()
        self.authenticated = False
    
    def authenticate(self, config: Dict) -> bool:
        """WebDAV认证"""
        self.base_url = config.get('url', '').rstrip('/')
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        
        if not all([self.base_url, self.username, self.password]):
            return False
        
        # 设置认证头
        auth_str = f"{self.username}:{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}'
        })
        
        # 测试连接
        try:
            response = self.session.request('PROPFIND', self.base_url, headers={'Depth': '0'})
            self.authenticated = response.status_code in [200, 207]
            return self.authenticated
        except Exception as e:
            print(f"WebDAV authentication failed: {e}")
            return False
    
    def upload_file(self, local_path: str, cloud_path: str,
                   progress_callback: Optional[Callable] = None) -> bool:
        """上传文件到WebDAV"""
        if not self.authenticated:
            return False
        
        # 确保路径格式正确
        if not cloud_path.startswith('/'):
            cloud_path = '/' + cloud_path
        
        url = self.base_url + cloud_path
        
        try:
            # 创建父目录
            parent_dir = os.path.dirname(cloud_path)
            if parent_dir and parent_dir != '/':
                self._ensure_directory_exists(parent_dir)
            
            # 上传文件
            file_size = os.path.getsize(local_path)
            uploaded = 0
            
            with open(local_path, 'rb') as f:
                if progress_callback:
                    # 分块上传以支持进度显示
                    chunk_size = 8192
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # 这里简化处理，实际应该支持断点续传
                        response = self.session.put(url, data=chunk)
                        uploaded += len(chunk)
                        progress = (uploaded / file_size) * 100
                        progress_callback(progress)
                else:
                    # 简单上传
                    response = self.session.put(url, data=f)
            
            return response.status_code in [200, 201, 204]
            
        except Exception as e:
            print(f"WebDAV upload failed: {e}")
            return False
    
    def download_file(self, cloud_path: str, local_path: str,
                     progress_callback: Optional[Callable] = None) -> bool:
        """从WebDAV下载文件"""
        if not self.authenticated:
            return False
        
        if not cloud_path.startswith('/'):
            cloud_path = '/' + cloud_path
        
        url = self.base_url + cloud_path
        
        try:
            response = self.session.get(url, stream=True)
            if response.status_code != 200:
                return False
            
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return True
            
        except Exception as e:
            print(f"WebDAV download failed: {e}")
            return False
    
    def list_files(self, cloud_path: str = "/") -> List[CloudFile]:
        """列出WebDAV目录文件"""
        if not self.authenticated:
            return []
        
        if not cloud_path.startswith('/'):
            cloud_path = '/' + cloud_path
        
        url = self.base_url + cloud_path
        
        try:
            headers = {'Depth': '1'}
            response = self.session.request('PROPFIND', url, headers=headers)
            
            if response.status_code != 207:
                return []
            
            return self._parse_webdav_response(response.content, cloud_path)
            
        except Exception as e:
            print(f"WebDAV list files failed: {e}")
            return []
    
    def delete_file(self, cloud_path: str) -> bool:
        """删除WebDAV文件"""
        if not self.authenticated:
            return False
        
        if not cloud_path.startswith('/'):
            cloud_path = '/' + cloud_path
        
        url = self.base_url + cloud_path
        
        try:
            response = self.session.delete(url)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"WebDAV delete failed: {e}")
            return False
    
    def create_folder(self, cloud_path: str) -> bool:
        """创建WebDAV文件夹"""
        if not self.authenticated:
            return False
        
        if not cloud_path.startswith('/'):
            cloud_path = '/' + cloud_path
        
        url = self.base_url + cloud_path
        
        try:
            response = self.session.request('MKCOL', url)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"WebDAV create folder failed: {e}")
            return False
    
    def get_file_info(self, cloud_path: str) -> Optional[CloudFile]:
        """获取WebDAV文件信息"""
        files = self.list_files(os.path.dirname(cloud_path))
        target_name = os.path.basename(cloud_path)
        
        for file in files:
            if file.name == target_name:
                return file
        
        return None
    
    def get_quota(self) -> Dict:
        """获取WebDAV存储配额"""
        # WebDAV配额支持有限，这里返回空字典
        return {}
    
    def _ensure_directory_exists(self, directory_path: str):
        """确保目录存在"""
        if not directory_path or directory_path == '/':
            return
        
        # 递归创建目录
        parent_dir = os.path.dirname(directory_path)
        if parent_dir and parent_dir != '/':
            self._ensure_directory_exists(parent_dir)
        
        # 检查目录是否存在
        url = self.base_url + directory_path
        response = self.session.request('PROPFIND', url, headers={'Depth': '0'})
        
        if response.status_code == 404:
            # 目录不存在，创建
            self.create_folder(directory_path)
    
    def _parse_webdav_response(self, xml_content: bytes, base_path: str) -> List[CloudFile]:
        """解析WebDAV PROPFIND响应"""
        files = []
        
        try:
            root = ET.fromstring(xml_content)
            namespaces = {
                'd': 'DAV:'
            }
            
            for response in root.findall('d:response', namespaces):
                href_elem = response.find('d:href', namespaces)
                if href_elem is None:
                    continue
                
                href = href_elem.text
                if not href:
                    continue
                

                if href.startswith(self.base_url):
                    rel_path = href[len(self.base_url):]
                else:
                    rel_path = href
                
                # 跳过当前目录
                if rel_path == base_path or rel_path == base_path + '/':
                    continue
                
                propstat = response.find('d:propstat', namespaces)
                if propstat is None:
                    continue
                
                prop = propstat.find('d:prop', namespaces)
                if prop is None:
                    continue
                
                # 检查是否是目录
                resource_type = prop.find('d:resourcetype', namespaces)
                is_directory = resource_type.find('d:collection', namespaces) is not None
                
                # 获取文件大小
                size_elem = prop.find('d:getcontentlength', namespaces)
                size = int(size_elem.text) if size_elem is not None and size_elem.text else 0
                
                # 获取修改时间
                mtime_elem = prop.find('d:getlastmodified', namespaces)
                mtime_str = mtime_elem.text if mtime_elem is not None else ""
                
                # 转换时间格式 (RFC 1123)
                modified_time = self._parse_rfc1123_date(mtime_str) if mtime_str else 0
                
                # 获取文件名
                displayname_elem = prop.find('d:displayname', namespaces)
                if displayname_elem is not None and displayname_elem.text:
                    name = displayname_elem.text
                else:
                    name = os.path.basename(rel_path.rstrip('/'))
                
                files.append(CloudFile(
                    name=name,
                    path=rel_path,
                    size=size,
                    modified_time=modified_time,
                    is_directory=is_directory,
                    cloud_provider="WebDAV"
                ))
            
        except Exception as e:
            print(f"Parse WebDAV response failed: {e}")
        
        return files
    
    def _parse_rfc1123_date(self, date_str: str) -> float:
        """解析RFC 1123日期格式"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.timestamp()
        except:
            return 0