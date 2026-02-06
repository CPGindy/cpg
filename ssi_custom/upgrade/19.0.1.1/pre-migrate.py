import logging

_logger = logging.getLogger(__name__)

MODULES_TO_UNINSTALL = [
    'sw_multi_search',
]


def migrate(env):
    for module_name in MODULES_TO_UNINSTALL:
        module = env['ir.module.module'].search([
            ('name', '=', module_name),
            ('state', '=', 'installed'),
        ], limit=1)
        if module:
            _logger.info("Uninstalling module: %s", module_name)
            module.button_immediate_uninstall()
            _logger.info("Successfully uninstalled: %s", module_name)
        else:
            _logger.info("Module %s not found or not installed, skipping.", module_name)