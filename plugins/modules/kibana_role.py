#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright: (c) 2020, TODO

from __future__ import absolute_import, division, print_function

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'metadata_version': '1.1'
}

DOCUMENTATION = '''
---
'''

EXAMPLES = '''
'''

RETURN = '''
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, url_argument_spec, basic_auth_header

__metaclass__ = type


class KibanaRoleInterface(object):

    def __init__(self, module):
        self._module = module
        # {{{ Authentication header
        self.headers = {"Content-Type": "application/json"}
        self.headers["Authorization"] = basic_auth_header(module.params['url_username'], module.params['url_password'])
        self.headers["kbn-xsrf"] = "true"
        # }}}
        self.kibana_url = module.params.get("url")

    def _send_request(self, url, data=None, headers=None, method="GET"):
        if data is not None:
            data = json.dumps(data, sort_keys=True)
        if not headers:
            headers = self.headers

        full_url = "{kibana_url}{path}".format(kibana_url=self.kibana_url, path=url)
        resp, info = fetch_url(self._module, full_url, data=data, headers=headers, method=method)
        status_code = info["status"]
        if status_code == 404:
            return None
        elif status_code == 401:
            self._module.fail_json(failed=True, msg="Unauthorized to perform action '%s' on '%s' header: %s" % (method, full_url, self.headers))
        elif status_code == 403:
            self._module.fail_json(failed=True, msg="Permission Denied")
        elif status_code == 204:
            return None        
        elif status_code == 200:
            return self._module.from_json(resp.read())
        body = resp.read() if resp else None
        self._module.fail_json(failed=True, msg="Kibana Role API answered with HTTP %s" % info['body'])

    def get_role(self, name):
        return self._send_request("/api/security/role/{name}".format(name=name))

    def prepare_payload(self, kibana):
        payload = []
        for role in kibana:
            spaces=["default"]
            if "spaces" in role.keys():
                spaces=[role["spaces"]]
            payload.append(dict(base=[role["base"]], spaces=spaces))
        return { "kibana": json.dumps(payload) }

    def create_role(self, name, kibana):
        # https://www.elastic.co/guide/en/kibana/current/role-management-api-put.html
        role_payload = self.prepare_payload(kibana)
        self._send_request("/api/security/role/{name}".format(name=name), data=role_payload, method="PUT")
        return self.get_role(name)

    def delete_role(self, name):
        role_payload = { "kibana": [] }
        self._send_request("/api/security/role/{name}".format(name=name), data=role_payload, method="DELETE")
        return self.get_role(name)


def is_role_update_required(target_role, kibana):
    return True


def setup_module_object():
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )
    return module


argument_spec = url_argument_spec()
# remove unnecessary arguments
del argument_spec['force']
del argument_spec['force_basic_auth']
del argument_spec['http_agent']


argument_spec.update(
    url=dict(type='str', required=True),
    url_username=dict(default='elastic'),
    url_password=dict(type='str', required=True, no_log=True),
    state=dict(choices=['present', 'absent'], default='present'),
    name=dict(type='str', required=True),
    kibana=dict(type='list', required=False, default=[]),
)


def main():
    module = setup_module_object()
    name = module.params['name']
    kibana = module.params['kibana']
    state = module.params['state']

    kibana_iface = KibanaRoleInterface(module)

    # search existing kibana role
    target_role = kibana_iface.get_role(name)
    if state == 'present':

        if (target_role is None) or (is_role_update_required(target_role, kibana)):
            # create or update role
            created_role = kibana_iface.create_role(name, kibana)
            module.exit_json(changed=True, role=created_role)

        module.exit_json(role=target_role)

    elif state == 'absent':
        if target_role is None:
            module.exit_json(message="No role found, nothing to do")
        result = kibana_iface.delete_role(name)
        module.exit_json(changed=True, message=result)


if __name__ == '__main__':
    main()
