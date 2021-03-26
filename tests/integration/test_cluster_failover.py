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
import subprocess
import unittest
from time import sleep
from unittest import TestCase

from grakn.api.database import ClusterDatabaseManager
from grakn.client import *


SCHEMA = GraknSession.Type.SCHEMA
WRITE = GraknTransaction.Type.WRITE
READ = GraknTransaction.Type.READ


class TestClusterFailover(TestCase):

    def setUp(self):
        with Grakn.cluster_client(["localhost:11729", "localhost:21729", "localhost:31729"]) as client:
            if client.databases().contains("grakn"):
                client.databases().get("grakn").delete()
            client.databases().create("grakn")

    def get_primary_replica(self, database_manager: ClusterDatabaseManager):
        retry_num = 0
        while retry_num < 10:
            print("Discovering replicas for database 'grakn'...")
            db = database_manager.get("grakn")
            print("Discovered " + str([str(replica) for replica in db.replicas()]))
            if db.primary_replica():
                return db.primary_replica()
            else:
                retry_num += 1
                print("There is no primary replica yet. Retrying in 2s...")
                sleep(2)
                return self.get_primary_replica(database_manager)
        assert False, "Retry limit exceeded while seeking a primary replica."

    def test_put_entity_type_to_crashed_primary_replica(self):
        with Grakn.cluster_client(["localhost:11729", "localhost:21729", "localhost:31729"]) as client:
            assert client.databases().contains("grakn")
            primary_replica = self.get_primary_replica(client.databases())
            print("Performing operations against the primary replica " + str(primary_replica))
            with client.session("grakn", SCHEMA) as session, session.transaction(WRITE) as tx:
                tx.concepts().put_entity_type("person")
                print("Put the entity type 'person'.")
                tx.commit()
            with client.session("grakn", SCHEMA) as session, session.transaction(READ) as tx:
                person = tx.concepts().get_entity_type("person")
                print("Retrieved entity type with label '%s' from primary replica." % person.get_label())
                assert person.get_label().name() == "person"
            iteration = 0
            while iteration < 10:
                iteration += 1
                primary_replica = self.get_primary_replica(client.databases())
                print("Stopping primary replica (test %d/10)..." % iteration)
                port = primary_replica.address()[10:15]
                lsof = subprocess.check_output(["lsof", "-i", ":%s" % port])
                primary_replica_server_pid = [conn.split()[1] for conn in lsof.decode("utf-8").split("\n") if "LISTEN" in conn][0]
                print("Primary replica is hosted by server with PID %s" % primary_replica_server_pid)
                subprocess.check_call(["kill", "-9", primary_replica_server_pid])
                print("Primary replica stopped successfully.")
                sleep(0.5)
                with client.session("grakn", SCHEMA) as session, session.transaction(READ) as tx:
                    person = tx.concepts().get_entity_type("person")
                    print("Retrieved entity type with label '%s' from new primary replica." % person.get_label())
                    assert person.get_label().name() == "person"
                idx = str(primary_replica.address())[10]
                subprocess.Popen(["./%s/grakn" % idx, "server", "--data", "server/data", "--address", "127.0.0.1:%s1729:%s1730" % (idx, idx), "--peer", "127.0.0.1:11729:11730", "--peer", "127.0.0.1:21729:21730", "--peer", "127.0.0.1:31729:31730"])
                lsof = None
                live_check_iteration = 0
                while not lsof and live_check_iteration < 60:
                    live_check_iteration += 1
                    try:
                        lsof = subprocess.check_output(["lsof", "-i", ":%s" % port])
                    except subprocess.CalledProcessError:
                        pass
                    sleep(0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
