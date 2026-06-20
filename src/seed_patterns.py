"""
🧠 Smart MCP - Seed patterns pour le RAG brain
Charge des patterns de diagrammes drawio réutilisables
"""

import sys
sys.path.insert(0, "/home/malek/workspace/smart-mcp")

from brain.rag import get_brain

# ── PATTERNS INITIAUX ──────────────────────────────────────────

PATTERNS = [
    {
        "title": "Architecture 3-tiers",
        "description": "Diagramme d'architecture 3 tiers classique : Frontend → Backend → Database avec utilisateurs et API",
        "tags": ["architecture", "3-tiers", "back-end", "database"],
        "xml": """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="u" value="👤 Utilisateurs" style="rounded=1;fillColor=#FFE0B2;strokeColor=#FF9800;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="50" y="40" width="140" height="60" as="geometry"/></mxCell>
<mxCell id="f" value="🌐 Frontend React" style="rounded=1;fillColor=#BBDEFB;strokeColor=#2196F3;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="50" y="180" width="140" height="60" as="geometry"/></mxCell>
<mxCell id="b" value="⚙️ Backend API" style="rounded=1;fillColor=#C8E6C9;strokeColor=#4CAF50;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="50" y="360" width="140" height="60" as="geometry"/></mxCell>
<mxCell id="d" value="💾 Base de données" style="rounded=1;fillColor=#D7CCC8;strokeColor=#795548;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="400" y="360" width="140" height="60" as="geometry"/></mxCell>
<mxCell id="e1" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="u" target="f"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e2" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="f" target="b"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e3" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="b" target="d"><mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel>"""
    },
    {
        "title": "Pipeline CI/CD",
        "description": "Pipeline CI/CD complet : Git → Build → Test → Deploy avec branches dev/staging/prod",
        "tags": ["ci/cd", "devops", "pipeline", "deployment"],
        "xml": """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="g" value="📦 Git Push" style="rounded=1;fillColor=#FFE0B2;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="140" height="50" as="geometry"/></mxCell>
<mxCell id="b" value="🔨 Build" style="rounded=1;fillColor=#BBDEFB;strokeColor=#2196F3;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="220" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="t" value="🧪 Tests" style="rounded=1;fillColor=#C8E6C9;strokeColor=#4CAF50;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="400" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="d" value="🚀 Deploy" style="rounded=1;fillColor=#E1BEE7;strokeColor=#9C27B0;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="580" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="e1" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="g" target="b"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e2" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="b" target="t"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e3" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="t" target="d"><mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel>"""
    },
    {
        "title": "Architecture microservices",
        "description": "Architecture microservices avec API Gateway, services, message broker et monitoring",
        "tags": ["architecture", "microservices", "gateway", "message-broker"],
        "xml": """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="gw" value="🚪 API Gateway" style="rounded=1;fillColor=#FFE0B2;strokeColor=#FF9800;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="140" height="50" as="geometry"/></mxCell>
<mxCell id="s1" value="📦 Service Auth" style="rounded=1;fillColor=#BBDEFB;fontSize=14;" vertex="1" parent="1"><mxGeometry x="40" y="180" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="s2" value="📦 Service Users" style="rounded=1;fillColor=#C8E6C9;fontSize=14;" vertex="1" parent="1"><mxGeometry x="200" y="180" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="s3" value="📦 Service Billing" style="rounded=1;fillColor=#E1BEE7;fontSize=14;" vertex="1" parent="1"><mxGeometry x="360" y="180" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="mq" value="📨 Message Broker" style="rounded=1;fillColor=#D7CCC8;strokeColor=#795548;fontSize=14;" vertex="1" parent="1"><mxGeometry x="40" y="300" width="180" height="50" as="geometry"/></mxCell>
<mxCell id="db" value="💾 DB Cluster" style="rounded=1;fillColor=#B2EBF2;strokeColor=#00BCD4;fontSize=14;" vertex="1" parent="1"><mxGeometry x="360" y="300" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="mon" value="📊 Monitoring" style="rounded=1;fillColor=#FFCDD2;strokeColor=#F44336;fontSize=14;" vertex="1" parent="1"><mxGeometry x="40" y="400" width="140" height="50" as="geometry"/></mxCell>
</root></mxGraphModel>"""
    },
    {
        "title": "Schéma de flux de données",
        "description": "Flux de données ETL : Source → Extraction → Transformation → Load → Data Warehouse → Dashboard",
        "tags": ["data", "etl", "warehouse", "dashboard"],
        "xml": """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="src" value="📡 Sources" style="rounded=1;fillColor=#FFE0B2;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="ext" value="🔄 Extraction" style="rounded=1;fillColor=#BBDEFB;fontSize=14;" vertex="1" parent="1"><mxGeometry x="200" y="40" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="trans" value="🛠️ Transformation" style="rounded=1;fillColor=#C8E6C9;fontSize=14;" vertex="1" parent="1"><mxGeometry x="200" y="160" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="load" value="📤 Load" style="rounded=1;fillColor=#E1BEE7;fontSize=14;" vertex="1" parent="1"><mxGeometry x="400" y="160" width="120" height="50" as="geometry"/></mxCell>
<mxCell id="wh" value="🏛️ Data Warehouse" style="rounded=1;fillColor=#D7CCC8;strokeColor=#795548;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="400" y="40" width="140" height="50" as="geometry"/></xCell>
<mxCell id="dash" value="📊 Dashboard" style="rounded=1;fillColor=#B2EBF2;strokeColor=#00BCD4;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="600" y="40" width="140" height="50" as="geometry"/></mxCell>
<mxCell id="e1" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="src" target="ext"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e2" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="ext" target="trans"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e3" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="trans" target="load"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e4" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=0;entryX=0.5;entryY=1;" edge="1" parent="1" source="load" target="wh"><mxGeometry relative="1" as="geometry"/></mxCell>
<mxCell id="e5" value="" style="endArrow=classic;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="wh" target="dash"><mxGeometry relative="1" as="geometry"/></mxCell>
</root></mxGraphModel>"""
    },
    {
        "title": "Diagramme de séquence API",
        "description": "Diagramme de séquence pour un appel API REST typique : Client → Auth → Resource → Database",
        "tags": ["sequence", "api", "auth", "rest"],
        "xml": """<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="c" value="🧑 Client" style="rounded=1;fillColor=#FFE0B2;fontSize=14;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="120" height="40" as="geometry"/></mxCell>
<mxCell id="a" value="🔐 Auth" style="rounded=1;fillColor=#BBDEFB;fontSize=14;" vertex="1" parent="1"><mxGeometry x="200" y="40" width="120" height="40" as="geometry"/></mxCell>
<mxCell id="r" value="📡 API" style="rounded=1;fillColor=#C8E6C9;fontSize=14;" vertex="1" parent="1"><mxGeometry x="400" y="40" width="120" height="40" as="geometry"/></mxCell>
<mxCell id="db" value="💾 DB" style="rounded=1;fillColor=#D7CCC8;fontSize=14;" vertex="1" parent="1"><mxGeometry x="600" y="40" width="120" height="40" as="geometry"/></mxCell>
<mxCell id="l1" value="1. POST /login" style="text;html=1;fontSize=13;" vertex="1" parent="1"><mxGeometry x="50" y="120" width="260" height="20" as="geometry"/></mxCell>
<mxCell id="l2" value="2. Validate credentials" style="text;html=1;fontSize=13;" vertex="1" parent="1"><mxGeometry x="210" y="160" width="300" height="20" as="geometry"/></mxCell>
<mxCell id="l3" value="3. Token JWT" style="text;html=1;fontSize=13;" vertex="1" parent="1"><mxGeometry x="210" y="200" width="280" height="20" as="geometry"/></xCell>
<mxCell id="l4" value="4. GET /resource" style="text;html=1;fontSize=13;" vertex="1" parent="1"><mxGeometry x="50" y="240" width="340" height="20" as="geometry"/></mxCell>
<mxCell id="l5" value="5. SELECT query" style="text;html=1;fontSize=13;" vertex="1" parent="1"><mxGeometry x="410" y="280" width="300" height="20" as="geometry"/></mxCell>
</root></mxGraphModel>"""
    }
]


def seed():
    b = get_brain()
    print(f"🧠 Patterns existants: {b.get_stats()['patterns_count']}")
    
    for p in PATTERNS:
        pid = b.add_pattern(
            title=p["title"],
            description=p["description"],
            xml_fragment=p["xml"],
            tags=p["tags"],
            source="seed"
        )
        print(f"  ✅ {p['title']} -> {pid}")
    
    print(f"\n📊 Stats: {b.get_stats()}")


if __name__ == "__main__":
    seed()