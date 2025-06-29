def create_nodes_and_relationships_for_cdr(row_dict):
    nodes = set()
    relationships = []
    
    a_party = row_dict.get("A_PARTY", "").strip()
    b_party = row_dict.get("B_PARTY", "").strip()
    imei = row_dict.get("IMEI_A", "").strip()
    imsi = row_dict.get("IMSI_A", "").strip()
    first_cell = row_dict.get("FIRST_CELL_ID_A", "").strip()
    last_cell = row_dict.get("LAST_CELL_ID_A", "").strip()
    address = row_dict.get("FIRST_CELL_ID_A_ADDRESS", "").strip()
    latitude = row_dict.get("LATITUDE", "").strip()
    longitude = row_dict.get("LONGITUDE", "").strip()
    date = row_dict.get("DATE", "").strip()
    time = row_dict.get("TIME", "").strip()
    duration = row_dict.get("DURATION", "").strip()
    call_type = row_dict.get("CALL_TYPE", "").strip()

    if a_party: nodes.add(("Party", a_party))
    if b_party: nodes.add(("Party", b_party))
    if imei: nodes.add(("IMEI", imei))
    if imsi: nodes.add(("IMSI", imsi))
    if first_cell: nodes.add(("Tower", first_cell))
    if last_cell: nodes.add(("Tower", last_cell))
    if address: nodes.add(("Location", address))
    if latitude and longitude:
        coord_id = f"{latitude},{longitude}"
        nodes.add(("Coordinates", coord_id))

    if a_party and b_party:
        # rel_type = 'CALLED' if call_type == 'CALL-IN ROAMING' else 'BEEN_CALLED'
        relationships.append(("Party", a_party, 'CALL', "Party", b_party, {
            "date": date, "time": time, "duration": duration, "type": call_type
        }))
    if a_party and imei:
        relationships.append(("Party", a_party, "USED_IMEI", "IMEI", imei, {}))
    if a_party and imsi:
        relationships.append(("Party", a_party, "USED_IMSI", "IMSI", imsi, {}))
    if a_party and first_cell:
        relationships.append(("Party", a_party, "STARTED_AT", "Tower", first_cell, {}))
    if a_party and last_cell:
        relationships.append(("Party", a_party, "ENDED_AT", "Tower", last_cell, {}))
    if first_cell and address:
        relationships.append(("Tower", first_cell, "HAS_LOCATION", "Location", address, {}))
    if first_cell and latitude and longitude:
        coord_id = f"{latitude},{longitude}"
        relationships.append(("Tower", first_cell, "LOCATED_AT", "Coordinates", coord_id, {}))

    return list(nodes), relationships

def create_nodes_and_relationships_for_ipdr(row_dict):
    nodes = set()
    relationships = []

    party = row_dict.get("LANDLINE/MSISDN/MDN/LEASED_CIRCUIT_ID_FOR_INTERNET_ACCESS", "").strip()
    user_id = row_dict.get("USER_ID_FOR_INTERNET_ACCESS_BASED_ON_AUTHENTICATION", "").strip()
    private_ip = row_dict.get("SOURCE_IP_ADDRESS", "").strip()
    public_ip = row_dict.get("TRANSLATED_IP_ADDRESS", "").strip()
    destination_ip = row_dict.get("DESTINATION_IP_ADDRESS", "").strip()
    source_port = row_dict.get("SOURCE_PORT", "").strip()
    dest_port = row_dict.get("DESTINATION_PORT", "").strip()
    pgw_ip = row_dict.get("PGW_IP_ADDRESS", "").strip()
    access_point = row_dict.get("ACCESS_POINT_NAME", "").strip()
    first_cell = row_dict.get("FIRST_CELL_ID", "").strip()
    last_cell = row_dict.get("LAST_CELL_ID", "").strip()
    session_duration = row_dict.get("SESSION_DURATION", "").strip()
    data_up = row_dict.get("DATA_VOLUME_UP_LINK", "").strip()
    data_down = row_dict.get("DATA_VOLUME_DOWN_LINK", "").strip()

    if party: nodes.add(("Party", party))
    if user_id and user_id != party: nodes.add(("Party", user_id))
    if private_ip: nodes.add(("PrivateIP", private_ip))
    if public_ip: nodes.add(("PublicIP", public_ip))
    if destination_ip: nodes.add(("DestinationIP", destination_ip))
    if pgw_ip: nodes.add(("Gateway", pgw_ip))
    if access_point: nodes.add(("AccessPoint", access_point))
    if first_cell: nodes.add(("Tower", first_cell))
    if last_cell: nodes.add(("Tower", last_cell))

    if party and private_ip:
        relationships.append(("Party", party, "USED_PRIVATE_IP", "PrivateIP", private_ip, {}))
    if private_ip and public_ip:
        relationships.append(("PrivateIP", private_ip, "NAT_TO", "PublicIP", public_ip, {}))
    if public_ip and destination_ip:
        relationships.append(("PublicIP", public_ip, "CONNECTED_TO", "DestinationIP", destination_ip, {
            "src_port": source_port, "dst_port": dest_port,
            "duration": session_duration, "data_up": data_up, "data_down": data_down
        }))
    if party and pgw_ip:
        relationships.append(("Party", party, "VIA_GATEWAY", "Gateway", pgw_ip, {}))
    if party and access_point:
        relationships.append(("Party", party, "USED_APN", "AccessPoint", access_point, {}))
    if party and first_cell:
        relationships.append(("Party", party, "CONNECTED_FROM", "Tower", first_cell, {}))
    if party and last_cell:
        relationships.append(("Party", party, "DISCONNECTED_AT", "Tower", last_cell, {}))

    return list(nodes), relationships

def create_nodes_and_relationships_for_towers(row_dict):
    nodes = set()
    relationships = []

    caller = row_dict.get("A_PARTY", "").strip()
    callee = row_dict.get("B_PARTY", "").strip()
    imei = row_dict.get("IMEI_A", "").strip()
    imsi = row_dict.get("IMSI_A", "").strip()
    start_tower = row_dict.get("FIRST_CELL_ID_A", "").strip()
    end_tower = row_dict.get("LAST_CELL_ID_A", "").strip()
    date = row_dict.get("DATE", "").strip()
    time = row_dict.get("TIME", "").strip()
    duration = row_dict.get("DURATION", "").strip()
    call_type = row_dict.get("CALL_TYPE", "").strip()
    address = row_dict.get("FIRST_CELL_ID_A_ADDRESS", "").strip()
    latitude = row_dict.get("LATITUDE", "").strip()
    longitude = row_dict.get("LONGITUDE", "").strip()

    # Create Party nodes
    if caller:
        nodes.add(("Party", caller))
    if callee and callee != caller:
        nodes.add(("Party", callee))

    # Device identifiers
    if imei:
        nodes.add(("IMEI", imei))
    if imsi:
        nodes.add(("IMSI", imsi))

    # Towers
    if start_tower:
        nodes.add(("Tower", start_tower))
    if end_tower:
        nodes.add(("Tower", end_tower))

    # CALL relationship
    if caller and callee:
        relationships.append((
            "Party", caller,
            "CALL", 
            "Party", callee,
            {
                "date": date,
                "time": time,
                "duration": duration,
                "type": call_type
            }
        ))

    # USED_IMEI
    if caller and imei:
        relationships.append((
            "Party", caller,
            "USED_IMEI",
            "IMEI", imei,
            {}
        ))

    # USED_IMSI
    if caller and imsi:
        relationships.append((
            "Party", caller,
            "USED_IMSI",
            "IMSI", imsi,
            {}
        ))

    # STARTED_AT Tower
    if caller and start_tower:
        relationships.append((
            "Party", caller,
            "STARTED_AT",
            "Tower", start_tower,
            {}
        ))

    # ENDED_AT Tower
    if caller and end_tower:
        relationships.append((
            "Party", caller,
            "ENDED_AT",
            "Tower", end_tower,
            {}
        ))
    
    # if tower_id:
    #     nodes.add(("Tower", tower_id))

    if latitude and longitude:
        coord_id = f"{latitude},{longitude}"
        nodes.add(("Coordinates", coord_id))
    return list(nodes), relationships