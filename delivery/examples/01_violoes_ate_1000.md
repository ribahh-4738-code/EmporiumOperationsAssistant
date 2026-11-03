# Cenário: violões até R$ 1000 (catálogo + filtro de preço)

**Contexto:** `./chat.sh` · dados em `data/products.csv` · SQL injeta produtos ativos com keyword `viol`/`violão` e `price_brl <= 1000`.

**O que demonstra:** consulta operacional ao catálogo (não inventa preços).

## Conversa

**Cliente:** Quais são as opções de violões disponíveis custando até R$1000?

**Maiara:** Temos várias opções de violões dentro desse valor, por exemplo:

- **Yamaha C40 Nylon Natural** — R$ 599,90 (estoque 12) — clássico nylon, ideal para iniciantes  
- **Tagima Memphis AC-39 Nylon Natural** — R$ 429,90 (15 un.)  
- **Rozini RC-104 Nylon Estudante** — R$ 459,90 (10 un.)  
- **Shelby SN-100 Folk Aço Preto** — R$ 549,00 (5 un.)  
- **Giannini GF-1R Aço Folk Sunburst** — R$ 579,90 (7 un.)  

Posso detalhar algum modelo ou verificar outra faixa de preço se quiser.
