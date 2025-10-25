#The file is using WebDAV to connect to cloud storage services
#and upload/download files

import os
import json
import hashlib
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict,List,Optional,Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

from sympy import real_root

class SyncStatus(Enum):
    IDLE="idle"
    PENDING="pending"
    SYNCING="syncing"
    ERROR="error"
    CONFLICT="conflict"

@dataclass
class CloudFile:
    #Basic metadata for a file in cloud storage
    name:str
    path:str
    size:int
    modified_time:float
    is_directory: bool = False
    etag: str = ""
    sync_status: SyncStatus = SyncStatus.IDLE
    local_path: str = ""
    cloud_provider: str = ""

class CloudService(ABC):
    @abstractmethod
    def upload_file(self, local_path:str, cloud_path:str) -> bool:
        pass

    @abstractmethod
    def download_file(self, cloud_path:str, local_path:str) -> bool:
        pass

    @abstractmethod
    def delete_file(self, cloud_path:str) -> bool:
        pass

    @abstractmethod
    def list_files(self, cloud_path:str) -> List[CloudFile]:
        pass

    @abstractmethod
    def get_file_metadata(self, cloud_path:str) -> Optional[CloudFile]:
        pass

    @abstractmethod
    def authenticate(self, credentials:Dict[str,str]) -> bool:
        pass

    @abstractmethod
    def create_folder(self, cloud_path:str) -> bool:
        pass

    @abstractmethod
    def share_file(self, cloud_path:str) -> str:
        pass

    @abstractmethod
    def get_quota(self) -> Dict[str,int]:
        pass

class CloudStorageManager:
    def __init__(self):
        self.services:Dict[str,CloudService]={}
        self.active_service:Optional[CloudService]=None
        self.sync_config=SyncConfig()
        self.cache=CloudCache()
        self.load_config()

    def register_service(self, name:str, service:CloudService):
        self.services[name]=service

    def get_service(self, name:str) -> Optional[CloudService]:
        return self.services.get(name)

    async def upload(self, service_name:str, local_path:str, cloud_path:str) -> bool:
        service=self.get_service(service_name)
        file_hash=self.calculate_file_hash(local_path)
        cloud_file=self.active_service.get_file_metadata(cloud_path)
        success=await service.upload_file(local_path,cloud_path)
        if cloud_file and cloud_file.etag==file_hash:
            if not self.handle_conflict(local_path,cloud_path):
                return False
        if success:
            try:
                self.cache.update_file_cache(
                    local_path, cloud_path, file_hash,
                    self.active_service.__class__.__name__
                )
            except Exception:
                # If cache update fails, ignore so upload result still propagates
                pass
            return True
        return False
            

    async def download(self, service_name:str, cloud_path:str, local_path:str) -> bool:
        service=self.get_service(service_name)
        
        if service:
            return await service.download_file(cloud_path,local_path)
        return False
    
    def set_active_service(self, service_name:str) -> bool:
        service=self.get_service(service_name)
        if service:
            self.active_service=service
            return True
        return False
    
    def calculate_file_hash(self, file_path:str) -> str:
        hash_md5=hashlib.md5()
        try:
            with open(file_path,"rb") as f:
                while chunk := f.read(8192):
                    hash_md5.update(chunk)
        except Exception:
            return ""
        return hash_md5.hexdigest()

    def handle_conflict(self, local_path:str, cloud_path:str) -> bool:
        # Simple conflict resolution strategy: retrieve cloud metadata and decide based on modification times
        local_mtime = os.path.getmtime(local_path)

        # Try to get cloud file metadata from the active service
        cloud_file = None
        if self.active_service:
            try:
                cloud_file = self.active_service.get_file_metadata(cloud_path)
            except Exception:
                cloud_file = None

        # If we don't have cloud metadata, assume no conflict (allow upload)
        if not cloud_file:
            return True

        cloud_mtime = cloud_file.modified_time
        base, ext = os.path.splitext(local_path)
        new_local_path = f"{base}_conflict{ext}"

        if local_mtime > cloud_mtime:
            # Local file is newer: keep local copy (rename original to preserve)
            os.rename(local_path, new_local_path)
            return True
        elif local_mtime < cloud_mtime:
            # Cloud file is newer: rename local and do not overwrite cloud
            os.rename(local_path, new_local_path)
            return False
        else:
            # Same mtime: check cache/hash to decide
            try:
                cached_info = self.cache.get_file_cache(local_path)
            except Exception:
                cached_info = None

            if cached_info:
                cached_hash = cached_info.get('hash') if isinstance(cached_info, dict) else getattr(cached_info, 'hash', None)
            else:
                cached_hash = None

            if cached_hash and cached_hash == self.calculate_file_hash(local_path):
                return True
            return False
            os.rename(local_path,new_local_path)
            return False
    def _scan_local_files(self, folder_path: str) -> List[CloudFile]:
        """扫描本地文件"""
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, folder_path)
                
                files.append(CloudFile(
                    name=filename,
                    path=rel_path,
                    size=os.path.getsize(full_path),
                    modified_time=os.path.getmtime(full_path),
                    is_directory=False,
                    local_path=full_path
                ))
        
        return files
    
    def _perform_sync(self, local_files: List[CloudFile], 
                     cloud_files: List[CloudFile], 
                     local_folder: str, cloud_folder: str,
                     sync_result: Dict):
        """执行同步逻辑"""
        # 创建文件映射
        local_map = {f.path: f for f in local_files}
        cloud_map = {f.path: f for f in cloud_files}
        
        all_paths = set(local_map.keys()) | set(cloud_map.keys())
        
        for path in all_paths:
            local_file = local_map.get(path)
            cloud_file = cloud_map.get(path)
            
            if local_file and not cloud_file:
                # 仅本地存在，上传
                cloud_path = os.path.join(cloud_folder, path).replace('\\', '/')
                try:
                    uploaded = asyncio.run(self.upload(
                        self.active_service.__class__.__name__,
                        local_file.local_path,
                        cloud_path
                    ))
                except Exception:
                    uploaded = False

                if uploaded:
                    sync_result['uploaded'].append(path)
                else:
                    sync_result['errors'].append(path)
            
            elif cloud_file and not local_file:
                # 仅云存在，下载
                local_path = os.path.join(local_folder, path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                try:
                    downloaded = asyncio.run(self.download(
                        self.active_service.__class__.__name__,
                        cloud_file.path,
                        local_path
                    ))
                except Exception:
                    downloaded = False

                if downloaded:
                    sync_result['downloaded'].append(path)
                else:
                    sync_result['errors'].append(path)
            
        for dirpath,dirnames,filenames in os.walk(local_folder):
            for filename in filenames:
                local_path=os.path.join(dirpath,filename)
                relative_path=os.path.relpath(local_path,local_folder)
                cloud_path=os.path.join(cloud_folder,relative_path).replace("\\","/")
                file_hash=self.calculate_file_hash(local_path)
                try:
                    cached_file = self.cache.get_file_cache(local_path)
                except Exception:
                    cached_file = None

                cached_etag = None
                if cached_file:
                    if isinstance(cached_file, dict):
                        cached_etag = cached_file.get('etag')
                    else:
                        cached_etag = getattr(cached_file, 'etag', None)

                if not cached_file or cached_etag != file_hash:
                    try:
                        asyncio.run(self.upload(
                            self.active_service.__class__.__name__,
                            local_path,
                            cloud_path
                        ))
                    except Exception:
                        pass
        config_file = Path.home() / '.office_suite_cloud_config.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 加载服务配置
                # 这里可以初始化已配置的服务
    
    def save_config(self):
        """保存配置"""
        config_file = Path.home() / '.office_suite_cloud_config.json'
        config = {
            'services': {},
            'active_service': self.active_service.__class__.__name__ if self.active_service else None
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

    def scan_local_files(self, local_root:str, cloud_root:str):
        for dirpath,dirnames,filenames in os.walk(local_root):
            for filename in filenames:
                local_path=os.path.join(dirpath,filename)
                relative_path=os.path.relpath(local_path,local_root)
                cloud_path=os.path.join(cloud_root,relative_path).replace("\\","/")
                file_hash=self.calculate_file_hash(local_path)
                cached_file=self.cache_manager.get_file_cache(local_path)
                if not cached_file or cached_file.etag!=file_hash:
                    asyncio.run(self.upload(
                        self.active_service.__class__.__name__,
                        local_path,
                        cloud_path
                    ))

class SyncConfig:
    auto_sync:bool=True
    conflict_resolution:str="timestamp"
    sync_interval:int=300  # in seconds
    exclude_patterns:List[str]=[]

    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns=[".tmp","~*"]

class CloudCache:
    def __init__(self):
        self.cache:Dict[str,Dict]={}

    def get_file_cache(self, local_path:str) -> Optional[Dict]:
        return self.cache.get(local_path)

    def update_file_cache(self, local_path:str, cloud_path:str, etag:str, provider:str):
        self.cache[local_path]={
            "cloud_path":cloud_path,
            "etag":etag,
            "provider":provider,
            "last_synced":time.time()
        }