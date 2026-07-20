"""Shared test fixtures — deterministic, no live ND, no LLM.

These exercise the `nd` library directly through an injected httpx MockTransport,
which is the same code path a CI gate or Ansible validate role would use.
"""

from __future__ import annotations

import httpx
import pytest

from nd import NdClient, NdConfig

FABRICS = {
    "fabrics": [
        {"name": "DC1-Prod", "category": "fabric",
         "management": {"type": "vxlanIbgp"}, "licenseTier": "premier"},
        {"name": "DC2-Edge", "category": "fabric",
         "management": {"type": "externalConnectivity"}, "licenseTier": "essentials"},
    ]
}

HEALTH = {
    "fabricHealthSummaryCollection": [
        {
            "switchName": "leaf-101",
            "telemetryHealthStats": [
                {"resource": "resourceUtilization", "state": "healthy"},
                {"resource": "flows", "state": "notAvailable"},
            ],
        },
    ],
    "totalSwitchCount": 12,
}

# Empty fabric: ND returns a null collection.
HEALTH_EMPTY = {"fabricHealthSummaryCollection": None, "totalSwitchCount": 0}

# Per-fabric summary (/fabrics/{name}/summary): overall health + config-sync.
FABRIC_SUMMARY = {
    "DC1-Prod": {
        "category": "fabric", "name": "DC1-Prod", "anomalyLevel": "critical",
        "connectivityStatus": "Up",
        "management": {"type": "vxlanIbgp", "configSyncStatus": {"syncStatus": "outOfSync"}},
    },
    "DC2-Edge": {
        "category": "fabric", "name": "DC2-Edge", "anomalyLevel": "healthy",
        "connectivityStatus": "Up",
        "management": {"type": "externalConnectivity",
                       "configSyncStatus": {"syncStatus": "notApplicable"}},
    },
}

SWITCHES = {
    "switches": [
        {"hostname": "leaf-101", "fabricManagementIp": "10.1.1.1", "serialNumber": "FDO123",
         "model": "N9K-C93180", "switchRole": "leaf",
         "additionalData": {"discoveryStatus": "ok", "configSyncStatus": "inSync"}},
    ]
}

INTERFACES = {
    "interfaces": [
        {"interfaceName": "Ethernet1/1", "interfaceType": "ethernet",
         "operData": {"adminStatus": "up", "operationalStatus": "down",
                      "operationalDescription": "to-host"}},
    ]
}

VRFS = {"vrfs": [{"vrfName": "TENANT-A", "vrfId": 50000, "vrfVlanId": 2000, "vrfStatus": "DEPLOYED"}]}

NETWORKS = {
    "networks": [
        {"networkName": "NET-10", "networkId": 30010, "vlanId": 110,
         "vrf": "TENANT-A", "networkStatus": "DEPLOYED"},
    ]
}

TEMPLATES = {
    "templates": [
        {"name": "int_access_host", "templateType": "policy", "templateSubType": "interface",
         "contentType": "templateCli", "description": "Access host port"},
        {"name": "fabric_vxlan", "templateType": "fabric", "templateSubType": "vxlan",
         "contentType": "python", "description": "VXLAN fabric"},
    ]
}

TEMPLATE_DETAIL = {
    "name": "int_access_host",
    "templateType": "policy",
    "content": "##template properties\ntemplateType = POLICY\n##",
    "parameters": [{"name": "VLAN", "parameterType": "integer", "optional": False}],
}


def _default_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    routes = {
        "/api/v1/infra/login": {"jwttoken": "test-token"},
        "/api/v1/manage/fabrics": FABRICS,
        "/api/v1/manage/fabrics/DC1-Prod": FABRICS["fabrics"][0],
        "/api/v1/manage/inventory/switches": SWITCHES,
        "/api/v1/manage/fabrics/DC1-Prod/switches": SWITCHES,
        "/api/v1/manage/fabrics/DC1-Prod/switches/FDO123/interfaces": INTERFACES,
        "/api/v1/manage/fabrics/DC1-Prod/vrfs": VRFS,
        "/api/v1/manage/fabrics/DC1-Prod/networks": NETWORKS,
        "/api/v1/manage/configTemplates": TEMPLATES,
        "/api/v1/manage/configTemplates/int_access_host": TEMPLATE_DETAIL,
    }
    if path == "/api/v1/analyze/telemetry/healthSummary":
        fabric = request.url.params.get("fabricName")
        return httpx.Response(200, json=HEALTH if fabric == "DC1-Prod" else HEALTH_EMPTY)
    if path.startswith("/api/v1/manage/fabrics/") and path.endswith("/summary"):
        name = path.split("/fabrics/", 1)[1].rsplit("/summary", 1)[0]
        if name in FABRIC_SUMMARY:
            return httpx.Response(200, json=FABRIC_SUMMARY[name])
    if path in routes:
        return httpx.Response(200, json=routes[path])
    return httpx.Response(404, json={"message": f"no route for {path}"})


@pytest.fixture
def config() -> NdConfig:
    return NdConfig(host="https://nd.test", username="admin", password="pw", verify_tls=False)


@pytest.fixture
def client(config: NdConfig) -> NdClient:
    transport = httpx.MockTransport(_default_handler)
    with NdClient(config, transport=transport) as c:
        yield c
