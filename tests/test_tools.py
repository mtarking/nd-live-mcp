"""Tool functions against a mocked ND (deterministic)."""

from __future__ import annotations

from nd.tools import fabrics, interfaces, networks, switches, templates, vrfs


def test_list_fabrics_compact(client) -> None:
    out = fabrics.list_fabrics(client)
    assert "DC1-Prod" in out
    assert "vxlanIbgp" in out  # management.type
    assert "premier" in out  # licenseTier
    assert "NAME" in out  # header
    assert "HEALTH" in out and "SYNC" in out  # status columns
    assert "critical" in out  # DC1-Prod anomalyLevel from summary
    assert "outOfSync" in out  # DC1-Prod config-sync from summary


def test_list_fabrics_status_off_skips_summary(client) -> None:
    out = fabrics.list_fabrics(client, status=False)
    assert "DC1-Prod" in out
    assert "critical" not in out  # summary not fetched


def test_list_fabrics_detail_is_json(client) -> None:
    out = fabrics.list_fabrics(client, detail=True)
    assert out.strip().startswith("{")
    assert "DC1-Prod" in out


def test_get_fabric(client) -> None:
    out = fabrics.get_fabric(client, "DC1-Prod")
    assert "DC1-Prod" in out


def test_fabric_health(client) -> None:
    out = fabrics.fabric_health(client, "DC1-Prod")
    assert "leaf-101" in out  # switchName
    assert "SWITCH" in out  # header
    assert "flows=notAvailable" in out  # non-healthy resource called out


def test_fabric_health_empty(client) -> None:
    out = fabrics.fabric_health(client, "empty-fabric")
    assert out == "(no results)"  # null collection -> no phantom row


def test_list_switches_scoped_and_global(client) -> None:
    assert "leaf-101" in switches.list_switches(client)
    out = switches.list_switches(client, fabric="DC1-Prod")
    assert "leaf-101" in out
    assert "SYNC" in out  # deployment/config-sync column header
    assert "inSync" in out  # additionalData.configSyncStatus


def test_switch_interfaces(client) -> None:
    out = interfaces.switch_interfaces(client, "DC1-Prod", "FDO123")
    assert "Ethernet1/1" in out
    assert "OPER" in out


def test_list_vrfs(client) -> None:
    out = vrfs.list_vrfs(client, "DC1-Prod")
    assert "TENANT-A" in out


def test_list_networks(client) -> None:
    out = networks.list_networks(client, "DC1-Prod")
    assert "NET-10" in out


def test_list_templates_and_type_filter(client) -> None:
    out = templates.list_templates(client)
    assert "int_access_host" in out and "fabric_vxlan" in out

    only_fabric = templates.list_templates(client, template_type="fabric")
    assert "fabric_vxlan" in only_fabric
    assert "int_access_host" not in only_fabric


def test_get_template_detail(client) -> None:
    out = templates.get_template(client, "int_access_host")
    assert "templateType" in out
    assert "parameters" in out
