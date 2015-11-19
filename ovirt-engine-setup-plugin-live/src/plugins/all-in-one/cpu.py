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
AIO cpu check plugin.
"""
import gettext
import sys

from otopi import plugin, util

from ovirt_engine_setup.ovirt_live import constants as oliveconst

from vdsm import cpuinfo


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-live')


@util.export
class Plugin(plugin.PluginBase):
    """
    AIO cpu check plugin.
    """
    # CPU list from: git grep ServerCPUList | grep 4.0
    CPU_FAMILIES = (
        {'model': 'model_POWER8', 'name': 'IBM POWER8'},
        {'model': 'model_Broadwell', 'name': 'Intel Broadwell Family'},
        {
            'model': 'model_Broadwell-noTSX',
            'name': 'Intel Broadwell-noTSX Family'
        },
        {'model': 'model_Haswell-noTSX', 'name': 'Intel Haswell-noTSX Family'},
        {'model': 'model_Haswell', 'name': 'Intel Haswell Family'},
        {'model': 'model_SandyBridge', 'name': 'Intel SandyBridge Family'},
        {'model': 'model_Westmere', 'name': 'Intel Westmere Family'},
        {'model': 'model_Nehalem', 'name': 'Intel Nehalem Family'},
        {'model': 'model_Penryn', 'name': 'Intel Penryn Family'},
        {'model': 'model_Conroe', 'name': 'Intel Conroe Family'},
        {'model': 'model_Opteron_G5', 'name': 'AMD Opteron G5'},
        {'model': 'model_Opteron_G4', 'name': 'AMD Opteron G4'},
        {'model': 'model_Opteron_G3', 'name': 'AMD Opteron G3'},
        {'model': 'model_Opteron_G2', 'name': 'AMD Opteron G2'},
        {'model': 'model_Opteron_G1', 'name': 'AMD Opteron G1'},
    )

    LIBVIRTD_SERVICE_NAME = 'libvirtd'

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    def _startLibvirt(self):
        """
        Starts libvirt service
        """
        ret = False

        if not self.services.status(
            name=self.LIBVIRTD_SERVICE_NAME
        ):
            self.services.state(
                name=self.LIBVIRTD_SERVICE_NAME,
                state=True,
            )
            ret = True

        return ret

    def _getCompatibleCpuModels(self):
        self.logger.debug('Attempting to load the caps vdsm module')
        savedPath = sys.path
        ret = None
        try:
            sys.path.append(oliveconst.FileLocations.AIO_VDSM_PATH)
            caps = util.loadModule(
                path=oliveconst.FileLocations.AIO_VDSM_PATH,
                name='caps',
            )
            ret = (
                cpuinfo.model(),
                caps._getCompatibleCpuModels(),
            )
        finally:
            sys.path = savedPath
        return ret

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment[oliveconst.CoreEnv.VDSM_CPU] = None
        self.environment[oliveconst.CoreEnv.SUPPORTED] = False

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.ENABLE
        ],
        priority=plugin.Stages.PRIORITY_HIGH,
    )
    def _setup(self):
        from ovirt_host_deploy import hardware
        virtualization = hardware.Virtualization()
        result = virtualization.detect()
        if result == virtualization.DETECT_RESULT_SUPPORTED:
            self.logger.info(_('Hardware supports virtualization'))
            self.environment[oliveconst.CoreEnv.SUPPORTED] = True

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.CONFIGURE
        ],
    )
    def _validation(self):
        shouldStopLibvirt = self._startLibvirt()
        try:
            cpu, compatible = self._getCompatibleCpuModels()
            self.logger.debug(
                'Compatible CPU models are: %s',
                compatible,
            )

            supported = (
                set([entry['model'] for entry in self.CPU_FAMILIES]) &
                set(compatible)
            )
            # All-in-one want the best cpu between compatible.
            # The preference is defined by the order of
            # CPU_FAMILIES
            # We need to save the corresponding CPU name for cluster
            # creation.
            for entry in self.CPU_FAMILIES:
                if entry['model'] in supported:
                    self.environment[
                        oliveconst.CoreEnv.VDSM_CPU
                    ] = entry['name']
                    break

        finally:
            if shouldStopLibvirt:
                self.services.state(
                    name=self.LIBVIRTD_SERVICE_NAME,
                    state=False,
                )


# vim: expandtab tabstop=4 shiftwidth=4
