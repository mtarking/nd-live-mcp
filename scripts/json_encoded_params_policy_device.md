# Policy/Device templates with JSON-encoded (composite) parameters

Total templates flagged: **39**

| Template | JSON-encoded parameters |
| --- | --- |
| `AI_Fabric_QOS_Classification_Custom` | `QOSDATA` (structureArray) |
| `community_list` | `standardCommunityListEntries` (structureArray)<br>`expandedCommunityListEntries` (structureArray) |
| `dc_border_gateway_inband_setup` | `moreNdDataSubnet` (structureArray)<br>`dciIntfEntries` (structureArray) |
| `dc_border_inband_setup` | `moreNdDataSubnet` (structureArray)<br>`edgeRouterEntries` (structureArray) |
| `Dynamic_Load_Balancing_CS` | `STATIC_PIN_LIST` (structureArray) |
| `Dynamic_Load_Balancing_S1` | `STATIC_PIN_LIST` (structureArray) |
| `ERSPAN` | `sources` (structureArray)<br>`destinations` (structureArray)<br>`vlanFilters` (structureArray) |
| `Ext_VRF_Lite_SVI` | `BGP_NEIGHBOR_LIST` (structureArray) |
| `extended_community_list` | `standardEntries` (structureArray)<br>`expandedEntries` (structureArray) |
| `igp_redistribute_static` | `ENTRY_LIST` (structureArray) |
| `ios_xe_ptp_telemetry` | `SUB_XPATH_LIST` (structureArray)<br>`TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `ios_xe_telemetry_cli` | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `ios_xe_vrf_rt` | `RT_IMPORT` (string[])<br>`RT_EXPORT` (string[])<br>`RT_IMPORT_EVPN` (string[])<br>`RT_EXPORT_EVPN` (string[]) |
| `ip_acl` | `ACES` (structureArray) |
| `ipfm_generic_multicast_telemetry` | `TELEM_RCVR_IP_LIST` (ipAddress[])<br>`TELEM_RCVR_IPV6_LIST` (ipAddress[]) |
| `ipfm_nat_telemetry` | `TELEM_RCVR_IP_LIST` (ipAddress[])<br>`TELEM_RCVR_IPV6_LIST` (ipAddress[]) |
| `ipfm_telemetry` | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `ipfm_telemetry_config` | `TELEM_RCVR_IP_LIST` (ipAddress[])<br>`TELEM_RCVR_IPV6_LIST` (ipAddress[]) |
| `ipfm_vrf` | `ASM_GROUP_RANGES` (structureArray) |
| `ipfm_vrf_msdp` | `MSDP_PEERS` (structureArray) |
| `ipv4_prefix_list` | `ENTRY_LIST` (structureArray) |
| `ipv4_prefix_list_internal` | `ENTRY_LIST` (structureArray)<br>`CUSTOM_ENTRY_LIST` (structureArray) |
| `ipv6_acl` | `ACES` (structureArray) |
| `ipv6_prefix_list` | `ENTRY_LIST` (structureArray) |
| `ipv6_prefix_list_internal` | `ENTRY_LIST` (structureArray)<br>`CUSTOM_ENTRY_LIST` (structureArray) |
| `lan_ptp_telemetry` | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `lan_ptp_telemetry_config` | `TELEM_RCVR_IP_LIST` (ipAddress[]) |
| `route_map_enhanced` | `entries` (structureArray) |
| `seed_switch` | `BOOTSTRAP_LIST` (structureArray) |
| `service_acl` | `ACES` (structureArray) |
| `service_epbr` | `CHAINING` (structureArray) |
| `sgm` | `groups` (structureArray)<br>`contracts` (structureArray)<br>`classMaps` (structureArray)<br>`policies` (structureArray) |
| `sgm_switch` | `groups` (structureArray)<br>`associations` (structureArray)<br>`classMaps` (structureArray)<br>`policies` (structureArray) |
| `SPAN` | `sources` (structureArray)<br>`vlanFilters` (structureArray) |
| `static_route_v4_v6` | `staticRoutes` (structureArray) |
| `TelemetrySensor_EF` | `PATHCMDS` (string[]) |
| `vlan_acl` | `matches` (structureArray) |
| `vrf_jython_internal` | `VRF_LITE_CONN` (structureArray) |
| `vrf_rt` | `RT_IMPORT` (string[])<br>`RT_EXPORT` (string[]) |
