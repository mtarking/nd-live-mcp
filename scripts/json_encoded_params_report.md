# Templates with JSON-encoded (composite) parameters

Total templates flagged: **74**

| Template | Type | SubType | JSON-encoded parameters |
| --- | --- | --- | --- |
| `AI_Fabric_QOS_Classification_Custom` | policy | device | `QOSDATA` (structureArray) |
| `community_list` | policy | device | `standardCommunityListEntries` (structureArray)<br>`expandedCommunityListEntries` (structureArray) |
| `dc_border_gateway_inband_setup` | policy | device | `moreNdDataSubnet` (structureArray)<br>`dciIntfEntries` (structureArray) |
| `dc_border_inband_setup` | policy | device | `moreNdDataSubnet` (structureArray)<br>`edgeRouterEntries` (structureArray) |
| `Default_Network_Extension_Universal` | profile | vxlan | `gatewayIpV6Address` (string[])<br>`dhcpServers` (structureArray)<br>`secondaryGWs` (structureArray)<br>`MULTISITE_CONN` (structureArray)<br>`switchRouteTargetImport` (string[])<br>`switchRouteTargetExport` (string[]) |
| `Default_Network_Universal` | profile | vxlan | `gatewayIpV6Address` (string[])<br>`dhcpServers` (structureArray)<br>`secondaryGWs` (structureArray) |
| `Default_VRF_Extension_Universal` | profile | vxlan | `switchRouteTargetImport` (string[])<br>`switchRouteTargetExport` (string[])<br>`switchRouteTargetImportEvpn` (string[])<br>`switchRouteTargetExportEvpn` (string[])<br>`routeTargetImport` (string[])<br>`routeTargetExport` (string[])<br>`routeTargetImportEvpn` (string[])<br>`routeTargetExportEvpn` (string[])<br>`routeTargetImportMvpn` (string[])<br>`routeTargetExportMvpn` (string[])<br>`cloudRouteTargetImportEvpn` (string[])<br>`cloudRouteTargetExportEvpn` (string[])<br>`VRF_LITE_CONN` (structureArray)<br>`MULTISITE_CONN` (structureArray) |
| `Default_VRF_Universal` | profile | vxlan | `switchRouteTargetImport` (string[])<br>`switchRouteTargetExport` (string[])<br>`switchRouteTargetImportEvpn` (string[])<br>`switchRouteTargetExportEvpn` (string[])<br>`routeTargetImport` (string[])<br>`routeTargetExport` (string[])<br>`routeTargetImportEvpn` (string[])<br>`routeTargetExportEvpn` (string[])<br>`routeTargetImportMvpn` (string[])<br>`routeTargetExportMvpn` (string[])<br>`cloudRouteTargetImportEvpn` (string[])<br>`cloudRouteTargetExportEvpn` (string[]) |
| `Dynamic_Load_Balancing_CS` | policy | device | `STATIC_PIN_LIST` (structureArray) |
| `Dynamic_Load_Balancing_S1` | policy | device | `STATIC_PIN_LIST` (structureArray) |
| `Easy_Fabric` | fabric | notApplicable | `DNS_SERVER_VRF` (string[])<br>`NTP_SERVER_IP_LIST` (string[])<br>`NTP_SERVER_VRF` (string[])<br>`SYSLOG_SERVER_IP_LIST` (string[])<br>`SYSLOG_SEV` (string[])<br>`SYSLOG_SERVER_VRF` (string[])<br>`bootstrapSubnetCollection` (structureArray)<br>`NETFLOW_EXPORTER_LIST` (structureArray)<br>`NETFLOW_RECORD_LIST` (structureArray)<br>`NETFLOW_MONITOR_LIST` (structureArray) |
| `Easy_Fabric_Classic` | fabric | notApplicable | `DNS_SERVER_VRF` (string[])<br>`NTP_SERVER_IP_LIST` (string[])<br>`NTP_SERVER_VRF` (string[])<br>`SYSLOG_SERVER_IP_LIST` (string[])<br>`SYSLOG_SEV` (string[])<br>`SYSLOG_SERVER_VRF` (string[])<br>`bootstrapSubnetCollection` (structureArray)<br>`NETFLOW_EXPORTER_LIST` (structureArray)<br>`NETFLOW_RECORD_LIST` (structureArray)<br>`NETFLOW_MONITOR_LIST` (structureArray)<br>`NETFLOW_SAMPLER_LIST` (structureArray) |
| `Easy_Fabric_eBGP` | fabric | notApplicable | `DNS_SERVER_VRF` (string[])<br>`NTP_SERVER_IP_LIST` (string[])<br>`NTP_SERVER_VRF` (string[])<br>`SYSLOG_SERVER_IP_LIST` (string[])<br>`SYSLOG_SEV` (string[])<br>`SYSLOG_SERVER_VRF` (string[])<br>`bootstrapSubnetCollection` (structureArray)<br>`NETFLOW_EXPORTER_LIST` (structureArray)<br>`NETFLOW_RECORD_LIST` (structureArray)<br>`NETFLOW_MONITOR_LIST` (structureArray) |
| `Easy_Fabric_IOS_XE` | fabric | notApplicable | `bootstrapSubnetCollection` (structureArray) |
| `Easy_Fabric_IPFM` | fabric | notApplicable | `ASM_GROUP_RANGES` (structureArray)<br>`DNS_SERVER_VRF` (string[])<br>`NTP_SERVER_IP_LIST` (string[])<br>`NTP_SERVER_VRF` (string[])<br>`SYSLOG_SERVER_IP_LIST` (string[])<br>`SYSLOG_SEV` (string[])<br>`SYSLOG_SERVER_VRF` (string[])<br>`bootstrapSubnetCollection` (structureArray) |
| `ERSPAN` | policy | device | `sources` (structureArray)<br>`destinations` (structureArray)<br>`vlanFilters` (structureArray) |
| `Ext_VRF_Lite_SVI` | policy | device | `BGP_NEIGHBOR_LIST` (structureArray) |
| `extended_community_list` | policy | device | `standardEntries` (structureArray)<br>`expandedEntries` (structureArray) |
| `External_Fabric` | fabric | notApplicable | `bootstrapSubnetCollection` (structureArray)<br>`NETFLOW_EXPORTER_LIST` (structureArray)<br>`NETFLOW_RECORD_LIST` (structureArray)<br>`NETFLOW_MONITOR_LIST` (structureArray)<br>`NETFLOW_SAMPLER_LIST` (structureArray)<br>`DNS_SERVER_VRF` (string[]) |
| `igp_redistribute_static` | policy | device | `ENTRY_LIST` (structureArray) |
| `int_ipfm_l3_port` | policy | interfaceEthernet | `IGMP_GROUP_RANGES` (structureArray) |
| `int_ipfm_loopback` | policy | interfaceLoopback | `SECONDARY_IP_LIST` (structureArray) |
| `int_ipfm_subif` | policy | interfaceEthernet | `IGMP_GROUP_RANGES` (structureArray) |
| `int_port_channel_pvlan_host` | policy | interfacePortChannel | `MAPPING_LIST` (structureArray)<br>`ASSOCIATION_LIST` (structureArray) |
| `int_port_channel_trunk_host` | policy | interfacePortChannel | `vlanMappingEntries` (structureArray) |
| `int_pvlan_host` | policy | interfaceEthernet | `MAPPING_LIST` (structureArray)<br>`ASSOCIATION_LIST` (structureArray) |
| `int_trunk_classic` | policy | interfaceEthernet | `MST_PATH_COST_LIST` (structureArray)<br>`MST_PORT_PRIO_LIST` (structureArray) |
| `int_trunk_host` | policy | interfaceEthernet | `vlanMappingEntries` (structureArray) |
| `int_vlan_dhcp_relay_internal` | policy | interfaceVlan | `dhcpServers` (structureArray) |
| `int_vpc_pvlan_host` | policy | interfaceVpc | `MAPPING_LIST` (structureArray)<br>`ASSOCIATION_LIST` (structureArray) |
| `int_vpc_pvlan_po` | policy | interfacePortChannel | `MAPPING_LIST` (structureArray)<br>`ASSOCIATION_LIST` (structureArray) |
| `int_vpc_trunk_host` | policy | interfaceVpc | `vlanMappingEntries` (structureArray) |
| `int_vpc_trunk_po_11_1` | policy | interfacePortChannel | `vlanMappingEntries` (structureArray) |
| `ios_xe_int_vlan` | policy | interfaceVlan | `dhcpServers` (structureArray) |
| `ios_xe_ptp_telemetry` | policy | device | `SUB_XPATH_LIST` (structureArray)<br>`TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `ios_xe_telemetry_cli` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `IOS_XE_VRF` | profile | vxlan | `VRF_LITE_CONN` (structureArray) |
| `ios_xe_vrf_rt` | policy | device | `RT_IMPORT` (string[])<br>`RT_EXPORT` (string[])<br>`RT_IMPORT_EVPN` (string[])<br>`RT_EXPORT_EVPN` (string[]) |
| `ip_acl` | policy | device | `ACES` (structureArray) |
| `IPFM_Classic` | fabric | notApplicable | `bootstrapSubnetCollection` (structureArray) |
| `ipfm_generic_multicast_telemetry` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[])<br>`TELEM_RCVR_IPV6_LIST` (ipAddress[]) |
| `ipfm_nat_telemetry` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[])<br>`TELEM_RCVR_IPV6_LIST` (ipAddress[]) |
| `ipfm_telemetry` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `ipfm_telemetry_config` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[])<br>`TELEM_RCVR_IPV6_LIST` (ipAddress[]) |
| `ipfm_vrf` | policy | device | `ASM_GROUP_RANGES` (structureArray) |
| `ipfm_vrf_msdp` | policy | device | `MSDP_PEERS` (structureArray) |
| `ipv4_prefix_list` | policy | device | `ENTRY_LIST` (structureArray) |
| `ipv4_prefix_list_internal` | policy | device | `ENTRY_LIST` (structureArray)<br>`CUSTOM_ENTRY_LIST` (structureArray) |
| `ipv6_acl` | policy | device | `ACES` (structureArray) |
| `ipv6_prefix_list` | policy | device | `ENTRY_LIST` (structureArray) |
| `ipv6_prefix_list_internal` | policy | device | `ENTRY_LIST` (structureArray)<br>`CUSTOM_ENTRY_LIST` (structureArray) |
| `issu_custom_report` | report | upgrade | `switches` (string[])<br>`ndiReports` (struct)<br>`checks` (structureArray) |
| `issu_prepost_custom_report` | report | upgrade | `switches` (string[])<br>`checks` (structureArray) |
| `LAN_Classic` | fabric | notApplicable | `bootstrapSubnetCollection` (structureArray)<br>`NETFLOW_EXPORTER_LIST` (structureArray)<br>`NETFLOW_RECORD_LIST` (structureArray)<br>`NETFLOW_MONITOR_LIST` (structureArray)<br>`NETFLOW_SAMPLER_LIST` (structureArray) |
| `lan_ptp_telemetry` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `lan_ptp_telemetry_config` | policy | device | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `MSD_Fabric` | fabric | notApplicable | `routeServerCollection` (structureArray) |
| `Network_Classic` | profile | vlan | `dhcpServers` (structureArray) |
| `Pvlan_Secondary_Network` | profile | vxlan | `MULTISITE_CONN` (structureArray) |
| `route_map_enhanced` | policy | device | `entries` (structureArray) |
| `seed_switch` | policy | device | `BOOTSTRAP_LIST` (structureArray) |
| `service_acl` | policy | device | `ACES` (structureArray) |
| `service_epbr` | policy | device | `CHAINING` (structureArray) |
| `Service_Network_Universal` | profile | service | `secondaryGWs` (structureArray) |
| `sgm` | policy | device | `groups` (structureArray)<br>`contracts` (structureArray)<br>`classMaps` (structureArray)<br>`policies` (structureArray) |
| `sgm_switch` | policy | device | `groups` (structureArray)<br>`associations` (structureArray)<br>`classMaps` (structureArray)<br>`policies` (structureArray) |
| `SPAN` | policy | device | `sources` (structureArray)<br>`vlanFilters` (structureArray) |
| `static_route_v4_v6` | policy | device | `staticRoutes` (structureArray) |
| `TelemetrySensor_EF` | policy | device | `PATHCMDS` (string[]) |
| `vlan_acl` | policy | device | `matches` (structureArray) |
| `VRF_Classic` | profile | vlan | `staticRoutes` (structureArray)<br>`VRF_LITE_CONN` (structureArray) |
| `vrf_classic_main` | policy | vlan | `VRF_LITE_CONN` (structureArray) |
| `vrf_jython_internal` | policy | device | `VRF_LITE_CONN` (structureArray) |
| `vrf_rt` | policy | device | `RT_IMPORT` (string[])<br>`RT_EXPORT` (string[]) |
