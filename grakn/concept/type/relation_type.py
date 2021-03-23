#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import grakn_protocol.common.concept_pb2 as concept_proto

from grakn.api.concept.type.relation_type import RelationType, RemoteRelationType
from grakn.common.label import Label
from grakn.common.rpc.request_builder import relation_type_create_req, relation_type_get_relates_req, \
    relation_type_set_relates_req, relation_type_unset_relates_req
from grakn.concept.thing.relation import _Relation
from grakn.concept.type.role_type import _RoleType
from grakn.concept.type.thing_type import _ThingType, _RemoteThingType


class _RelationType(RelationType, _ThingType):

    @staticmethod
    def of(type_proto: concept_proto.Type):
        return _RelationType(Label.of(type_proto.label), type_proto.root)

    def as_remote(self, transaction):
        return _RemoteRelationType(transaction, self.get_label(), self.is_root())


class _RemoteRelationType(RemoteRelationType, _RemoteThingType):

    def as_remote(self, transaction):
        return _RemoteRelationType(transaction, self.get_label(), self.is_root())

    def create(self):
        return _Relation.of(self.execute(relation_type_create_req(self.get_label())).relation_type_create_res.relation)

    def get_relates(self, role_label: str = None):
        if role_label:
            res = self.execute(relation_type_get_relates_req(self.get_label(), role_label))
            return _RoleType.of(res.role_type) if res.HasField("role_type") else None
        else:
            return [_RoleType.of(rt) for rp in self.stream(relation_type_get_relates_req(self.get_label()))
                    for rt in rp.relation_type_get_relates_res_part.roles]

    def set_relates(self, role_label: str, overridden_label: str = None):
        self.execute(relation_type_set_relates_req(self.get_label(), role_label, overridden_label))

    def unset_relates(self, role_label: str):
        self.execute(relation_type_unset_relates_req(self.get_label(), role_label))
