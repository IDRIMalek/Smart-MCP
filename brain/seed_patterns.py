"""
🧠 Smart MCP - Seed patterns pour le RAG brain
Charge des patterns de diagrammes drawio réutilisables
"""

import sys
from pathlib import Path
# S'assurer que le répertoire racine est dans sys.path pour les imports locaux
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from brain.rag import RAGBrain, get_brain

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
    },

    {
        "title": "Kanban board complet (2 sections, 6 colonnes)",
        "description": "Tableau Kanban complet 2 sections (Hermes + Benchmarks GPU), 3 colonnes (A faire / En cours / Termine). Layout 1250x1100px, cartes ombragees, colonnes colorees.",
        "tags": ["kanban", "board", "tableau", "taches", "sprint", "agile", "todo", "gestion"],
        "xml": """<diagram id="kanban" name="📋 Kanban">
    <mxGraphModel grid="0" page="0" pageWidth="1800" pageHeight="1400" dx="0" dy="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- ========== SECTION 1: Hermès ========== -->

        <!-- Section title -->
        <mxCell id="2" value="🏠 Hermès — Config maison" style="text;html=1;fontSize=20;fontStyle=1;fillColor=none;strokeColor=none;whiteSpace=wrap;" vertex="1" parent="1">
          <mxGeometry x="60" y="40" width="350" height="40" as="geometry"/>
        </mxCell>

        <!-- Col 1: À faire (background) -->
        <mxCell id="3" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#BBDEFB;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="60" y="100" width="350" height="500" as="geometry"/>
        </mxCell>
        <!-- Col 1 header -->
        <mxCell id="4" value="📋 À faire" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1;fillColor=#2196F3;strokeColor=#2196F3;fontColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="75" y="110" width="330" height="50" as="geometry"/>
        </mxCell>
        <!-- Col 1 cards -->
        <mxCell id="5" value="Configurer les providers LLM" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="175" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="6" value="Automatiser les workflows cron" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="240" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="7" value="Créer des skills réutilisables" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="305" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="8" value="Documenter le setup" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="370" width="280" height="45" as="geometry"/>
        </mxCell>

        <!-- Col 2: En cours (background) -->
        <mxCell id="9" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#FFE0B2;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="470" y="100" width="350" height="500" as="geometry"/>
        </mxCell>
        <!-- Col 2 header -->
        <mxCell id="10" value="🔄 En cours" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1;fillColor=#FF9800;strokeColor=#FF9800;fontColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="485" y="110" width="330" height="50" as="geometry"/>
        </mxCell>
        <!-- Col 2 cards -->
        <mxCell id="11" value="Intégrer les MCP servers" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="505" y="175" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="12" value="Tester les subagents locaux" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="505" y="240" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="13" value="Dashboard Hermès WebUI" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="505" y="305" width="280" height="45" as="geometry"/>
        </mxCell>

        <!-- Col 3: Terminé (background) -->
        <mxCell id="14" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#C8E6C9;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="880" y="100" width="350" height="500" as="geometry"/>
        </mxCell>
        <!-- Col 3 header -->
        <mxCell id="15" value="✅ Terminé" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1;fillColor=#4CAF50;strokeColor=#4CAF50;fontColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="895" y="110" width="330" height="50" as="geometry"/>
        </mxCell>
        <!-- Col 3 cards -->
        <mxCell id="16" value="Setup Hermès de base" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="915" y="175" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="17" value="Connexion MCP drawio" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="915" y="240" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="18" value="Config Ollama GPU" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="915" y="305" width="280" height="45" as="geometry"/>
        </mxCell>

        <!-- ========== SECTION 2: Benchmarks GPU ========== -->

        <!-- Section title -->
        <mxCell id="19" value="📊 Benchmarks GPU" style="text;html=1;fontSize=20;fontStyle=1;fillColor=none;strokeColor=none;whiteSpace=wrap;" vertex="1" parent="1">
          <mxGeometry x="60" y="660" width="350" height="40" as="geometry"/>
        </mxCell>

        <!-- Col 1: À faire (background) -->
        <mxCell id="20" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#BBDEFB;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="60" y="720" width="350" height="400" as="geometry"/>
        </mxCell>
        <!-- Col 1 header -->
        <mxCell id="21" value="📋 À faire" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1;fillColor=#2196F3;strokeColor=#2196F3;fontColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="75" y="730" width="330" height="50" as="geometry"/>
        </mxCell>
        <!-- Col 1 cards -->
        <mxCell id="22" value="Benchmark qwen3.5-4b-agent-opt" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="795" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="23" value="Dashboard Plotly interactif" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="860" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="24" value="Comparer CPU vs GPU vs iGPU" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="925" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="25" value="Benchmark contexte 128K" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="95" y="990" width="280" height="45" as="geometry"/>
        </mxCell>

        <!-- Col 2: En cours (background) -->
        <mxCell id="26" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#FFE0B2;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="470" y="720" width="350" height="400" as="geometry"/>
        </mxCell>
        <!-- Col 2 header -->
        <mxCell id="27" value="🔄 En cours" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1;fillColor=#FF9800;strokeColor=#FF9800;fontColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="485" y="730" width="330" height="50" as="geometry"/>
        </mxCell>
        <!-- Col 2 cards -->
        <mxCell id="28" value="Benchmark qwen2.5-coder:14b" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="505" y="795" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="29" value="Heatmap des perf par modèle" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="505" y="860" width="280" height="45" as="geometry"/>
        </mxCell>

        <!-- Col 3: Terminé (background) -->
        <mxCell id="30" value="" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#C8E6C9;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="880" y="720" width="350" height="400" as="geometry"/>
        </mxCell>
        <!-- Col 3 header -->
        <mxCell id="31" value="✅ Terminé" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1;fillColor=#4CAF50;strokeColor=#4CAF50;fontColor=#FFFFFF;" vertex="1" parent="1">
          <mxGeometry x="895" y="730" width="330" height="50" as="geometry"/>
        </mxCell>
        <!-- Col 3 cards -->
        <mxCell id="32" value="Benchmark initial Ollama" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="915" y="795" width="280" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="33" value="Routeur/cascade/pipeline optim" style="rounded=1;whiteSpace=wrap;html=1;shadow=1;arcSize=20;fillColor=#FFFFFF;strokeColor=#BDBDBD;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="915" y="860" width="280" height="45" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>"""
    },
]


def seed(persist_dir: str = None):
    if persist_dir:
        b = RAGBrain(persist_dir)
    else:
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