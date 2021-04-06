#include "pch.h"
#include <stdio.h>
#include <stdlib.h>
#define _USE_MATH_DEFINES
#include <math.h>

#define H 5000											//�摜�̃s�N�Z�����ݒ�
#define W 5000											//���̃T�C�Y���傫���Ȃ邱�Ƃ͂قږ����̂Ŋ�{������Ȃ��ėǂ����A����Ȃ��ꍇ�͍Đݒ肷��
#define NODE_MAX 25000									//�m�[�h���ő�l�ݒ�B�������ɓ���
#define BUFMAX 128
#define INF 1000000
#define SIZEMIN 168
#define SIZEMAX 245
#define LINK_MAX 20000

/* �����N�����i�[����\���� */
struct data{
	int start_x;
	int start_y;
	int end_x;
	int end_y;
	int length;
	int width;
};
struct data linkscan[LINK_MAX];//������

/* �����珇�ɁA���������A�ǌa���A�t���O���A���i�[����z��*/
int net[H][W], width[H][W], flag[H][W];

/* �G���[�����t��fopen */
FILE *my_fopen(const char *file, const char *mode){
	FILE *fp;
	errno_t error;
	
	if((error = fopen_s(&fp,file, mode)) != 0){
		fprintf(stderr, "\"%s\" open error!\n", file);
		exit(EXIT_FAILURE);
	}

	return fp;
}

/* �G���[�����t��fclose */
int my_fclose(FILE *fp){
	int ret;
	
	ret = fclose(fp);
	if(ret == EOF){
		fprintf(stderr, "file close error!\n");
		exit(EXIT_FAILURE);
	}
	
	return ret;
}

/*����̃s�N�Z���̔ԍ��t��*/
void number_around(int x, int y, int l[][2]){

	l[0][0]=net[x][y+1];
	l[1][0]=net[x-1][y+1];
	l[2][0]=net[x-1][y];
	l[3][0]=net[x-1][y-1];
	l[4][0]=net[x][y-1];
	l[5][0]=net[x+1][y-1];
	l[6][0]=net[x+1][y];
	l[7][0]=net[x+1][y+1];

	l[0][1]=flag[x][y+1];
	l[1][1]=flag[x-1][y+1];
	l[2][1]=flag[x-1][y];
	l[3][1]=flag[x-1][y-1];
	l[4][1]=flag[x][y-1];
	l[5][1]=flag[x+1][y-1];
	l[6][1]=flag[x+1][y];
	l[7][1]=flag[x+1][y+1];

}

/*����ɖ������̃s�N�Z�������邩�ǂ������`�F�b�N*/
int scan_around(int x, int y){
	int n;
	int a=0;
	int l[8][2]={0};

	number_around(x,y,l);

	for(n=0;n<8;n++){
		if(l[n][0]!=0 && l[n][1]==0) a++;
	}
	
	return a;
}

/*�m�[�h,�����N����̃m�[�h�̍��W�𓾂�xy�ɓ���ĕԂ�*/
void get_node_coordinates(int x,int y,int a,int xy[]){
	int i,n=0;
	int l[8][2],m[8];

	number_around(x,y,l);

	for(i=0;i<8;i++)	m[i]=0;

	//�w�肳�ꂽCN���������̃s�N�Z����T���A���Ă͂܂���̂������m[]���P�Ƃ���
	for(i=0;i<8;i++){	
		if(l[i][0]==a && l[i][1]==0){
			m[i]=1;
			n++;
		}
	}

	/*�G���[�`�F�b�N(�w�肳�ꂽCN�̃s�N�Z������ȏ�̎��̏���)*/
	if(n>1){
		for(i=0;i<8;i++){
			if(m[i]!=0 && (i%2)==1) m[i]=0;		//�㉺���E(�ԍ��t�ł͋����̂���)�ɂ�����̂�D��
		}
		n=1;
	}

	/*�ʏ�̏���*/
	if(n==1){

			 if(m[0]==1){xy[0] = x;	xy[1] = y+1;}
		else if(m[1]==1){xy[0] = x-1;	xy[1] = y+1;}
		else if(m[2]==1){xy[0] = x-1;	xy[1] = y;}
		else if(m[3]==1){xy[0] = x-1;	xy[1] = y-1;}
		else if(m[4]==1){xy[0] = x;	xy[1] = y-1;}
		else if(m[5]==1){xy[0] = x+1;	xy[1] = y-1;}
		else if(m[6]==1){xy[0] = x+1;	xy[1] = y;}
		else if(m[7]==1){xy[0] = x+1;	xy[1] = y+1;}

	}
	else if(n==0){
		xy[0] = x;	xy[1] = y;
	}

/*����Ɏw�肳�ꂽCN�̃s�N�Z�����Ȃ��ꍇ�A���̍��W��Ԃ�*/
}

/*�m�[�h,�����N����̃����N�̍��W�𓾂�xy�ɓ���ĕԂ�*/
void get_link_coordinates(int x,int y,int a,int xy[]){
	int n=0;
	int l[8][2];

	number_around(x,y,l);

	//�������̂��̂����ɃX�L�����B�����ςł���΃X�L�b�v
	do{
		if(l[n%8][0]==a && l[n%8][1]==0)	break;
		else n++;

		if(l[(n+1)%8][1]==1) n+=2;

	}while(n<8);

		 if(n==0){xy[0] = x;	xy[1] = y+1;}
	else if(n==1){xy[0] = x-1;	xy[1] = y+1;}
	else if(n==2){xy[0] = x-1;	xy[1] = y;}
	else if(n==3){xy[0] = x-1;	xy[1] = y-1;}
	else if(n==4){xy[0] = x;	xy[1] = y-1;}
	else if(n==5){xy[0] = x+1;	xy[1] = y-1;}
	else if(n==6){xy[0] = x+1;	xy[1] = y;}
	else if(n==7){xy[0] = x+1;	xy[1] = y+1;}
	else         {xy[0] = x;	xy[1] = y;}

/*����Ɏw�肳�ꂽCN�̃s�N�Z�����Ȃ��ꍇ�A���̍��W��Ԃ�*/
}

/*���[�v�\���̏����B�A���S���Y����get_node_coordinates�Ɠ��l�����A�����ς̏ꍇ�ł��ǂݎ��B*/
void process_loop(int x, int y, int xy[]){
	int i,n=0;
	int l[8][2],m[8];

	number_around(x,y,l);

	for(i=0;i<8;i++)	m[i]=0;

	for(i=0;i<8;i++){	
		if(l[i][0]==4){
			m[i]=1;
			n++;
		}
	}

	if(n==0){
		for(i=0;i<8;i++){
			if(l[i][0]==3)	m[i]=1;
		}
			 if(m[0]==1){xy[0] = x;	xy[1] = y+1;}
		else if(m[1]==1){xy[0] = x-1;	xy[1] = y+1;}
		else if(m[2]==1){xy[0] = x-1;	xy[1] = y;}
		else if(m[3]==1){xy[0] = x-1;	xy[1] = y-1;}
		else if(m[4]==1){xy[0] = x;	xy[1] = y-1;}
		else if(m[5]==1){xy[0] = x+1;	xy[1] = y-1;}
		else if(m[6]==1){xy[0] = x+1;	xy[1] = y;}
		else if(m[7]==1){xy[0] = x+1;	xy[1] = y+1;}
	}

	else{
			 if(m[0]==1){xy[0] = x;	xy[1] = y+1;}
		else if(m[1]==1){xy[0] = x-1;	xy[1] = y+1;}
		else if(m[2]==1){xy[0] = x-1;	xy[1] = y;}
		else if(m[3]==1){xy[0] = x-1;	xy[1] = y-1;}
		else if(m[4]==1){xy[0] = x;	xy[1] = y-1;}
		else if(m[5]==1){xy[0] = x+1;	xy[1] = y-1;}
		else if(m[6]==1){xy[0] = x+1;	xy[1] = y;}
		else if(m[7]==1){xy[0] = x+1;	xy[1] = y+1;}
	}
}

/*�X�L�������̌v�Z*/
void add_length_width(int X, int Y,int I, int J,int m){
	int buf1,buf2;

	flag[X][Y]=1;

	/* �ǌa�𑫂��B�l�b�g���[�N�̑̐ς��Z�o����ꍇ�͂����Ŋǌa���悵�đ����Ă��� */
//	linkscan[m].width += width[X][Y] * width[X][Y];
	linkscan[m].width += width[X][Y];

	/*�����𑫂�*/
	/*�΂߂ɓ������ꍇ*/
	buf1 = (I+X)%2;
	buf2 = (J+Y)%2;
	if(buf1==1 && buf2==1)	linkscan[m].length += 1;	//�΂߂ɓ������ꍇ�A�O��̍��W�𑫂���x�Ay�Ƃ��Ɋ�ɂȂ邱�Ƃ𗘗p
	/*����ȊO�i�c���j*/
	else linkscan[m].length += 1;
}

/*�m�[�h(1,3,4)���Ȃ������X�L�����A�����N(2)������ꍇ�͌J��Ԃ�*/
void scan_while(int *X,int *Y,int *I,int *J,int m){
	int xy[2];

	while(1){
			get_node_coordinates(*X,*Y,4,xy);
			*I=xy[0];
			*J=xy[1];
	
			if(*I==*X && *J==*Y){
				get_node_coordinates(*X,*Y,3,xy);
				*I=xy[0];
				*J=xy[1];
	
				if(*I==*X && *J==*Y){
					get_node_coordinates(*X,*Y,1,xy);
					*I=xy[0];
					*J=xy[1];
	
					if(*I==*X && *J==*Y){
						get_link_coordinates(*X,*Y,2,xy);
						*I=xy[0];
						*J=xy[1];

						if(*I==*X && *J==*Y){	//���[�v�\���̔���B���[�v�ł���Ύn�_�ƏI�_�������ł��邽�ߏI�_�������ςƂȂ��Ă���A�X�L�������ł���ɂ��ւ�炸�A�ǂ�CN��������Ȃ����ƂɂȂ�
							process_loop(*X,*Y,xy);
							*I=xy[0];
							*J=xy[1];

							add_length_width(*X,*Y,*I,*J,m);

							linkscan[m].end_x=*I;
							linkscan[m].end_y=*J;
							break;
						}

						else{
							add_length_width(*X,*Y,*I,*J,m);

							*X=*I;
							*Y=*J;

							continue;
						}
					}
					else {
						add_length_width(*X,*Y,*I,*J,m);
						flag[*I][*J]=1;
						linkscan[m].end_x=*I;
						linkscan[m].end_y=*J;
						break;
					}
				}
				else {
					add_length_width(*X,*Y,*I,*J,m);
					linkscan[m].end_x=*I;
					linkscan[m].end_y=*J;
					break;
				}
			}
			else {
				add_length_width(*X,*Y,*I,*J,m);
				linkscan[m].end_x=*I;
				linkscan[m].end_y=*J;
				break;
			}
		}
}

/*�X�L�������s*/
int scan(int x,int y,int m){
	int X,Y,I,J;

	/*�C�ӂ̃s�N�Z���̎��肪�������̊ԑ�����*/
	while(scan_around(x,y) != 0){
		X=x;
		Y=y;

		scan_while(&X,&Y,&I,&J,m);

		linkscan[m].start_x=x;
		linkscan[m].start_y=y;
		m++;

		/*�P�ƂR�ƂS�̊Ԃ̈ړ��̏ꍇ*/
		if(net[X][Y]==1 && net[I][J]==1)	break;
		if(net[X][Y]==1 && net[I][J]==3)	break;
		if(net[X][Y]==1 && net[I][J]==4)	break;
		if(net[X][Y]==3 && net[I][J]==1)	break;
		if(net[X][Y]==3 && net[I][J]==3)	break;
		if(net[X][Y]==3 && net[I][J]==4)	break;
		if(net[X][Y]==4 && net[I][J]==1)	break;
		if(net[X][Y]==4 && net[I][J]==3)	break;
		if(net[X][Y]==4 && net[I][J]==4)	break;

	}

	return m;

}

int LinkScan(char rfile[],char wfile[]){
	int i,j,m=0,x,y,cn,wid;
	FILE *fp;
	char buff[BUFMAX];

	/*�t�@�C���ǂݍ���*/
	fp = my_fopen(rfile,"r");
		while( (fgets(buff,BUFMAX,fp) != NULL) ){
		sscanf_s(buff,"%d %d %d %d",&x,&y,&cn,&wid,sizeof(buff));
		net[x][y]=cn;
		width[x][y]=wid;
	}
	my_fclose(fp); 

	/*�m�[�h�𑖍��A���W�𓾂�B����ɖ�����������΃X�L�����J�n*/
	for(j=0;j<W;j++){
		for(i=0;i<H;i++){
			if(net[i][j]==0 || net[i][j]==2)	continue;

			if(scan_around(i,j) == 0) continue;
			else{
				m = scan(i,j,m);
			}
		}
	}

	/*�����f�[�^�̏����o��*/	
	fp = my_fopen(wfile,"w");
	for(i=0;i<m;i++){
		//���e�F�n�_�̍��W(x�Ay) �I�_�̍��W(x�Ay)�@�ǒ�(pixel)�@�ǌa��f�l�̍��v
		fprintf(fp,"%d	%d	%d	%d	%d	%d\n",linkscan[i].start_x,linkscan[i].start_y,linkscan[i].end_x,linkscan[i].end_y,linkscan[i].length,linkscan[i].width);
	}
	my_fclose(fp);
	
	return m;

}


/*�m�[�h�ԍ��𓾂�֐�*/
int get_node_num(int n,int x, int y,int node[]){
	int k;

	for(k=0;k<n;k++){
		if (node[k * 3 + 0] == x && node[k * 3 + 1] == y)	break;
	}

	return k;
}

/*�X�L�������s*/
void scan_connection(int m, int n, int x, int y, int new_cnt[],int node[]){
	int i,j,k,l,p,q,a,cnt=0,*dist;
	int tmp_x, tmp_y, next_x, next_y;
	int	new_dist=0;

	dist = calloc(n, sizeof(int));
	for(i=0;i<n;i++)	dist[i] = INF;	//�m�[�h�̎n�_����̍ŒZ��������INF�ŏ�����

	k = get_node_num(n,x,y,node);
	dist[k] = 0;						//�n�_���O�Ƃ��ĊJ�n

	while(1){
		a = 0;

		for(j=0;j<n;j++){

			tmp_x = node[j*3+0];
			tmp_y = node[j*3+1];

			if(dist[j]==INF)	continue;	//���X�L�����̏ꍇ�X�L�b�v�A��ɖ߂��Ă���B
			for(i=0;i<m;i++){				//�_�C�N�X�g���@�̃A���S���Y���Ŏn�_����e�m�[�h�ւ̍ŒZ�������v�Z
				if(tmp_x==linkscan[i].start_x && tmp_y==linkscan[i].start_y){
					next_x = linkscan[i].end_x;
					next_y = linkscan[i].end_y;

					k = get_node_num(n,tmp_x,tmp_y,node);
					new_dist = dist[k] + linkscan[i].length;

					l = get_node_num(n,next_x,next_y,node);
					if(new_dist < dist[l]){
						dist[l] = new_dist;
						a=1;				//�ύX���������ꍇ�t���O�ύX
					}
				}
				else if(tmp_x==linkscan[i].end_x && tmp_y==linkscan[i].end_y){		//���̕����͌��f�[�^�̓s����A�ꍇ�������Ă���
					next_x = linkscan[i].start_x;
					next_y = linkscan[i].start_y;

					k = get_node_num(n,tmp_x,tmp_y,node);
					new_dist = dist[k] + linkscan[i].length;

					l = get_node_num(n,next_x,next_y,node);
					if(new_dist < dist[l]){
						dist[l] = new_dist;
						a=1;
					}
				}
			}
		}

		if(a==0)	break;					//�ύX���Ȃ���ΏI��
	}

	//�N���X�^�[�T�C�Y(�m�[�h��)�ƒ[�_�������߂�B�e�m�[�h�ɑ΂��āA�n�_����̋�����񂪍X�V����Ă����cnt++
	for(i=0;i<n;i++){
		tmp_x = node[i*3+0];
		tmp_y = node[i*3+1];

		if(net[tmp_x][tmp_y] != 2 && dist[i] != INF){
			new_cnt[0]++;
		}

		if(net[tmp_x][tmp_y] == 1 && dist[i] != INF){
			new_cnt[1]++;
			node[i*3+2] = 1;
		}
	}

	//�̐ς̏��B�ǌa^2�̑��a�𑫂��Ă���
	for (i = 0; i < m; i++){
		p = get_node_num(n, linkscan[i].start_x, linkscan[i].start_y,node);
		q = get_node_num(n, linkscan[i].end_x, linkscan[i].end_y,node);

		if (dist[p] != INF && dist[q] != INF){
			new_cnt[2] += linkscan[i].width;
		}
	}

	free(dist);

}

/*�����w���ƘA���w�������߂�֐�*/
void Connection(int m,int k,int result[][3], char wfile[]){
	int i, j, x, y, n = 0, new_cnt[3] = { 0 }, cnt[3] = { 0 },*node;
//	double r=0,w=0,new_w=0;
//	double new_r,p;
//	int x1,x2,y1,y2,
//	char wfile[128] = WRITE_FILE_NAME_2;
//	FILE *fp;

	//�z��node�̊m��
	for (j = 0; j<W; j++){
		for (i = 0; i<H; i++){
			if (net[i][j] == 2 || net[i][j] == 0) continue;
			else	n++;
		}
	}
	node = calloc(n * 3, sizeof(int));

	//�m�[�h�̔ԍ��t��
	n = 0;
	for(j=0;j<W;j++){
		for(i=0;i<H;i++){
			if(net[i][j]==2 || net[i][j]==0) continue;
			else{
				node[n*3+0] = i;
				node[n*3+1] = j;
				n++;
			}
//			if(net[i][j]==1)endpoint++;
		}	
	}

//	if(n>NODE_MAX){
//		printf("n = %d	Error! NODE_MAX size too small.",n);
//		exit(EXIT_FAILURE);
//	}

//	fp = my_fopen(wfile,"w");

//	for(i=0;i<m;i++){
//		r = 0;
//		l = linkscan[i].length;
//		w = linkscan[i].width / (double)l;

			for(j=0;j<n;j++){
				new_cnt[0] = 0;
				new_cnt[1] = 0;
				new_cnt[2] = 0;

				if(node[j*3+2]==1)	continue;	//�X�L�����ς݂̏ꍇ�X�L�b�v

				x = node[j*3+0];
				y = node[j*3+1];

				if (net[x][y] == 1){
					scan_connection(m, n, x, y, new_cnt,node);
					if (new_cnt[0]>cnt[0]){
						//�ő�N���X�^�[�̏��̋L���B
						cnt[0] = new_cnt[0];	//cluster
						cnt[1] = new_cnt[1];	//endpoint
						cnt[2] = new_cnt[2];	//volume(width^2)
					}
//					new_cnt = scan_connection(m,n,x,y);
//					new_r = ((double)cnt / (double)endpoint) * 100;		//�S�̂ɂ�����䗦�̌v�Z
//					if(new_cnt>cnt)	cnt = new_cnt;								//�ő�̂��݂̂̂�\��	
//					fprintf(fp,"%d\n",cnt);
				}
			}
//			linkscan[i].start_x = x1;
//			linkscan[i].start_y = y1;
//			linkscan[i].end_x = x2;
//			linkscan[i].end_y = y2;

//			for(j=0;j<n;j++)	node[j][2]=0;
//			p = (double)i/(double)m * 100;
//			printf("Now Scanning...	%6.2f %%\n",p);
//		}
//	}

//	my_fclose(fp);

//	return cnt;
//	return w;
			//���ʂ�Ԃ�
			result[k][0] = cnt[0];
			result[k][1] = cnt[1];
			result[k][2] = cnt[2];

			free(node);
}

/*���b�V���x�̌v�Z������֐�*/
//double Meshedness(int m){
//	int i,j,n=0,f,f_max;
//	double M;

//	for(j=0;j<W;j++){
//		for(i=0;i<H;i++){
//			if(net[i][j]==2 || net[i][j]==0) continue;
//			else	n++;
//		}	
//	}
//	if (m == 0){
//		M = 0.0;
//	}
//	else{
//		f = m - n + 1;
//		f_max = 2 * n - 5;
//		M = (double)f / (double)f_max;
//	}

//	return M;

//}

/*�n�_����̊K�w���v�Z����֐�*/
void ClassCount(int m, int x, int y,char wfile[]){
	int i, j, k, l, a, n = 0,*node,*dist;
	int tmp_x, tmp_y, next_x, next_y;
	int	new_dist = 0;
	FILE *fp;

	//�z��node�̊m��
	for (j = 0; j<W; j++){
		for (i = 0; i<H; i++){
			if (net[i][j] == 2 || net[i][j] == 0) continue;
			else	n++;
		}
	}
	node = calloc(n * 3, sizeof(int));
	dist = calloc(n, sizeof(int));

	//�m�[�h�̔ԍ��t��
	n = 0;
	for (j = 0; j<W; j++){
		for (i = 0; i<H; i++){
			if (net[i][j] == 2 || net[i][j] == 0) continue;
			else{
				node[n * 3 + 0] = i;
				node[n * 3 + 1] = j;
				n++;
			}
		}
	}

	//������
	for (i = 0; i < n; i++)	dist[i] = INF;			//�m�[�h�̎n�_����̍ŒZ��������INF�ŏ�����
	k = get_node_num(n, x, y, node);
	dist[k] = 0;						//�n�_���O�Ƃ��ĊJ�n

	//�_�C�N�X�g���@�ɂ�鋗�����Z
	while (1){
		a = 0;

		for (j = 0; j<n; j++){

			tmp_x = node[j*3+0];
			tmp_y = node[j*3+1];

			if (dist[j] == INF)	continue;	//���X�L�����̏ꍇ�X�L�b�v�A��ɖ߂��Ă���B
			for (i = 0; i<m; i++){				//�_�C�N�X�g���@�̃A���S���Y���Ŏn�_����e�m�[�h�ւ̍ŒZ�������v�Z
				if (tmp_x == linkscan[i].start_x && tmp_y == linkscan[i].start_y){
					next_x = linkscan[i].end_x;
					next_y = linkscan[i].end_y;

					k = get_node_num(n, tmp_x, tmp_y,node);
					new_dist = dist[k] + 1;

					l = get_node_num(n, next_x, next_y,node);
					if (new_dist < dist[l]){
						dist[l] = new_dist;
						a = 1;				//�ύX���������ꍇ�t���O�ύX
					}
				}
				else if (tmp_x == linkscan[i].end_x && tmp_y == linkscan[i].end_y){		//���̕����͌��f�[�^�̓s����A�ꍇ�������Ă���
					next_x = linkscan[i].start_x;
					next_y = linkscan[i].start_y;

					k = get_node_num(n, tmp_x, tmp_y,node);
					new_dist = dist[k] + 1;

					l = get_node_num(n, next_x, next_y,node);
					if (new_dist < dist[l]){
						dist[l] = new_dist;
						a = 1;
					}
				}
			}
		}

		if (a == 0)	break;					//�ύX���Ȃ���ΏI��
	}

	fp = my_fopen(wfile, "w");
	for (j = 0; j < n; j++){
		tmp_x = node[j*3+0];
		tmp_y = node[j*3+1];
		if (net[tmp_x][tmp_y] == 1){
			fprintf(fp, "%d	%d	%d\n", tmp_x,tmp_y,dist[j]);
		}
	}
	my_fclose(fp);
	free(node);
	free(dist);
}

int main(void){
	int i,k,l,m=0,n,e,v;	//m:�����N�̑����ɑ�������l
	char rfile[75],wfile[75]="mesh.txt",wfile_n[75]="node.txt",wfile_e[75]="edge.txt";	//�o�̓t�@�C����
	double mesh[SIZEMAX - SIZEMIN + 1];		//���b�V���x
	int edge[SIZEMAX - SIZEMIN + 1];			//�}��
	int nodes[SIZEMAX - SIZEMIN + 1];			//�m�[�h��
	int size = SIZEMAX - SIZEMIN + 1;		//�J��Ԃ���
//	int st = 1400, art = 388;	//�n�_�̍��W�L�q
	FILE *fp;
//	int result[100][3];		//�ő�N���X�^�[���
	int cnt[75];		//�����w�����

		for(i=SIZEMIN;i<=SIZEMAX;i++){

			//������
			for(k=0;k<W;k++){
				for(l=0;l<H;l++){
					net[l][k]=0;
					width[l][k]=0;
					flag[l][k]=0;
				}
			}
			for(k=0;k<LINK_MAX;k++){
				linkscan[k].start_x=0;
				linkscan[k].start_y=0;
				linkscan[k].end_x=0;
				linkscan[k].end_y=0;
				linkscan[k].length=0;
				linkscan[k].width=0;
			}
			n = 0;
			e = 0;
			v = 0;

			//���̓t�@�C�����L�q
			sprintf_s(rfile,sizeof(rfile),"I:\\Picures\\network_analysis\\2019_05_19_%d.txt",i);
//			sprintf_s(wfile1,sizeof(wfile1),"Linkscan_result_2019_05_19_%d.txt",i);
//			sprintf_s(wfile2,sizeof(wfile2),"Connection_result_1510oat_101213_rnd_%d.txt",i);

			//�X�L�������s
			m = LinkScan(rfile,wfile);					//�}���̎擾

//			Connection(m,i-1,result,wfile2);			//�Ȃ�����̎擾

//			mesh[i-1] = Meshedness(m);					//���b�V���x�̎擾

			edge[i-1] = m;								//�}��

//			ClassCount(m, st, art, wfile_c);			//�K�w���̎擾

			//�c���m�[�h���A�[�_���A�̐ς𐔂���
			for(k=0;k<W;k++){
				for(l=0;l<H;l++){
					if (net[l][k] == 1 || net[l][k] == 3 || net[l][k] == 4) n++;
					if (net[l][k] == 1) e++;
				}	
			}
//			for (k = 0; k < m; k++){ v += linkscan[k].width; }

			nodes[i - 1] = n;
//			cnt[i-1] = n;
//			cnt[i-1][1] = e;
//			cnt[i-1][2] = v;

			//�i�s�󋵕\��
			printf("%d %%...\n",i);
		}

/**************************���ʏo��*******************************/
/*
//�A���w���p
		fp = my_fopen(wfile,"w");

		for(i=0;i<max;i++){
			//�m�[�h���A�[�_���A�ǌa^2���v
			fprintf(fp,"%d %d %d\n",result[i][0],result[i][1],result[i][2]);
		}

		my_fclose(fp);


//�����w���p
		fp = my_fopen(wfile_c, "w");

		for (i = 0; i<max; i++){
			//�m�[�h���A�[�_���A�ǌa^2���v
			fprintf(fp, "%d %d %d\n", cnt[i][0], cnt[i][1], cnt[i][2]);
		}

		my_fclose(fp);
*/

//���b�V���x�p
//		fp = my_fopen(wfile,"w");

//		for(i=0;i<max;i++){
//			fprintf(fp,"%f\n",mesh[i]);
//		}

//		my_fclose(fp);

//�}���p
		fp = my_fopen(wfile_e, "w");

		for (i = 0; i<max; i++){
			fprintf(fp, "%d\n", edge[i]);
		}

		my_fclose(fp);

//�m�[�h���p
		fp = my_fopen(wfile_n, "w");

		for (i = 0; i<max; i++){
			fprintf(fp, "%d\n", nodes[i]);
		}

		my_fclose(fp);

	return 0;

}