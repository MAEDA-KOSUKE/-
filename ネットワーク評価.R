###形態評価のためのグラフを作成する###

TIME_1 <- TIME+1

###管体積の時間変化をグラフ化###
#Vtube = Σ(sqrt(Di)*Li)

#V_archiveの作成
for(i in 1:TIME_1){
  V <- 0
  for(j in 1:all_link){
    V <- V + sqrt(D_archive[i,j])*L[j]
  }
  V_archive[i+1] <- V
}


data <- matrix(nrow=TIME+1, ncol=2)

for(i in 1:TIME_1){
  data[i,1] <- i
  data[i,2] <- V0
}

#保存するフォルダと図の名前を指定
file_name <- sprintf("./Vtube.png")
png(file_name, width=700, height=700)

matplot(V_archive, xlim=c(0,TIME), ylim=c(5,V0*1.2), type="l",lwd=3, xlab="Timestep",ylab="Vtube", col="red", lty=1)
matplot(data[,1],data[,2], xlim=c(min,max), ylim=c(5,V0*1.2), type="l",lwd=3, xlab="Timestep",ylab="Vtube", col="black", lty=2, add=TRUE)

#図の書き込み終了
dev.off()
##################################


###ノード数の時間変化をグラフ化###

node_sum <- numeric(TIME+1)

for(i in 1:TIME_1){
  for(j in 1:all_node){
    if(node_archive[i,j]==1) node_sum[i] <- node_sum[i]+1
  }
}

#保存するフォルダと図の名前を指定
file_name <- sprintf("./node.png")
png(file_name, width=700, height=700)

matplot(node_sum, xlim=c(0,TIME), type="l",lwd=3, xlab="Timestep",ylab="Node", col=1, lty=1)

#図の書き込み終了
dev.off()
##################################



###リンク数の時間変化をグラフ化###

link_sum <- numeric(TIME+1)

for(i in 1:TIME_1){
  for(j in 1:all_link){
    if(D_archive[i,j]>0) link_sum[i] <- link_sum[i]+1
  }
}

#保存するフォルダと図の名前を指定
file_name <- sprintf("./link.png")
png(file_name, width=700, height=700)

matplot(link_sum, xlim=c(0,TIME), type="l",lwd=3, xlab="Timestep",ylab="Link", col=1, lty=1)

#図の書き込み終了
dev.off()
##################################




###重心座標の移動距離の時間変化をグラフ化###
#全ノードの平均座標を重心座標とする
#Centroid = (1/all_node)*Σ(xi,yi)

Centroid <- matrix(0, nrow=TIME+1, ncol=2) #タイムステップごとの重心座標(x,y)
Distance <- numeric(TIME+1) #タイムステップごとの重心座標の移動距離

for(i in 1:TIME_1){
  
  node_status <- numeric(all_node) #ノードの存在(1),不在(0)を保存
  node_count <- 0 #ノード数を足しあげる

  #node_status[i,]の作成
  for(j in 1:all_link){
    if(D_archive[i,j]>0){ #リンクjが存在する場合
      
      node1 <- link_connection[j,1] #両端のノードを検出
      node2 <- link_connection[j,2] #両端のノードを検出
      
      node_status[node1] <- 1 #ノードの存在を保存
      node_status[node2] <- 1 #ノードの存在を保存
      
    }
  }
  
  for(j in 1:all_node){
    if(node_status[j]==1){
      Centroid[i,1] <- Centroid[i,1] + node_potision[j,1]
      Centroid[i,2] <- Centroid[i,2] + node_potision[j,2]
      node_count <- node_count+1
    }
  }
  
  Centroid[i,] <- Centroid[i,]/node_count #全ノード座標を平均し、重心座標を求める
  Distance[i] <- sqrt( Centroid[i,1]^2 + Centroid[i,2]^2 ) #d=sqrt(x^2+y^2)
    
}

#重心座標の移動距離の時間変化を描画
matplot(Distance, xlim=c(0,TIME), type="l",lwd=3, xlab="Timestep",ylab="Distance", col=1, lty=1)

#ネットワーク上に重心座標を描画する
#描画リセット
plot(0, 0, xlim=c(-horizontal , horizontal), ylim=c(-vertical, vertical), type="n", xlab="", ylab="", xaxt="n", yaxt="n")

#リンクの描画
for(i in 1:all_link){
    par(new=T)
    segments(link_potision[i,1], link_potision[i,2], link_potision[i,3], link_potision[i,4], xlim=c(-horizontal, horizontal), ylim=c(-vertical, vertical), xlab="", ylab="", lwd=1, col="black", lty=2)
  }

#中心ノードの描画
par(new=T)
plot(node_potision[1,1], node_potision[1,2], xlim=c(-horizontal, horizontal), ylim=c(-vertical, vertical), xlab="", ylab="", cex=1.5, lwd=2, pch=16, col="black")


#ノードの描画（ソースは赤,シンクは青,それ以外は黒で表示）
for(i in 1:all_node){
  par(new=T)
  plot(node_potision[i,1], node_potision[i,2], xlim=c(-horizontal, horizontal), ylim=c(-vertical, vertical), xlab="", ylab="", cex=0.7, lwd=2, pch=16, col="black")
}

#重心座標のプロット（黄色線）
for(i in 1:TIME_1){
  par(new=T)
  plot(Centroid[i,1], Centroid[i,2], xlim=c(-horizontal, horizontal), ylim=c(-vertical, vertical), xlab="", ylab="", cex=0.5, lwd=2, pch=16, col="yellow")
}

##################################


###密度の時間変化をグラフ化###
#Density = (存在するリンクの数)/(接続可能なリンクの数)

link_possible <- matrix(0, nrow=TIME+1, ncol=all_link) #タイムステップごとの接続可能リンクの保存(可能:1, 不可能:0)
link_possible_sum <- numeric(TIME+1) #タイムステップごとの接続可能リンクの総数
link_sum <- numeric(TIME+1) #タイムステップごとの存在しているリンクの総数

for(i in 1:TIME_1){ #タイムステップiにおいて(実際はi-1)
  
  for(j in 1:all_link){
    if(D_archive[i,j]>0){ #リンクjが存在する場合
      node1 <- link_connection[j,1] #両端のノードを検出
      node2 <- link_connection[j,2] #両端のノードを検出
      
      for(k in 1:6){ #両端のノードに隣接するリンクを接続可能リンクとして保存
        if(node_connection[node1,k]!=0)  link_possible[i,node_connection[node1,k]] <- 1
        if(node_connection[node2,k]!=0)  link_possible[i,node_connection[node2,k]] <- 1
      }
      
      link_sum[i] <- link_sum[i]+1 #リンクjを存在するリンクの数にカウント
      
    }
  }
  
  for(j in 1:all_link){ #接続可能リンクの総数を算出する
    if(link_possible[i,j]==1) link_possible_sum[i] <- link_possible_sum[i]+1 
  }
  
}

Density <- link_sum/link_possible_sum

matplot(Density, xlim=c(0,TIME), type="l",lwd=3, xlab="Timestep",ylab="Density", col=1, lty=1)

##################################



###メッシュ度計算###
node_sum <- numeric(TIME+1)

for(i in 1:TIME_1){
  for(j in 1:all_node){
    if(node_archive[i,j]==1) node_sum[i] <- node_sum[i]+1
  }
}

link_sum <- numeric(TIME+1)

for(i in 1:TIME_1){
  for(j in 1:all_link){
    if(D_archive[i,j]>0) link_sum[i] <- link_sum[i]+1
  }
}

mesh <- numeric(TIME+1)

for(i in 1:TIME_1){
  mesh[i] <- (link_sum[i]-node_sum[i]+1)/(2*node_sum[i]-5)
}

matplot(mesh, xlim=c(0,TIME), ylim=c(0,1), type="l",lwd=3, xlab="Timestep",ylab="Mesh", col=1, lty=1)



###平均次数K###############
K <- numeric(TIME_1)

for(i in 1:TIME_1){
  
  #node_status[i,]の作成
  node_status <- numeric(all_node)
  for(j in 1:all_link){
    if(D_archive[i,j]>0){ #リンクjが存在する場合
      
      node1 <- link_connection[j,1] #両端のノードを検出
      node2 <- link_connection[j,2] #両端のノードを検出
      
      node_status[node1] <- 1 #ノードの存在を保存
      node_status[node2] <- 1 #ノードの存在を保存
      
    }
  }
  
  K_sum <- 0
  node_sum <- 0
  
  for(j in 1:all_node){
    #次数足し上げ
    if(node_status[j]==1){
      node_sum <- node_sum+1
      
      for(k in 1:6){
        num <- node_connection[j,k]
        if(D_archive[i,num]>0 && num!=0) K_sum <- K_sum+1
      }
    }
  }
  K[i] <- K_sum/node_sum
}

plot(K)

##########################




###媒介中心性　最大値#######
bw_max2 <- numeric(TIME_1)

for(i in 1:TIME_1){
    for(j in 1:all_node){
      if(bw_max2[i] < bw_archive[i,j])
        bw_max2[i] <- bw_archive[i,j]
  }
}

plot(bw_max2, ylim=c(0,1), type="l", las=1, xlab="", ylab="")

#
x1 <- c(0:2000)
y1 <- -0.08*log(x1)+1
par(new=T)
plot(x1,y1, ylim=c(0,1), type="l", las=1, xlab="", ylab="", col="red")


x2 <- c(0:2000)
y2 <- -0.12*log(x1)+1
par(new=T)
plot(x2,y2, ylim=c(0,1), type="l", las=1, xlab="", ylab="", col="blue")

labels=c("ソース", "a=0.09", "a=0.12")
cols=c("black","red","blue")
legend("topright", legend = labels, col = cols, lty=1)