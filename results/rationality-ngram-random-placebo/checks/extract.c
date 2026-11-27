/* Read Google Books Ngram v3 1-gram lines from stdin.
   Output (stdout), for alphabetic forms only:
   U <form> <total1850_2019> <c1850> ... <c2019>   untagged form, total >= MINU
   T <form> <TAG> <total1850_2019>                 tagged form (form_TAG), total >= MINT
   Years outside 1850..2019 are ignored. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#define Y0 1850
#define Y1 2019
#define NY (Y1-Y0+1)
#define MINU 2000LL
#define MINT 1000LL
int main(void){
  char *line=NULL; size_t cap=0; ssize_t n;
  long long c[NY];
  while((n=getline(&line,&cap,stdin))>0){
    char *tab=strchr(line,'\t'); if(!tab) continue; *tab=0;
    char *ng=line; char *us=strrchr(ng,'_'); char *tag=NULL;
    if(us && us!=ng && us[1] && isupper((unsigned char)us[1])){ *us=0; tag=us+1; }
    int ok=1; for(char *p=ng;*p;p++){ if(!isalpha((unsigned char)*p)){ok=0;break;} }
    if(!ok || !*ng) continue;
    if(tag){ for(char *p=tag;*p;p++){ if(!isupper((unsigned char)*p)){ok=0;break;} } if(!ok) continue; }
    memset(c,0,sizeof c); long long tot=0;
    char *p=tab+1;
    while(*p && *p!='\n'){
      long y=strtol(p,&p,10); if(*p!=',') break; p++;
      long long m=strtoll(p,&p,10); if(*p!=',') break; p++;
      strtoll(p,&p,10);
      if(y>=Y0 && y<=Y1){ c[y-Y0]+=m; tot+=m; }
      while(*p=='\t') p++;
    }
    if(tag){ if(tot>=MINT) printf("T\t%s\t%s\t%lld\n",ng,tag,tot); }
    else if(tot>=MINU){ printf("U\t%s\t%lld",ng,tot); for(int i=0;i<NY;i++) printf("\t%lld",c[i]); putchar('\n'); }
  }
  return 0;
}
