class Node:
    def __init__(self,val):
        self.data=val
        self.left=None
        self.right=None
class Solution:
    def preorder(self,root,arr):
        if root is None:
            return
        self.preorder(root.left,arr)
        arr.append(root.data)
        self.preorder(root.right,arr)
    def PreOrder(self,root):
        arr=[]
        self.preorder(root,arr)
        return arr
if __name__=='__main__':
    root=Node(1)
    root.left=Node(2)
    root.right=Node(3)
    root.left.left=Node(4)
    root.left.right=Node(5)
    sol=Solution()
    result=sol.PreOrder(root)
    print("preorder traversal: ",end="")
    for val in result:
        print(val,end="")
        print()


