#
# ovirt-engine-setup -- oVirt Live
# Copyright (C) 2013-2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""
Firewall configuration plugin for AIO.
"""

import gettext

from otopi import plugin
from otopi import util

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.ovirt_live import constants as oliveconst


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-live')


@util.export
class Plugin(plugin.PluginBase):
    """
    Firewall configuration plugin for AIO
    """

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        after=(
            osetupcons.Stages.NET_FIREWALL_MANAGER_AVAILABLE,
            oliveconst.Stages.AIO_CONFIG_AVAILABLE,
        ),
        # must be run before firewall_manager plugin
        condition=lambda self: self.environment[oliveconst.CoreEnv.CONFIGURE],
        # must be always enabled to create examples
    )
    def _configuration(self):
        self.environment[osetupcons.NetEnv.FIREWALLD_SERVICES].append(
            {
                'name': 'ovirt-aio',
                'directory': 'ovirt-engine'
            }
        )


# vim: expandtab tabstop=4 shiftwidth=4