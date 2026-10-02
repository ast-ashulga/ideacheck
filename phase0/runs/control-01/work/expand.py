import duckdb,collections
c=duckdb.connect('data/extract.duckdb',read_only=True)
seeds=['JP-5186041-B2','EP-2383163-B1','EP-2743121-B1','US-8676420-B2','JP-2012090409-A','JP-2007055480-A','KR-20250143405-A','CN-107719447-A','KR-20120045692-A','US-8672081-B2']
print(c.sql(f"select publication_number,family_id,priority_date,cpc from publications where publication_number in {tuple(seeds)}").fetchall())
fams=[r[0] for r in c.sql(f"select distinct family_id from publications where publication_number in {tuple(seeds)}").fetchall()]
print('family members:')
for r in c.sql(f"select publication_number,family_id,title_en[1] from publications where family_id in {tuple(fams)} order by family_id").fetchall(): print(r)
cnt=collections.Counter()
for s in seeds:
    rows=c.sql(f"""with s as (select embedding_v1 e, family_id f from publications where publication_number='{s}')
    select p.publication_number,p.family_id,p.title_en[1],list_cosine_similarity(p.embedding_v1,s.e) sim from publications p,s where p.family_id<>s.f and len(p.embedding_v1)=64 and len(s.e)=64 order by sim desc limit 25""").fetchall()
    for r in rows: cnt[(r[0],r[2])]+=1
print('kNN:')
for k,v in cnt.most_common(60): print(v,k)
sim=collections.Counter()
for r in c.sql(f"select unnest(\"similar\") from publications where publication_number in {tuple(seeds)}").fetchall(): sim[r[0]]+=1
print('similar:')
for k,v in sim.most_common(60):
    t=c.sql(f"select title_en[1] from publications where publication_number='{k}'").fetchall()
    print(v,k,t[0][0] if t else '-')
