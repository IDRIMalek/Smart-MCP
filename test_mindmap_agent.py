#!/usr/bin/env python3
"""
🧪 Test du MindmapAgent — validation directe sans passer par le serveur MCP
Usage : python test_mindmap_agent.py [--debug]
"""

import sys
import json
import time

sys.path.insert(0, ".")


def test_agent_initialization():
    """Test 1 : création de l'agent et vérification du MCP draw.io"""
    print("\n=== Test 1: Agent initialization ===")
    from brain.mindmap_agent import get_agent

    agent = get_agent(debug=True)
    print("✅ Agent créé")

    # Connexion au MCP draw.io
    from mcp_client.drawio import get_drawio
    drawio = get_drawio()
    drawio._initialize()
    print(f"✅ Draw.io MCP initialisé (process actif: {drawio.session_active})")

    return agent


def test_plan_structure(agent):
    """Test 2 : le LLM planifie une mindmap"""
    print("\n=== Test 2: Planification ===")
    plan = agent._plan_structure(
        "mindmap about remote work with branches: productivity tools, challenges, team communication"
    )
    print(f"  Root: {plan.get('root')}")
    print(f"  Branches: {len(plan.get('branches', []))}")
    for i, b in enumerate(plan.get("branches", [])):
        print(f"    [{i}] {b.get('label')} (angle={b.get('angle')}, color={b.get('color')})")
        for j, c in enumerate(b.get("children", [])):
            print(f"      └─ [{j}] {c.get('label')}")
    return plan


def test_create_mindmap(agent):
    """Test 3 : création complète d'une mindmap sur draw.io"""
    print("\n=== Test 3: Create mindmap ===")

    # Démarrer la session
    agent.agent.ensure_session()
    print("✅ Session draw.io active")

    prompt = "mindmap about machine learning types: supervised, unsupervised, reinforcement"
    result = agent.create_mindmap(prompt)

    status = result.get("status")
    print(f"  Status: {status}")
    print(f"  Operations: {result.get('operations', 0)}")
    print(f"  Nodes: {result.get('nodes', 0)}")

    if status == "success":
        print("  Canvas state:")
        for line in result.get("canvas", "").split("\n"):
            print(f"    {line}")
        return True
    else:
        print(f"  ERROR: {result.get('error', 'unknown')}")
        return False


def test_edit_mindmap(agent):
    """Test 4 : édition interactive"""
    print("\n=== Test 4: Edit mindmap ===")

    # Ajouter un nœud
    result = agent.edit_mindmap("add a 'deep learning' sub-branch under supervised in blue")
    print(f"  Edit add: {result.get('status')} — {result.get('action', '?')}")
    if "error" in result:
        print(f"    {result['error']}")

    # Changer une couleur
    print("\n  --- Essai changement de couleur ---")
    result2 = agent.edit_mindmap("change the color of 'unsupervised' to orange")
    print(f"  Edit color: {result2.get('status')} — {result2.get('action', '?')}")
    if "error" in result2:
        print(f"    {result2['error']}")

    return result


def test_state(agent):
    """Test 5 : lire l'état du canvas"""
    print("\n=== Test 5: Canvas state ===")
    state = agent.get_canvas_text()
    print(state)
    return state


if __name__ == "__main__":
    debug = "--debug" in sys.argv

    print("🧪 MindmapAgent Test Suite")
    print("=" * 50)

    # Test 1 : init
    agent = test_agent_initialization()

    # Test 2 : planification (sans draw.io)
    plan = test_plan_structure(agent)

    # Test 3 : création complète
    ok = test_create_mindmap(agent)

    if ok:
        # Test 4 : édition
        test_edit_mindmap(agent)

        # Test 5 : état
        test_state(agent)

        print("\n" + "=" * 50)
        print("🎉 Tous les tests passés !")
        print("📐 Ouvre le navigateur draw.io pour voir la mindmap")
    else:
        print("\n" + "=" * 50)
        print("❌ Tests échoués — vérifie les logs au-dessus")