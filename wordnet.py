

def build_synset_graph(synsets):
  node2hyponyms = {}
  for synset in synsets:
    paths = synset.hypernym_paths()
    for path in paths:
      for i in range(0, len(path)-1):
        hyponym = path[i+1].offset()
        node = path[i].offset()
        if node not in node2hyponyms:
          node2hyponyms[node] = set()
        node2hyponyms[node].add(hyponym)

  as_hyponym_hit = {}
  nodes = set()
  for node in node2hyponyms:
    nodes.add(node)
    hyponyms = node2hyponyms[node]
    for hyponym in hyponyms:
      if hyponym not in as_hyponym_hit:
        as_hyponym_hit[hyponym] = 0
      as_hyponym_hit[hyponym] += 1
      nodes.add(hyponym)
  src_nodes = nodes - set(as_hyponym_hit.keys())
  dst_nodes = nodes - set(node2hyponyms.keys())

  return node2hyponyms, nodes, src_nodes, dst_nodes


def retrieve_dst_nodes_from_node(node, node2hyponyms):
  dst_nodes = []
  if node in node2hyponyms:
    hyponyms = node2hyponyms[node]
    for hyponym in hyponyms:
      result = retrieve_dst_nodes_from_node(hyponym, node2hyponyms)
      dst_nodes.extend(result)
  else:
    dst_nodes.append(node)
  return dst_nodes
