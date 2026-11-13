import os,json
from urllib.request import*
U=os.getenv('MAKEFUN_ENV_URL')
def p(a,b):return json.load(urlopen(U+a,json.dumps(b).encode()))
V=0,100,320,330,500,900,0
P=[ord(c)*5-375 for c in'KKKKUUUUMMOQLLMPKKKOLJIKLMMGKKKKACEECGKKEKMNELNOEKNOELMNCGKLACEEGIIIIKKKIKLMILLMIKMMIMMMILKKGIII'+'KKKKLMMM'+'JKKK'*5+'KKKL'+'GIIJIKKKIKLLJKLLKKLLILLLIKLKGIIJ'+'ECCA'*4+'GEECIGGGOOKKOQMK']
A=(-33,-31,-18,-14,14,18,31,33);D=(-17,-15,15,17);O=(-16,-1,1,16);G=D+O;J=(0,1,2,3,3,2,1,0)
Y={4:3,116:12,0:2,7:1,112:8,119:4}
H={};I=1e5;E=1e6
class AB(Exception):pass
def q(s):return chr(97+s%8)+str(s//16+1)
def y(m):return q(m[0])+q(m[1])+('','x','n','b','r','q')[m[2]]
def F(f):
 global B,T,C,W,X,S
 w=f.split();B=[0]*128;S=[]
 s=112
 for ch in w[0]:
  if ch=='/':s-=24
  elif'/'<ch<':':s+=int(ch)
  else:B[s]=' PNBRQK'.index(ch.upper())*((ch<'a')*2-1);s+=1
 T=1-2*(w[1]=='b')
 C=sum((c in w[2])<<i for i,c in enumerate('KQkq'))
 W=B.index(6);X=B.index(-6)
def z(s,by):
 b=B
 for o,p in(((-15*by,-17*by),1),(A,2),(G,6)):
  for d in o:
   t=s+d
   if not t&0x88 and b[t]==by*p:return 1
 for o,p,q in((D,3,5),(O,4,5)):
  for d in o:
   t=s+d
   while not t&0x88:
    if b[t]:
     if b[t]in(by*p,by*q):return 1
     break
    t+=d
 return 0
def g(cap):
 ms=[];ap=ms.append;b=B;w=T
 def h(s,t):
  if(t>>4)==7*(T>0):
   for q in(5,4,3,2):ap((s,t,q))
  else:ap((s,t,0))
 for s,p in enumerate(b):
  if p*w<=0:continue
  a=abs(p)
  if a==1:
   d=16*w;t=s+d
   if not b[t]:
    if(t>>4)==7*(w>0):h(s,t)
    elif not cap:
     ap((s,t,0))
     if(s>>4)==1+5*(w<0)and not b[s+2*d]:ap((s,s+2*d,0))
   for t in(s+d-1,s+d+1):
    if not t&0x88 and b[t]*w<0:h(s,t)
  else:
   for d in(A,D,O,G,G)[a-2]:
    t=s+d
    while not t&0x88:
     if b[t]:
      if b[t]*w<0:ap((s,t,0))
      break
     if not cap:ap((s,t,0))
     if a%4==2:break
     t+=d
 if not cap:
  ks=4+112*(w<0)
  for msk,sgn in((1,1),(2,-1)):
   if C&msk<<2*(w<0)and not(z(ks,-w)or z(ks+sgn,-w))and not(b[ks+sgn]or b[ks+2*sgn])and(sgn>0 or not b[ks+3*sgn]):ap((ks,ks+2*sgn,0))
 return ms
def M(m):
 global T,C,W,X
 f,t,pr=m;b=B;cap=b[t]
 S.append((m,cap,C))
 b[t]=pr*T or b[f];b[f]=0
 if abs(b[t])>5:
  W,X=(t,X)if T>0 else(W,t)
  if abs(t-f)==2:
   r=112*(T<0)+7*(t>f);b[(t+f)//2]=b[r];b[r]=0
 C&=~Y.get(f,0)&~Y.get(t,0)
 T=-T
def u():
 global T,C,W,X
 m,cap,C=S.pop()
 f,t,pr=m;T=-T;b=B
 b[f]=T if pr else b[t];b[t]=0
 if cap:b[t]=cap
 if abs(b[f])>5:
  W,X=(f,X)if T>0 else(W,f)
  if abs(t-f)==2:
   r=112*(T<0)+7*(t>f);b[r]=b[(t+f)//2];b[(t+f)//2]=0
def L(ms):
 o=[]
 K=(X,W)[T>0];c=z(K,-T)
 for m in ms:
  d=m[0]-K
  if c or B[m[0]]==6*T or not(d%15 and d%17 and d%16 and abs(d)>7):M(m);o.append(m)if not z((W,X)[T>0],T)else 0;u()
  else:o.append(m)
 return o
def ev():
 s=0
 for sq,p in enumerate(B):
  if p:
   a=abs(p);r=sq>>4;f=sq&7;v=V[a]+P[(a-1)*32+(r^7*(p>0))*4+J[f]]
   s+=v*(p>0)*2-v
 return s*T
def f(d,a,b,ply,r):
 global n
 n+=1
 if n>4e4:raise AB
 if d<=0:
  if r>=6:return ev()
  chk=z((W,X)[T<0],-T)
  ms=L(g(0)if chk else g(1))
  if chk and not ms:return-I+ply
  s=ev()if not chk else-E
  if s>=b:return b
  if s>a:a=s
  for m in ms:
   M(m);s=-f(0,-b,-a,ply+1,r+1);u()
   if s>=b:return b
   if s>a:a=s
  return a
 k=(tuple(B),T,C)
 bm=(h:=H.get(k))and h[3]
 if h and h[0]>=d and(h[1]!=1 or h[2]<=a)and(h[1]!=2 or h[2]>=b):return h[2]
 ms=L(g(0))
 if not ms:return-I+ply if z((W,X)[T<0],-T)else 0
 ms.sort(key=lambda m:-(E*(m==bm)+V[abs(B[m[1]])]+20*V[m[2]]))
 ao=a;best=bbm=-E
 for m in ms:
  M(m);s=-f(d-1,-b,-a,ply+1,0);u()
  if s>best:best,bbm=s,m
  if s>a:a=s
  if a>=b:break
 H[k]=(d,(best>=b)*2+(best<=ao),best,bbm)
 return best
def d():
 global n
 n=0
 H.clear()
 ms=L(g(0))
 if not ms:return
 best=ms[0]
 try:
  for i in range(1,64):
   ms.sort(key=best.__ne__)
   a=-E;cb=best
   for m in ms:
    M(m);s=-f(i-1,-E,-a,1,0);u()
    if s>a:a=s;cb=m
   best=cb
 except AB:pass
 return best
def main():
 while True:
  g=p('/game',{})
  if g['status'][0]=='d':break
  while g['status'][0]=='y':
   F(g['fen'])
   m=d()
   g=p('/move',{'game':g['game'],'move':y(m)if m else g['legal_moves'][0]})
__name__[2]=='m'and main()
