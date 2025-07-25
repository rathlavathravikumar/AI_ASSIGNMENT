class state:
    def __init__(self,list,emptyIndex):
        self.list=list
        self.emptyIndex=emptyIndex
        
    def goalTest(self):
        if self.list==['w','w','w','_','e','e','e']:
            return True
        else:
            return False
            
    def moveGen(self):
        new_moves=[-2,-1,1,2]
        childern=[]
        for i in new_moves:
            new_empty=self.emptyIndex+i
            if 0<=new_empty<len(self.list):
                if (self.list[new_empty]=='e' and self.emptyIndex>new_empty) or (self.list[new_empty]=='w' and self.emptyIndex<new_empty):
                    new_list=self.list[:new_empty]+['_']+self.list[new_empty+1:]
                    new_list[self.emptyIndex]=self.list[new_empty]
                    childern.append(state(new_list,new_empty))
        return childern

    def removeSeen(self,childern,open,closed):
        open_n=[n for n,parent in open]
        closed_n=[n for n,parent in closed]
        
        unseen_c=[c for c in childern if c not in open_n and c not in closed_n]
        return unseen_c

    def reconstructPath(self,closed,node_pair):
        path=[]
        path_map={}
        for node,parent in closed:
            path_map[node]=parent

        node,parent=node_pair
        path_map[node]=parent
        while node is not None:
            path.append(node)
            node=path_map[node]
        path.reverse() 
        return path

    def reconstructpath(self, closed, goal_node_pair):
        path = []
        path_map = {}

        for node, parent in closed:
            path_map[node] = parent
        node = goal_node_pair[0]

        while node is not None:
            path.append(node)
            node = path_map.get(node) 

        path.reverse()  
        return path
    
    def __str__(self):
        print(self.list)
        return ''
        
    
    def __eq__(s1,s2):
        if s1.list==s2.list:
            return True
        else:
            return False

    def __hash__(self):
        return hash(tuple(self.list))

    def DFS(self):
        open=[]
        closed=[]
        open.append((self,None))
        while open:
            node_pair=open.pop(0)
            N,parent=node_pair
            if N.goalTest():
                return self.reconstructPath(closed,node_pair)
            else:
                closed.append(node_pair)
                childern=N.moveGen()
                unseen_childern=N.removeSeen(childern,open,closed)
                new_nodes=[(c,N) for c in unseen_childern]
                open=new_nodes+open
        return []
            
obj=state(['e', 'e', 'e', '_', 'w', 'w', 'w'],3)
childern=obj.moveGen()
path=obj.DFS()
for c in path:
    print(c)
    print('\n')
