import numpy as np
import math
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import csv
import tqdm

import function as fn

###パラメータ################################################
###培地情報###
size = 10 #network-size
time = 1000
oat = 10
KCL = 10
agar = 1.5
env = [1,1] #[上,下] 忌避:-1 通常:0 誘引:1

###伸展パラメータ(伸展確率計算)###
Pcyt = 0.55 #新たにリンクを出す事象が発生する確率を調整
μs = 2 #関数Pexの傾きを調整
hs = 0.4 #P0(hs)=1/2を満たす
Tr = 0.6 #過去に縮退の形跡がある場合は伸展確率をTr倍する
Pr = 0.6 #伸展するリンクの太さを調節
np.random.seed(124)

###伸展パラメータ(培地)###
g0 = 0.1700 #グラフにおける変数gと区別のため0を追加
r = 1.271
b0 = 0.2015
B = 0.1150
agar0 = 0.8712

#管径成長パラメータ
μ = 1.3 #成長方程式パラメータμ(3.0)
a = 30 #成長方程式パラメータa(20)
α = 0.5 #ポテンシャル関数Uの第一項と第二項を調整するパラメータ(0.1)
V0 = 40 #理想体積V0(20)
I0 = 1 #総流量
L = 1 #リンク長

#描画パラメータ
extent = 1 #drawing extent
###パラメータ################################################


###ネットワーク情報算出#######################################
node_num = 3*size*(size+1)+1 #the number of node
link_num = 3*size*(3*size+1) #the number of link
compA = fn.complement(size) #補完接続行列
link_connection = fn.link_connection(size) #リンク-ノードの接続関係を記述
node_connection = fn.node_connection(size) #ノード-リンクの接続関係を記述
node_x, node_y = fn.coo_node(size, extent) #ノードの座標(描画用)
link_x1, link_y1, link_x2, link_y2 = fn.coo_link(size, extent, link_connection) #リンクの座標(描画用)
environment = fn.environment(size,link_y1,link_y2) #培地環境リスト
###ネットワーク情報算出#######################################


###パラメータ・変数初期値設定##################################
D = np.zeros(link_num) #コンダクタンス(計算用)
D[0:6] = 1
D_archive = np.zeros((time+1, link_num)) #コンダクタンス(出力用)
D_archive[0,] = D

link_status = np.zeros(link_num) #リンクが存在している場合1、していない場合0
link_status[0:6] = 1

#伸展の方向性に依存するパラメータの計算（培地環境に依存）[上,下]
s = np.zeros(2)
b = np.zeros(2)
for i in range(0,2):
  if env[i]==1:
    s[i] = 1/(oat+1) #誘引
    b[i] = b0 + B*(math.log(oat)+1)
  elif env[i]==-1: #忌避
    s[i] = KCL/(KCL+1) + 1
    b[i] = b0 - B*(math.log(KCL)+1)
  else: #通常
    s[i] = 1.0
    b[i] = b0

###伸展パラメータ###
P_0 = g0*np.tanh(r*(agar-agar0)) + np.tanh(r*agar0) + b #要素数２のベクトル

Q = np.zeros((link_num, 1))#流量
Q[0:6,0] = I0/6

###管径成長###
sink_source =np.zeros((node_num,1)) #流量行列
sink_source[0,0] = -I0
sink_source[1:7] = I0/6 
sink_source_archive = np.zeros((time,node_num))#タイムステップごとにシンクとソースノードを保存（シンク;1, ソース;2, それ以外;0）#最終ステップに選択は起きない行数はtime

A = np.zeros((link_num, node_num)) #接続行列
A [0:6, ] = compA[0:6,]

sink_source_archive = np.zeros((time,node_num)) #タイムステップごとにシンクとソースノードを保存（シンク;1, ソース;2, それ以外;0）#最終ステップに選択はされないため行数はTIME
node_archive = np.zeros((time+1,node_num)) #タイムステップごとに ノードの有無を保存
L = [1]*link_num

V_archive = [0]*(time+1) #タイムステップごとに管体積を保存
for i in range(1,link_num+1):
    V_archive[0] += math.sqrt(D[i-1]*L[i-1])

#matrixD = np.diag(D) #Dに関する対角行列
matrixL = np.diag(L) #Lに関する対角行列
invL = np.linalg.inv(matrixL) #逆行列

bw_archive = np.zeros((time+1, node_num)) #タイムステップごとに各ノードの媒介中心性を保存
bw_archive[0,0] = 1 #初期段階での媒介中心性（正規化前は30）

def f_dev(q,d,l,V,a,μ,α,V0): #成長方程式右辺計算-関数-
  return  ( ((1+a)*(abs(q))**μ) / (1+a*(abs(q))**μ) ) -d + α*(V0-V)*l/math.sqrt(d) #体積制約あり
  #return ( ((1+a)*(abs(q))^μ) / (1+a*(abs(q))^μ) ) -d #体積制約なし

###縮退###
Dmin = 0.005
Trace = np.zeros(link_num) #縮退が起きていれば1,起きていなければ0
###パラメータ・初期値計算#####################################


###モデル運用(メイン)################################################
for i in tqdm.tqdm(range(1,time+1)):
    
    #同じタイムステップ中に伸展したリンクが他のリンクの伸展に影響しないように一度saveに保存する
    D_save = D
    link_status_save = link_status
    A_save = A

    ###伸展##########
    for j in range(1,node_num+1): #ノードjに関して
        count = 0 #接続リンクの数をカウント
        for k in range(1,7): #6本の周辺リンクの少なくとも1本が存在するかどうかの確認
            if node_connection[j-1,k-1]!=0: #最外の考慮（存在しないリンクを省く）
                if link_status[node_connection[j-1,k-1]-1]==1: #リンク(通し番号node_connection[j,k])が存在する場合
                    count += 1
    
        qm = [1,1,1,1,1,1] #伸展確率(かけ合わせていく)

        if count>=1 and count<=5: #周辺に伸展可能な場合

            for k in range(1,7): #既存の周辺リンクから伸展確率を計算する
                num = node_connection[j-1,k-1] #リンクの通し番号
                if num!=0: #最外の考慮（存在しないリンクを省く）
                    if link_status[num-1]==1: #リンク(通し番号num)が存在する場合
                        #qm = qm*fn.extension(j,k,environment[num-1]) #伸展確率をかけ合わせる
                        
                        posi = environment[num-1]
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
                            P_00 = g0*np.tanh(r*(agar-agar0)) + np.tanh(r*agar0) +b0
                        
                        Qave = fn.Qave(j, node_connection, link_status, Q)
                        P0 = (Qave/hs)**μs / (1+(Qave/hs)**μs)
                        ext = [1,1,1,1,1,1]

                        #伸展確率計算
                        if k==1:
                            m = [mark,2,1,0,1,2]
                            for l in range(1,7):
                                ext[l-1] = Pcyt*P0*math.exp(-s0*m[l-1])*P_00
                            ext[k-1] = 0
                        
                        elif k==2:
                            m = [2,mark,2,1,0,1]
                            for l in range(1,7):
                                ext[l-1] = Pcyt*P0*math.exp(-s0*m[l-1])*P_00
                            ext[k-1] = 0
                        
                        elif k==3:
                            m = [1,2,mark,2,1,0]
                            for l in range(1,7):
                                ext[l-1] = Pcyt*P0*math.exp(-s0*m[l-1])*P_00
                            ext[k-1] = 0
                        
                        elif k==4:
                            m = [0,1,2,mark,2,1]
                            for l in range(1,7):
                                ext[l-1] = Pcyt*P0*math.exp(-s0*m[l-1])*P_00
                            ext[k-1] = 0
                        
                        elif k==5:
                            m = [1,0,1,2,mark,2]
                            for l in range(1,7):
                                ext[l-1] = Pcyt*P0*math.exp(-s0*m[l-1])*P_00
                            ext[k-1] = 0
                        
                        elif k==6:
                            m = [2,1,0,1,2,mark]
                            for l in range(1,7):
                                ext[l-1] = Pcyt*P0*math.exp(-s0*m[l-1])*P_00
                            ext[k-1] = 0

                        for l in range(1,7):
                            qm[l-1] = qm[l-1]*ext[l-1]

            #伸展確率と乱数から伸展するか判定を行う
            for k in range(1,7): #周辺リンクについて
                num = node_connection[j-1,k-1] #リンクの通し番号
                
                
                if num==0: #最外の考慮（存在しないリンク）
                    qm[k-1] = 0 #空間内に存在しないリンクの伸展確率をゼロにする
                
                else: #リンクが空間内に存在する場合
                    random = np.random.rand() #一様乱数を生成(周辺リンク６本に対してそれぞれ異なる乱数を生成することになる)
                    
                    if Trace[num-1]==0: #縮退の痕跡がない場合
                        if qm[k-1]>random: #伸展確率が乱数を上回った場合
                            qm[k-1] = 1 #伸展確率qmを1にする(伸展)
                        else: #伸展確率が乱数を上回らなかった場合
                            qm[k-1] = 0 #伸展確率qmを0にする
                    
                    elif Trace[num-1]==1: #縮退の痕跡がある場合
                        if qm[k-1]*Tr>random: #伸展確率にTrをかけた値が乱数を上回った場合
                            qm[k-1] = 1 #伸展確率qmを1にする(伸展)
                        else: #伸展確率が乱数を上回らなかった場合
                            qm[k-1] = 0 #伸展確率qmを0にする

            for k in range(1,7):
                if qm[k-1]==1: #新規伸展リンクについて
                    num = node_connection[j-1,k-1] #リンクの通し番号
                    link_status_save[num-1] = 1
                    A_save[num-1,] = compA[num-1,]
                    D_save[num-1] = Pr*fn.Dave(j, node_connection, D, link_status)
    ###伸展終了###

    link_status = link_status_save
    A = A_save
    D = D_save


    #リンクステータスからノードステータスの更新
    node_status = np.zeros(node_num) #ノードステータスを白紙にする（縮退に対応するため）
  
    for j in range(1,link_num+1):
        if link_status[j-1]==1: #リンクjが存在する場合
      
            node1 = link_connection[j-1,0] #両端のノードを検出
            node2 = link_connection[j-1,1] #両端のノードを検出
      
            node_status[node1-1] = 1 #ノードの存在を保存
            node_status[node2-1] = 1 #ノードの存在を保存
    
    #ノード数をカウントする
    node_sum = 0
    for j in range(1,node_num+1):
        if node_status[j-1]==1:
            node_sum = node_sum + 1


    ###管径の成長##########
    #シンクノードの選択
    sink_count = 0 #シンクの数をカウントする（最終的にシンクの総数となる）
    source_count = 0 #ソースの数をカウントする（最終的にソースの総数となる）
    sink_node = [0]*node_num #シンクノードであれば1,それ以外は0
    source_node = [0]*node_num #シンクノードであれば1,それ以外は0

    for j in range(1,node_num+1):
        if fn.sink_judge(j, size , link_status, node_connection)==1:
            sink_count += 1
            sink_node[j-1] = 1
    
    #ソースノードに流入・シンクノードから流出する原形質量を計算
    sink_source = np.zeros((node_num,1)) #流量行列

    #シンクノードのQaveを足し合わせる
    Qave_sum = 0 #シンクノードにおけQaveの総量
    Qaverage =  [0]*node_num
    for j in range(1,node_num+1):
        if sink_node[j-1]==1:
            Qaverage[j-1] = fn.Qave(j, node_connection, link_status, Q)
            Qave_sum += Qaverage[j-1]
    
    for j in range(1,node_num+1):
        if sink_node[j-1]==1:
            sink_source[j-1,0] = I0*Qaverage[j-1]/Qave_sum #流量行列にシンクノードから流出する原形質量を代入
    

    # グラフ化（ソースノード選択のため）
    G = nx.Graph() # Graphオブジェクトの作成
    count = 0
    for j in range(1,link_num):
        if link_status[j-1]==1 and count!=0:
            G_link += [(link_connection[j-1,0],link_connection[j-1,1])]
        elif link_status[j-1]==1 and count==0:
            G_link = [(link_connection[j-1,0],link_connection[j-1,1])]
            count = 1
    
    G_node = range(1,node_num+1)
    
    G.add_nodes_from(G_node)
    G.add_edges_from(G_link)

    #媒介中心性の計算
    between_centers = nx.betweenness_centrality(G)
    bw = list(between_centers.values())
    bw_max = 0

    #媒介中心性が最大のノードを特定
    for j in range(1,node_num+1):
        if bw[j-1] > bw_max: #最大値更新
            source_node = [0]*node_num
            source_node[j-1] = 1
            bw_max = bw[j-1]
        elif bw[j-1] == bw_max: #最大値と同値
            source_node[j-1] <- 1

    #ソースノードのカウント
    source_count = 0
    for j in range(1,node_num):
        if source_node[j-1]==1:
            source_count += 1

    D_archive[i,] = D
    np.savetxt('D.csv',D_archive,delimiter=',') #行列csv出力

    #正規化した媒介中心性を保存（正規化する予定）
    bw_archive[i,] = bw

    #流量行列にソースノードに流入する原形質量を代入（ソースを優先的に決定するためシンクのあと）
    for j in range(1,node_num+1):
        if source_node[j-1]==1:
            sink_source[j-1,0] <- -I0/source_count
    
    #タイムステップごとにシンクとソースノードを保存（シンク;1, ソース;2, それ以外;0）
    for j in range(1,node_num):
        if sink_node[j-1]==1:
            sink_source_archive[i-1,j-1] = 1
        if source_node[j-1]==1:
            sink_source_archive[i-1,j-1] = 2

    matrixD = np.diag(D) #Dの対角行列
    tA = A.T #Aの転置行列

    #流量の計算
    Q = np.dot(np.dot(np.dot(np.dot(-1*matrixD,invL),A),np.linalg.pinv(np.dot(np.dot(np.dot(tA,matrixD),invL),A))),sink_source)

    #管体積の算出
    V = 0
    for j in range(1,link_num+1):
        V = V + math.sqrt(D[j-1])*L[j-1]
    
    #成長方程式の適用
    for j in range(1,link_num+1):
        if D[j-1]>0: #管が存在する場合
            Dd = fn.Rungekutta(Q[j-1,0], D[j-1], L[j-1], V, a, μ, α, V0, f_dev) #成長方程式によって新たなコンダクタンスDを算出(ルンゲクッタ)
            
            V = V - D[j-1] + Dd #管体積の更新
            D[j-1] = Dd #コンダクタンスの更新
            
            if Dd==0: #ルンゲクッタの計算中に管を縮退した場合
                #link_status[j-1] = 0
                #A[j-1,] = 0
                D[j-1] = 0.000001 #本来は0にするが描画のために少しDに値を与える（わかりやすくシンクノードを描画するため） #縮退の処理は縮退フェイズで行われる

    #タイムステップごとに各リンクのDを保存する（描画のため）
    D_archive[i,] = D
  
    #タイムステップごとにノードの有無を保存する（解析のため）
    node_archive[i,] = node_status

    #管体積を保存
    V = 0
    for j in range(1,link_num+1):
        V = V + math.sqrt(D[j-1])*L[j-1]
    V_archive[i] <- V


    ###縮退##########
    #コンダクタンスDがDmin以下のリンクを縮退させる
    #ノードステータスの更新は必要がないので省略
    #粘菌が分断される可能性がある
    for j in range(1,link_num+1):
        if link_status[j-1]==1 and D[j-1]<Dmin:
            D[j-1] = 0
            link_status[j-1] = 0
            A[j-1,] = 0
            Trace[j-1] = 1

###モデル運用################################################

###ファイル出力###
np.savetxt("D.csv", D_archive, delimiter=",")

####描画#####################################################
#描画用に背景のリンクの座標をリストにまとめる
links_back = fn.links_back(size, link_x1, link_y1, link_x2, link_y2)

#描画開始
last = int(time/10)
for i0 in range(0,last+1):

    i = i0*10+1 #描画枚数を減らす

    #描画用にノード・リンクの座標をリストにまとめる
    links_exist, node_exist_x, node_exist_y = fn.exist(size, link_connection, D_archive[i-1,], link_x1, link_y1, link_x2, link_y2, node_x, node_y)

    # figure
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('navy')

    # plot
    ax.add_collection(mc.LineCollection(links_back, linewidths=0.9, colors="white", linestyle=':'))
    ax.add_collection(mc.LineCollection(links_exist, linewidths=5, colors="yellow", linestyle='-'))
    ax.scatter(node_exist_x, node_exist_y, color='black', s=40/size, alpha=1, zorder=2)


    # x axis
    plt.xlim([-extent*1.1, extent*1.1])
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_xlabel("")

    # y axis
    plt.ylim([-extent*1.1, extent*1.1])
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_ylabel("")
    #ax.set_title(str(i), x=0, y=-1.0, colors="white")
    fig.text(0.458, 0.13, "Timestep:"+str(i), fontsize=11, color="white")

    #plt.show()

    # save as png
    for count in range(0,1):
        write_file_name = "./Network/Network" + str(i) + ".png"
        plt.savefig(write_file_name) # -----(2)
    print(write_file_name)

####描画#####################################################

