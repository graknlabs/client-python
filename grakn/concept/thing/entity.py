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

from grakn.api.concept.thing.entity import Entity, RemoteEntity
from grakn.api.concept.type.entity_type import EntityType
from grakn.concept.proto import concept_proto_reader
from grakn.concept.thing.thing import _Thing, _RemoteThing


class _Entity(Entity, _Thing):

    def __init__(self, iid: str, entity_type: EntityType):
        super(_Entity, self).__init__(iid)
        self._type = entity_type

    @staticmethod
    def of(thing_proto: concept_proto.Thing):
        return _Entity(concept_proto_reader.iid(thing_proto.iid), concept_proto_reader.type_(thing_proto.type))

    def get_type(self) -> "EntityType":
        return self._type

    def as_remote(self, transaction):
        return _RemoteEntity(transaction, self._iid, self.get_type())


class _RemoteEntity(RemoteEntity, _RemoteThing):

    def __init__(self, transaction, iid: str, entity_type: EntityType):
        super(_RemoteEntity, self).__init__(transaction, iid)
        self._type = entity_type

    def as_remote(self, transaction):
        return _RemoteEntity(transaction, self._iid, self.get_type())

    def get_type(self) -> "EntityType":
        return self._type
