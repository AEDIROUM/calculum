n = 100

parent = [i for  i in range(n)]
size = [1 for _ in range(n)]


def find(a):
    if parent[a]==a:
        return a
    parent[a] = find(parent[a])
    return parent[a]
    
def union(a, b):
    a, b = find(a), find(b)
    b, a = sorted(
        [a, b],
        key=lambda x: size[x]
        )
    size[a] += size[b]
    size[b] = 0
    parent[b] = a