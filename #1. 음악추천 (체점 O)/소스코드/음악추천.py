class Date():
    month = "0 Jen Feb Mar Apl May Jun Jly Aug Sep Oct Nov Dec".split()
    #  Wed Nov 04 2020 08:14:50 GMT+0900 (GMT+09:00)
    
    def __init__(self, *string):

        if len(string)==1:
            a = str(string).split()
            self.y, self.m, self.d, self.h, self.mi, self.s = tuple(
                map(int, (a[3], Date.month.index(a[1]), a[2], a[4][0:2], a[4][3:5], a[4][6:])))
        else: self.y, self.m, self.d, self.h, self.mi, self.s = string

    def text(s):
        return "%d-%02d-%02d %02d:%02d:%02d" % (s.y, s.m, s.d, s.h, s.mi, s.s)

    def __int__(s):
        return int("%d%02d%02d%02d%02d%02d"%(s.y, s.m, s.d, s.h, s.mi, s.s))
    
    def is_same_play(self,d1,d2):
        def d2min(d): return d.h*60+d.mi
    
        if d1==0 or d2==0: return True
        elif d1.d==d2.d and abs(d2min(d1)-d2min(d2))<30 : return True # 30분 이내에 들었으면, 참을 반환.
        else: return False
    
import csv

f=open('log.csv', encoding='UTF8')
sl=[]
totol_list=[]
r=csv.reader(f)

def c_name(name):
    return name.replace('.mp3','')
                

for i in r:
    totol_list.append([Date(i[0]),c_name(i[1])])
    a=Date(i[0])
    sl.append(c_name(i[1]))

# 간단하게 곡별 재생횟수를 찍을 수 있음.
def song_each(sl,if_print=False):
    ssl=set(sl)
    d=[] # 곡별 재생횟수가 담김
    for i in ssl:
        d.append([i,sl.count(i)])
    d.sort(key=lambda x:-x[1])
    if if_print:
        for i in d: print(*i[::-1])
    return d

song_each(sl) #각 재생 목록을 확인해보는 코드

class Album:
    def __init__(self,al_name):
        self.album=al_name
        
    def print_info(self):
        print('album',self.al_name)
        
class Song(Album): #엘범 정보를 상속
    __s_dict={}
    
    def __init__(self,name): # 재정의
        l = name.split('/')
        
        super().__init__('' if len(l)==1 else l[0])
        self.name=name if len(l)==1 else l[1];
        self.nodes=[] # 연관된 것들!
        #self.list=eval(str([[]]*5))
        #self.list_max=5
        Song.__s_dict[name]=self
        
        
    def next_node(self,line,th): #일종의 node를 추가하기
        self.nodes.append({'line':line,'th':th})
        
    def print_info(self):
        print('name:',self.name)
        
    def get_song(self,name):
        if name in Song.__s_dict: return Song.__s_dict[name]
        else: return False
    

class Song_line(): 
    lines=[]
    def __init__(self,line):
        self.line=line
        Song_line.lines.append(self)
        
        for i in range(len(line)):
            name = line[i][1] #이름이 저장된 것을 꺼내옴
            Song.get_song(0,name).next_node(self,i)#이 line과 Song 클래스를 연결
            
    def get(self,th):
        if len(self.list)<=th or th<0: return False
        else: return self.list[th]




# 생성
for i in set(sl): Song(i)

# 그래프 생성
st_day=day=0
same_day_played=[]
for i in range(len(totol_list)):
    pre_day=day #전날 갱신
    day=totol_list[i][0]
    if not Date.is_same_play(0,day,pre_day): #같은 날이 아니면.
        Song_line(totol_list[st_day:i])
        day=0
        st_day=i
        
        
# 탐색
from math import exp
from random import random as rand

class Station(Song, Song_line): #관련도 분석을 위한 클래스이다. bfs에 맞게 구성되어있다. 
    stns=[]
    __stn_dict={} # 접근 방지를 위해 설정
    __total_p=0
    
    def get_p(self,deep,trans):
        if not trans: return 0
        
        return exp(-deep/5)*exp(-trans/3)
        
        
    def __init__(self,song_name,deep,trans): #song에는 Song이 들어감.
        if trans>6: return; # 재귀 방지를 위해 빨리 정리
        
        self.song_name=song_name
        self.deep=deep
        self.trans=trans
        self.p=Station.get_p(self,deep,trans)
        
        Station.__stn_dict[song_name]=True
        Station.stns.append(self)
        Station.__total_p+=self.p
        
    def in_this(self,name):
        return name in Station.__stn_dict
        
    def print_info(self):
        print('song_name',self.song_name, 'deep',self.deep, 'trans',self.trans, 'p',self.p)
         

    def initial(self,name): #연관도 분석을 실시하는 함수
        
        #초기화
        Station.stns=[]
        Station.__stn_dict={}
        Station.__total_p=0
        Station(name,0,0)
        
        #분석, 일종의 BFS 구현
        for st in Station.stns:
            #st.print_info()
            for line in Song.get_song(0,st.song_name).nodes: # 각각의 라인
                th=line['th']
                for i in range(len(line['line'].line)):
                    name = line['line'].line[i][1] #이름임
                    if i-th and not Station.in_this(0,name):
                        Station( name, abs(i-th)+st.deep+1, st.trans+1)
                        
                        
    def get_one(self=0): # 랜덤으로 가중평균해서 곡을 뽑아주는 함수
        r_i = rand()*Station.__total_p #결과값
        p_sum=0 #누적해서 찾자
        for i in Station.stns:
            p_sum+=i.p
            if r_i<p_sum: return i.song_name
        return False

        

    def rand_song(self,name):  #Station 클래스를 조작한다.
        print('분석요청',name)
        song=Song.get_song(0,name)
        if not song or not song.nodes:
            print("데이터가 부족합니다")
            return False

        Station.initial(0,name)
        return Station.get_one()
    

#Station.rand_song(0,input("분석할 노래를 입력: ")) #스탠딩 에그 - 오래된 노래






# 외부 서비스를 위해서, 웹서버 모듈을 갖고 왔다. 파이썬 내장 함수이다.
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse # url 디코딩

port=8080  # 내가 사용하는 다른 프로그램과 겹치지 않는 포트
class myHandler(BaseHTTPRequestHandler): # 오버라이딩 과정을 통해 함수를 만든다.
    def do_GET(self):
        data=Station.rand_song(0,parse.unquote(self.path[1:])) #받아오기
        print('결과',data)
        if not data:
            data="곡에 대한 정보가 부족합니다"
            self.send_response(404)
        else: self.send_response(200)
        self.send_header('Content-type','text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(data.encode())
        return

print('Server listening on localhost:'+str(port))
print("""위의 주소로 접속한 다음, 분석하고 싶은 노래 제목을 주소창에 치시면 본인(김영진) 취향에 맞는 노래가 반환됩니다. \n ex: "http://localhost:8080/beatles - i will\"""")
httpd = HTTPServer(('',port), myHandler) 
httpd.serve_forever() # 서버 가동시키기

