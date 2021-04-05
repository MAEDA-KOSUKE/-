###functions###

import numpy as np
#import matplotlib
#import matplotlib.pyplot as plt
#import matplotlib.collections as mc
import math

def complement(size):
    node_num = 3*size*(size+1)+1 #the number of node
    link_num = 3*size*(3*size+1) #the number of link
    compA = np.zeros((link_num,node_num),dtype=int) # complement array of A
    size_count = 1 #the number of cycles

    for i in range(1,link_num+1):
        if i<=6:  #1st cycle 1st～6th link
            compA[i-1,0] = 1
            compA[i-1,i] = -1
        
        elif i>=7 and i<=11:  #1st cycle 7th～11th link
            compA[i-1,i-6] = 1
            compA[i-1,i-5] = -1
        
        elif i==12:  #1st cycle 12th link
            compA[11,6] = 1
            compA[11,1] = -1
        
        elif i>=13:  #2nd~ cycle
            if i>3*(size_count-1)*(3*(size_count-1)+1) and i<=3*(size_count-1)*(3*(size_count-1)+1) + 12*size_count-6: #outward
                compA[i-1,link_start-1] = 1
                compA[i-1,link_goal-1] = -1
      
            if i==link_first+2*(size_count-2)*(node_count_start-1)+3*(node_count_start-1)+1: #outward start node (vertex)
                link_start = link_start+1
                node_count_start = node_count_start+1
            elif (i-(link_first+2*(size_count-2)*(node_count_start-2)+3*(node_count_start-2)+1))%2 == 0  and i!=link_first+2*(size_count-2)*(node_count_start-1)+3*(node_count_start-1): #outward start node (not vertex)
                link_start += 1
                 
            if i==link_first+2*(size_count-1)*(node_count_goal-1)+(node_count_goal-1): #outward goal node（vertex）
                link_goal += 1
                node_count_goal += 1
            elif (i-(link_first+2*(size_count-1)*(node_count_goal-2)+(node_count_goal-2)))%2 == 0: #outward goal node（not vertex）
                link_goal += 1
            
            
            if i==3*(size_count-1)*(3*(size_count-1)+1) + 12*size_count-6:  ##the last of outward link 
                compA[i-1,] = 0
                compA[i-1,3*(size_count-2)*(size_count-1)+2-1] = 1
                compA[i-1,3*size_count*(size_count+1)+1-1] = -1
            
            
            if i>3*(size_count-1)*(3*(size_count-1)+1) + 12*size_count-6 and i<3*size_count*(3*size_count+1): #circuit link
                compA[i-1,3*(size_count-1)*size_count+2 + i-(3*(size_count-1)*(3*(size_count-1)+1) + 12*size_count-6 +1)-1] = 1
                compA[i-1,3*(size_count-1)*size_count+2 + i-(3*(size_count-1)*(3*(size_count-1)+1) + 12*size_count-6)-1+1-1] = -1
            
            
            if i==3*size_count*(3*size_count+1):  #last circuit link
                compA[i-1,3*size_count*(size_count+1)+1-1] = 1
                compA[i-1,3*(size_count-1)*size_count+2-1] = -1
        
        if i==3*size_count*(3*size_count+1): #finish calculation at each cycle 
            node_count_start = 1
            node_count_goal = 1
            link_start = 3*(size_count-1)*size_count+2
            link_goal = 3*size_count*(size_count+1)+2
            size_count += 1
            link_first = 3*(size_count-1)*(3*(size_count-1)+1)+1
  
    return compA

def link_connection(size):
    node_num = 3*size*(size+1)+1 #the number of node
    link_num = 3*size*(3*size+1) #the number of link
    compA = complement(size)
    link_connection = np.empty((link_num, 2),dtype=int)

    for i in range(1,link_num+1):
        for j in  range(1,node_num+1):
            if compA[i-1,j-1]==1:  #start node
                link_connection[i-1,0] = j
    
            if compA[i-1,j-1]==-1:  #goal node
                link_connection[i-1,1] = j
    
    return link_connection

def node_connection(size):
    node_num = 3*size*(size+1)+1 #the number of node
    link_num = 3*size*(3*size+1) #the number of link
    compA = complement(size)
    
    node_connection = np.empty((node_num, 6),dtype=int)
    size_count = 1
    node_start = 2

    #補完接続行列から各ノードの接続リンクをノード接続行列に格納する
    for i in range(1,node_num+1):
        save = np.array([0,0,0,0,0,0],dtype=int) #save array
        count = 1
   
        #補完接続行列から保管配列1に接続リンクの通し番号を格納（昇順） 
        for j in range(1,link_num+1):
            if compA[j-1,i-1]==1 or compA[j-1,i-1]==-1:
                save[count-1] = j
                count += 1

            if count==7:
                break
        
        #リンクの配向に従って保管配列1からノード接続行列を作成
        if i==1: #ノード1（中央）
            node_connection[0,0] = save[0]
            node_connection[0,1] = save[5]
            node_connection[0,2] = save[4]
            node_connection[0,3] = save[3]
            node_connection[0,4] = save[2]
            node_connection[0,5] = save[1]
        
        elif i==node_start: #始点ノード
            node_connection[i-1,0] = save[0]
            node_connection[i-1,1] = save[1]
            node_connection[i-1,2] = save[4]
            node_connection[i-1,3] = save[3]
            node_connection[i-1,4] = save[5]
            node_connection[i-1,5] = save[2]

        elif (i-node_start)%size_count==0: #頂点ノード（始点ノードを除く）
            node_connection[i-1,0] = save[0]
            node_connection[i-1,1] = save[2]
            node_connection[i-1,2] = save[5]
            node_connection[i-1,3] = save[4]
            node_connection[i-1,4] = save[3]
            node_connection[i-1,5] = save[1]
        
        else: #中央と頂点以外
            node_connection[i-1,0] = save[0]
            node_connection[i-1,1] = save[1]
            node_connection[i-1,2] = save[3]
            node_connection[i-1,3] = save[5]
            node_connection[i-1,4] = save[4]
            node_connection[i-1,5] = save[2]
    
    
        if i==3*size_count*(size_count+1)+1: #各周の計算修了
            size_count = size_count+1 #サイズカウントの更新
            node_start = 3*(size_count-1)*size_count+2 #始点ノードの更新

    return node_connection

def coo_node(size, extent):
    node_num = 3*size*(size+1)+1 #the number of node
    link_num = 3*size*(3*size+1) #the number of link
    
    length = extent/size  #length of link
    node_x = [0] #x-coordinates of node
    node_y = [0] #y-coordinates of node
    size_count = 1 #the number of cycles
    node_count = 1 #the number of edges at each cycle
    node_start = 2 #start node of each edge


    for i in range(2,node_num+1):
        if i==node_start: #start node
            node_x.append(length*size_count)
            node_y.append(0)
        
        elif node_count==1: #1st edge
            node_x.append(node_x[i-2]-length/2)
            node_y.append(node_y[i-2]+length*np.sqrt(3)/2)

        elif node_count==2: #2nd edge
            node_x.append(node_x[i-2]-length)
            node_y.append(node_y[i-2])

        elif node_count==3: #3rd edge
            node_x.append(node_x[i-2]-length/2)
            node_y.append(node_y[i-2]-length*np.sqrt(3)/2)

        elif node_count==4: #4th edge
            node_x.append(node_x[i-2]+length/2)
            node_y.append(node_y[i-2]-length*np.sqrt(3)/2)
        
        elif node_count==5: #5th edge
            node_x.append(node_x[i-2]+length)
            node_y.append(node_y[i-2])
        
        elif node_count==6: #6th edge
            node_x.append(node_x[i-2]+length/2)
            node_y.append(node_y[i-2]+length*np.sqrt(3)/2)


        if (i-node_start)%size_count==0 and i!=node_start: #node_count updating
            node_count += 1

        if  i==3*size_count*(size_count+1)+1: #finish calculation at each cycle 
            size_count += 1 #updating
            node_count = 1 #updating
            node_start = 3*(size_count-1)*size_count+2 #updating
    
    return node_x, node_y

def coo_link(size, extent, link_connection):
    node_num = 3*size*(size+1)+1 #the number of node
    link_num = 3*size*(3*size+1) #the number of link
    node_x, node_y = coo_node(size, extent)
    #link_connection = link_connection(size)

    link_x1 = [0]*link_num
    link_y1 = [0]*link_num
    link_x2 = [0]*link_num
    link_y2 = [0]*link_num

    for i in range(1,link_num+1):
        link_x1[i-1] = node_x[link_connection[i-1,0]-1]
        link_y1[i-1] = node_y[link_connection[i-1,0]-1]
        link_x2[i-1] = node_x[link_connection[i-1,1]-1]
        link_y2[i-1] = node_y[link_connection[i-1,1]-1]

    return link_x1, link_y1, link_x2, link_y2

def environment(size,link_y1,link_y2):
    link_num = 3*size*(3*size+1) #the number of link
    environment = [0]*link_num

    for i in range(1,link_num+1):
        if link_y1[i-1]>=0 and link_y2[i-1]>=0:
            environment[i-1] = 1
        if link_y1[i-1]<=0 and link_y2[i-1]<=0:
            environment[i-1] = -1
        if link_y1[i-1]==0 and link_y2[i-1]==0:
            environment[i-1] = 0
    
    return environment

def links_back(size, link_x1, link_y1, link_x2, link_y2):
    link_num = 3*size*(3*size+1) #the number of link
    links_back = [[(link_x1[0], link_y1[0]), (link_x2[0], link_y2[0])]]
    for i in range(2,link_num+1):
        links_back.append([(link_x1[i-1], link_y1[i-1]), (link_x2[i-1], link_y2[i-1])])
    return links_back

def exist(size, link_connection, D, link_x1, link_y1, link_x2, link_y2, node_x, node_y):
    link_num = 3*size*(3*size+1) #the number of link
    for i in range(1,link_num+1):
        count=0
        for i in range(1,link_num+1):
            if D[i-1]!=0 and count!=0:
                links_exist.append([[link_x1[i-1], link_y1[i-1]], [link_x2[i-1], link_y2[i-1]]])
                node_exist_x.append(node_x[link_connection[i-1,0]-1])
                node_exist_x.append(node_x[link_connection[i-1,1]-1])
                node_exist_y.append(node_y[link_connection[i-1,0]-1])
                node_exist_y.append(node_y[link_connection[i-1,1]-1])   
            elif D[i-1]!=0 and count==0:
                links_exist = [[(link_x1[i-1], link_y1[i-1]), (link_x2[i-1], link_y2[i-1])]]
                node_exist_x = [node_x[link_connection[i-1,0]-1], node_x[link_connection[i-1,1]-1]]
                node_exist_y = [node_y[link_connection[i-1,0]-1], node_y[link_connection[i-1,1]-1]]
                count += 1
    return links_exist, node_exist_x, node_exist_y

def Qave(node, node_connection, link_status, Q):
    flow = 0 #周囲のリンクにおける流量の合計
    link_number = 0 #周囲のリンクの本数
  
    for i in range(1,7): #周囲のリンクiにおいて
        if node_connection[node-1,i-1] != 0: #最外ノードのそもそも存在しないリンクをはじく
            if link_status[node_connection[node-1,i-1]-1]==1: #リンクが存在する場合
                flow = flow + abs( Q[node_connection[node-1,i-1]-1,0] ) #流量を足し合わせる
                link_number = link_number+1 #リンクの本数を1追加
  
    if link_number==0:
        Qave = 0
    else:
        Qave = flow/link_number

    return Qave

def extension(node, link_num, posi, s0, Pcyt, μs, hs, Tr, Pr):
    mark = 1 #既存リンクのマーカー（実際は必要ないがわかりやすくするため.形式的に1とする.）
  
    #左右の判別(下:posi=-1 上:posi=1 中央:posi=0)
    #関数内でパラメータ名に0を追加
    if posi==1:
        s0 = s[0]
        P_00 = P_0[0]   
    elif posi==-1:
        s0 = s[1]
        P_00 = P_0[1]
    elif posi==0:
        s0 = 1.0
        P_00 = g0*tanh(r*(agar-agar0)) + tanh(r*agar0) +b0
    
    Qave = Qave(node, node_connection, link_status, Q)
    P0 = (Qave/hs)^μs / (1+(Qave/hs)^μs)

    #伸展確率計算
    if link_num==1:
        m = [mark,2,1,0,1,2]
        ext = Pcyt*P0*math.exp(-s0*m)*P_00
        ext[link_num-1] = 0
    
    elif link_num==2:
        m = [2,mark,2,1,0,1]
        ext = Pcyt*P0*math.exp(-s0*m)*P_00
        ext[link_num-1] = 0
    
    elif link_num==3:
        m = [1,2,mark,2,1,0]
        ext = Pcyt*P0*math.exp(-s0*m)*P_00
        ext[link_num-1] = 0
    
    elif link_num==4:
        m = [0,1,2,mark,2,1]
        ext = Pcyt*P0*math.exp(-s0*m)*P_00
        ext[link_num-1] = 0
    
    elif link_num==5:
        m = [1,0,1,2,mark,2]
        ext = Pcyt*P0*math.exp(-s0*m)*P_00
        ext[link_num-1] = 0
    
    elif link_num==6:
        m = [2,1,0,1,2,mark]
        ext = Pcyt*P0*math.exp(-s0*m)*P_00
        ext[link_num] = 0
  
    return ext
    
def Dave(node, node_connection, D, link_status):
    sum = 0 #周囲のリンクのコンダクタンスの合算値
    link_number = 0 #周囲のリンクの本数
  
    for i in range(1,7): #周囲のリンクiにおいて
        num = node_connection[node-1,i-1]
        if num != 0: #最外ノードのそもそも存在しないリンクをはじく
            if link_status[num-1]==1: #リンクが存在する場合
                sum += D[num-1] #コンダクタンスを足し合わせる
                link_number += 1 #リンクの本数を1追加 
 
    if link_number==0:
        Dave = 0
    else:
        Dave = sum/link_number
  
    return Dave

def  sink_judge(node, size , link_status, node_connection):  
    link_count = 0 #ノードに接続しているリンクの総数
  
    if node<=3*(size-1)*size+1: #最外ノード以外
        for i in range(1,6):
            if link_status[node_connection[node-1,i-1]-1]==1:
                link_count = link_count+1

        if link_count==1: #リンクが1本接続
            return 1 #シンクである(1を返す)
        
        elif link_count==2: #リンクが2本接続
            #2本のリンクが隣り合う場合
            if (link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1) or (link_status[node_connection[node-1,1]-1]==1 and link_status[node_connection[node-1,2]-1]==1) or (link_status[node_connection[node-1,2]-1]==1 and link_status[node_connection[node-1,3]-1]==1) or (link_status[node_connection[node-1,3]-1]==1 and link_status[node_connection[node-1,4]-1]==1) or (link_status[node_connection[node-1,5-1]-1]==1 and link_status[node_connection[node-1,5]-1]==1) or (link_status[node_connection[node-1,5]-1]==1 and link_status[node_connection[node-1,0]-1]==1):
                return 1 #シンクである(1を返す)
            else:
                return 0
        
        elif link_count==3: #リンクが3本接続
            #3本のリンクが隣り合う場合
            if (link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1 and link_status[node_connection[node-1,2]-1]==1) or (link_status[node_connection[node-1,1]-1]==1 and link_status[node_connection[node-1,2]-1]==1 and link_status[node_connection[node-1,3]-1]==1) or (link_status[node_connection[node-1,2]-1]==1 and link_status[node_connection[node-1,3]-1]==1 and link_status[node_connection[node-1,4]-1]==1) or (link_status[node_connection[node-1,3]-1]==1 and link_status[node_connection[node-1,4]-1]==1 and link_status[node_connection[node-1,5]-1]==1) or (link_status[node_connection[node-1,4]-1]==1 and link_status[node_connection[node-1,5]-1]==1 and link_status[node_connection[node-1,0]-1]==1) or (link_status[node_connection[node-1,5]-1]==1 and link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1):
                return(1) #シンクである(1を返す)
            else:
                return 0 
        
        else: #リンクが0本もしくは4本以上接続
            return (0) #シンクではない(0を返す)
    

    else: #最外ノード
        if (node-(3*(size-1)*size+2))%size==0: #最外頂点
            if link_status[node_connection[node-1,0]-1]==1:
                link_count += 1
            if link_status[node_connection[node-1,1]-1]==1:
                link_count += 1
            if link_status[node_connection[node-1,5]-1]==1:
                link_count += 1
            
            if link_count==0: #リンクが0本接続
                return 0 #シンクではない(0を返す)
            
            elif link_count==1: #リンクが1本接続
                return 1 #シンクである(1を返す)
                
            elif link_count==2: #リンクが2本接続
                #2本のリンクが隣り合う場合
                if (link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1) or (link_status[node_connection[node-1,5]-1]==1 and link_status[node_connection[node-1,0]-1]==1):
                    return 1 #シンクである(1を返す)
                else:
                    return 0
                
            elif link_count==3: #リンクが3本接続
                return 1 #シンクである(1を返す)
        
        else: #最外かつ頂点以外
            if link_status[node_connection[node-1,0]-1]==1:
                link_count += 1
            if link_status[node_connection[node-1,1]-1]==1:
                link_count += 1
            if link_status[node_connection[node-1,2]-1]==1:
                link_count += 1
            if link_status[node_connection[node-1,5]-1]==1:
                link_count += 1
            
            if link_count==0 or link_count==4: #リンクが0本接続
                return 0 #シンクではない(0を返す)
                
            elif link_count==1: #リンクが1本接続
                return 1 #シンクである(1を返す)
                
            elif link_count==2: #リンクが2本接続
                #2本のリンクが隣り合う場合
                if (link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1) or (link_status[node_connection[node-1,1]-1]==1 and link_status[node_connection[node-1,2]-1]==1) or (link_status[node_connection[node-1,5]-1]==1 and link_status[node_connection[node-1,0]-1]==1):
                    return 1 #シンクである(1を返す)
                else:
                    return 0
                
            elif link_count==3: #リンクが3本接続
                #3本のリンクが隣り合う場合
                if (link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1 and link_status[node_connection[node-1,2]-1]==1) or (link_status[node_connection[node-1,5]-1]==1 and link_status[node_connection[node-1,0]-1]==1 and link_status[node_connection[node-1,1]-1]==1):
                    return 1 #シンクである(1を返す)
                else:
                    return 0

def f(q,d,l,V,a,μ,α,V0): #成長方程式右辺計算-関数-
  return  ( ((1+a)*(abs(q))^μ) / (1+a*(abs(q))^μ) ) -d + α*(V0-V)*l/math.sqrt(d) #体積制約あり
  #return ( ((1+a)*(abs(q))^μ) / (1+a*(abs(q))^μ) ) -d #体積制約なし

#ルンゲ＝クッタ法-関数-
def Rungekutta(q,d,l,V,a,μ,α,V0,f):
    f1 = d
    dt = 0.01
    count = 0
    #for i in range(1,2):
    k1 = f(q,d,l,V,a,μ,α,V0)
    if (f1+k1/2)<0:
        return 0
    k2 = f(q,(f1+k1*dt/2),l,V,a,μ,α,V0)
    if (f1+k2/2)<0:
        return 0
    k3 = f(q,(f1+k2*dt/2),l,V,a,μ,α,V0)
    if (f1+k3)<0:
        return(0)
    k4 = f(q,(f1+k3*dt),l,V,a,μ,α,V0)
        
    f2 = f1 + (k1 + 2*k2 + 2*k3 + k4)*dt/6
    if f2<0:
        return(0)
    f1 = f2
        
    return f2