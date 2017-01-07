class DisjointSet:
  class Node:
    def __init__(self, val):
      self._rank = 1
      self._val = val
      self._parent = self

    @property
    def val(self):
      return self.val

  def __init__(self):
    self._sets = {}

  def makeSet(self, val):
    if val not in self._sets:
      self._sets[val] = self.Node(val)

  def join(self, valLhs, valRhs):
    lhs = self._sets[valLhs]
    rhs = self._sets[valRhs]
    lhsParent = self.find(lhs)
    rhsParent = self.find(rhs)

    if lhsParent == rhsParent:
      return

    parent = lhsParent
    child = rhsParent
    if lhsParent._rank < rhsParent._rank: # path compress
      parent = rhsParent
      child = lhsParent
    child._parent = parent
    parent._rank = max(parent._rank, child._rank+1)

  def find(self, node):
    nodes = [node]
    while node._parent != node:
      nodes.append(node)
      node = node._parent

    # path compress trick
    for i in range(1, len(nodes)):
      nodes[-i]._parent = nodes[-i+1]._parent

    return nodes[0]._parent

  def findVal(self, val):
    return self.find(self._sets[val])


class DoubleLinkedList(object):
  class Node(object):
    def __init__(self, data=None):
      self.prev = None
      self.next = None
      self.data = data

  def __init__(self, arr=None):
    self.head = self.Node()
    self.tail = self.Node()
    self.head.next = self.tail
    self.tail.prev = self.head
    self.cur = self.head

    if arr is not None:
      self.init_from_list(arr)

  def append_to_tail(self, data):
    node = self.Node(data)
    prev = self.tail.prev

    node.prev = prev
    prev.next = node

    node.next = self.tail
    self.tail.prev = node

  def insert_to_head(self, data):
    node = self.Node(data)
    next = self.head.next

    node.next = next
    next.prev = node

    node.prev = self.head
    self.head.next = node

  # after remove, the cur points to the removed node
  def remove_cur(self): 
    self._remove(self.cur)

  def _remove(self, node):
    node.prev.next = node.next
    node.next.prev = node.prev

  def init_from_list(self, arr):
    for d in arr:
      self.append_to_tail(d)

  def move_to_head(self):
    self.cur = self.head

  def move_to_tail(self):
    self.cur = self.tail

  def next(self):
    if cur.next == self.tail:
      return False
    else:
      cur = cur.next
      return True

  def prev(self):
    if cur.prev == self.head:
      return False
    else:
      cur = cur.prev
      return True

  def cur_data(self):
    return self.cur.data

  def is_empty(self):
    return self.head.next == self.tail
