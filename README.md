## Relatório Técnico: Otimização de Estoque com Programação Dinâmica

Integrantes:

 rm555152 - Willian Moreira 
rm557421 - Gabriel Galerani
 rm556830 - Gabriel Frageri 
rm557876 - Gustavo Teixeira 
rm554880 - Pedro Paulo

### Introdução
Unidades de diagnóstico lidam com um desafio logístico crítico: a gestão de insumos (reagentes, kits, descartáveis). A falta de um item pode impedir a realização de exames, impactando diretamente o atendimento ao paciente. Por outro lado, o excesso de estoque leva a custos de armazenagem (especialmente para itens refrigerados) e ao risco de perdas por vencimento. O registro impreciso do consumo diário agrava esse problema, tornando o controle manual ineficiente.

Este projeto propõe uma solução baseada em Programação Dinâmica para modelar o problema de controle de estoque. O objetivo é determinar uma política de reposição ótima que minimize os custos totais (pedido, armazenagem e falta) ao longo de um horizonte de tempo, melhorando a visibilidade do consumo e reduzindo desperdícios.

**1. Formulação do Problema (Modelo de Programação Dinâmica)**

Para modelar o problema, precisamos definir seus quatro componentes fundamentais. Vamos considerar um único tipo de insumo e um horizonte de planejamento de T dias.

**a. Estados (*S*)**

O estado do sistema precisa conter toda a informação necessária para tomar uma decisão ótima para o futuro. Em qualquer dia t, a única informação que precisamos para decidir sobre a reposição é a quantidade de insumos atualmente em estoque.

- Estado (*s t*): É definido pelo par (*t,i*), onde:

  - t: O dia atual no horizonte de planejamento (*t∈{0,1,...,T}*).

  - i: O nível do inventário no início do dia *t (i∈{0,1,...,I max})*, onde I max é a capacidade máxima de armazenamento.


**b. Decisões (*A*)**

Em cada estado (*t,i*), a decisão a ser tomada é sobre a quantidade de insumos a ser pedida.

- Decisão (*x t*): É a quantidade de insumos a serem pedidos no dia t. A restrição é que o estoque após o pedido não pode exceder a capacidade máxima: *x t∈{0,1,...,I max
−i}*.

**c. Função de Transição *(T(s t,x t))***

A função de transição descreve como o estado do sistema evolui de um dia para o outro, dada uma decisão. O estado no dia t+1 depende do estado em t, da decisão ***x***t e da demanda (consumo) ***d***t no dia *t*.

- O nível de estoque após receber o pedido é *i**+***x***t*.

- A demanda dt é então subtraída. Como o consumo não é registrado com precisão, usaremos uma previsão de demanda para cada dia.

- O nível de estoque no início do dia *t+1* será: *it+1 =max(0,i+xt −dt)*. O *max(0,...)* garante que o estoque não fique negativo.

Portanto, a transição de estado é: *st+1 =(t+1,max(0,i+xt−dt))*.

**d. Função Objetivo (Custo)**

O objetivo é minimizar o custo total acumulado ao longo do horizonte de planejamento. O custo em um dia t, dado o estado (t,i) e a decisão xt, é a soma de três componentes:

1. **Custo de Pedido**: Um custo fixo K se um pedido é feito (xt > 0), mais um custo variável c por unidade pedida.

<img width="316" height="81" alt="image" src="https://github.com/user-attachments/assets/734d0371-380b-463b-8402-a331306a56f3" />


2. **Custo de Armazenagem (Holding Cost)**: Um custo h por unidade mantida em estoque no final do dia.

<img width="346" height="47" alt="image" src="https://github.com/user-attachments/assets/6aadd62a-49fa-472d-b363-ba7079bf70a9" />


3. **Custo de Falta (Shortage Cost)**: Um custo de penalidade p por unidade de demanda não atendida. Este custo representa a urgência de não deixar faltar um insumo crítico.

<img width="347" height="44" alt="image" src="https://github.com/user-attachments/assets/10b115f0-9cbf-4c49-9e3e-f5242d01784d" />

A **relação de recorrência de Bellman** para o custo mínimo, V(t,i), a partir do estado (t,i) até o final do horizonte é:

<img width="554" height="58" alt="image" src="https://github.com/user-attachments/assets/b6faacc9-17ab-475d-9783-72da34cbce48" />

Onde *C(t,i,xt)* é a soma dos três custos imediatos.

- **Caso Base**: O custo no final do horizonte de planejamento é zero: *V(T,i)=0* para todo *i*.

O objetivo final é encontrar *V(0,i0)*, onde ***i***0 é o estoque inicial.

## 2. Implementação em Python
A seguir, apresentamos as três versões do algoritmo: recursiva, com memorização e iterativa.

**Estrutura do Código**




    import sys
    
    # Para aumentar o limite de recursão na versão puramente recursiva
    sys.setrecursionlimit(2000)
    
    # --- Parâmetros do Problema ---
    # Custos
    CUSTO_FIXO_PEDIDO = 50  # (K) Custo administrativo/frete por pedido
    CUSTO_POR_UNIDADE = 2   # (c) Custo de compra por item
    CUSTO_ARMAZENAGEM = 1   # (h) Custo por item em estoque no fim do dia
    CUSTO_FALTA = 10        # (p) Penalidade alta por item em falta
    
    # Restrições
    HORIZONTE_DIAS = 30     # (T) Período de planejamento
    ESTOQUE_MAXIMO = 100    # (I_max) Capacidade máxima de armazenamento
    ESTOQUE_INICIAL = 20    # (i_0) Estoque no dia 0
    
    # Previsão de Demanda Diária (d_t)
    # Em um cenário real, isso viria de um modelo de forecasting
    demanda_diaria = [15, 20, 10, 25, 18, 30, 12, 15, 22, 17,
                      28, 19, 13, 21, 24, 16, 26, 11, 19, 23,
                      20, 27, 14, 18, 22, 25, 15, 20, 10, 30]
    
    # --- 1. Versão Recursiva Pura ---
    def solve_recursive(t, i):
        """Calcula o custo mínimo de forma recursiva."""
        if t == HORIZONTE_DIAS:
            return 0
    
        min_custo = float('inf')
    
        # Itera sobre todas as decisões possíveis (quanto pedir)
        for x in range(ESTOQUE_MAXIMO - i + 1):
            # --- Calcula os custos imediatos para a decisão x ---
            custo_pedido = (CUSTO_FIXO_PEDIDO + CUSTO_POR_UNIDADE * x) if x > 0 else 0
            
            demanda_atual = demanda_diaria[t]
            estoque_apos_pedido = i + x
    
            custo_armazenagem = CUSTO_ARMAZENAGEM * max(0, estoque_apos_pedido - demanda_atual)
            custo_falta = CUSTO_FALTA * max(0, demanda_atual - estoque_apos_pedido)
    
            custo_imediato = custo_pedido + custo_armazenagem + custo_falta
            
            # --- Transição para o próximo estado ---
            proximo_estoque = max(0, estoque_apos_pedido - demanda_atual)
            
            custo_futuro = solve_recursive(t + 1, proximo_estoque)
            
            min_custo = min(min_custo, custo_imediato + custo_futuro)
            
        return min_custo
    
    # --- 2. Versão com Memorização (Top-Down) ---
    memo = {} # Cache para armazenar resultados (t, i) -> custo
    
    def solve_memoization(t, i):
        """Calcula o custo mínimo usando recursão com memorização."""
        if t == HORIZONTE_DIAS:
            return 0
        if (t, i) in memo:
            return memo[(t, i)]
    
        min_custo = float('inf')
    
        # Itera sobre todas as decisões possíveis (quanto pedir)
        for x in range(ESTOQUE_MAXIMO - i + 1):
            custo_pedido = (CUSTO_FIXO_PEDIDO + CUSTO_POR_UNIDADE * x) if x > 0 else 0
            
            demanda_atual = demanda_diaria[t]
            estoque_apos_pedido = i + x
    
            custo_armazenagem = CUSTO_ARMAZENAGEM * max(0, estoque_apos_pedido - demanda_atual)
            custo_falta = CUSTO_FALTA * max(0, demanda_atual - estoque_apos_pedido)
    
            custo_imediato = custo_pedido + custo_armazenagem + custo_falta
            
            proximo_estoque = max(0, estoque_apos_pedido - demanda_atual)
            
            custo_futuro = solve_memoization(t + 1, proximo_estoque)
            
            min_custo = min(min_custo, custo_imediato + custo_futuro)
            
        memo[(t, i)] = min_custo
        return min_custo
    
    # --- 3. Versão Iterativa (Bottom-Up) ---
    def solve_bottom_up():
        """Calcula o custo mínimo e a política ótima de forma iterativa."""
        # dp[t][i] armazena o custo mínimo do dia t até o fim, com estoque i
        dp = [[0] * (ESTOQUE_MAXIMO + 1) for _ in range(HORIZONTE_DIAS + 1)]
        
        # politica[t][i] armazena a decisão ótima (quanto pedir)
        politica = [[0] * (ESTOQUE_MAXIMO + 1) for _ in range(HORIZONTE_DIAS)]
    
        # Itera de trás para frente no tempo
        for t in range(HORIZONTE_DIAS - 1, -1, -1):
            # Itera sobre todos os possíveis níveis de estoque
            for i in range(ESTOQUE_MAXIMO + 1):
                min_custo = float('inf')
                melhor_x = 0
    
                # Itera sobre todas as decisões possíveis
                for x in range(ESTOQUE_MAXIMO - i + 1):
                    custo_pedido = (CUSTO_FIXO_PEDIDO + CUSTO_POR_UNIDADE * x) if x > 0 else 0
                    
                    demanda_atual = demanda_diaria[t]
                    estoque_apos_pedido = i + x
    
                    custo_armazenagem = CUSTO_ARMAZENAGEM * max(0, estoque_apos_pedido - demanda_atual)
                    custo_falta = CUSTO_FALTA * max(0, demanda_atual - estoque_apos_pedido)
    
                    custo_imediato = custo_pedido + custo_armazenagem + custo_falta
                    
                    proximo_estoque = max(0, estoque_apos_pedido - demanda_atual)
                    
                    custo_total = custo_imediato + dp[t + 1][proximo_estoque]
                    
                    if custo_total < min_custo:
                        min_custo = custo_total
                        melhor_x = x
                
                dp[t][i] = min_custo
                politica[t][i] = melhor_x
                
        # Recupera a política ótima a partir do estado inicial
        politica_otima = []
        estoque_atual = ESTOQUE_INICIAL
        for t in range(HORIZONTE_DIAS):
            pedido = politica[t][estoque_atual]
            politica_otima.append((t, estoque_atual, pedido))
            
            demanda = demanda_diaria[t]
            estoque_apos_pedido = estoque_atual + pedido
            estoque_atual = max(0, estoque_apos_pedido - demanda)
    
        return dp[0][ESTOQUE_INICIAL], politica_otima
    
    # --- Garantia de Resultados ---
    if __name__ == "__main__":
        print("Iniciando cálculos...")
    
        # A versão recursiva é muito lenta para um horizonte grande,
        # então usamos um horizonte menor apenas para demonstração de igualdade.
        HORIZONTE_DIAS_CURTO = 5
        demanda_curta = demanda_diaria[:HORIZONTE_DIAS_CURTO]
        
        # Redefine o escopo global para a função recursiva de teste
        globals()['HORIZONTE_DIAS'] = HORIZONTE_DIAS_CURTO
        globals()['demanda_diaria'] = demanda_curta
        
        # Custo_rec = solve_recursive(0, ESTOQUE_INICIAL) # Pode ser extremamente lento
        
        memo.clear()
        custo_memo_curto = solve_memoization(0, ESTOQUE_INICIAL)
        
        # Redefine para o problema principal
        globals()['HORIZONTE_DIAS'] = 30
        globals()['demanda_diaria'] = [15, 20, 10, 25, 18, 30, 12, 15, 22, 17,
                                       28, 19, 13, 21, 24, 16, 26, 11, 19, 23,
                                       20, 27, 14, 18, 22, 25, 15, 20, 10, 30]
        
        custo_iterativo_curto, _ = solve_bottom_up() # Temporariamente recalcula com T curto
    
        print(f"\n--- Verificação de Igualdade (Horizonte T={HORIZONTE_DIAS_CURTO}) ---")
        print(f"Custo Mínimo (Memorização): {custo_memo_curto:.2f}")
        # O resultado iterativo precisa ser recalculado para o horizonte curto
        globals()['HORIZONTE_DIAS'] = HORIZONTE_DIAS_CURTO
        globals()['demanda_diaria'] = demanda_curta
        custo_iterativo_curto, _ = solve_bottom_up()
        print(f"Custo Mínimo (Iterativo):   {custo_iterativo_curto:.2f}")
        assert abs(custo_memo_curto - custo_iterativo_curto) < 1e-9, "Resultados não são iguais!"
        print("Resultados da versão com memorização e iterativa são idênticos. (Sucesso!)")
    
        # Resolve o problema completo (T=30)
        print("\n--- Resolvendo o Problema Completo (Horizonte T=30) ---")
        globals()['HORIZONTE_DIAS'] = 30
        globals()['demanda_diaria'] = [15, 20, 10, 25, 18, 30, 12, 15, 22, 17,
                                       28, 19, 13, 21, 24, 16, 26, 11, 19, 23,
                                       20, 27, 14, 18, 22, 25, 15, 20, 10, 30]
    
        custo_total_otimo, politica_execucao = solve_bottom_up()
        print(f"\nCusto Total Mínimo para {HORIZONTE_DIAS} dias: {custo_total_otimo:.2f}")
        print("\nPolítica de Reposição Ótima (Dia, Estoque no Início, Pedido):")
        for dia, estoque, pedido in politica_execucao:
            if pedido > 0:
                print(f"Dia {dia:2d}: Com {estoque:3d} itens, PEDIR {pedido:3d} unidades.")
            else:
                print(f"Dia {dia:2d}: Com {estoque:3d} itens, NÃO pedir.")



### Resultado: 


    Iniciando cálculos...
    
    --- Verificação de Igualdade (Horizonte T=5) ---
    Custo Mínimo (Memorização): 269.00
    Custo Mínimo (Iterativo):   269.00
    Resultados da versão com memorização e iterativa são idênticos. (Sucesso!)
    
    --- Resolvendo o Problema Completo (Horizonte T=30) ---
    
    Custo Total Mínimo para 30 dias: 2103.00
    
    Política de Reposição Ótima (Dia, Estoque no Início, Pedido):
    Dia  0: Com  20 itens, NÃO pedir.
    Dia  1: Com   5 itens, PEDIR  25 unidades.
    Dia  2: Com  10 itens, NÃO pedir.
    Dia  3: Com   0 itens, PEDIR  43 unidades.
    Dia  4: Com  18 itens, NÃO pedir.
    Dia  5: Com   0 itens, PEDIR  57 unidades.
    Dia  6: Com  27 itens, NÃO pedir.
    Dia  7: Com  15 itens, NÃO pedir.
    Dia  8: Com   0 itens, PEDIR  39 unidades.
    Dia  9: Com  17 itens, NÃO pedir.
    Dia 10: Com   0 itens, PEDIR  60 unidades.
    Dia 11: Com  32 itens, NÃO pedir.
    Dia 12: Com  13 itens, NÃO pedir.
    Dia 13: Com   0 itens, PEDIR  61 unidades.
    Dia 14: Com  40 itens, NÃO pedir.
    Dia 15: Com  16 itens, NÃO pedir.
    Dia 16: Com   0 itens, PEDIR  56 unidades.
    Dia 17: Com  30 itens, NÃO pedir.
    Dia 18: Com  19 itens, NÃO pedir.
    Dia 19: Com   0 itens, PEDIR  43 unidades.
    Dia 20: Com  20 itens, NÃO pedir.
    Dia 21: Com   0 itens, PEDIR  41 unidades.
    Dia 22: Com  14 itens, NÃO pedir.
    Dia 23: Com   0 itens, PEDIR  40 unidades.
    Dia 24: Com  22 itens, NÃO pedir.
    Dia 25: Com   0 itens, PEDIR  40 unidades.
    Dia 26: Com  15 itens, NÃO pedir.
    Dia 27: Com   0 itens, PEDIR  30 unidades.
    Dia 28: Com  10 itens, NÃO pedir.
    Dia 29: Com   0 itens, PEDIR  30 unidades.


## 3. Explicação das Estruturas e Algoritmos

### a. Estruturas de Dados**

- **Matriz 2D (list de list em Python)**: É a estrutura central na solução iterativa (bottom-up).

  - dp[t][i]: Armazena o resultado do subproblema "qual o custo mínimo do dia t em diante, começando com i unidades de estoque". A matriz é ideal porque o estado é definido por duas dimensões (t e i), permitindo acesso direto e eficiente ao resultado de qualquer subproblema já resolvido.

  - politica[t][i]: Uma matriz auxiliar que armazena a decisão ótima (x) para cada estado (t, i). É essencial para reconstruir a sequência de ações após o cálculo dos custos ótimos.

- **Dicionário (dict em Python)**: Usado na solução com memorização (memo).

  - Funciona como um "cache" ou tabela de memorização. A chave do dicionário é uma tupla (t, i) representando o estado, e o valor é o custo mínimo calculado para esse estado. É mais flexível que uma matriz se os estados fossem esparsos, mas para este problema, uma matriz seria igualmente eficiente.

- **Listas (list em Python)**:

  - demanda_diaria: Armazena a previsão de consumo para cada dia do horizonte. Uma lista é a estrutura mais natural para representar essa série temporal.

### b. Algoritmos

**1. Recursão Pura (solve_recursive)**

  - Como foi usado: Esta é a tradução direta da relação de recorrência de Bellman para uma função. A função se chama recursivamente para resolver o problema para o dia seguinte (t+1), explorando todas as decisões possíveis (x) no dia atual.

  - Contexto do Problema: Ajuda a validar a lógica da formulação matemática. No entanto, é computacionalmente inviável para problemas realistas, pois recalcula os mesmos subproblemas (mesmo estado (t,i)) múltiplas vezes, levando a uma complexidade exponencial.

**2. Memorização / PD Top-Down (solve_memoization)**

  - Como foi usado: É uma otimização da abordagem recursiva. Antes de iniciar o cálculo para um estado (t, i), o algoritmo verifica se o resultado já está no cache (memo). Se estiver, retorna o valor salvo. Caso contrário, calcula, salva no cache e depois retorna.

  - Contexto do Problema: Resolve o problema da ineficiência da recursão pura, garantindo que cada subproblema seja resolvido apenas uma vez. Mantém a estrutura lógica da recursão, que pode ser mais intuitiva.

**3. Iterativo / PD Bottom-Up (solve_bottom_up)**

  - Como foi usado: Esta abordagem elimina a recursão. Ela preenche a tabela dp de forma sistemática, começando pelos casos-base (o último dia, t=T-1) e avançando para trás até o início (t=0). Ao calcular dp[t][i], os valores necessários (dp[t+1][...]) já foram calculados e estão prontos na tabela.

  - Contexto do Problema: É a abordagem mais eficiente em termos de desempenho (velocidade e consumo de memória, pois não sobrecarrega a pilha de recursão). Ela não só calcula o custo ótimo, mas facilita a reconstrução da política ótima (a sequência de decisões) ao armazenar a melhor decisão em cada estado na matriz politica.
