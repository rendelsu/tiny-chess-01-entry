import os,json
from urllib.request import*
U=os.getenv('MAKEFUN_ENV_URL')
def p(a,b):return json.load(urlopen(U+a,json.dumps(b).encode()))
V=0,100,320,330,500,900,0
P=[ord(c)*5-375 for c in'KKKKUUUUMMOQLLMPKKKOLJIKLMMGKKKKACEECGKKEKMNELNOEKNOELMNCGKLACEEGIIIIKKKIKLMILLMIKMMIMMMILKKGIII'+'KKKKLMMM'+'JKKK'*5+'KKKL'+'GIIJIKKKIKLLJKLLKKLLILLLIKLKGIIJ'+'ECCA'*4+'GEECIGGGOOKKOQMK']
A=(-33,-31,-18,-14,14,18,31,33);D=(-17,-15,15,17);O=(-16,-1,1,16);G=D+O
Y={4:3,116:12,0:2,7:1,112:8,119:4}
B=[0]*128;T=1;C=0;W=4;X=116;S=[];H={};n=0;I=10**5
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
 C=sum(1<<'KQkq'.index(c)for c in w[2]if c in'KQkq')
 W=B.index(6);X=B.index(-6)
def z(s,by):
 for d in(-15*by,-17*by):
  t=s+d
  if not t&0x88 and B[t]==by:return 1
 for O_,pc in((A,2),(G,6)):
  for d in O_:
   t=s+d
   if not t&0x88 and B[t]==by*pc:return 1
 for O_,p1,p2 in((D,3,5),(O,4,5)):
  for d in O_:
   t=s+d
   while not t&0x88:
    if B[t]:
     if B[t]in(by*p1,by*p2):return 1
     break
    t+=d
 return 0
def g(cap):
 ms=[];ap=ms.append
 def h(s,t):
  if(t>>4)==7*(T>0):
   for q in(5,4,3,2):ap((s,t,q))
  else:ap((s,t,0))
 for s,p in enumerate(B):
  if p*T<=0:continue
  a=abs(p)
  if a==1:
   d=16*T;t=s+d
   if not B[t]:
    if(t>>4)==7*(T>0):h(s,t)
    elif not cap:
     ap((s,t,0))
     if(s>>4)==1+5*(T<0)and not B[s+2*d]:ap((s,s+2*d,0))
   for t in(s+d-1,s+d+1):
    if not t&0x88 and B[t]*T<0:h(s,t)
  else:
   for d in(A,D,O,G,G)[a-2]:
    t=s+d
    while not t&0x88:
     if B[t]:
      if B[t]*T<0:ap((s,t,0))
      break
     if not cap:ap((s,t,0))
     if a%4==2:break
     t+=d
 if not cap:
  for msk,ks,sgn in((1,4,1),(2,4,-1),(4,116,1),(8,116,-1)):
   if C&msk and not z(ks,-T)and not z(ks+sgn,-T)and not B[ks+sgn]and not B[ks+2*sgn]and(sgn>0 or not B[ks+3*sgn]):ap((ks,ks+2*sgn,0))
 return ms
def M(m):
 global T,C,W,X
 f,t,pr=m;cap=B[t]
 S.append((m,cap,C))
 B[t]=pr*T or B[f];B[f]=0
 if abs(B[t])>5:
  W,X=(t,X)if T>0 else(W,t)
  if abs(t-f)==2:
   r=112*(T<0)+7*(t>f);B[(t+f)//2]=B[r];B[r]=0
 for x in(f,t):C&=~Y.get(x,0)
 T=-T
def u():
 global T,C,W,X
 m,cap,C=S.pop()
 f,t,pr=m;T=-T
 B[f]=T if pr else B[t];B[t]=0
 if cap:B[t]=cap
 if abs(B[f])>5:
  W,X=(f,X)if T>0 else(W,f)
  if abs(t-f)==2:
   r=112*(T<0)+7*(t>f);B[r]=B[(t+f)//2];B[(t+f)//2]=0
def L(ms):
 o=[]
 [(M(m),o.append(m)if not z((W,X)[T>0],T)else 0,u())for m in ms]
 return o
def ev():
 s=0
 for sq,p in enumerate(B):
  if p:
   a=abs(p);r=sq>>4;f=sq&7;v=V[a]+P[(a-1)*32+(r^7*(p>0))*4+min(f,7-f)]
   s+=v*(p>0)*2-v
 return s*T
def f(d,a,b,ply,r):
 global n
 n+=1
 if n>40000:raise AB
 if d<=0:
  if r>=6:return ev()
  chk=z((W,X)[T<0],-T)
  ms=L(g(0)if chk else g(1))
  if chk and not ms:return-I+ply
  s=ev()if not chk else-I*10
  if s>=b:return b
  if s>a:a=s
  for m in ms:
   M(m);s=-f(0,-b,-a,ply+1,r+1);u()
   if s>=b:return b
   if s>a:a=s
  return a
 k=(tuple(B),T,C)
 bm=(h:=H.get(k))and h[3]
 if h and h[0]>=d and(h[2]<=a if h[1]==1 else h[2]>=b if h[1]==2 else 1):return h[2]
 ms=L(g(0))
 if not ms:return-I+ply if z((W,X)[T<0],-T)else 0
 ms.sort(key=lambda m:-(I*10*(m==bm)+V[abs(B[m[1]])]+9000*bool(m[2])+V[m[2]]))
 ao=a;best=-I*10;bbm=0
 for m in ms:
  M(m);s=-f(d-1,-b,-a,ply+1,0);u()
  if s>best:best=s;bbm=m
  if s>a:a=s
  if a>=b:break
 H[k]=(d,(best>=b)*2+1-(best>ao),best,bbm)
 return best
def d():
 global n
 n=0
 H.clear()
 ms=L(g(0))
 if not ms:return None
 best=ms[0]
 try:
  for i in range(1,64):
   ms.sort(key=best.__ne__)
   a=-I*10;cb=best
   for m in ms:
    M(m);s=-f(i-1,-I*10,-a,1,0);u()
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
   g=p('/move',{'game':g['game'],'move':y(m)if m else min(g['legal_moves'])})
if __name__[2]=='m':main()
