# upgrade/19.0.1.1/pre-migrate.py
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Starting pre-migration: cleaning up sw_multi_search...")

    cr.execute("""
        DELETE FROM ir_ui_view 
        WHERE model = 'sw.multi.search' 
        OR name ILIKE '%%sw_multi_search%%'
    """)

    cr.execute("""
        DELETE FROM ir_ui_menu 
        WHERE id IN (
            SELECT res_id FROM ir_model_data 
            WHERE module = 'sw_multi_search' 
            AND model = 'ir.ui.menu'
        )
    """)

    cr.execute("""
        DELETE FROM ir_act_window 
        WHERE id IN (
            SELECT res_id FROM ir_model_data 
            WHERE module = 'sw_multi_search' 
            AND model = 'ir.actions.act_window'
        )
    """)

    cr.execute("DELETE FROM ir_model_data WHERE module = 'sw_multi_search'")

    cr.execute("""
        UPDATE ir_module_module 
        SET state = 'uninstalled' 
        WHERE name = 'sw_multi_search' AND state = 'installed'
    """)

    _logger.info("Pre-migration cleanup for sw_multi_search completed.")