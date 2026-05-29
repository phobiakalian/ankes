"""
Dashboard plugin for Yn Security Bot.
Displays group statistics and activity metrics.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import logging

from yn.utils.db import db
from yn.utils.loggers.activity_logger import ActivityLogger
from yn.plugins.i18n.translations import get_text, DEFAULT_LANGUAGE
from yn.utils.utils import admin_check

logger = logging.getLogger(__name__)

# Initialize activity logger
activity_logger = ActivityLogger(db)


def get_chat_language(chat_id: int) -> str:
    """Get language for a chat."""
    try:
        cursor = db.execute(
            "SELECT language_code FROM chat_languages WHERE chat_id = ?",
            (chat_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else DEFAULT_LANGUAGE
    except Exception:
        return DEFAULT_LANGUAGE


@Client.on_message(filters.command(["dashboard", "stats"]) & filters.group)
@admin_check
async def dashboard(client: Client, message: Message):
    """
    Display group statistics dashboard.
    """
    lang = get_chat_language(message.chat.id)
    chat_id = message.chat.id
    
    try:
        # Get dashboard stats
        stats = activity_logger.get_dashboard_stats(chat_id)
        
        # Format the last updated time
        last_updated = stats.get("last_updated")
        if last_updated:
            try:
                dt = datetime.fromisoformat(last_updated)
                last_updated_str = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                last_updated_str = last_updated
        else:
            last_updated_str = "Belum ada data"
        
        # Build dashboard message
        dashboard_text = (
            f"{get_text(lang, 'dashboard_title')}\n\n"
            f"{get_text(lang, 'dashboard_new_members', count=stats['new_members_today'])}\n"
            f"{get_text(lang, 'dashboard_messages_deleted', count=stats['messages_deleted_today'])}\n"
            f"{get_text(lang, 'dashboard_violations', count=stats['violations_today'])}\n"
            f"{get_text(lang, 'dashboard_warnings', count=stats['warnings_today'])}\n"
            f"{get_text(lang, 'dashboard_mutes', count=stats['mutes_today'])}\n"
            f"{get_text(lang, 'dashboard_bans', count=stats['bans_today'])}\n\n"
            f"{get_text(lang, 'dashboard_last_updated', time=last_updated_str)}"
        )
        
        # Create inline keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📊 Laporan Aktivitas", callback_data="dash_activity_report"),
                InlineKeyboardButton("🔄 Refresh", callback_data="dash_refresh")
            ],
            [
                InlineKeyboardButton("🔥 Top User Aktif", callback_data="dash_top_active"),
                InlineKeyboardButton("⚠️ Pelanggaran", callback_data="dash_violations")
            ]
        ])
        
        await message.reply(dashboard_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error displaying dashboard: {e}")
        await message.reply(get_text(lang, "error") + " Gagal menampilkan dashboard.")


@Client.on_callback_query(filters.regex(r"^dash_"))
async def dashboard_callback(client, callback_query):
    """
    Handle dashboard callback queries.
    """
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    lang = get_chat_language(chat_id)
    
    try:
        if data == "dash_refresh":
            # Refresh dashboard
            stats = activity_logger.get_dashboard_stats(chat_id)
            
            last_updated = stats.get("last_updated")
            if last_updated:
                try:
                    dt = datetime.fromisoformat(last_updated)
                    last_updated_str = dt.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    last_updated_str = last_updated
            else:
                last_updated_str = "Belum ada data"
            
            dashboard_text = (
                f"{get_text(lang, 'dashboard_title')}\n\n"
                f"{get_text(lang, 'dashboard_new_members', count=stats['new_members_today'])}\n"
                f"{get_text(lang, 'dashboard_messages_deleted', count=stats['messages_deleted_today'])}\n"
                f"{get_text(lang, 'dashboard_violations', count=stats['violations_today'])}\n"
                f"{get_text(lang, 'dashboard_warnings', count=stats['warnings_today'])}\n"
                f"{get_text(lang, 'dashboard_mutes', count=stats['mutes_today'])}\n"
                f"{get_text(lang, 'dashboard_bans', count=stats['bans_today'])}\n\n"
                f"{get_text(lang, 'dashboard_last_updated', time=last_updated_str)}"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📊 Laporan Aktivitas", callback_data="dash_activity_report"),
                    InlineKeyboardButton("🔄 Refresh", callback_data="dash_refresh")
                ],
                [
                    InlineKeyboardButton("🔥 Top User Aktif", callback_data="dash_top_active"),
                    InlineKeyboardButton("⚠️ Pelanggaran", callback_data="dash_violations")
                ]
            ])
            
            await callback_query.message.edit_text(dashboard_text, reply_markup=keyboard)
            await callback_query.answer("Dashboard diperbarui!")
        
        elif data == "dash_activity_report":
            # Generate activity report
            report = activity_logger.generate_activity_report(chat_id, period_days=7)
            
            report_text = (
                f"{get_text(lang, 'activity_report_title')}\n\n"
                f"{get_text(lang, 'activity_period', start=report['period_start'], end=report['period_end'])}\n\n"
            )
            
            # Most active users
            if report['most_active_users']:
                report_text += f"{get_text(lang, 'activity_most_active')}\n"
                for i, (user_id, username, count) in enumerate(report['most_active_users'][:5], 1):
                    user_mention = f"@{username}" if username else f"User {user_id}"
                    report_text += f"{i}. {user_mention} - {count} pesan\n"
                report_text += "\n"
            
            # Most muted users
            if report['most_muted_users']:
                report_text += f"{get_text(lang, 'activity_most_muted')}\n"
                for i, (user_id, count) in enumerate(report['most_muted_users'][:5], 1):
                    report_text += f"{i}. User {user_id} - {count} kali\n"
                report_text += "\n"
            
            # Most kicked users
            if report['most_kicked_users']:
                report_text += f"{get_text(lang, 'activity_most_kicked')}\n"
                for i, (user_id, count) in enumerate(report['most_kicked_users'][:5], 1):
                    report_text += f"{i}. User {user_id} - {count} kali\n"
            
            if not any([report['most_active_users'], report['most_muted_users'], report['most_kicked_users']]):
                report_text += get_text(lang, "activity_no_data")
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="dash_back")]
            ])
            
            await callback_query.message.edit_text(report_text, reply_markup=keyboard)
            await callback_query.answer()
        
        elif data == "dash_top_active":
            # Show top active users
            active_users = activity_logger.get_most_active_users(chat_id, limit=10, period_days=7)
            
            if active_users:
                text = "🔥 **Top 10 User Paling Aktif (7 Hari Terakhir)**\n\n"
                for i, (user_id, username, count) in enumerate(active_users, 1):
                    user_mention = f"@{username}" if username else f"User {user_id}"
                    text += f"{i}. {user_mention} - {count} pesan\n"
            else:
                text = get_text(lang, "activity_no_data")
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="dash_back")]
            ])
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
        
        elif data == "dash_violations":
            # Show violations by type
            violations = activity_logger.get_violations_by_type(chat_id, period_days=7)
            
            if violations:
                text = "⚠️ **Pelanggaran Terdeteksi (7 Hari Terakhir)**\n\n"
                violation_names = {
                    "forward": "Forward Pesan",
                    "link": "Link",
                    "command": "Command",
                    "hashtag": "Hashtag",
                    "voice": "Voice Note",
                    "flood": "Spam/Flood",
                    "badword": "Kata Kasar"
                }
                
                for vtype, count in sorted(violations.items(), key=lambda x: x[1], reverse=True):
                    vname = violation_names.get(vtype, vtype.capitalize())
                    text += f"• {vname}: {count}\n"
            else:
                text = "✅ Tidak ada pelanggaran terdeteksi dalam 7 hari terakhir."
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="dash_back")]
            ])
            
            await callback_query.message.edit_text(text, reply_markup=keyboard)
            await callback_query.answer()
        
        elif data == "dash_back":
            # Go back to main dashboard
            await dashboard(client, callback_query.message)
            await callback_query.answer()
    
    except Exception as e:
        logger.error(f"Error handling dashboard callback: {e}")
        await callback_query.answer(get_text(lang, "error") + " Terjadi kesalahan.", show_alert=True)


@Client.on_message(filters.command(["activityreport", "report"]) & filters.group)
@admin_check
async def activity_report_command(client: Client, message: Message):
    """
    Generate activity report command.
    """
    lang = get_chat_language(message.chat.id)
    chat_id = message.chat.id
    
    # Parse period from command
    period_days = 7  # Default
    if len(message.command) > 1:
        try:
            period_days = int(message.command[1])
            if period_days < 1 or period_days > 90:
                period_days = 7
        except ValueError:
            pass
    
    try:
        report = activity_logger.generate_activity_report(chat_id, period_days=period_days)
        
        report_text = (
            f"{get_text(lang, 'activity_report_title')}\n\n"
            f"{get_text(lang, 'activity_period', start=report['period_start'], end=report['period_end'])}\n\n"
        )
        
        # Most active users
        if report['most_active_users']:
            report_text += f"{get_text(lang, 'activity_most_active')}\n"
            for i, (user_id, username, count) in enumerate(report['most_active_users'][:5], 1):
                user_mention = f"@{username}" if username else f"User {user_id}"
                report_text += f"{i}. {user_mention} - {count} pesan\n"
            report_text += "\n"
        
        # Most muted users
        if report['most_muted_users']:
            report_text += f"{get_text(lang, 'activity_most_muted')}\n"
            for i, (user_id, count) in enumerate(report['most_muted_users'][:5], 1):
                report_text += f"{i}. User {user_id} - {count} kali di-mute\n"
            report_text += "\n"
        
        # Most kicked users
        if report['most_kicked_users']:
            report_text += f"{get_text(lang, 'activity_most_kicked')}\n"
            for i, (user_id, count) in enumerate(report['most_kicked_users'][:5], 1):
                report_text += f"{i}. User {user_id} - {count} kali di-kick/ban\n"
            report_text += "\n"
        
        # Violations by type
        if report['violations_by_type']:
            report_text += "**Pelanggaran per Tipe:**\n"
            for vtype, count in sorted(report['violations_by_type'].items(), key=lambda x: x[1], reverse=True):
                report_text += f"• {vtype}: {count}\n"
        
        if not any([report['most_active_users'], report['most_muted_users'], 
                   report['most_kicked_users'], report['violations_by_type']]):
            report_text += get_text(lang, "activity_no_data")
        
        await message.reply(report_text)
    except Exception as e:
        logger.error(f"Error generating activity report: {e}")
        await message.reply(get_text(lang, "error") + " Gagal membuat laporan aktivitas.")
