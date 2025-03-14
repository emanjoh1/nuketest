# -*- coding: utf-8 -*-

"""Module deleting all redshift resources."""

from typing import Iterator, Dict

from botocore.exceptions import ClientError, EndpointConnectionError

from nuke.client_connections import AwsClient
from nuke.exceptions import nuke_exceptions


class NukeRedshift:
    """Abstract redshift nuke in a class."""

    def __init__(self, region_name=None) -> None:
        """Initialize redshift nuke."""
        self.redshift = AwsClient().connect("redshift", region_name)

        try:
            self.redshift.describe_clusters()
        except EndpointConnectionError:
            print("Redshift resource is not available in this aws region")
            return

    def nuke(self, older_than_seconds: float, required_tags: Dict[str, str] = None) -> None:
        """Redshift resources deleting function.

        Deleting all redshift resources with
        a timestamp greater than older_than_seconds.
        That include:
          - clusters
          - snapshots
          - subnets
          - param groups

        :param int older_than_seconds:
            The timestamp in seconds used from which the aws
            resource will be deleted
        :param dict required_tags:
            A dictionary of required tags (key-value pairs) for the Redshift clusters to exclude from deletion
        """
        self.nuke_clusters(older_than_seconds, required_tags)
        self.nuke_snapshots(older_than_seconds)
        self.nuke_subnets()
        self.nuke_param_groups()

    def nuke_clusters(self, time_delete: float, required_tags: Dict[str, str] = None) -> None:
        """Redshift cluster deleting function.

        Deleting redshift clusters with a timestamp lower than
        time_delete and not matching the required tags.

        :param int time_delete:
            The timestamp in seconds used from which the aws resource
            will be deleted
        :param dict required_tags:
            A dictionary of required tags (key-value pairs) for the Redshift clusters to exclude from deletion
        """
        for cluster in self.list_clusters(time_delete, required_tags):
            try:
                self.redshift.delete_cluster(
                    ClusterIdentifier=cluster, SkipFinalClusterSnapshot=True
                )
                print("Nuke redshift cluster {0}".format(cluster))
            except ClientError as exc:
                nuke_exceptions("redshift cluster", cluster, exc)

    def nuke_snapshots(self, time_delete: float) -> None:
        """Redshift snapshot deleting function.

        Deleting redshift snapshots with a timestamp lower than
        time_delete.

        :param int time_delete:
            The timestamp in seconds used from which the aws resource
            will be deleted
        """
        for snapshot in self.list_snapshots(time_delete):
            try:
                self.redshift.delete_cluster_snapshot(
                    SnapshotIdentifier=snapshot
                )
                print("Nuke redshift snapshot {0}".format(snapshot))
            except ClientError as exc:
                nuke_exceptions("redshift snapshot", snapshot, exc)

    def nuke_subnets(self) -> None:
        """Redshift subnet deleting function.

        Deleting redshift subnets with a timestamp lower than
        time_delete.

        :param int time_delete:
            The timestamp in seconds used from which the aws resource
            will be deleted
        """
        for subnet in self.list_subnet():
            try:
                self.redshift.delete_cluster_subnet_group(
                    ClusterSubnetGroupName=subnet
                )
                print("Nuke redshift subnet {0}".format(subnet))
            except ClientError as exc:
                nuke_exceptions("redshift subnet", subnet, exc)

    def nuke_param_groups(self) -> None:
        """Redshift parameter group deleting function.

        Deleting redshift parameter groups with a timestamp lower than
        time_delete.

        :param int time_delete:
            The timestamp in seconds used from which the aws resource
            will be deleted
        """
        for param in self.list_cluster_params():
            try:
                self.redshift.delete_cluster_parameter_group(
                    ParameterGroupName=param
                )
                print("Nuke redshift param {0}".format(param))
            except ClientError as exc:
                nuke_exceptions("redshift param", param, exc)

    def list_clusters(self, time_delete: float, required_tags: Dict[str, str] = None) -> Iterator[str]:
        """Redshift cluster list function.

        List IDs of all redshift clusters with a timestamp lower than
        time_delete and not matching the required tags.

        :param int time_delete:
            Timestamp in seconds used for filter redshift clusters
        :param dict required_tags:
            A dictionary of required tags (key-value pairs) for the Redshift clusters to exclude from deletion

        :yield Iterator[str]:
            Redshift cluster IDs
        """
        paginator = self.redshift.get_paginator("describe_clusters")

        for page in paginator.paginate():
            for cluster in page["Clusters"]:
                if cluster["ClusterCreateTime"].timestamp() < time_delete:
                    if required_tags and not self._cluster_has_required_tags(cluster, required_tags):
                        continue
                    yield cluster["ClusterIdentifier"]

    def list_snapshots(self, time_delete: float) -> Iterator[str]:
        """Redshift snapshot list function.

        List IDs of all redshift snapshots with a timestamp
        lower than time_delete.

        :param int time_delete:
            Timestamp in seconds used for filter redshift snapshots

        :yield Iterator[str]:
            Redshift snapshots IDs
        """
        paginator = self.redshift.get_paginator("describe_cluster_snapshots")

        for page in paginator.paginate():
            for snapshot in page["Snapshots"]:
                if snapshot["SnapshotCreateTime"].timestamp() < time_delete:
                    yield snapshot["SnapshotIdentifier"]

    def list_subnet(self) -> Iterator[str]:
        """Redshift subnet list function.

        :yield Iterator[str]:
            Redshift subnet names
        """
        paginator = self.redshift.get_paginator("describe_cluster_subnet_groups")

        for page in paginator.paginate():
            for subnet in page["ClusterSubnetGroups"]:
                yield subnet["ClusterSubnetGroupName"]

    def list_cluster_params(self) -> Iterator[str]:
        """Redshift cluster parameter list function.

        :yield Iterator[str]:
            Redshift cluster parameter names
        """
        paginator = self.redshift.get_paginator("describe_cluster_parameter_groups")

        for page in paginator.paginate():
            for param in page["ParameterGroups"]:
                yield param["ParameterGroupName"]

    def _cluster_has_required_tags(self, cluster: dict, required_tags: Dict[str, str]) -> bool:
        """Check if the cluster has the required tags.

        :param dict cluster:
            The Redshift cluster dictionary
        :param dict required_tags:
            A dictionary of required tags (key-value pairs) to exclude from deletion

        :return bool:
            True if the cluster has all the required tags, False otherwise
        """
        try:
            tags = self.redshift.list_tags_for_resource(ResourceName=cluster["ClusterIdentifier"])
            tag_dict = {tag["Key"]: tag["Value"] for tag in tags["TaggedResources"]}
            for key, value in required_tags.items():
                if tag_dict.get(key) != value:
                    return False
            return True
        except ClientError as e:
            print(f"Failed to get tags for Redshift cluster {cluster['ClusterIdentifier']}: {e}")
            return False
