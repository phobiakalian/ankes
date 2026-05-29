"""
Internationalization (i18n) module for Yn Security Bot.
Supports multiple languages with automatic detection and manual override.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = {
    "id": "Indonesian",
    "en": "English",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean"
}

# Translations dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "id": {
        # Common
        "success": "✅ Berhasil!",
        "error": "❌ Error!",
        "warning": "⚠️ Peringatan",
        "info": "ℹ️ Info",
        "confirm": "Konfirmasi",
        "cancel": "Batal",
        "yes": "Ya",
        "no": "Tidak",
        
        # Start command
        "start_welcome": "Halo {user}! Selamat datang di {group}.\n\nSaya adalah bot keamanan yang akan membantu melindungi grup Anda dari spam dan konten tidak diinginkan.",
        "start_help": "Klik tombol di bawah untuk melihat bantuan atau mengatur preferensi bahasa.",
        
        # Help command
        "help_title": "📚 Bantuan - Yn Security Bot",
        "help_description": "Pilih kategori di bawah untuk melihat perintah yang tersedia:",
        "help_admin": "👮 Admin Commands",
        "help_user": "👤 User Commands",
        "help_settings": "⚙️ Settings",
        "help_back": "🔙 Kembali",
        
        # Admin commands
        "admin_mute_success": "✅ {user} telah di-mute selama {duration}.\nAlasan: {reason}",
        "admin_unmute_success": "✅ {user} telah di-unmute.",
        "admin_ban_success": "✅ {user} telah di-ban.\nAlasan: {reason}",
        "admin_unban_success": "✅ {user} telah di-unban.",
        "admin_need_reply": "❌ Balas pesan user atau berikan username/user_id.",
        "admin_not_admin": "❌ Anda bukan admin di grup ini.",
        "admin_invalid_duration": "❌ Format durasi tidak valid. Gunakan format: 1d, 2h, 30m, 45s",
        
        # Notes
        "note_saved": "✅ Catatan '{name}' berhasil disimpan.",
        "note_deleted": "✅ Catatan '{name}' berhasil dihapus.",
        "note_not_found": "❌ Catatan '{name}' tidak ditemukan.",
        "note_list_title": "📝 Daftar Catatan:",
        "note_list_empty": "📭 Belum ada catatan yang disimpan.",
        "note_usage": "Gunakan #nama_catatan atau /get nama_catatan untuk memanggil catatan.",
        
        # Activity Logger
        "activity_report_title": "📊 Laporan Aktivitas Grup",
        "activity_period": "Periode: {start} - {end}",
        "activity_most_active": "🔥 User Paling Aktif:",
        "activity_most_muted": "🔇 Paling Sering Di-Mute:",
        "activity_most_kicked": "🚫 Paling Sering Di-Kick:",
        "activity_no_data": "📭 Belum ada data aktivitas.",
        "activity_user": "User: {user}",
        "activity_count": "Jumlah: {count}",
        
        # Dashboard
        "dashboard_title": "📈 Dashboard Statistik Grup",
        "dashboard_new_members": "👥 Member Baru Hari Ini: {count}",
        "dashboard_messages_deleted": "🗑️ Pesan Dihapus: {count}",
        "dashboard_violations": "⚠️ Pelanggaran Terdeteksi: {count}",
        "dashboard_warnings": "⚡ Peringatan Diberikan: {count}",
        "dashboard_mutes": "🔇 Total Mute: {count}",
        "dashboard_bans": "🚫 Total Ban: {count}",
        "dashboard_last_updated": "Terakhir diperbarui: {time}",
        
        # Settings
        "settings_title": "⚙️ Pengaturan Grup",
        "settings_language": "🌐 Bahasa: {lang}",
        "settings_language_changed": "✅ Bahasa diubah ke {lang}.",
        "settings_toggle_on": "✅ {feature} diaktifkan.",
        "settings_toggle_off": "❌ {feature} dimatikan.",
        
        # Violations
        "violation_forward": "⚠️ Forward pesan tidak diizinkan di grup ini.",
        "violation_link": "⚠️ Mengirim link tidak diizinkan di grup ini.",
        "violation_command": "⚠️ Menggunakan command tidak diizinkan di grup ini.",
        "violation_hashtag": "⚠️ Menggunakan hashtag tidak diizinkan di grup ini.",
        "violation_voice": "⚠️ Mengirim voice note tidak diizinkan di grup ini.",
        "violation_flood": "⚠️ Spam terdeteksi! Anda telah di-mute sementara.",
        "violation_badword": "⚠️ Kata tidak pantas terdeteksi!",
        "violation_warning": "⚠️ Peringatan {current}/{max}",
        "violation_kicked": "🚫 Anda telah dikeluarkan dari grup karena terlalu banyak pelanggaran.",
        
        # Captcha
        "captcha_title": "🤖 Verifikasi Manusia",
        "captcha_instruction": "Silakan klik tombol di bawah untuk membuktikan bahwa Anda bukan bot.",
        "captcha_success": "✅ Verifikasi berhasil! Selamat bergabung.",
        "captcha_failed": "❌ Verifikasi gagal. Anda akan dikeluarkan.",
        "captcha_timeout": "⏰ Waktu verifikasi habis.",
        
        # Errors
        "error_permission": "❌ Saya tidak memiliki izin untuk melakukan tindakan ini.",
        "error_user_not_found": "❌ User tidak ditemukan.",
        "error_group_only": "❌ Perintah ini hanya bisa digunakan di grup.",
        "error_private_only": "❌ Perintah ini hanya bisa digunakan di private chat."
    },
    
    "en": {
        # Common
        "success": "✅ Success!",
        "error": "❌ Error!",
        "warning": "⚠️ Warning",
        "info": "ℹ️ Info",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "yes": "Yes",
        "no": "No",
        
        # Start command
        "start_welcome": "Hello {user}! Welcome to {group}.\n\nI am a security bot that will help protect your group from spam and unwanted content.",
        "start_help": "Click the buttons below to see help or set language preferences.",
        
        # Help command
        "help_title": "📚 Help - Yn Security Bot",
        "help_description": "Select a category below to see available commands:",
        "help_admin": "👮 Admin Commands",
        "help_user": "👤 User Commands",
        "help_settings": "⚙️ Settings",
        "help_back": "🔙 Back",
        
        # Admin commands
        "admin_mute_success": "✅ {user} has been muted for {duration}.\nReason: {reason}",
        "admin_unmute_success": "✅ {user} has been unmuted.",
        "admin_ban_success": "✅ {user} has been banned.\nReason: {reason}",
        "admin_unban_success": "✅ {user} has been unbanned.",
        "admin_need_reply": "❌ Reply to a user message or provide username/user_id.",
        "admin_not_admin": "❌ You are not an admin in this group.",
        "admin_invalid_duration": "❌ Invalid duration format. Use format: 1d, 2h, 30m, 45s",
        
        # Notes
        "note_saved": "✅ Note '{name}' saved successfully.",
        "note_deleted": "✅ Note '{name}' deleted successfully.",
        "note_not_found": "❌ Note '{name}' not found.",
        "note_list_title": "📝 Notes List:",
        "note_list_empty": "📭 No notes saved yet.",
        "note_usage": "Use #note_name or /get note_name to retrieve a note.",
        
        # Activity Logger
        "activity_report_title": "📊 Group Activity Report",
        "activity_period": "Period: {start} - {end}",
        "activity_most_active": "🔥 Most Active Users:",
        "activity_most_muted": "🔇 Most Frequently Muted:",
        "activity_most_kicked": "🚫 Most Frequently Kicked:",
        "activity_no_data": "📭 No activity data yet.",
        "activity_user": "User: {user}",
        "activity_count": "Count: {count}",
        
        # Dashboard
        "dashboard_title": "📈 Group Statistics Dashboard",
        "dashboard_new_members": "👥 New Members Today: {count}",
        "dashboard_messages_deleted": "🗑️ Messages Deleted: {count}",
        "dashboard_violations": "⚠️ Violations Detected: {count}",
        "dashboard_warnings": "⚡ Warnings Given: {count}",
        "dashboard_mutes": "🔇 Total Mutes: {count}",
        "dashboard_bans": "🚫 Total Bans: {count}",
        "dashboard_last_updated": "Last updated: {time}",
        
        # Settings
        "settings_title": "⚙️ Group Settings",
        "settings_language": "🌐 Language: {lang}",
        "settings_language_changed": "✅ Language changed to {lang}.",
        "settings_toggle_on": "✅ {feature} enabled.",
        "settings_toggle_off": "❌ {feature} disabled.",
        
        # Violations
        "violation_forward": "⚠️ Forwarding messages is not allowed in this group.",
        "violation_link": "⚠️ Sending links is not allowed in this group.",
        "violation_command": "⚠️ Using commands is not allowed in this group.",
        "violation_hashtag": "⚠️ Using hashtags is not allowed in this group.",
        "violation_voice": "⚠️ Sending voice notes is not allowed in this group.",
        "violation_flood": "⚠️ Spam detected! You have been temporarily muted.",
        "violation_badword": "⚠️ Inappropriate word detected!",
        "violation_warning": "⚠️ Warning {current}/{max}",
        "violation_kicked": "🚫 You have been removed from the group due to too many violations.",
        
        # Captcha
        "captcha_title": "🤖 Human Verification",
        "captcha_instruction": "Please click the button below to prove you are not a bot.",
        "captcha_success": "✅ Verification successful! Welcome aboard.",
        "captcha_failed": "❌ Verification failed. You will be removed.",
        "captcha_timeout": "⏰ Verification timeout.",
        
        # Errors
        "error_permission": "❌ I don't have permission to perform this action.",
        "error_user_not_found": "❌ User not found.",
        "error_group_only": "❌ This command can only be used in groups.",
        "error_private_only": "❌ This command can only be used in private chat."
    },
    
    "ar": {
        # Common
        "success": "✅ نجح!",
        "error": "❌ خطأ!",
        "warning": "⚠️ تحذير",
        "info": "ℹ️ معلومات",
        "confirm": "تأكيد",
        "cancel": "إلغاء",
        "yes": "نعم",
        "no": "لا",
        
        # Start command
        "start_welcome": "مرحباً {user}! أهلاً بك في {group}.\n\nأنا بوت أمان سيساعد في حماية مجموعتك من الرسائل المزعجة والمحتوى غير المرغوب فيه.",
        "start_help": "انقر على الأزرار أدناه لعرض المساعدة أو إعداد تفضيلات اللغة.",
        
        # Help command
        "help_title": "📚 مساعدة - بوت Yn للأمان",
        "help_description": "اختر فئة أدناه لعرض الأوامر المتاحة:",
        "help_admin": "👮 أوامر المشرفين",
        "help_user": "👤 أوامر المستخدمين",
        "help_settings": "⚙️ الإعدادات",
        "help_back": "🔙 رجوع",
        
        # Admin commands
        "admin_mute_success": "✅ تم كتم صوت {user} لمدة {duration}.\nالسبب: {reason}",
        "admin_unmute_success": "✅ تم إلغاء كتم صوت {user}.",
        "admin_ban_success": "✅ تم حظر {user}.\nالسبب: {reason}",
        "admin_unban_success": "✅ تم إلغاء حظر {user}.",
        "admin_need_reply": "❌ رد على رسالة مستخدم أو قدم اسم المستخدم/معرف المستخدم.",
        "admin_not_admin": "❌ لست مشرفاً في هذه المجموعة.",
        "admin_invalid_duration": "❌ تنسيق المدة غير صالح. استخدم التنسيق: 1d, 2h, 30m, 45s",
        
        # Notes
        "note_saved": "✅ تم حفظ الملاحظة '{name}' بنجاح.",
        "note_deleted": "✅ تم حذف الملاحظة '{name}' بنجاح.",
        "note_not_found": "❌ الملاحظة '{name}' غير موجودة.",
        "note_list_title": "📝 قائمة الملاحظات:",
        "note_list_empty": "📭 لا توجد ملاحظات محفوظة بعد.",
        "note_usage": "استخدم #اسم_الملاحظة أو /get اسم_الملاحظة لاسترجاع ملاحظة.",
        
        # Activity Logger
        "activity_report_title": "📊 تقرير نشاط المجموعة",
        "activity_period": "الفترة: {start} - {end}",
        "activity_most_active": "🔥 أكثر المستخدمين نشاطاً:",
        "activity_most_muted": "🔇 الأكثر كتمًا للصوت:",
        "activity_most_kicked": "🚫 الأكثر طرداً:",
        "activity_no_data": "📭 لا توجد بيانات نشاط بعد.",
        "activity_user": "المستخدم: {user}",
        "activity_count": "العدد: {count}",
        
        # Dashboard
        "dashboard_title": "📈 لوحة إحصائيات المجموعة",
        "dashboard_new_members": "👥 أعضاء جدد اليوم: {count}",
        "dashboard_messages_deleted": "🗑️ رسائل محذوفة: {count}",
        "dashboard_violations": "⚠️ انتهاكات مكتشفة: {count}",
        "dashboard_warnings": "⚡ تحذيرات مُعطاة: {count}",
        "dashboard_mutes": "🔇 إجمالي الكتم: {count}",
        "dashboard_bans": "🚫 إجمالي الحظر: {count}",
        "dashboard_last_updated": "آخر تحديث: {time}",
        
        # Settings
        "settings_title": "⚙️ إعدادات المجموعة",
        "settings_language": "🌐 اللغة: {lang}",
        "settings_language_changed": "✅ تم تغيير اللغة إلى {lang}.",
        "settings_toggle_on": "✅ تم تفعيل {feature}.",
        "settings_toggle_off": "❌ تم تعطيل {feature}.",
        
        # Violations
        "violation_forward": "⚠️ إعادة توجيه الرسائل غير مسموح بها في هذه المجموعة.",
        "violation_link": "⚠️ إرسال الروابط غير مسموح به في هذه المجموعة.",
        "violation_command": "⚠️ استخدام الأوامر غير مسموح به في هذه المجموعة.",
        "violation_hashtag": "⚠️ استخدام الهاشتاقات غير مسموح به في هذه المجموعة.",
        "violation_voice": "⚠️ إرسال ملاحظات صوتية غير مسموح به في هذه المجموعة.",
        "violation_flood": "⚠️ تم اكتشاف رسائل مزعجة! تم كتم صوتك مؤقتاً.",
        "violation_badword": "⚠️ تم اكتشاف كلمة غير لائقة!",
        "violation_warning": "⚠️ تحذير {current}/{max}",
        "violation_kicked": "🚫 تم إزالتك من المجموعة بسبب كثرة الانتهاكات.",
        
        # Captcha
        "captcha_title": "🤖 التحقق من البشرية",
        "captcha_instruction": "يرجى النقر على الزر أدناه لإثبات أنك لست روبوتاً.",
        "captcha_success": "✅ نجح التحقق! أهلاً بك.",
        "captcha_failed": "❌ فشل التحقق. ستتم إزالتك.",
        "captcha_timeout": "⏰ انتهت مهلة التحقق.",
        
        # Errors
        "error_permission": "❌ ليس لدي صلاحية تنفيذ هذا الإجراء.",
        "error_user_not_found": "❌ المستخدم غير موجود.",
        "error_group_only": "❌ يمكن استخدام هذا الأمر فقط في المجموعات.",
        "error_private_only": "❌ يمكن استخدام هذا الأمر فقط في الدردشة الخاصة."
    }
}

# Default language
DEFAULT_LANGUAGE = "id"


def get_text(lang_code: str, key: str, **kwargs) -> str:
    """
    Get translated text for a given key and language.
    
    Args:
        lang_code: Language code (e.g., 'id', 'en', 'ar')
        key: Translation key
        **kwargs: Format arguments for the translation string
    
    Returns:
        Translated text with formatted arguments
    """
    # Fallback to default language if language not found
    if lang_code not in TRANSLATIONS:
        lang_code = DEFAULT_LANGUAGE
    
    # Fallback to English if key not found in target language
    if key not in TRANSLATIONS[lang_code]:
        if key in TRANSLATIONS["en"]:
            text = TRANSLATIONS["en"][key]
        else:
            text = f"[Missing: {key}]"
    else:
        text = TRANSLATIONS[lang_code][key]
    
    # Format the text with provided arguments
    try:
        return text.format(**kwargs)
    except KeyError as e:
        logger.warning(f"Missing format argument {e} for key {key} in language {lang_code}")
        return text


def get_available_languages() -> Dict[str, str]:
    """
    Get dictionary of available languages.
    
    Returns:
        Dictionary mapping language codes to language names
    """
    return SUPPORTED_LANGUAGES.copy()


def is_language_supported(lang_code: str) -> bool:
    """
    Check if a language is supported.
    
    Args:
        lang_code: Language code to check
    
    Returns:
        True if language is supported, False otherwise
    """
    return lang_code in SUPPORTED_LANGUAGES


def detect_language_from_chat(chat_title: str) -> str:
    """
    Detect language from chat title (basic heuristic).
    
    Args:
        chat_title: Title of the chat
    
    Returns:
        Detected language code
    """
    # Basic heuristic - can be improved with language detection libraries
    chat_title_lower = chat_title.lower()
    
    # Arabic script detection
    if any('\u0600' <= c <= '\u06FF' for c in chat_title):
        return "ar"
    
    # Chinese/Japanese/Korean detection
    if any('\u4e00' <= c <= '\u9fff' for c in chat_title):
        return "zh"
    if any('\u3040' <= c <= '\u309f' for c in chat_title):
        return "ja"
    if any('\uac00' <= c <= '\ud7af' for c in chat_title):
        return "ko"
    
    # Default to Indonesian for now
    return DEFAULT_LANGUAGE


class LanguageManager:
    """
    Manager class for handling language settings per chat.
    """
    
    def __init__(self, db_connection):
        """
        Initialize LanguageManager.
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables for language settings."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chat_languages (
                chat_id INTEGER PRIMARY KEY,
                language_code TEXT DEFAULT 'id',
                auto_detect BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()
    
    def get_chat_language(self, chat_id: int) -> str:
        """
        Get language setting for a chat.
        
        Args:
            chat_id: Chat ID
        
        Returns:
            Language code for the chat
        """
        cursor = self.db.execute(
            "SELECT language_code FROM chat_languages WHERE chat_id = ?",
            (chat_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        return DEFAULT_LANGUAGE
    
    def set_chat_language(self, chat_id: int, lang_code: str) -> bool:
        """
        Set language for a chat.
        
        Args:
            chat_id: Chat ID
            lang_code: Language code to set
        
        Returns:
            True if successful, False otherwise
        """
        if not is_language_supported(lang_code):
            return False
        
        self.db.execute("""
            INSERT OR REPLACE INTO chat_languages 
            (chat_id, language_code, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (chat_id, lang_code))
        self.db.commit()
        
        return True
    
    def enable_auto_detect(self, chat_id: int) -> bool:
        """
        Enable automatic language detection for a chat.
        
        Args:
            chat_id: Chat ID
        
        Returns:
            True if successful
        """
        self.db.execute("""
            INSERT OR REPLACE INTO chat_languages 
            (chat_id, auto_detect, updated_at) 
            VALUES (?, TRUE, CURRENT_TIMESTAMP)
        """, (chat_id,))
        self.db.commit()
        
        return True
    
    def disable_auto_detect(self, chat_id: int) -> bool:
        """
        Disable automatic language detection for a chat.
        
        Args:
            chat_id: Chat ID
        
        Returns:
            True if successful
        """
        self.db.execute("""
            UPDATE chat_languages 
            SET auto_detect = FALSE, updated_at = CURRENT_TIMESTAMP 
            WHERE chat_id = ?
        """, (chat_id,))
        self.db.commit()
        
        return True
    
    def is_auto_detect_enabled(self, chat_id: int) -> bool:
        """
        Check if auto-detect is enabled for a chat.
        
        Args:
            chat_id: Chat ID
        
        Returns:
            True if auto-detect is enabled
        """
        cursor = self.db.execute(
            "SELECT auto_detect FROM chat_languages WHERE chat_id = ?",
            (chat_id,)
        )
        result = cursor.fetchone()
        
        return result[0] if result else False
