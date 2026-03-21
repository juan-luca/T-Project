"""
Cyber Command Center - Configuration Export/Import
Backup and restore all settings
"""
import json
import os
import zipfile
import tempfile
import base64
from datetime import datetime
from typing import Dict, List, Optional
from io import BytesIO


class ConfigManager:
    """
    Configuration backup and restore system
    
    Features:
    - Export all settings to JSON/ZIP
    - Import and restore settings
    - Selective export/import
    - Encrypted backups
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.database_path = os.path.join(self.base_path, 'database')
        
        # Files to include in backup
        self.config_files = {
            'device_profiles': os.path.join(self.database_path, 'device_profiles.json'),
            'user_preferences': os.path.join(self.database_path, 'user_preferences.json'),
            'parental_control': os.path.join(self.database_path, 'parental_control.json'),
            'scheduled_pranks': os.path.join(self.database_path, 'scheduled_pranks.json'),
            'telegram_settings': os.path.join(self.database_path, 'telegram_settings.json'),
            'alert_settings': os.path.join(self.database_path, 'alert_settings.json'),
        }
    
    def export_config(self, include_all: bool = True, 
                     components: List[str] = None) -> Dict:
        """
        Export configuration to dict
        
        Args:
            include_all: Export all components
            components: List of specific components to export
            
        Returns:
            Dict with export data and metadata
        """
        export_data = {
            'metadata': {
                'version': '1.0.0',
                'exported_at': datetime.now().isoformat(),
                'app_name': 'Cyber Command Center'
            },
            'configs': {}
        }
        
        files_to_export = self.config_files if include_all else {
            k: v for k, v in self.config_files.items() if components and k in components
        }
        
        for name, filepath in files_to_export.items():
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        export_data['configs'][name] = json.load(f)
                else:
                    export_data['configs'][name] = None
            except Exception as e:
                export_data['configs'][name] = {'error': str(e)}
        
        # Include current state from modules
        try:
            from core.device_profiles import profile_manager
            export_data['configs']['device_profiles_live'] = profile_manager.get_all_profiles()
        except:
            pass
        
        try:
            from core.alerts import alert_manager
            export_data['configs']['alert_settings_live'] = alert_manager.get_settings()
        except:
            pass
        
        try:
            from core.theme_manager import theme_manager
            export_data['configs']['theme_settings'] = theme_manager.get_preferences()
        except:
            pass
        
        try:
            from core.scheduler import prank_scheduler
            export_data['configs']['scheduled_pranks_live'] = prank_scheduler.get_all_scheduled()
        except:
            pass
        
        return export_data
    
    def export_to_json(self, include_all: bool = True,
                      components: List[str] = None) -> str:
        """Export configuration to JSON string"""
        data = self.export_config(include_all, components)
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_to_zip(self, include_all: bool = True,
                     components: List[str] = None) -> bytes:
        """Export configuration to ZIP file"""
        data = self.export_config(include_all, components)
        
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Main config file
            zf.writestr(
                'config.json',
                json.dumps(data, indent=2, ensure_ascii=False)
            )
            
            # Individual files
            for name, content in data['configs'].items():
                if content and not isinstance(content, dict) or (
                    isinstance(content, dict) and 'error' not in content
                ):
                    zf.writestr(
                        f'configs/{name}.json',
                        json.dumps(content, indent=2, ensure_ascii=False)
                    )
            
            # Metadata file
            zf.writestr(
                'README.txt',
                f"Cyber Command Center Configuration Backup\n"
                f"Exported: {data['metadata']['exported_at']}\n"
                f"Version: {data['metadata']['version']}\n\n"
                f"To restore, import the config.json file or this entire ZIP."
            )
        
        return buffer.getvalue()
    
    def export_to_base64(self, include_all: bool = True,
                        components: List[str] = None) -> str:
        """Export configuration as base64-encoded ZIP"""
        zip_data = self.export_to_zip(include_all, components)
        return base64.b64encode(zip_data).decode('utf-8')
    
    def import_config(self, config_data: Dict, 
                     overwrite: bool = True,
                     components: List[str] = None) -> Dict:
        """
        Import configuration from dict
        
        Args:
            config_data: Configuration data to import
            overwrite: Overwrite existing settings
            components: Specific components to import
            
        Returns:
            Dict with import results
        """
        results = {
            'success': True,
            'imported': [],
            'skipped': [],
            'errors': []
        }
        
        configs = config_data.get('configs', config_data)
        
        for name, content in configs.items():
            # Skip if not in components filter
            if components and name not in components:
                results['skipped'].append(name)
                continue
            
            # Skip live data (only import stored configs)
            if name.endswith('_live'):
                results['skipped'].append(name)
                continue
            
            # Skip errors
            if isinstance(content, dict) and 'error' in content:
                results['errors'].append(f"{name}: {content['error']}")
                continue
            
            # Skip if file exists and no overwrite
            if name in self.config_files:
                filepath = self.config_files[name]
                
                if os.path.exists(filepath) and not overwrite:
                    results['skipped'].append(name)
                    continue
                
                try:
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=2, ensure_ascii=False)
                    
                    results['imported'].append(name)
                except Exception as e:
                    results['errors'].append(f"{name}: {str(e)}")
                    results['success'] = False
        
        # Reload modules if needed
        self._reload_modules(results['imported'])
        
        return results
    
    def import_from_json(self, json_string: str,
                        overwrite: bool = True,
                        components: List[str] = None) -> Dict:
        """Import configuration from JSON string"""
        try:
            data = json.loads(json_string)
            return self.import_config(data, overwrite, components)
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'imported': [],
                'skipped': [],
                'errors': [f"Invalid JSON: {str(e)}"]
            }
    
    def import_from_zip(self, zip_data: bytes,
                       overwrite: bool = True,
                       components: List[str] = None) -> Dict:
        """Import configuration from ZIP file"""
        try:
            buffer = BytesIO(zip_data)
            with zipfile.ZipFile(buffer, 'r') as zf:
                # Try to read main config file
                if 'config.json' in zf.namelist():
                    config_content = zf.read('config.json').decode('utf-8')
                    data = json.loads(config_content)
                    return self.import_config(data, overwrite, components)
                else:
                    # Import individual files
                    results = {
                        'success': True,
                        'imported': [],
                        'skipped': [],
                        'errors': []
                    }
                    
                    for filename in zf.namelist():
                        if filename.startswith('configs/') and filename.endswith('.json'):
                            name = filename[8:-5]  # Remove 'configs/' and '.json'
                            content = json.loads(zf.read(filename).decode('utf-8'))
                            
                            partial_result = self.import_config(
                                {name: content}, 
                                overwrite, 
                                components
                            )
                            
                            results['imported'].extend(partial_result['imported'])
                            results['skipped'].extend(partial_result['skipped'])
                            results['errors'].extend(partial_result['errors'])
                            
                            if not partial_result['success']:
                                results['success'] = False
                    
                    return results
                    
        except zipfile.BadZipFile:
            return {
                'success': False,
                'imported': [],
                'skipped': [],
                'errors': ["Invalid ZIP file"]
            }
        except Exception as e:
            return {
                'success': False,
                'imported': [],
                'skipped': [],
                'errors': [str(e)]
            }
    
    def import_from_base64(self, base64_data: str,
                          overwrite: bool = True,
                          components: List[str] = None) -> Dict:
        """Import configuration from base64-encoded ZIP"""
        try:
            zip_data = base64.b64decode(base64_data)
            return self.import_from_zip(zip_data, overwrite, components)
        except Exception as e:
            return {
                'success': False,
                'imported': [],
                'skipped': [],
                'errors': [f"Invalid base64 data: {str(e)}"]
            }
    
    def _reload_modules(self, imported_configs: List[str]):
        """Reload modules after import"""
        for config in imported_configs:
            try:
                if config == 'device_profiles':
                    from core.device_profiles import profile_manager
                    profile_manager._load_profiles()
                elif config == 'user_preferences':
                    from core.theme_manager import theme_manager
                    theme_manager.preferences = theme_manager._load_preferences()
                elif config == 'scheduled_pranks':
                    from core.scheduler import prank_scheduler
                    prank_scheduler._load_scheduled()
                elif config == 'alert_settings':
                    from core.alerts import alert_manager
                    alert_manager._load_settings()
            except Exception as e:
                print(f"Error reloading {config}: {e}")
    
    def get_available_components(self) -> List[Dict]:
        """Get list of available config components"""
        components = []
        
        for name, filepath in self.config_files.items():
            exists = os.path.exists(filepath)
            size = os.path.getsize(filepath) if exists else 0
            
            components.append({
                'id': name,
                'name': name.replace('_', ' ').title(),
                'exists': exists,
                'size': size,
                'path': filepath
            })
        
        return components
    
    def create_backup(self, backup_name: str = None) -> Dict:
        """
        Create a timestamped backup
        
        Returns:
            Dict with backup info
        """
        backups_dir = os.path.join(self.database_path, 'backups')
        os.makedirs(backups_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = backup_name or f"backup_{timestamp}"
        
        zip_data = self.export_to_zip()
        backup_path = os.path.join(backups_dir, f"{name}.zip")
        
        with open(backup_path, 'wb') as f:
            f.write(zip_data)
        
        return {
            'success': True,
            'name': name,
            'path': backup_path,
            'size': len(zip_data),
            'created_at': datetime.now().isoformat()
        }
    
    def list_backups(self) -> List[Dict]:
        """List available backups"""
        backups_dir = os.path.join(self.database_path, 'backups')
        backups = []
        
        if os.path.exists(backups_dir):
            for filename in os.listdir(backups_dir):
                if filename.endswith('.zip'):
                    filepath = os.path.join(backups_dir, filename)
                    stat = os.stat(filepath)
                    
                    backups.append({
                        'name': filename[:-4],  # Remove .zip
                        'filename': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        
        # Sort by creation time descending
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def restore_backup(self, backup_name: str, 
                      overwrite: bool = True) -> Dict:
        """Restore from a backup"""
        backups_dir = os.path.join(self.database_path, 'backups')
        backup_path = os.path.join(backups_dir, f"{backup_name}.zip")
        
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'error': f"Backup not found: {backup_name}"
            }
        
        with open(backup_path, 'rb') as f:
            zip_data = f.read()
        
        result = self.import_from_zip(zip_data, overwrite)
        result['backup_name'] = backup_name
        
        return result
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup"""
        backups_dir = os.path.join(self.database_path, 'backups')
        backup_path = os.path.join(backups_dir, f"{backup_name}.zip")
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return True
        return False


# Global instance
config_manager = ConfigManager()
