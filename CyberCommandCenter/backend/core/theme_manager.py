"""
Cyber Command Center - Theme System
Dark/Light themes with customization
"""
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"  # Follow system preference


@dataclass
class ThemeColors:
    """Theme color palette"""
    primary: str = "#3B82F6"  # Blue
    secondary: str = "#10B981"  # Green
    accent: str = "#8B5CF6"  # Purple
    danger: str = "#EF4444"  # Red
    warning: str = "#F59E0B"  # Amber
    success: str = "#10B981"  # Green
    
    # Background colors
    bg_primary: str = "#1F2937"
    bg_secondary: str = "#374151"
    bg_tertiary: str = "#4B5563"
    
    # Text colors
    text_primary: str = "#F9FAFB"
    text_secondary: str = "#D1D5DB"
    text_muted: str = "#9CA3AF"
    
    # Border
    border: str = "#4B5563"
    
    def to_dict(self) -> Dict:
        return {
            'primary': self.primary,
            'secondary': self.secondary,
            'accent': self.accent,
            'danger': self.danger,
            'warning': self.warning,
            'success': self.success,
            'bgPrimary': self.bg_primary,
            'bgSecondary': self.bg_secondary,
            'bgTertiary': self.bg_tertiary,
            'textPrimary': self.text_primary,
            'textSecondary': self.text_secondary,
            'textMuted': self.text_muted,
            'border': self.border
        }


# Predefined themes
THEMES = {
    'dark': ThemeColors(
        primary="#3B82F6",
        secondary="#10B981",
        accent="#8B5CF6",
        bg_primary="#1F2937",
        bg_secondary="#374151",
        bg_tertiary="#4B5563",
        text_primary="#F9FAFB",
        text_secondary="#D1D5DB",
        text_muted="#9CA3AF",
        border="#4B5563"
    ),
    'light': ThemeColors(
        primary="#2563EB",
        secondary="#059669",
        accent="#7C3AED",
        bg_primary="#FFFFFF",
        bg_secondary="#F3F4F6",
        bg_tertiary="#E5E7EB",
        text_primary="#111827",
        text_secondary="#374151",
        text_muted="#6B7280",
        border="#D1D5DB"
    ),
    'hacker': ThemeColors(
        primary="#00FF00",
        secondary="#00CC00",
        accent="#00FF88",
        danger="#FF0000",
        warning="#FFFF00",
        success="#00FF00",
        bg_primary="#000000",
        bg_secondary="#0D0D0D",
        bg_tertiary="#1A1A1A",
        text_primary="#00FF00",
        text_secondary="#00CC00",
        text_muted="#008800",
        border="#00FF00"
    ),
    'cyberpunk': ThemeColors(
        primary="#FF00FF",
        secondary="#00FFFF",
        accent="#FFFF00",
        danger="#FF0055",
        warning="#FF9500",
        success="#00FF88",
        bg_primary="#0D001A",
        bg_secondary="#1A0033",
        bg_tertiary="#2D0052",
        text_primary="#FFFFFF",
        text_secondary="#FF00FF",
        text_muted="#AA00AA",
        border="#FF00FF"
    ),
    'ocean': ThemeColors(
        primary="#0EA5E9",
        secondary="#06B6D4",
        accent="#0284C7",
        danger="#F43F5E",
        warning="#F59E0B",
        success="#10B981",
        bg_primary="#0C1929",
        bg_secondary="#162438",
        bg_tertiary="#1E3A5F",
        text_primary="#F0F9FF",
        text_secondary="#BAE6FD",
        text_muted="#7DD3FC",
        border="#0369A1"
    ),
    'sunset': ThemeColors(
        primary="#F97316",
        secondary="#EF4444",
        accent="#F59E0B",
        danger="#DC2626",
        warning="#FBBF24",
        success="#84CC16",
        bg_primary="#1C1917",
        bg_secondary="#292524",
        bg_tertiary="#44403C",
        text_primary="#FAFAF9",
        text_secondary="#E7E5E4",
        text_muted="#A8A29E",
        border="#57534E"
    )
}


@dataclass
class UserPreferences:
    """User preferences including theme"""
    theme_name: str = "dark"
    theme_mode: ThemeMode = ThemeMode.DARK
    custom_colors: Optional[ThemeColors] = None
    font_size: str = "medium"  # small, medium, large
    sidebar_collapsed: bool = False
    dashboard_layout: str = "default"
    notifications_enabled: bool = True
    sound_enabled: bool = True
    animations_enabled: bool = True
    language: str = "es"  # es, en
    
    def to_dict(self) -> Dict:
        return {
            'themeName': self.theme_name,
            'themeMode': self.theme_mode.value,
            'customColors': self.custom_colors.to_dict() if self.custom_colors else None,
            'fontSize': self.font_size,
            'sidebarCollapsed': self.sidebar_collapsed,
            'dashboardLayout': self.dashboard_layout,
            'notificationsEnabled': self.notifications_enabled,
            'soundEnabled': self.sound_enabled,
            'animationsEnabled': self.animations_enabled,
            'language': self.language
        }


class ThemeManager:
    """
    Theme management system
    
    Features:
    - Multiple predefined themes
    - Custom theme support
    - User preference persistence
    - CSS variable generation
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
        
        self.config_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'database',
            'user_preferences.json'
        )
        
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> UserPreferences:
        """Load user preferences from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                prefs = UserPreferences(
                    theme_name=data.get('themeName', 'dark'),
                    theme_mode=ThemeMode(data.get('themeMode', 'dark')),
                    font_size=data.get('fontSize', 'medium'),
                    sidebar_collapsed=data.get('sidebarCollapsed', False),
                    dashboard_layout=data.get('dashboardLayout', 'default'),
                    notifications_enabled=data.get('notificationsEnabled', True),
                    sound_enabled=data.get('soundEnabled', True),
                    animations_enabled=data.get('animationsEnabled', True),
                    language=data.get('language', 'es')
                )
                
                # Load custom colors
                if data.get('customColors'):
                    cc = data['customColors']
                    prefs.custom_colors = ThemeColors(
                        primary=cc.get('primary', '#3B82F6'),
                        secondary=cc.get('secondary', '#10B981'),
                        accent=cc.get('accent', '#8B5CF6'),
                        danger=cc.get('danger', '#EF4444'),
                        warning=cc.get('warning', '#F59E0B'),
                        success=cc.get('success', '#10B981'),
                        bg_primary=cc.get('bgPrimary', '#1F2937'),
                        bg_secondary=cc.get('bgSecondary', '#374151'),
                        bg_tertiary=cc.get('bgTertiary', '#4B5563'),
                        text_primary=cc.get('textPrimary', '#F9FAFB'),
                        text_secondary=cc.get('textSecondary', '#D1D5DB'),
                        text_muted=cc.get('textMuted', '#9CA3AF'),
                        border=cc.get('border', '#4B5563')
                    )
                
                return prefs
        except Exception as e:
            print(f"Error loading preferences: {e}")
        
        return UserPreferences()
    
    def _save_preferences(self):
        """Save preferences to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.preferences.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def get_current_theme(self) -> Dict:
        """Get current theme colors"""
        if self.preferences.custom_colors:
            colors = self.preferences.custom_colors
        elif self.preferences.theme_name in THEMES:
            colors = THEMES[self.preferences.theme_name]
        else:
            colors = THEMES['dark']
        
        return {
            'name': self.preferences.theme_name,
            'mode': self.preferences.theme_mode.value,
            'colors': colors.to_dict()
        }
    
    def set_theme(self, theme_name: str) -> bool:
        """Set theme by name"""
        if theme_name not in THEMES:
            return False
        
        self.preferences.theme_name = theme_name
        self.preferences.custom_colors = None
        
        # Update mode based on theme
        if theme_name == 'light':
            self.preferences.theme_mode = ThemeMode.LIGHT
        else:
            self.preferences.theme_mode = ThemeMode.DARK
        
        self._save_preferences()
        return True
    
    def set_custom_theme(self, colors: Dict) -> bool:
        """Set custom theme colors"""
        try:
            self.preferences.custom_colors = ThemeColors(
                primary=colors.get('primary', '#3B82F6'),
                secondary=colors.get('secondary', '#10B981'),
                accent=colors.get('accent', '#8B5CF6'),
                danger=colors.get('danger', '#EF4444'),
                warning=colors.get('warning', '#F59E0B'),
                success=colors.get('success', '#10B981'),
                bg_primary=colors.get('bgPrimary', '#1F2937'),
                bg_secondary=colors.get('bgSecondary', '#374151'),
                bg_tertiary=colors.get('bgTertiary', '#4B5563'),
                text_primary=colors.get('textPrimary', '#F9FAFB'),
                text_secondary=colors.get('textSecondary', '#D1D5DB'),
                text_muted=colors.get('textMuted', '#9CA3AF'),
                border=colors.get('border', '#4B5563')
            )
            self.preferences.theme_name = 'custom'
            self._save_preferences()
            return True
        except Exception as e:
            print(f"Error setting custom theme: {e}")
            return False
    
    def get_available_themes(self) -> List[Dict]:
        """Get list of available themes"""
        themes = []
        for name, colors in THEMES.items():
            themes.append({
                'name': name,
                'displayName': name.capitalize(),
                'preview': {
                    'primary': colors.primary,
                    'background': colors.bg_primary,
                    'text': colors.text_primary
                }
            })
        return themes
    
    def update_preferences(self, prefs: Dict):
        """Update user preferences"""
        if 'fontSize' in prefs:
            self.preferences.font_size = prefs['fontSize']
        if 'sidebarCollapsed' in prefs:
            self.preferences.sidebar_collapsed = prefs['sidebarCollapsed']
        if 'dashboardLayout' in prefs:
            self.preferences.dashboard_layout = prefs['dashboardLayout']
        if 'notificationsEnabled' in prefs:
            self.preferences.notifications_enabled = prefs['notificationsEnabled']
        if 'soundEnabled' in prefs:
            self.preferences.sound_enabled = prefs['soundEnabled']
        if 'animationsEnabled' in prefs:
            self.preferences.animations_enabled = prefs['animationsEnabled']
        if 'language' in prefs:
            self.preferences.language = prefs['language']
        
        self._save_preferences()
    
    def get_preferences(self) -> Dict:
        """Get all user preferences"""
        return self.preferences.to_dict()
    
    def generate_css_variables(self) -> str:
        """Generate CSS variables for current theme"""
        theme = self.get_current_theme()
        colors = theme['colors']
        
        css = ":root {\n"
        for key, value in colors.items():
            # Convert camelCase to kebab-case
            css_key = ''.join(['-' + c.lower() if c.isupper() else c for c in key]).lstrip('-')
            css += f"  --color-{css_key}: {value};\n"
        css += "}\n"
        
        return css
    
    def reset_to_default(self):
        """Reset to default theme"""
        self.preferences = UserPreferences()
        self._save_preferences()


# Global instance
theme_manager = ThemeManager()
