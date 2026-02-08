"""Map resource type strings to Diagrams node classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from diagrams.azure.compute import (
    ACR,
    AKS,
    AppServices,
    AvailabilitySets,
    BatchAccounts,
    ContainerApps,
    ContainerInstances,
    ContainerRegistries,
    Disks,
    FunctionApps,
    KubernetesServices,
    ServiceFabricClusters,
    SpringCloud,
    VM,
    VirtualMachine,
    VMScaleSet,
)
from diagrams.azure.database import (
    BlobStorage as DbBlobStorage,
    CacheForRedis,
    CosmosDb,
    DataExplorerClusters,
    DataFactory,
    DataLake,
    DatabaseForMariadbServers,
    DatabaseForMysqlServers,
    DatabaseForPostgresqlServers,
    ElasticDatabasePools,
    ManagedDatabases,
    SQL,
    SQLDatabases,
    SQLManagedInstances,
    SQLServers,
    SynapseAnalytics,
)
from diagrams.azure.network import (
    ApplicationGateway,
    ApplicationSecurityGroups,
    CDNProfiles,
    DNSPrivateZones,
    DNSZones,
    ExpressrouteCircuits,
    Firewall,
    FrontDoors,
    LoadBalancers,
    NetworkInterfaces,
    PrivateEndpoint,
    PublicIpAddresses,
    RouteTables,
    Subnets,
    TrafficManagerProfiles,
    VirtualNetworkGateways,
    VirtualNetworks,
    VirtualWans,
)
from diagrams.azure.storage import (
    ArchiveStorage,
    AzureFileshares,
    AzureNetappFiles,
    BlobStorage,
    DataBox,
    DataLakeStorage,
    GeneralStorage,
    NetappFiles,
    QueuesStorage,
    StorageAccounts,
    StorageSyncServices,
    TableStorage,
)
from diagrams.azure.security import (
    AzureSentinel,
    KeyVaults,
    SecurityCenter,
    Sentinel,
)
from diagrams.azure.integration import (
    APIManagement,
    AppConfiguration,
    AzureServiceBus,
    EventGridDomains,
    EventGridTopics,
    LogicApps,
    ServiceBus,
)
from diagrams.azure.web import (
    AppServiceEnvironments,
    AppServicePlans,
    AppServices as WebAppServices,
    CognitiveSearch,
    CognitiveServices,
    MediaServices,
    NotificationHubNamespaces,
    Search,
    Signalr,
    StaticApps,
)
from diagrams.azure.analytics import (
    AnalysisServices,
    AzureDatabricks,
    Databricks,
    EventHubClusters,
    EventHubs,
    HDInsightClusters,
    LogAnalyticsWorkspaces,
    StreamAnalyticsJobs,
)
from diagrams.azure.identity import (
    ActiveDirectory,
    AzureADB2C,
    AzureADDomainServices,
    ConditionalAccess,
    EnterpriseApplications,
    ManagedIdentities,
    Users,
)
from diagrams.azure.iot import (
    DeviceProvisioningServices,
    DigitalTwins,
    IotCentralApplications,
    IotHub,
    Maps,
)
from diagrams.azure.ml import (
    AzureOpenAI,
    BotServices,
    CognitiveServices as MlCognitiveServices,
    MachineLearningServiceWorkspaces,
)
from diagrams.azure.monitor import (
    ApplicationInsights,
    LogAnalyticsWorkspaces as MonLogAnalyticsWorkspaces,
    Monitor,
)
from diagrams.azure.devops import (
    AzureDevops,
    DevtestLabs,
    Pipelines,
    Repos,
)
from diagrams.azure.general import Subscriptions

# AWS imports
try:
    from diagrams.aws.compute import EC2, ECS, Lambda, ElasticBeanstalk, Batch as AwsBatch, Fargate
    from diagrams.aws.database import RDS, Dynamodb, Redshift, ElastiCache, Aurora
    from diagrams.aws.network import VPC, ELB, ALB, NLB, CloudFront, Route53, APIGateway
    from diagrams.aws.storage import S3, EBS, EFS
    from diagrams.aws.security import IAM, KMS, WAF
    from diagrams.aws.integration import SQS, SNS, StepFunctions, Eventbridge
    _AWS_AVAILABLE = True
except ImportError:
    _AWS_AVAILABLE = False

try:
    from diagrams.gcp.compute import ComputeEngine, AppEngine, Functions as GcpFunctions, KubernetesEngine, Run
    from diagrams.gcp.database import SQL as GcpSQL, Spanner, Bigtable, Firestore, Memorystore
    from diagrams.gcp.network import LoadBalancing, CDN as GcpCDN, DNS as GcpDNS, VPC as GcpVPC
    from diagrams.gcp.storage import GCS
    _GCP_AVAILABLE = True
except ImportError:
    _GCP_AVAILABLE = False

try:
    from diagrams.k8s.compute import Pod, Deployment, ReplicaSet, StatefulSet, DaemonSet, Job, CronJob
    from diagrams.k8s.network import Service, Ingress, NetworkPolicy
    from diagrams.k8s.storage import PersistentVolume, PersistentVolumeClaim, StorageClass
    from diagrams.k8s.group import Namespace
    _K8S_AVAILABLE = True
except ImportError:
    _K8S_AVAILABLE = False

if TYPE_CHECKING:
    pass

NODE_MAP: dict[str, type] = {
    # --- Compute ---
    "app-service": AppServices,
    "app-services": AppServices,
    "vm": VirtualMachine,
    "virtual-machine": VirtualMachine,
    "virtual-machines": VirtualMachine,
    "vmss": VMScaleSet,
    "vm-scale-set": VMScaleSet,
    "aks": KubernetesServices,
    "kubernetes-services": KubernetesServices,
    "kubernetes": KubernetesServices,
    "acr": ContainerRegistries,
    "container-registry": ContainerRegistries,
    "container-registries": ContainerRegistries,
    "container-instances": ContainerInstances,
    "container-apps": ContainerApps,
    "function-apps": FunctionApps,
    "func": FunctionApps,
    "functions": FunctionApps,
    "batch-accounts": BatchAccounts,
    "batch": BatchAccounts,
    "availability-sets": AvailabilitySets,
    "disks": Disks,
    "service-fabric": ServiceFabricClusters,
    "spring-cloud": SpringCloud,
    "spring-apps": SpringCloud,
    # --- Database ---
    "sql-database": SQLDatabases,
    "sql-databases": SQLDatabases,
    "sql": SQL,
    "sql-server": SQLServers,
    "sql-servers": SQLServers,
    "sql-managed-instance": SQLManagedInstances,
    "sql-managed-instances": SQLManagedInstances,
    "cosmos": CosmosDb,
    "cosmos-db": CosmosDb,
    "cosmosdb": CosmosDb,
    "azure-cosmos-db": CosmosDb,
    "redis": CacheForRedis,
    "cache-redis": CacheForRedis,
    "cache-for-redis": CacheForRedis,
    "data-factory": DataFactory,
    "adf": DataFactory,
    "data-lake": DataLake,
    "data-explorer": DataExplorerClusters,
    "mysql": DatabaseForMysqlServers,
    "mariadb": DatabaseForMariadbServers,
    "postgres": DatabaseForPostgresqlServers,
    "postgresql": DatabaseForPostgresqlServers,
    "elastic-pool": ElasticDatabasePools,
    "managed-database": ManagedDatabases,
    "synapse": SynapseAnalytics,
    "synapse-analytics": SynapseAnalytics,
    # --- Network ---
    "firewall": Firewall,
    "vnet": VirtualNetworks,
    "virtual-network": VirtualNetworks,
    "virtual-networks": VirtualNetworks,
    "subnet": Subnets,
    "subnets": Subnets,
    "subnets-with-delegation": Subnets,
    "load-balancer": LoadBalancers,
    "load-balancers": LoadBalancers,
    "lb": LoadBalancers,
    "application-gateway": ApplicationGateway,
    "application-gateways": ApplicationGateway,
    "agw": ApplicationGateway,
    "nsg": ApplicationSecurityGroups,
    "network-security-groups": ApplicationSecurityGroups,
    "front-door": FrontDoors,
    "front-doors": FrontDoors,
    "frontdoor": FrontDoors,
    "cdn": CDNProfiles,
    "cdn-profiles": CDNProfiles,
    "traffic-manager": TrafficManagerProfiles,
    "expressroute": ExpressrouteCircuits,
    "expressroute-circuits": ExpressrouteCircuits,
    "vpn-gateway": VirtualNetworkGateways,
    "virtual-network-gateways": VirtualNetworkGateways,
    "virtual-wan": VirtualWans,
    "virtual-wans": VirtualWans,
    "private-endpoint": PrivateEndpoint,
    "dns-zone": DNSZones,
    "dns-zones": DNSZones,
    "dns-private-zone": DNSPrivateZones,
    "dns-private-zones": DNSPrivateZones,
    "public-ip": PublicIpAddresses,
    "public-ip-addresses": PublicIpAddresses,
    "route-table": RouteTables,
    "route-tables": RouteTables,
    "nic": NetworkInterfaces,
    "network-interfaces": NetworkInterfaces,
    # --- Storage ---
    "storage": StorageAccounts,
    "storage-accounts": StorageAccounts,
    "storage-account": StorageAccounts,
    "blob-storage": BlobStorage,
    "file-share": AzureFileshares,
    "azure-fileshares": AzureFileshares,
    "queue-storage": QueuesStorage,
    "table-storage": TableStorage,
    "data-lake-storage": DataLakeStorage,
    "data-box": DataBox,
    "archive-storage": ArchiveStorage,
    "netapp-files": NetappFiles,
    "storage-sync": StorageSyncServices,
    # --- Security ---
    "key-vault": KeyVaults,
    "key-vaults": KeyVaults,
    "kv": KeyVaults,
    "security-center": SecurityCenter,
    "sentinel": Sentinel,
    "azure-sentinel": AzureSentinel,
    # --- Integration ---
    "api-management": APIManagement,
    "api-management-services": APIManagement,
    "apim": APIManagement,
    "service-bus": ServiceBus,
    "azure-service-bus": AzureServiceBus,
    "logic-apps": LogicApps,
    "logic-app": LogicApps,
    "event-grid": EventGridTopics,
    "event-grid-topics": EventGridTopics,
    "event-grid-domains": EventGridDomains,
    "app-configuration": AppConfiguration,
    # --- Web ---
    "app-service-plan": AppServicePlans,
    "app-service-plans": AppServicePlans,
    "app-service-environment": AppServiceEnvironments,
    "app-service-environments": AppServiceEnvironments,
    "static-app": StaticApps,
    "static-apps": StaticApps,
    "static-web-app": StaticApps,
    "cognitive-search": CognitiveSearch,
    "cognitive-services": CognitiveServices,
    "media-services": MediaServices,
    "signalr": Signalr,
    "notification-hub": NotificationHubNamespaces,
    "search": Search,
    # --- Analytics ---
    "event-hub": EventHubs,
    "event-hubs": EventHubs,
    "event-hub-cluster": EventHubClusters,
    "databricks": Databricks,
    "azure-databricks": AzureDatabricks,
    "hdinsight": HDInsightClusters,
    "hdinsight-clusters": HDInsightClusters,
    "stream-analytics": StreamAnalyticsJobs,
    "log-analytics": LogAnalyticsWorkspaces,
    "log-analytics-workspaces": LogAnalyticsWorkspaces,
    "law": LogAnalyticsWorkspaces,
    "analysis-services": AnalysisServices,
    # --- Identity ---
    "active-directory": ActiveDirectory,
    "aad": ActiveDirectory,
    "azure-ad": ActiveDirectory,
    "azure-ad-b2c": AzureADB2C,
    "b2c": AzureADB2C,
    "azure-ad-domain-services": AzureADDomainServices,
    "conditional-access": ConditionalAccess,
    "enterprise-applications": EnterpriseApplications,
    "managed-identity": ManagedIdentities,
    "managed-identities": ManagedIdentities,
    "users": Users,
    # --- IoT ---
    "iot-hub": IotHub,
    "iot-central": IotCentralApplications,
    "digital-twins": DigitalTwins,
    "device-provisioning": DeviceProvisioningServices,
    "maps": Maps,
    # --- ML / AI ---
    "azure-openai": AzureOpenAI,
    "openai": AzureOpenAI,
    "bot-service": BotServices,
    "bot-services": BotServices,
    "machine-learning": MachineLearningServiceWorkspaces,
    "ml-workspace": MachineLearningServiceWorkspaces,
    # --- Monitor ---
    "application-insights": ApplicationInsights,
    "app-insights": ApplicationInsights,
    "monitor": Monitor,
    # --- DevOps ---
    "devops": AzureDevops,
    "azure-devops": AzureDevops,
    "devtest-labs": DevtestLabs,
    "pipelines": Pipelines,
    "repos": Repos,
    # --- General ---
    "subscription": Subscriptions,
    "subscriptions": Subscriptions,
    "resource-group": None,  # handled as Cluster, not a node
    "resource-groups": None,
}

AWS_NODE_MAP: dict[str, type] = {}
if _AWS_AVAILABLE:
    AWS_NODE_MAP = {
        "ec2": EC2, "ecs": ECS, "lambda": Lambda, "elastic-beanstalk": ElasticBeanstalk,
        "batch": AwsBatch, "fargate": Fargate,
        "rds": RDS, "dynamodb": Dynamodb, "redshift": Redshift, "elasticache": ElastiCache, "aurora": Aurora,
        "vpc": VPC, "elb": ELB, "alb": ALB, "nlb": NLB, "cloudfront": CloudFront, "route53": Route53,
        "api-gateway": APIGateway,
        "s3": S3, "ebs": EBS, "efs": EFS,
        "iam": IAM, "kms": KMS, "waf": WAF,
        "sqs": SQS, "sns": SNS, "step-functions": StepFunctions, "eventbridge": Eventbridge,
    }

GCP_NODE_MAP: dict[str, type] = {}
if _GCP_AVAILABLE:
    GCP_NODE_MAP = {
        "compute-engine": ComputeEngine, "app-engine": AppEngine, "functions": GcpFunctions,
        "gke": KubernetesEngine, "kubernetes-engine": KubernetesEngine, "cloud-run": Run,
        "cloud-sql": GcpSQL, "spanner": Spanner, "bigtable": Bigtable, "firestore": Firestore,
        "memorystore": Memorystore,
        "load-balancing": LoadBalancing, "cdn": GcpCDN, "dns": GcpDNS, "vpc": GcpVPC,
        "gcs": GCS, "cloud-storage": GCS,
    }

K8S_NODE_MAP: dict[str, type] = {}
if _K8S_AVAILABLE:
    K8S_NODE_MAP = {
        "pod": Pod, "deployment": Deployment, "replica-set": ReplicaSet,
        "stateful-set": StatefulSet, "daemon-set": DaemonSet, "job": Job, "cron-job": CronJob,
        "service": Service, "ingress": Ingress, "network-policy": NetworkPolicy,
        "pv": PersistentVolume, "persistent-volume": PersistentVolume,
        "pvc": PersistentVolumeClaim, "persistent-volume-claim": PersistentVolumeClaim,
        "storage-class": StorageClass,
        "namespace": Namespace,
    }


def resolve_node_class(resource_type: str) -> type | None:
    """Resolve a resource type string to a Diagrams node class.

    Supports namespace prefix routing for aws/, gcp/, k8s/, and azure/.
    Returns ``None`` if no mapping is found.
    """
    key = resource_type.lower()

    # Check namespace prefix routing
    if "/" in key:
        prefix, suffix = key.split("/", 1)
        if prefix == "aws" and _AWS_AVAILABLE:
            cls = AWS_NODE_MAP.get(suffix)
            if cls is not None:
                return cls
        elif prefix == "gcp" and _GCP_AVAILABLE:
            cls = GCP_NODE_MAP.get(suffix)
            if cls is not None:
                return cls
        elif prefix == "k8s" and _K8S_AVAILABLE:
            cls = K8S_NODE_MAP.get(suffix)
            if cls is not None:
                return cls
        # Strip namespace for Azure/other lookups
        key = suffix

    cls = NODE_MAP.get(key)
    if cls is not None:
        return cls

    # Fuzzy fallback: check if key is a substring of any map key
    for map_key, map_cls in NODE_MAP.items():
        if map_cls is not None and (key in map_key or map_key in key):
            return map_cls

    return None
