class DisjointSet(object):
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
    self.size = 0

    if arr is not None:
      self.init_from_list(arr)

  def append_to_tail(self, data):
    node = self.Node(data)
    prev = self.tail.prev

    node.prev = prev
    prev.next = node

    node.next = self.tail
    self.tail.prev = node

    self.size += 1

  def insert_to_head(self, data):
    node = self.Node(data)
    next = self.head.next

    node.next = next
    next.prev = node

    node.prev = self.head
    self.head.next = node

    self.size += 1

  # N.B. after remove, the cur points to the removed node
  # thus, next() and prev() still functions well after remove_cur()
  def remove_cur(self): 
    self._remove(self.cur)

  def _remove(self, node):
    node.prev.next = node.next
    node.next.prev = node.prev
    self.size -= 1

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

  def pop_front(self):
    if self.head.next != self.tail:
      self.head.next = self.head.next.next
      self.head.next.prev = self.head
      self.size -= 1
    else:
      raise Exception("""try to pop_front empty DoubleLinkedList""")

  def pop_back(self):
    if self.tail.prev != self.head:
      self.tail.prev = self.tail.prev.prev
      self.tail.prev.next = self.tail
      self.size -= 1
    else:
      raise Exception("""try pop_tail empty DoubleLinkedList""")

  def front(self):
    node = self.head.next
    return node.data

  def back(self):
    node = self.tail.prev
    return node.data


# the data format is tuple and the 1st element is the key
# it is a max-heap
class Heap(object):
  def __init__(self):
    self._data = [(None,)]

  @property
  def data(self):
    return self._data

  def len(self):
    return len(self._data) - 1

  def _heapify(self, i):
    while i < len(self._data):
      l = i*2
      r = i*2+1
      largest = i
      if l < len(self._data) and self._data[l][0] > self._data[largest][0]:
        largest = l
      if r < len(self._data) and self._data[r][0] > self._data[largest][0]:
        largest = r
      if largest != i:
        tmp = self._data[i]
        self._data[i] = self._data[largest]
        self._data[largest] = tmp
        i = largest
      else:
        break

  def build_heap(self, data):
    self._data = [(None,)] + data
    i = len(data)/2
    while i > 0:
      self._heapify(i)
      i -= 1

  def is_empty(self):
    return len(self._data) == 1

  def max(self):
    assert len(self._data) > 1
    return self._data[1]

  def pop(self):
    self._data[1] = self._data[-1]
    self._data.pop()
    self._heapify(1)

  def push(self, d):
    i = len(self._data)
    self._data.append((None,))
    while i > 1 and self._data[i/2][0] < d[0]:
      self._data[i] = self._data[i/2]
      i /= 2
    self._data[i] = d
