try:
    from graphviz import Digraph
    print("Graphviz is working!")
    dot = Digraph()
    dot.node('A', 'Start')
    dot.node('B', 'End')
    dot.edge('A', 'B')
    dot.render('test_graph', view=True)
    print("Check test_graph.pdf")
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Run: pip install graphviz")
    print("2. Install Graphviz software from https://graphviz.org/download/")
    print("3. Ensure 'C:\\Program Files\\Graphviz\\bin' is in your PATH")