
from collections import defaultdict
try:
    from .config import driver
    from .documentParsers import (
        create_nodes_and_relationships_for_cdr,
        create_nodes_and_relationships_for_ipdr,
        create_nodes_and_relationships_for_towers,
    )
except ImportError:
    from config import driver
    from documentParsers import (
        create_nodes_and_relationships_for_cdr,
        create_nodes_and_relationships_for_ipdr,
        create_nodes_and_relationships_for_towers,
    )

def normalize_column(col):
    return col.strip().replace(" ", "_").upper()

def detect_file_type(columns):
    cols = set(c.upper().strip().replace(" ", "_") for c in columns)
    if {"A_PARTY", "B_PARTY", "CALL_TYPE", "IMEI_A", "IMSI_A"}.issubset(cols):
        if {'ROAMING_A'}.issubset(cols):
            return 'TD'
        return "CDR"
    elif {"SOURCE_IP_ADDRESS", "TRANSLATED_IP_ADDRESS", "DESTINATION_IP_ADDRESS", "SESSION_DURATION"}.intersection(cols):
        return "IPDR"
    return "UNKNOWN"

def batch_merge_nodes(tx, label, nodes):
    tx.run(f"""
        UNWIND $nodes AS node
        MERGE (n:`{label}` {{id: node.id}})
    """, nodes=nodes)

def batch_merge_relationships(tx, l1, l2, rel, rels):
    tx.run(f"""
        UNWIND $rels AS r
        MATCH (a:`{l1}` {{id: r.from}})
        MATCH (b:`{l2}` {{id: r.to}})
        MERGE (a)-[rel:`{rel}`]->(b)
        SET rel += r.props
    """, rels=rels)

def push_to_neo4j(df, file_type):
    all_nodes = defaultdict(set)
    all_relationships = defaultdict(list)

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        if file_type == "CDR":
            nodes, relationships = create_nodes_and_relationships_for_cdr(row_dict)
        elif file_type == "TD":
            nodes, relationships = create_nodes_and_relationships_for_towers(row_dict)
        else:
            nodes, relationships = create_nodes_and_relationships_for_ipdr(row_dict)

        for label, id_val in nodes:
            all_nodes[label].add(id_val)

        for item in relationships:
            if not isinstance(item, tuple) or len(item) != 6:
                print("⚠️ Skipping malformed relationship:", item)
                continue
            l1, v1, rel, l2, v2, props = item
            all_relationships[(l1, rel, l2)].append({
                "from": v1, "to": v2, "props": props
            })

    with driver.session() as session:
        for label, values in all_nodes.items():
            session.write_transaction(batch_merge_nodes, label, [{"id": v} for v in values])
        for (l1, rel, l2), rel_list in all_relationships.items():
            session.write_transaction(batch_merge_relationships, l1, l2, rel, rel_list)
