#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2013 Red Hat, Inc.
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
oVirtLive plugin.
"""

import time
import os
import shutil
import glob
import gettext
_ = lambda m: gettext.dgettext(message=m, domain='ovirt-engine-setup')


from otopi import util
from otopi import plugin
from otopi import filetransaction
from otopi import constants as otopicons


import oliveconst


from ovirt_engine_setup import util as osetuputil
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup import dialog


@util.export
class Plugin(plugin.PluginBase):
    """
    oVirtLive plugin.
    """

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._enabled = True

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            oliveconst.CoreEnv.ENABLE
        )
        self.environment.setdefault(
            oliveconst.IsoEnv.ISO_NAME,
            oliveconst.Defaults.DEFAULT_ISO_NAME
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
        condition=lambda self: self.environment[
            oliveconst.CoreEnv.ENABLE
        ],
    )
    def _setup(self):
        self._enabled = True

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
    )
    def _validation(self):
        import ovirtsdk.api
        import ovirtsdk.xml
        self._ovirtsdk_api = ovirtsdk.api
        self._ovirtsdk_xml = ovirtsdk.xml

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.INIT,
        before=(
            oliveconst.Stages.CONFIG_STORAGE,
        ),
        after=(
            osetupcons.Stages.AIO_CONFIG_VDSM,
        ),
    )
    def _initapi(self):
        self._engine_api = self._ovirtsdk_api.API(
            url='https://{fqdn}:{port}/api'.format(
                fqdn=self.environment[osetupcons.ConfigEnv.FQDN],
                port=self.environment[osetupcons.ConfigEnv.PUBLIC_HTTPS_PORT],
            ),
            username='{user}@{domain}'.format(
                user=osetupcons.Const.USER_ADMIN,
                domain=osetupcons.Const.DOMAIN_INTERNAL,
            ),
            password=self.environment[osetupcons.ConfigEnv.ADMIN_PASSWORD],
            ca_file=osetupcons.FileLocations.OVIRT_ENGINE_PKI_ENGINE_CA_CERT,
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.CONFIG_STORAGE,
        before=(
            oliveconst.Stages.COPY_ISO,
        ),
        after=(
            oliveconst.Stages.INIT,
        ),
    )
    def _createstorage(self):
        self.logger.debug('Attaching iso domain')
        time.sleep(10)
        self._engine_api.datacenters.get(
            self.environment[
                oliveconst.CoreEnv.LOCAL_DATA_CENTER
            ]
        ).storagedomains.add(
            self._engine_api.storagedomains.get(
                self.environment[
                   oliveconst.IsoEnv.ISO_NAME
                ]
            )
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.COPY_ISO,
        before=(
            oliveconst.Stages.CREATE_VM,
        ),
        after=(
            oliveconst.Stages.CONFIG_STORAGE,
        ),
    )
    def _copyiso(self):
        self.logger.debug('Copying Iso Files')
        fileList = glob.glob('/home/oVirtuser/oVirtLiveFiles/iso/*.iso')
        targetPath = os.path.join(
            self.environment[
                osetupcons.ConfigEnv.ISO_DOMAIN_NFS_MOUNT_POINT
            ],
            self.environment[
                osetupcons.ConfigEnv.ISO_DOMAIN_SD_UUID
            ],
            'images',
            osetupcons.Const.ISO_DOMAIN_IMAGE_UID
        )
        self.logger.debug('target path' + targetPath)
        for filename in fileList:
            self.logger.debug(filename)
            shutil.move(filename, targetPath)
            os.chown(
                os.path.join(targetPath, os.path.basename(filename)),
                osetuputil.getUid(
                        osetupcons.Defaults.DEFAULT_SYSTEM_USER_VDSM
                ),
                osetuputil.getGid(
                        osetupcons.Defaults.DEFAULT_SYSTEM_GROUP_KVM
                )
            )

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        condition=lambda self: self._enabled,
        name=oliveconst.Stages.CREATE_VM,
        after=(
            oliveconst.Stages.COPY_ISO,
        ),
    )
    def _createvm(self):
        # Defins OS param for the boot option
        params = self._ovirtsdk_xml.params
        os = params.OperatingSystem(
            type_='unassigned',
            boot=(
                params.Boot(dev='cdrom'),
                params.Boot(dev='hd'),
            ),
        )
        MB = 1024*1024
        GB = 1024*MB

        # Create VM
        vm = self._engine_api.vms.add(
            params.VM(
                name='local_vm',
                memory=1*GB,
                os=os,
                cluster=self._engine_api.clusters.get('local_cluster'),
                template=self._engine_api.templates.get('Blank'),
            ),
        )

        # Create NIC
        self._engine_api.vms.get('local_vm').nics.add(
            params.NIC(
                name='eth0',
                network=params.Network(name='ovirtmgmt'),
                interface='virtio',
            ),
        )

        diskParam = params.Disk(
            storage_domains=params.StorageDomains(
                storage_domain=(
                    self._engine_api.storagedomains.get('local_storage'),
                ),
            ),
            size=6*GB,
            type_='data',
            interface='virtio',
            format='cow',
            bootable=True,
        )

        self._engine_api.vms.get(
            'local_vm'
        ).disks.add(diskParam)


# vim: expandtab tabstop=4 shiftwidth=4
